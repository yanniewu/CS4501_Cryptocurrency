# Submission information for the Arbitrage HW
# https://aaronbloomfield.github.io/ccc/hws/arbitrage/

# The filename of this file must be 'arbitrage.py', else the submission
# verification routines will not work properly.

# You are welcome to have additional variables or fields in this file; you
# just cant remove variables or fields.


# Who are you?  Name and UVA userid.  The name can be in any human-readable format.
userid = "ylw4sj"
name = "Yannie Wu"


# eth.coinbase: not really required for this assignment, but the Gradescope
# checking program wants to see it anyway, so submit your eth_coinbase from a
# previous assignment.
eth_coinbase = "0x0f9b42095ECBBf261C831D16EC38f2f1782c2729"


# This dictionary contains the contract addresses of the various contracts
# that need to be deployed for this assignment.  The addresses do not need to
# be in checksummed form.  The contracts do, however, need to be deployed by
# the eth_coinbase address, above.  Be sure to include the leading '0x' in
# the address.
contracts = {

	# nothing is required in this dictionary for this assignment

}


# This dictionary contains various information that will vary depending on the
# assignment.
other = {
	
	# nothing is required in this dictionary for this assignment

}


# These are various sanity checks, and are meant to help you ensure that you
# submitted everything that you are supposed to submit.  Other than
# submitting the necessary files to Gradescope (which checks for those
# files), all other submission requirements are listed herein.  These values 
# need to be changed to True (instead of False).
sanity_checks = {

	# Can your code handle *both* types of URI connections:
	# whether 'connection_is_ipc' (in arbitrage_config.py) is both True and
	# False?
	'can_handle_both_types_of_connections': True,

	# Does your program produce NO other output other than one call to the
	# output() function?
	'no_output_other_than_output_call': True,

	# In your transactions, do you always set the gasPrice to a fixed value of
	# 10 gwei?
	'gasprice_set_to_10_gwei': True,

}


# While some of these are optional, you still have to replace those optional
# ones with the empty string (instead of None).
comments = {

	# How long did this assignment take, in hours?  Please format as an
	# integer or float.
	'time_taken': 5,

	# Any suggestions for how to improve this assignment?  This part is
	# completely optional.  If none, then you can have the value here be the
	# empty string (but not None).
	'suggestions': "",

	# Any other comments or feedback?  This part is completely optional. If
	# none, then you can have the value here be the empty string (but not
	# None).
	'comments': "",
}