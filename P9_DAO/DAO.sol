// SPDX-License-Identifier: GPL-3.0-or-later
// Yannie Wu, ylw4sj

pragma solidity ^0.8.21;

import "./IERC165.sol";
import "./IDAO.sol";
import "./NFTManager.sol";

contract DAO is IDAO {

    constructor() {
        curator = msg.sender;
        //nftmanager = address(new NFTManager("Reptiles", "REP")); Gradescope version
        nftmanager = address(new NFTManager());
        purpose = "Is Santa real?";
        howToJoin = "Bake some christmas cookies";
        string memory uri = substring(Strings.toHexString(curator),2,34);
        NFTManager(nftmanager).mintWithURI(curator, uri);
    }



    address public nftmanager;


    // Public variables
    mapping(uint => Proposal) public override proposals;
    uint constant public override minProposalDebatePeriod = 600;
    address public override tokens = nftmanager;
    string public override purpose;
    mapping(address => mapping(uint => bool) ) public override votedYes;
    mapping(address => mapping(uint => bool) ) public override votedNo;
    uint public override numberOfProposals; 
    string public override howToJoin;
    uint public override reservedEther;
    address public override curator;


    receive() external payable {
    }

    function newProposal(address recipient, uint amount, string memory description, uint debatingPeriod) external payable returns (uint) {

        require(debatingPeriod >= minProposalDebatePeriod, "The debating period must be greater than the minimum.");
        require(isMember(msg.sender), "Only members can open proposals.");

        proposals[numberOfProposals] = Proposal(recipient, amount, description, block.timestamp + debatingPeriod, true, false, 0, 0, msg.sender);
        numberOfProposals++;
        reservedEther += amount;
        emit NewProposal(numberOfProposals - 1, recipient, amount, description);
        return numberOfProposals - 1;
    }

    function vote(uint proposalID, bool supportsProposal) external {

        require(isMember(msg.sender), "only members can vote on proposals.");
        require(votedYes[msg.sender][proposalID] == false && votedNo[msg.sender][proposalID] == false, "The sender has already voted.");
        require(proposals[proposalID].open == true, "The proposal is not open to voting");
        require(proposals[proposalID].votingDeadline - block.timestamp > 0, "The voting deadline has passed.");

        if (supportsProposal){
            proposals[proposalID].yea++;
            votedYes[msg.sender][proposalID] = true;
        }

        else {
            proposals[proposalID].nay++;
            votedNo[msg.sender][proposalID] = true;
        }

        emit Voted(proposalID, supportsProposal, msg.sender);

    }

    function closeProposal(uint proposalID) external {

        require(block.timestamp > proposals[proposalID].votingDeadline, "The voting deadline has not passed yet.");
        require(isMember(msg.sender), "only members can close proposals");
        require(proposals[proposalID].open == true, "The proposal is already closed");

        proposals[proposalID].open = false;   

        if (proposals[proposalID].yea > proposals[proposalID].nay) {
            proposals[proposalID].proposalPassed = true;
            (bool success, ) = payable(proposals[proposalID].recipient).call{value: proposals[proposalID].amount}("");
            require (success, "Payment failed.");
        }

        reservedEther -= proposals[proposalID].amount;
        emit ProposalClosed(proposalID, proposals[proposalID].proposalPassed);
    }

    function isMember(address who) public view returns (bool) {
        
        if(NFTManager(nftmanager).balanceOf(who) > 0) {
            return true;
        }

        return false;
    }

    function addMember(address who) public {
        require(isMember(who) == false, "Member is already in the DAO.");
        require(isMember(msg.sender) == true, "Only DAO members can add new members.");
        
        string memory uri = substring(Strings.toHexString(who),2,34);
        NFTManager(nftmanager).mintWithURI(who, uri);
    }

    function requestMembership() public {
        require(isMember(msg.sender) == false, "Member is already in the DAO.");

        string memory uri = substring(Strings.toHexString(msg.sender),2,34);
        NFTManager(nftmanager).mintWithURI(msg.sender, uri);
    }


    function supportsInterface(bytes4 interfaceID) public pure override returns (bool) {
        return interfaceID == type(IDAO).interfaceId
            || interfaceID == type(IERC165).interfaceId;
    }



    function substring(string memory str, uint startIndex, uint endIndex) public pure returns (string memory) {

        bytes memory strBytes = bytes(str);

        bytes memory result = new bytes(endIndex-startIndex);

        for(uint i = startIndex; i < endIndex; i++)

            result[i-startIndex] = strBytes[i];

        return string(result);

    }



}