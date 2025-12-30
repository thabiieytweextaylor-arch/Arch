# GCP Deployment Steps (summary)

1. Setup
   - Create GCP Project, enable billing and these APIs: Cloud Functions, Cloud Run, Firestore, Cloud Tasks, Secret Manager, Cloud Build.

2. Firestore
   - Create Firestore database in production mode and set security rules.

3. Secrets & IAM
   - Store relayer private key in Secret Manager and restrict access to the Mint Worker service account.
   - Create a service account for Cloud Tasks to call Cloud Run with OIDC tokens.

4. Deploy Cloud Function (Claim endpoint)
   - `gcloud functions deploy claim --entry-point app --runtime python311 --trigger-http --allow-unauthenticated --set-env-vars MINT_WORKER_URL=...,MINT_QUEUE_PATH=...,TASK_SA=...`

5. Create Cloud Tasks queue and set up Cloud Run mint worker
   - Deploy mint worker to Cloud Run with e.g., `gcloud run deploy mint-worker --image gcr.io/PROJECT/mint-worker --platform managed`.
   - Ensure `CONTRACT_ADDRESS`, `CONTRACT_ABI_PATH`, `PRIVATE_KEY_SECRET`, `CHAIN_RPC` ENV vars are set.

6. Monitoring & Billing
   - Add alerts for high error rate, task queue backlog, and failed mints. Export billing and BigQuery analytics as needed.

7. Test on staging network
   - Use Polygon Mumbai or Immutable testnet. Verify end-to-end: claim → queued → minted → tx visible.

8. Production rollout
   - White-list developer apps, prepare Play Console declarations, rate-limit claims, and monitor mint economics.
