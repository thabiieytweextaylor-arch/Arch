# Arch — Achievement-to-Asset Bridge (A2A)

This repository contains reference implementations and docs for the Achievement-to-Asset Bridge: a middleware platform that verifies Google Play Games achievements server-side and mints corresponding Web3 assets (NFTs / Soulbound) on low-fee chains (Polygon / Immutable X).

Structure:
- `services/cloud_function`: Claim endpoint (Cloud Function)
- `services/mint_worker`: Cloud Run worker that performs minting
- `contracts`: Solidity contract `A2ABadge.sol` (ERC721 + SBT support)
- `docs`: integration and deployment guides
- `.github`: CI workflows

See `docs/*` for usage and deployment steps.

Contracts deployment

- Use the Hardhat scripts in `contracts/` to deploy to Polygon Mumbai (testnet).
- A GitHub Actions workflow `Deploy contracts to Polygon Mumbai` (`.github/workflows/deploy_contracts.yml`) can be triggered manually or by pushing a `deploy-*` tag. Ensure repository secrets `POLYGON_MUMBAI_RPC`, `DEPLOYER_PRIVATE_KEY`, and optionally `POLYGONSCAN_API_KEY` are set.

