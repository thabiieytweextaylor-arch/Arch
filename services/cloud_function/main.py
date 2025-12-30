import os
import json
import hashlib
import requests
from google.cloud import firestore, tasks_v2, secretmanager
from google.cloud.tasks_v2.types import HttpMethod
from flask import Flask, request, jsonify
from eth_account.messages import encode_defunct
from eth_account import Account

app = Flask(__name__)
db = firestore.Client()
PROJECT_ID = os.environ.get('GCP_PROJECT')
QUEUE_PATH = os.environ.get('MINT_QUEUE_PATH')  # e.g., projects/.../locations/.../queues/...
MINT_WORKER_URL = os.environ.get('MINT_WORKER_URL')
TASK_SA = os.environ.get('TASK_SA')
PLAY_GAMES_BASE = "https://www.googleapis.com/games/v1"


def make_claim_id(player_id: str, achievement_id: str) -> str:
    return hashlib.sha256(f"{player_id}:{achievement_id}".encode()).hexdigest()


def verify_wallet_signature(wallet: str, nonce: str, signature: str) -> bool:
    # Expect signature of the nonce (utf-8) with ECDSA (Ethereum)
    message = encode_defunct(text=nonce)
    try:
        recovered = Account.recover_message(message, signature=signature)
        return recovered.lower() == wallet.lower()
    except Exception:
        return False


@app.route('/claim', methods=['POST'])
def claim_reward():
    data = request.get_json(silent=True) or {}
    # expected: { "achievementId": "...", "accessToken": "...", "walletAddress": "...", "nonce": "...", "signature": "..." }
    achievement_id = data.get('achievementId')
    access_token = data.get('accessToken')
    wallet = data.get('walletAddress')
    signature = data.get('signature')
    nonce = data.get('nonce')

    if not all([achievement_id, access_token, wallet, signature, nonce]):
        return jsonify({"error": "missing parameters"}), 400

    # Verify Google access token by calling Play Games API for this achievement
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        r = requests.get(f"{PLAY_GAMES_BASE}/players/me/achievements/{achievement_id}", headers=headers, timeout=10)
    except requests.RequestException as e:
        return jsonify({"error": "games API request failed", "detail": str(e)}), 502

    if r.status_code != 200:
        return jsonify({"error": "failed to verify achievement", "detail": r.text}), 401

    ach = r.json()
    if ach.get('achievementState') != 'UNLOCKED':
        return jsonify({"error": "achievement not unlocked"}), 403

    # Resolve player id from the games API response
    player_id = ach.get('player', {}).get('playerId') or ach.get('playerId') or 'unknown_player'
    claim_id = make_claim_id(player_id, achievement_id)

    # verify wallet ownership by signature of nonce (server-supplied)
    if not verify_wallet_signature(wallet, nonce, signature):
        return jsonify({"error": "invalid wallet signature"}), 401

    # Idempotency: check if claim already processed or queued
    claim_doc_ref = db.collection('claims').document(claim_id)

    def _txn(txn):
        doc = txn.get(claim_doc_ref)
        if doc.exists:
            return doc.to_dict()
        # Fetch mapping for achievement -> token metadata
        mapping_doc = db.collection('mappings').document(achievement_id).get()
        mapping = mapping_doc.to_dict() if mapping_doc.exists else None
        if not mapping:
            raise Exception("No token mapping for this achievement")
        claim_data = {
            'playerId': player_id,
            'achievementId': achievement_id,
            'wallet': wallet,
            'status': 'queued',
            'metadata': mapping,
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        txn.set(claim_doc_ref, claim_data)
        return claim_data

    try:
        claim = db.run_transaction(_txn)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Enqueue Cloud Task for mint worker
    try:
        client = tasks_v2.CloudTasksClient()
        payload = json.dumps({'claimId': claim_id}).encode()
        # include a shared task secret header for Cloud Run verification
        task_secret = os.environ.get('TASK_SECRET')
        headers = {'Content-Type': 'application/json'}
        if task_secret:
            headers['X-Task-Secret'] = task_secret

        task = {
            'http_request': {
                'http_method': HttpMethod.POST,
                'url': MINT_WORKER_URL,
                'oidc_token': {'service_account_email': TASK_SA},
                'headers': headers,
                'body': payload
            }
        }
        client.create_task(parent=QUEUE_PATH, task=task)
    except Exception as e:
        # If task enqueue fails, set claim to error for visibility
        claim_doc_ref.update({'status': 'error', 'error': f'enqueue_failed: {str(e)}'})
        return jsonify({"error": "failed to enqueue mint task", "detail": str(e)}), 502

    return jsonify({"claimId": claim_id, "status": "queued"}), 202


# Simple health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})
