# Arch — Achievement-to-Asset Bridge (A2A)

This repository contains reference implementations and docs for the Achievement-to-Asset Bridge: a middleware platform that verifies Google Play Games achievements server-side and mints corresponding Web3 assets (NFTs / Soulbound) on low-fee chains (Polygon / Immutable X).

Structure:
- `services/cloud_function`: Claim endpoint (Cloud Function)
- `services/mint_worker`: Cloud Run worker that performs minting
- `contracts`: Solidity contract `A2ABadge.sol` (ERC721 + SBT support)
- `docs`: integration and deployment guides
- `.github`: CI workflows

See `docs/*` for usage and deployment steps.
