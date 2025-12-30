const hre = require('hardhat');

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log('Deploying contracts with account:', deployer.address);
  const A2ABadge = await hre.ethers.getContractFactory('A2ABadge');
  const contract = await A2ABadge.deploy('A2A Badge', 'A2AB', deployer.address, 250);
  await contract.deployed();
  console.log('A2ABadge deployed to:', contract.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
