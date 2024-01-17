// SPDX-License-Identifier: GPL-3.0-or-later
// Yannie Wu, ylw4sj

pragma solidity ^0.8.21;

import "./IAuctioneer.sol";
import "./NFTManager.sol";

contract Auctioneer is IAuctioneer {

    constructor(){
        deployer = msg.sender;
        nftmanager = address(new NFTManager());
    }
   
    address public override nftmanager;
    uint public override num_auctions;
    uint public override totalFees;
    uint public override uncollectedFees;
    mapping(uint => Auction) public auctions;
    address public override deployer;
  
    function collectFees() public override  {
        require(msg.sender == deployer, "Only the deployer of the contract can collect fees.");
        (bool collected, ) = payable(deployer).call{value: uncollectedFees}("");
        require(collected, "Failed to collect fees");

        uncollectedFees = 0; // Reset fee counter
    }

    function startAuction(uint m, uint h, uint d, string memory data, uint reserve, uint nftid) public override returns (uint) {  
        // 1. Sanity checks
        require(m > 0 || h > 0 || d > 0, "Invalid auction duration; must be greater than 0.");
        require(bytes(data).length > 0, "Invalid data; can't be an empty string.");
        require(nftmanager!= address(0), "Invalid NFT Manager address."); // uneccessary?
        for (uint i = 0; i < num_auctions; i++) {       // Ensure no auction with that NFT ID is running
            require(auctions[i].nftid != nftid, "Auction already running.");
        }

        // 2. Transfer the NFT over to this contract
        require(NFTManager(nftmanager).ownerOf(nftid) == msg.sender, "No ownership; NFT could not be transferred.");
        NFTManager(nftmanager).transferFrom(msg.sender, address(this), nftid);

        // 3. Create the Auction struct
        uint endTime = block.timestamp + (m * 60) + (h * 3600) + (d * 86400); // Convert to seconds
        auctions[num_auctions] = Auction(num_auctions, 0, data, reserve, msg.sender, msg.sender, nftid, endTime, true);
        num_auctions++;

        // 4. Emit the appropriate event
        emit auctionStartEvent(nftid);

        return num_auctions - 1; // Auction ID must start from 0
    }

    function closeAuction(uint _id) public override {
         // Sanity checks
        require(auctionTimeLeft(_id) == 0, "Auction can't be closed; there is still time left.");

        // Transfer ether and NFT
        if (auctions[_id].num_bids > 0) {
            NFTManager(nftmanager).transferFrom(address(this), auctions[_id].winner, _id);
            uint fees = auctions[_id].highestBid / 100;
            uint earnings = auctions[_id].highestBid - fees;
            (bool success, ) = payable(auctions[_id].initiator).call{value: earnings}(""); 
            require(success, "Failed to transfer ETH.");

            uncollectedFees += fees;
            totalFees += fees;
        }
        else { // No bids were placed; transfer NFT back to initiator
            NFTManager(nftmanager).transferFrom(address(this), auctions[_id].initiator, _id);    
        }

        // Mark the auction as inactive
        auctions[_id].active = false;

        // Emit the appropriate event
        emit auctionCloseEvent(_id);
    }

    function placeBid(uint id) payable external {
        // Sanity checks
        require(auctionTimeLeft(id) > 0, "Couldn't place bid; auction has already ended.");
        require(auctions[id].active == true, "Couldn't place bid; auction is inactive.");
        require(msg.value > auctions[id].highestBid, "Bid must be greater than the current highest bid.");
        
        // Refund previously highest winning bidder
        if (auctions[id].num_bids > 0) { // Can't refund if there haven't been any bids yet
            (bool success, ) = payable(auctions[id].winner).call{value: auctions[id].highestBid}("");
            require(success, "Failed to refund the previously highest winning bidder");
        }
        
        // Update highest winning bid
        auctions[id].winner = msg.sender;
        auctions[id].highestBid = msg.value;
        auctions[id].num_bids++;
        
        // Emit the appropriate event
        emit higherBidEvent(id);
    }

    function auctionTimeLeft(uint id) public view override returns (uint) {
        if (auctions[id].endTime > block.timestamp) {
            return auctions[id].endTime - block.timestamp;
        }
        else {
            return 0;
        }
    }

    function supportsInterface(bytes4 interfaceID) public pure override returns (bool) {
        return interfaceID == type(IERC165).interfaceId
            || interfaceID == type(IAuctioneer).interfaceId;
    }
}