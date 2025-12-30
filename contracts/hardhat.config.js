require('@nomicfoundation/hardhat-toolbox');

/****
 * Minimal Hardhat config for compiling A2ABadge.sol
 * To deploy to testnet, set environment variables in scripts/deploy_testnet.js
 */
module.exports = {
  solidity: {
    version: '0.8.20',
    settings: {
      optimizer: { enabled: true, runs: 200 }
    }
  },
  networks: {
    hardhat: {},
  }
};
