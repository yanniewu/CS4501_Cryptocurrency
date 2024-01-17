pragma solidity ^0.8.21;

import "./IGradebook.sol";

contract Gradebook is IGradebook {

    //-----------AUTO IMPLEMENTED-----------//

    // Returns whether the passed address has been designated as a teaching assistan
    mapping (address => bool) public override tas;

    // Returns the max score for the given assignment
    mapping (uint => uint ) public override max_scores;

    // Returns the name of the given assignment
    mapping (uint => string ) public assignment_names;

    // Returns the score for the given assignment ID and the given student
    mapping (uint => mapping(string => uint) ) public override scores;

    // Returns how many assignments there are; the assignments are assumed to be indexed from 0
    uint public override num_assignments;

    // Returns the address of the instructor, who is the person who deployed this smart contract
    address public override instructor;

    constructor() {
        instructor = msg.sender;
    }

    //-----------MANUALLY IMPLEMENTED-----------//
    function designateTA(address ta) virtual override public {
        require(instructor == msg.sender, "Only the instructor can designate TAs");
        tas[ta] = true;

    }

    function addAssignment(string memory name, uint max_score) external override returns (uint){
        //Check
        require(instructor == msg.sender || tas[msg.sender] == true, "Only the instructor and TAs can add assignments");
        require(max_score > 0, "Max score must be greater than 0");

        // Assign assignment an id
        assignment_names[num_assignments] = name;

        // Assign assignment max score
        max_scores[num_assignments] = max_score;

        // Increment num of assignments
        num_assignments +=1;

        // Emit event
        emit assignmentCreationEvent(num_assignments);

        return num_assignments;

    }

    function addGrade(string memory student, uint assignment, uint score) virtual override public{
        //Check
        require(instructor == msg.sender || tas[msg.sender] == true, "Only the instructor and TAs can add grades");
        require(assignment < num_assignments, "Invalid assignment ID");
        require(max_scores[assignment] >= score, "Grade can't be higher than the max score");
        require(score >= 0, "Grade can't be a negative number");

        // Assign score to student's assignment
        scores[assignment][student] = score;

        // Emit event
        emit gradeEntryEvent(assignment);
    }

    function getAverage(string memory student) external override view returns (uint){

        uint total_score = 0;
        uint max_score = 0;
        for (uint i=0; i < num_assignments; i++) {
            total_score += scores[i][student];
            max_score += max_scores[i];
        }

        uint avg_score = (total_score * 10000)/ max_score;

        return avg_score;
    }

    function requestTAAccess() virtual override public{
        tas[msg.sender] = true;
    }

    function supportsInterface(bytes4 interfaceId) external pure returns (bool) {
        return interfaceId == type(IGradebook).interfaceId || interfaceId == 0x01ffc9a7;
    }


}