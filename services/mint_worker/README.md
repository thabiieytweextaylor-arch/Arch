Mint Worker

This service processes queued claims and performs on-chain minting using a relayer private key stored in Secret Manager.

Environment variables:
- CHAIN_RPC - RPC URL for chain
- PRIVATE_KEY_SECRET - Secret Manager resource name: projects/<proj>/secrets/<name>/versions/latest
- CONTRACT_ADDRESS - Deployed contract address
- CONTRACT_ABI_PATH - Path to contract ABI JSON
- TASK_SECRET - (optional) shared secret header to validate Cloud Tasks calls

Run locally (for tests):
- export TASK_SECRET=testsecret
- pytest
