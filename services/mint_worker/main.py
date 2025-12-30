import os
import json
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
from google.cloud import firestore, secretmanager
from flask import Flask, request, jsonify

app = Flask(__name__)
db = firestore.Client()
secret_client = secretmanager.SecretManagerServiceClient()

RPC_URL = os.environ.get('CHAIN_RPC')  # e.g., https://rpc-mumbai.maticvigil.com
PRIVATE_KEY_SECRET = os.environ.get('PRIVATE_KEY_SECRET')  # Secret Manager resource name
CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
CONTRACT_ABI_PATH = os.environ.get('CONTRACT_ABI_PATH', '/secrets/abi.json')

w3 = Web3(Web3.HTTPProvider(RPC_URL))
# If using Polygon PoS testnets, add POA middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


def get_private_key():
    # TODO: use appropriate Secret Manager access patterns and IAM
    name = PRIVATE_KEY_SECRET
    resp = secret_client.access_secret_version(request={"name": name})
    return resp.payload.data.decode('utf-8').strip()


def load_contract():
    with open(CONTRACT_ABI_PATH, 'r') as f:
        abi = json.load(f)
    return w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)


@app.route('/mint', methods=['POST'])
def handle_mint():
    body = request.get_json(silent=True) or {}
    claim_id = body.get('claimId')
    if not claim_id:
        return jsonify({'error': 'missing claimId'}), 400

    # Verify task secret header to ensure only Cloud Tasks can call this endpoint
    expected_secret = os.environ.get('TASK_SECRET')
    if expected_secret:
        provided = request.headers.get('X-Task-Secret')
        if not provided or provided != expected_secret:
            return jsonify({'error': 'unauthorized'}), 401

    claim_ref = db.collection('claims').document(claim_id)

    def _txn_process(txn):
        doc = txn.get(claim_ref)
        if not doc.exists:
            return {'error': 'claim not found', 'code': 404}
        data = doc.to_dict()
        status = data.get('status')
        # If already minted, return early
        if status == 'minted':
            return {'status': 'already minted', 'tx': data.get('txHash')}
        # Only process if queued (to implement idempotency / locking)
        if status != 'queued':
            return {'error': f'unexpected status {status}', 'code': 409}
        # set to processing
        txn.update(claim_ref, {'status': 'processing', 'processingAt': firestore.SERVER_TIMESTAMP})
        return {'ok': True, 'data': data}

    try:
        res = db.run_transaction(_txn_process)
        if res.get('error'):
            return jsonify({'error': res['error']}), res.get('code', 400)
        claim = res['data']

        contract = load_contract()
        private_key = get_private_key()
        relayer = w3.eth.account.from_key(private_key).address

        # Prepare mint call - deterministic token id from claim id hash
        metadata = claim.get('metadata', {})
        token_id = int.from_bytes(hashlib.sha256(claim_id.encode()).digest()[:8], 'big')
        token_uri = metadata.get('tokenURI') or metadata.get('uri') or ''
        soulbound = bool(metadata.get('soulbound', False))

        txn = contract.functions.mint(claim.get('wallet'), token_id, token_uri, soulbound).build_transaction({
            'from': relayer,
            'nonce': w3.eth.get_transaction_count(relayer),
            'gas': 500_000,
            'gasPrice': w3.eth.gas_price
        })

        signed = w3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        claim_ref.update({'status': 'minted', 'txHash': tx_hash.hex(), 'tokenId': token_id, 'mintedAt': firestore.SERVER_TIMESTAMP})
        return jsonify({'status': 'minted', 'txHash': tx_hash.hex()}), 200

    except Exception as e:
        # mark as error for visibility and allow retry
        try:
            claim_ref.update({'status': 'error', 'error': str(e)})
        except Exception:
            pass
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})
