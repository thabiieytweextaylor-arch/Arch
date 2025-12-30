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
    mumbai: {
      url: process.env.POLYGON_MUMBAI_RPC || process.env.POLYGON_RPC_URL || '',
      accounts: process.env.DEPLOYER_PRIVATE_KEY ? [process.env.DEPLOYER_PRIVATE_KEY] : []
    }
  },
  etherscan: {
    apiKey: {
      polygonMumbai: process.env.POLYGONSCAN_API_KEY || process.env.POLYGONSCAN_KEY || ''
    }
  }
};
