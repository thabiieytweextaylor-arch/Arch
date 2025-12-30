# Deploying A2ABadge to Polygon Mumbai (Testnet)

This document explains how to deploy the `A2ABadge` contract to Polygon Mumbai using the provided Hardhat script and the GitHub Actions workflow.

Required secrets (GitHub repository secrets):
- `POLYGON_MUMBAI_RPC`: RPC URL for Polygon Mumbai (Alchemy / Infura / public RPC)
- `DEPLOYER_PRIVATE_KEY`: hex private key for deployer (no 0x prefix or include it; the script accepts either)
- `POLYGONSCAN_API_KEY` (optional): Polygonscan API key to verify contracts

Local deploy (recommended for testing):
1. Install dependencies:
   cd contracts && npm install
2. Export environment variables locally (example):
   export POLYGON_MUMBAI_RPC="https://polygon-mumbai.g.alchemy.com/v2/<key>"
   export DEPLOYER_PRIVATE_KEY="0xYOURKEY"
   export POLYGONSCAN_API_KEY="<key>"  # optional
3. Run deploy script:
   npx hardhat run scripts/deploy_testnet.js --network mumbai

The script writes `contracts/deployed/address.json` containing the deployed address, network and transaction hash.

GitHub Actions deploy:
- The workflow `Deploy contracts to Polygon Mumbai` can be triggered manually (workflow_dispatch) or by pushing a tag matching `deploy-*`.
- Add the following repository secrets in your repo settings: `POLYGON_MUMBAI_RPC`, `DEPLOYER_PRIVATE_KEY`, and optionally `POLYGONSCAN_API_KEY`.
- After adding secrets, trigger the workflow manually via the Actions tab or from the command line with `gh workflow run "Deploy contracts to Polygon Mumbai"`.
- It will output the deployed address as an artifact named `deployed-address`.

Security notes:
- Use a deployer account with minimal funds on testnet.
- For production deployments, use secure key management and avoid storing private keys directly in repository or logs.
