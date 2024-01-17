// SPDX-License-Identifier: GPL-3.0-or-later
// Yannie Wu, ylw4sj

pragma solidity ^0.8.21;

import "./INFTManager.sol";
import "./ERC721.sol";

contract NFTManager is INFTManager, ERC721 {

    mapping(uint256 => string) private tokenToURI;
    uint256 public override count;
    string private baseURL = "https://andromeda.cs.virginia.edu/ccc/ipfs/files/";

    constructor() ERC721("Reptiles", "REP") {
    }

    function mintWithURI(address _to, string memory _uri) public override returns (uint) {
        for (uint key = 0; key < count; key++) {
            require(keccak256(bytes(tokenToURI[key])) != keccak256(bytes(_uri)), "Duplicate URI");
        }
        uint token_id = count;
        _safeMint(_to,count);
        tokenToURI[count] = _uri;
        count++;
        return token_id;
    }

    function mintWithURI(string memory _uri) external override returns (uint) {
       return mintWithURI(msg.sender, _uri);
    }   

    function supportsInterface(bytes4 interfaceId) public view virtual override (IERC165,ERC721) returns (bool) {
        return
            interfaceId == type(IERC721).interfaceId ||
            interfaceId == type(IERC721Metadata).interfaceId ||
            interfaceId == type(IERC165).interfaceId ||
            interfaceId == type(INFTManager).interfaceId;
    }

    function tokenURI(uint256 tokenId) public view override(ERC721, IERC721Metadata) returns (string memory) {
        require(bytes(tokenToURI[tokenId]).length > 0, "Invalid token ID");
        return string.concat(baseURL, tokenToURI[tokenId]);
    }

    //function count() external override view returns (uint);
}
