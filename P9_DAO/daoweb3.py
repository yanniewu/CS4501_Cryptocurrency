# Submission information for the DAO & Web3 HW
# https://aaronbloomfield.github.io/ccc/hws/daoweb3/

# The filename of this file must be 'daoweb3.py', else the submission
# verification routines will not work properly.

# You are welcome to have additional variables or fields in this file; you
# just cant remove variables or fields.


# Who are you?  Name and UVA userid.  The name can be in any human-readable format.
userid = "ylw4sj"
name = "Yannie Wu"


# eth.coinbase: this is the account that you deployed the smart contracts
# (and performed any necessary transactions) for this assignment.  Be sure to
# include the leading '0x' in the address.
eth_coinbase = "0x0f9b42095ECBBf261C831D16EC38f2f1782c2729"


# This dictionary contains the contract addresses of the various contracts
# that need to be deployed for this assignment.  The addresses do not need to
# be in checksummed form.  The contracts do, however, need to be deployed by
# the eth_coinbase address, above.  Be sure to include the leading '0x' in
# the address.
contracts = {

	# Your deployed DAO contract.  All of the other information in this file
	# is assumed to be from this contract.  The address does not need to be
	# in checksummed form.  It must have been deployed by the eth_coinbase
	# address, above.
	'dao': '0x3cebbd53D5D0C55bbb1a56f6A316f187304fFA27',

}


# This dictionary contains various information that will vary depending on the
# assignment.
other = {
	
	# The transaction hash where you voted on one of the course-wide DAO
	# proposals.  It doesn't matter which one you voted for or how you voted.
	'dao_vote_txn': '0x308b99c96164d1a8c4a60ec59829e74ce29726c52c9f7ef708de001b9b763e18',

	# What is the 8 hex digit suffix for your dao_XXXXXXXX.html file?  Just
	# the 8 hex digits, please.
	'dao.html_suffix': '121eb1ff',

}


# These are various sanity checks, and are meant to help you ensure that you
# submitted everything that you are supposed to submit.  Other than
# submitting the necessary files to Gradescope (which checks for those
# files), all other submission requirements are listed herein.  These values 
# need to be changed to True (instead of False).
sanity_checks = {
	
	# Did you compute the suffix for your dao_XXXXXXXX.html file, as per the
	# instructions?
	'computed_dao.html_suffix': True,

	# Have you ensured that the `dao.html` file (without the suffix) does NOT
	# exist?
	'dao.html_does_not_exist': True,

	# Did you run the `touch ~/public_html/index.html` command on portal?  
	# One way to check is if you view https://www.cs.virginia.edu/~mst3k 
	# (for your userid), then you should NOT see your dao_xxxxxxxx.html file.
	'touched_index.html': True,

	# Did you add the three required proposals to your DAO?  One should have
	# expired, one expires week after the due date, and one is your choice.
	'added_three_required_dao_proposals': True,

	# Did you make the isntructor account a member of your DAO?  The account
	# address in on the Collab landing page.
	'made_instructor_dao_member': True,

	# Is the URL of your dao.html exactly:
	# https://www.cs.virginia.edu/~mst3k/dao_XXXXXXXX.html, where 'mst3k' is
	# your userid?
	'dao_url_is_correct': True,

	# Does your dao_XXXXXXXX.html web page specifically load up the information
	# on *your* DAO, and the latest version (that has the three proposals
	# mentioned above?)
	'dao_contract_addr_is_correct': True,

	# Did you join the course-wide DAO and vote on one of the proposals?
	'voted_on_course_dao': True,

}


# While some of these are optional, you still have to replace those optional
# ones with the empty string (instead of None).
comments = {

	# How long did this assignment take, in hours?  Please format as an
	# integer or float.
	'time_taken': 4,

	# Any suggestions for how to improve this assignment?  This part is
	# completely optional.  If none, then you can have the value here be the
	# empty string (but not None).
	'suggestions': "",

	# Any other comments or feedback?  This part is completely optional. If
	# none, then you can have the value here be the empty string (but not
	# None).
	'comments': "",
}