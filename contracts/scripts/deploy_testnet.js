const hre = require('hardhat');

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log('Deploying contracts with account:', deployer.address);
  const A2ABadge = await hre.ethers.getContractFactory('A2ABadge');
  const contract = await A2ABadge.deploy('A2A Badge', 'A2AB', deployer.address, 250);
  await contract.deployed();
  console.log('A2ABadge deployed to:', contract.address);

  // write deployed address to a JSON file for CI/consumers
  const fs = require('fs');
  fs.mkdirSync('deployed', { recursive: true });
  const deployedInfo = { address: contract.address, chain: hre.network.name, tx: contract.deployTransaction.hash };
  fs.writeFileSync('deployed/address.json', JSON.stringify(deployedInfo, null, 2));

  // Attempt verification if POLYGONSCAN_API_KEY is set
  if (process.env.POLYGONSCAN_API_KEY) {
    console.log('Attempting contract verification on Polygonscan...');
    try {
      await hre.run('verify:verify', {
        address: contract.address,
        constructorArguments: ['A2A Badge', 'A2AB', deployer.address, 250]
      });
      console.log('Verified on Polygonscan');
    } catch (err) {
      console.warn('Verification failed or skipped:', err.message || err);
    }
  } else {
    console.log('POLYGONSCAN_API_KEY not set; skipping verification.');
  }
}



main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
