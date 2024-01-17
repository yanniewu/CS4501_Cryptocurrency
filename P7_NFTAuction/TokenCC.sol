// SPDX-License-Identifier: GPL-3.0-or-later
// Yannie Wu, ylw4sj

pragma solidity ^0.8.21;

import "./ITokenCC.sol";
import "./ERC20.sol";


contract TokenCC is ITokenCC, ERC20 {

    constructor() ERC20("HotCheetoCoin", "HCC") {
        _mint(msg.sender, 1000000 * 10**10);
    }

    function requestFunds() public pure override {
        revert();
    }

    function supportsInterface(bytes4 interfaceId) public view virtual override returns (bool) {
        return
            interfaceId == type(IERC165).interfaceId ||
            interfaceId == type(IERC20).interfaceId ||
            interfaceId == type(IERC20Metadata).interfaceId ||
            interfaceId == type(ITokenCC).interfaceId;
    }

    function decimals() public pure override (ERC20, IERC20Metadata) returns(uint8) {
        return 10;
    }
    
}


