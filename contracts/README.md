A2A Badge contracts

This folder contains the sample ERC-721 / Soulbound contract used by the Achievement-to-Asset Bridge.

Quick start (Hardhat):

1. npm init -y && npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox @openzeppelin/contracts
2. Create a Hardhat config and compile:
   npx hardhat compile

The sample contract is `A2ABadge.sol` and supports a MINTER_ROLE, EIP-2981 royalties and optional soulbound tokens.
