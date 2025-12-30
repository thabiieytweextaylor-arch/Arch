// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";

contract A2ABadge is ERC721URIStorage, AccessControl, ERC2981 {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    mapping(uint256 => bool) public soulbound;

    constructor(string memory name, string memory symbol, address royaltyReceiver, uint96 feeNumerator) ERC721(name, symbol) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setDefaultRoyalty(royaltyReceiver, feeNumerator); // feeNumerator example: 250 = 2.5% (denominator 10000)
    }

    function mint(address to, uint256 tokenId, string memory uri, bool _soulbound) external onlyRole(MINTER_ROLE) {
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        soulbound[tokenId] = _soulbound;
    }

    // Prevent transfers for soulbound tokens
    function _beforeTokenTransfer(address from, address to, uint256 tokenId) internal virtual override {
        super._beforeTokenTransfer(from, to, tokenId);
        if (soulbound[tokenId] && from != address(0)) {
            revert("SBT: non-transferable");
        }
    }

    // EIP-2981 support
    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721, AccessControl, ERC2981) returns (bool) {
        return ERC721.supportsInterface(interfaceId) || AccessControl.supportsInterface(interfaceId) || ERC2981.supportsInterface(interfaceId);
    }
}
