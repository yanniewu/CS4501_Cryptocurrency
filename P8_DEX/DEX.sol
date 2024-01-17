// SPDX-License-Identifier: GPL-3.0-or-later
// Yannie Wu, ylw4sj

pragma solidity ^0.8.0;

import "./IDEX.sol";
import "./TokenCC.sol";

contract DEX is IDEX {

    // Public variables
    uint256 public override k;
    uint256 public override x;
    uint256 public override y;

    uint256 public override decimals;
    uint256 public override feeNumerator;
    uint256 public override feeDenominator;
    uint256 public override feesToken;
    uint256 public override feesEther;

    mapping(address => uint) public etherLiquidityForAddress;
    mapping(address => uint) public tokenLiquidityForAddress;

    address public override etherPricer;
    address public override ERC20Address;
    
    bool public poolCreated = false;
    bool changingLiquidity;
    
    // Short functions
    string public override symbol;
    
    address public deployer;
    constructor() {
        deployer = msg.sender;
    }

    // function symbol() external view returns (string memory) {
    //     return IEtherPriceOracle(etherPricer).name();
    // }

    function getEtherPrice() public override view returns (uint) {
        require(poolCreated, "No pool has been created yet.");
        require(etherPricer != address(0), "The pricer contract must not be the null contract.");
        return IEtherPriceOracle(etherPricer).price();
    }

    function getTokenPrice() public override view returns (uint) {
        require(poolCreated, "No pool has been created yet.");
        uint totalEtherValue = (getEtherPrice() * x * 10**decimals) / (10**18); // scale based on exchange ratio
        uint tokenPrice = totalEtherValue / y; // y = num tokens in pool
        return tokenPrice;
    }

    function getPoolLiquidityInUSDCents() public override view returns (uint) {
        return (x * (getEtherPrice() * 2)) / (10**18);

    }

    function setEtherPricer(address p) public override {
        require(p != address(0), "The ether pricer cannot be the 0 address");
        etherPricer = p;
    }

    // 0: the address of *this* DEX contract (address)
    // 1: token cryptocurrency abbreviation (string memory)
    // 2: token cryptocurrency name (string memory)
    // 3: ERC-20 token cryptocurrency address (address)
    // 4: k (uint)
    // 5: ether liquidity (uint)
    // 6: token liquidity (uint)
    // 7: fee numerator (uint)
    // 8: fee denominator (uint)
    // 9: token decimals (uint)
    // 10: fees collected in ether (uint)
    // 11: fees collected in the token CC (uint)
    function getDEXinfo() external view returns (address, string memory, string memory, 
                            address, uint, uint, uint, uint, uint, uint, uint, uint) {

        return (address(this), symbol, ERC20(ERC20Address).name(), ERC20Address, k, x, y, 
                feeNumerator, feeDenominator, decimals, feesEther, feesToken);
    }

    //------------------------------------------------------------
    // Functions for a future assignment

    // This should just revert.  It is going to be used in the Arbitrage
    // assignment, so we are putting it into the interface now.
    function reset() public override {
    }

    function supportsInterface(bytes4 interfaceId) public override pure returns (bool) {
        return
            interfaceId == type(IERC165).interfaceId ||
            interfaceId == type(IERC20Receiver).interfaceId ||
            interfaceId == type(IDEX).interfaceId;
    }
    

    // Long functions
    //------------------------------------------------------------
    // Pool creation

    // This can be called exactly once, and creates the pool; only the
    // deployer of the contract call this.  Some amount of ETH is passed in
    // along with this call.  For purposes of this assignment, the ratio is
    // then defined based on the amount of ETH paid with this call and the
    // amount of the token cryptocurrency stated in the first parameter.  The
    // first parameter is how many of the token cryptocurrency (with all the
    // decimals) to add to the pool; the ERC-20 contract that manages that
    // token cryptocurrency is the fourth parameter (the caller needs to
    // approve this contract for that much of the token cryptocurrency before
    // the call).  The second and third parameters define the fraction --
    // 0.1% would be 1 and 1000, for example.  The last parameter is the
    // contract address of the EtherPricer contract being used, and can be
    // updated later via the setEtherPricer() function.
    function createPool(uint _tokenAmount, uint _feeNumerator, uint _feeDenominator, 
                        address _erc20token, address _etherPricer) public override payable {
        
        require(msg.sender == deployer, "Only the contract deployer can create the pool.");
        require(!poolCreated, "Only one pool can be created at a time.");
        require(msg.value > 0, "Must transfer an ether amount greater than 0.");
        require(_tokenAmount > 0, "Must transfer a token amount greater than 0.");
        
        changingLiquidity = true;
        poolCreated = true;
        ERC20Address = _erc20token;
        etherPricer = _etherPricer;
        feeNumerator = _feeNumerator;
        feeDenominator = _feeDenominator;
        x = msg.value;
        y = _tokenAmount;
        k = x * y;

        etherLiquidityForAddress[msg.sender] = msg.value;
        tokenLiquidityForAddress[msg.sender] = _tokenAmount;

        ERC20 tokenContract = ERC20(ERC20Address);

        bool tokenSuccess = tokenContract.transferFrom(deployer, address(this), _tokenAmount);
        require(tokenSuccess, "the token transfer was not completed successfully");

        decimals = tokenContract.decimals();
        symbol = tokenContract.symbol();
        
        changingLiquidity = false;
        emit liquidityChangeEvent();
    }

    function addLiquidity() public override payable {
        require(poolCreated, "No pool has been created yet");
        
        changingLiquidity = true;
        uint numTokens = (y / x) * msg.value; // num tokens to be transferred
        ERC20(ERC20Address).transferFrom(msg.sender, address(this), numTokens);
        x += msg.value;
        y += numTokens;
        k = x * y;

        etherLiquidityForAddress[msg.sender] += msg.value;
        tokenLiquidityForAddress[msg.sender] += numTokens;

        changingLiquidity = false;
        emit liquidityChangeEvent();
    }

    function removeLiquidity(uint amountEther) public override {
        require(address(this).balance >= amountEther, "Can't remove more ether than is in the pool.");
        require(amountEther <= etherLiquidityForAddress[msg.sender], "Can't remove more ether than you own.");
        
        changingLiquidity = true;
        uint numTokens = (y / x) * amountEther;
        ERC20(ERC20Address).transfer(msg.sender, numTokens);
        (bool success, ) = payable(msg.sender).call{value: amountEther}("");
            require (success, "Ether transfer failed; did not remove liquidity.");
        y -= numTokens;
        x -= amountEther;
        k = x * y;

        etherLiquidityForAddress[msg.sender] -= amountEther;
        tokenLiquidityForAddress[msg.sender] -= numTokens;

        changingLiquidity = false;
        emit liquidityChangeEvent();
    }

    //------------------------------------------------------------
    // Exchanging currencies

    receive() external override payable {
        require(poolCreated, "Pool has not been created yet.");

        if(changingLiquidity) {
            return;
        }
        else {
            x += msg.value;
            uint exchangeAmount = y - (k / x);
            y = k / x;
            uint fees = (exchangeAmount * feeNumerator) / feeDenominator;
            feesToken += fees;
            exchangeAmount -= fees;

            ERC20(ERC20Address).transfer(msg.sender, exchangeAmount);

            emit liquidityChangeEvent();
        }
    }

    function onERC20Received(address from, uint amount, address erc20) public override returns (bool) {
        
        require(erc20==ERC20Address,"Invalid ERC20 address");

        if(changingLiquidity){
            return true;
        }

        else{
            y += amount;
            uint exchangeAmount = x - (k / y);
            x = k / y;
            uint fees = (exchangeAmount * feeNumerator) / feeDenominator;
            feesEther += fees;
            exchangeAmount -= fees;


            (bool success, ) = payable(from).call{value: exchangeAmount}("");
            require (success, "Ether transfer for tokens failed");

            emit liquidityChangeEvent();
            return true;
        }       
    }

}