#!/usr/bin/python3

# This is the homework file for the BTC Parsing homework, which can be found
# at http://aaronbloomfield.github.io/ccc/hws/btcscript.

# Students are not expected to understand the contents of this file, although
# they are welcome to look through it.

# DO NOT EDIT THIS FILE!


import sys, os, requests, hashlib

from bitcoin import SelectParams
from bitcoin.core import b2x, lx, COIN, CMutableTxIn, CMutableTxOut, COutPoint, CMutableTransaction
from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress, CBitcoinAddress
from bitcoin.core.script import CScript, SignatureHash, SIGHASH_ALL
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH

SelectParams('testnet')

from scripts import *


utxo = -1
def get_utxo_index():
	global utxo
	if utxo == -1:
		assert utxo_index != -1, "UTXO not set to a valid value"
		return utxo_index
	else:
		assert utxo >= 0, "UTXO not set to a valid value" 
		return utxo

def broadcast_transaction(tx, network):
	if network == 'btc-test3':
		url = 'https://api.blockcypher.com/v1/btc/test3/txs/push'
	elif network == 'bcy-test':
		url = 'https://api.blockcypher.com/v1/bcy/test/txs/push'
	else:
		raise Exception("Network must be one of either 'btc-test3', 'bcy-test'")
	raw_transaction = b2x(tx.serialize())
	headers = {'content-type': 'application/x-www-form-urlencoded'}
	if broadcast_transactions:
		return requests.post(url, headers=headers, data='{"tx": "%s"}' % raw_transaction)
	else:
		return None


def split_coins(which):
	if which == 'split':
		my_private_key = CBitcoinSecret(my_private_key_str)
		txid = txid_split
		network = 'btc-test3'
	else: # split == 'splitbcy'
		my_private_key = CBitcoinSecret.from_secret_bytes(x(bob_private_key_bcy_str))
		txid = txid_bob_bcy_funding
		network = 'bcy-test'
	my_public_key = my_private_key.pub
	address = P2PKHBitcoinAddress.from_pubkey(my_public_key)
	txin_scriptPubKey = address.to_scriptPubKey()
	txin = CMutableTxIn(COutPoint(lx(txid), get_utxo_index()))
	txout_scriptPubKey = address.to_scriptPubKey()
	split_utxo_output = split_amount_to_split / split_into_n
	txout = CMutableTxOut(split_utxo_output*COIN, CScript(txout_scriptPubKey))
	tx = CMutableTransaction([txin], [txout]*(split_into_n-1))
	sighash = SignatureHash(txin_scriptPubKey, tx, 0, SIGHASH_ALL)
	txin.scriptSig = CScript([my_private_key.sign(sighash) + bytes([SIGHASH_ALL]), my_public_key])
	VerifyScript(txin.scriptSig, txin_scriptPubKey, tx, 0, (SCRIPT_VERIFY_P2SH,))
	response = broadcast_transaction(tx,network)
	if not broadcast_transactions:
		print("Not broadcasting transactions, so no response received")
	else:
		print(response.status_code, response.reason)
		print(response.text)


def keygen(_):
	private_key = CBitcoinSecret.from_secret_bytes(os.urandom(32))
	print("Private key:", private_key)
	print("Address:", P2PKHBitcoinAddress.from_pubkey(private_key.pub))


def get_urls(_):
	urlbase = "live.blockcypher.com/btc-testnet"
	#urlbase = "www.blockchain.com/btc-testnet" # not using, as it's slow to update
	if my_invoice_address_str != "":
		print("Your tBTC wallet:  \thttps://" + urlbase + "/address/" + my_invoice_address_str)
	if bob_invoice_address_str != "":
		print("Bob's tBTC wallet:  \thttps://" + urlbase + "/address/" + bob_invoice_address_str)
	tbtc_txids = {}
	for i in range(len(txid_funding_list)):
		tbtc_txids["Initial funding TXN " + str(i+1) + ":"] = txid_funding_list[i]
	for i in range(len(txid_split_list)):
		tbtc_txids["Split TXN " + str(i+1) + ":     "] = txid_split_list[i]
	tbtc_txids["\nPart 1: P2PKH TX:"] = txid_p2pkh
	tbtc_txids["\nPart 2a: puzzle TX 1:"] = txid_puzzle_txn1
	tbtc_txids["Part 2b: puzzle TX 2:"] = txid_puzzle_txn2
	tbtc_txids["\nPart 3a: multisig TX 1:"] = txid_multisig_txn1
	tbtc_txids["Part 3b: multisig TX 2:"] = txid_multisig_txn2
	tbtc_txids["\nPart 4a: your send TX:"] = txid_atomicswap_alice_send_tbtc
	tbtc_txids["Part 4d: B's redeem TX:"] = txid_atomicswap_bob_redeem_tbtc

	for k,v in tbtc_txids.items():
		if v != "":
			print(k + "\thttps://" + urlbase + "/tx/" + v)
	# BCY wallets and transactions
	urlbase = "live.blockcypher.com/bcy"
	if my_invoice_address_bcy_str != "":
		print("\nYour BCY wallet:  \thttps://" + urlbase + "/address/" + my_invoice_address_bcy_str)
	if bob_invoice_address_bcy_str != "":
		print("Bob's BCY wallet:  \thttps://" + urlbase + "/address/" + bob_invoice_address_bcy_str)
	bcy_txids = {"Bob's BCY funding TX:":txid_bob_bcy_funding,
				 "Bob's BCY split TX:":txid_bob_bcy_split,
				 "Part 4b: B's send TX:":txid_atomicswap_bob_send_bcy,
				 "Part 4c: your redeem TX":txid_atomicswap_alice_redeem_bcy,
				}
	for k,v in bcy_txids.items():
		if v != "":
			print(k + "\thttps://" + urlbase + "/tx/" + v)


def create_signed_transaction(txin, txout, txin_scriptPubKey,
                              txin_scriptSig, verify_script = True):
	tx = CMutableTransaction([txin], [txout])
	txin.scriptSig = CScript(txin_scriptSig)
	#print(txin, "\n\n", txout, "\n\n", txin_scriptPubKey, "\n\n", txin_scriptSig)
	if verify_script:
	    VerifyScript(txin.scriptSig, CScript(txin_scriptPubKey),
	                 tx, 0, (SCRIPT_VERIFY_P2SH,))
	return tx


def handle_txn(param):
	# get the sender info
	sender_private_key = CBitcoinSecret(my_private_key_str)
	sender_public_key = sender_private_key.pub
	sender_address = P2PKHBitcoinAddress.from_pubkey(sender_public_key)
	# get hash of secret for part 4
	shahash = hashlib.new('sha256')
	rmdhash = hashlib.new('ripemd160')
	shahash.update(atomic_swap_secret.to_bytes(4,'little'))
	rmdhash.update(shahash.digest())
	secret_hash = rmdhash.digest()
	#secret_hash = secret_hash[::-1]
	# set up our transaction output
	if param == "part2a":
		txout_scriptPubKey = puzzle_scriptPubKey()
	elif param == "part3a":
		txout_scriptPubKey = multisig_scriptPubKey()
	elif param == "part4a":
		txout_scriptPubKey = atomicswap_scriptPubKey(sender_public_key, bob_private_key.pub, secret_hash)
	elif param == "part4b":
		bob_prikey_bcy = CBitcoinSecret.from_secret_bytes(x(bob_private_key_bcy_str))
		my_prikey_bcy = CBitcoinSecret.from_secret_bytes(x(my_private_key_bcy_str))
		txout_scriptPubKey = atomicswap_scriptPubKey(bob_prikey_bcy.pub, my_prikey_bcy.pub, secret_hash)
	elif param == "part4c":
		txout_scriptPubKey = P2PKH_scriptPubKey(bcy_dest_address)
	else: # all others: pay to the facuet address
		txout_scriptPubKey = P2PKH_scriptPubKey(tbtc_return_address)
	# second transactions have to lower the send_amount to allow for fees
	factor = 1.0
	if param in ['part2b','part3b','part4c','part4d']:
		factor = 0.9
	txout = CMutableTxOut(factor*send_amount*COIN, CScript(txout_scriptPubKey))
	# set up our transaction input; this varies for the different parts, but
	# many are spending a standard P2PKH transaction from the faucet (or split)
	if param in ["part1", "part2a", "part3a","part4a"]:
		txin_scriptPubKey = P2PKH_scriptPubKey(sender_address)
		txin = CMutableTxIn(COutPoint(lx(txid_utxo), get_utxo_index()))
		txin_scriptSig = P2PKH_scriptSig(txin, txout, txin_scriptPubKey, sender_private_key)
	elif param == "part2b":
		txin_scriptPubKey = puzzle_scriptPubKey()
		txin = CMutableTxIn(COutPoint(lx(txid_puzzle_txn1), get_utxo_index()))
		txin_scriptSig = puzzle_scriptSig()
	elif param == "part3b":
		txin_scriptPubKey = multisig_scriptPubKey()
		txin = CMutableTxIn(COutPoint(lx(txid_multisig_txn1), get_utxo_index()))
		txin_scriptSig = multisig_scriptSig(txin, txout, txin_scriptPubKey)
	elif param == "part4b":
		bob_prikey_bcy = CBitcoinSecret.from_secret_bytes(x(bob_private_key_bcy_str))
		bob_invoice_addr_bcy = P2PKHBitcoinAddress.from_pubkey(bob_prikey_bcy.pub)
		txin_scriptPubKey = P2PKH_scriptPubKey(bob_invoice_addr_bcy)
		txin = CMutableTxIn(COutPoint(lx(txid_bob_bcy_split), get_utxo_index()))
		txin_scriptSig = P2PKH_scriptSig(txin, txout, txin_scriptPubKey, bob_prikey_bcy)
	elif param == "part4c": # BCY Bob -> Alice
		# re-create UTXO's pubKey script and sign it
		my_prikey_bcy = CBitcoinSecret.from_secret_bytes(x(my_private_key_bcy_str))
		my_invoice_addr_bcy = P2PKHBitcoinAddress.from_pubkey(my_prikey_bcy.pub)
		bob_prikey_bcy = CBitcoinSecret.from_secret_bytes(x(bob_private_key_bcy_str))
		txin_scriptPubKey = atomicswap_scriptPubKey(bob_prikey_bcy.pub, my_prikey_bcy.pub, secret_hash)
		txin = CMutableTxIn(COutPoint(lx(txid_atomicswap_bob_send_bcy), get_utxo_index()))
		signature = create_CHECKSIG_signature(txin,txout,txin_scriptPubKey,my_prikey_bcy)
		# create our input (sigScript) script
		txin_scriptSig = atomcswap_scriptSig_redeem(signature,atomic_swap_secret)
	elif param == "part4d": # tBTC Alice -> Bob
		# re-create UTXO's pubKey script and sign it
		txin_scriptPubKey = atomicswap_scriptPubKey(sender_public_key, bob_private_key.pub, secret_hash)
		txin = CMutableTxIn(COutPoint(lx(txid_atomicswap_alice_send_tbtc), get_utxo_index()))
		signature = create_CHECKSIG_signature(txin,txout,txin_scriptPubKey,bob_private_key)
		# create our input (sigScript) script
		txin_scriptSig = atomcswap_scriptSig_redeem(signature,atomic_swap_secret)
	else:
		raise Exception("Unknown part in handle_txn():",param)
	# which network?
	network = 'btc-test3'
	if param in ["part4b", "part4c"]:
		network = 'bcy-test'
	# combine into a new transaction, and broadcast
	new_tx = create_signed_transaction(txin, txout, txin_scriptPubKey, txin_scriptSig)
	response = broadcast_transaction(new_tx,network)
	if not broadcast_transactions:
		print("Not broadcasting transactions, so no response received")
	else:
		print(response.status_code, response.reason)
		print(response.text)


functions = {
	'keygen': keygen,
	'genkey': keygen,
	'split': split_coins,
	'splitbcy': split_coins,
	'part1': handle_txn,
	'part2a': handle_txn,
	'part2b': handle_txn,
	'part3a': handle_txn,
	'part3b': handle_txn,
	'part4a': handle_txn,
	'part4b': handle_txn,
	'part4c': handle_txn,
	'part4d': handle_txn,
	'geturls': get_urls,
	'urls': get_urls,
	'url': get_urls,
}


def sanity_checks():
	if my_private_key_str != "" or my_invoice_address_str != "":
		private_key = CBitcoinSecret(my_private_key_str)
		public_key = private_key.pub
		address = P2PKHBitcoinAddress.from_pubkey(my_public_key)
		assert(str(address) == my_invoice_address_str)


def main():
	global utxo
	if len(sys.argv) < 2 or len(sys.argv) > 3:
		print ("You must supply at least one or two command-line parameters to use this program.")
		print ("See the homework for details.")
		exit()
	if len(sys.argv) == 3:
		try:
			utxo = int(sys.argv[2])
		except:
			print("Error: the second command-line parameter should be an integer UTXO")
			exit()
	if sys.argv[1] not in functions.keys():
		print ("Unknown function:",sys.argv[1])
		exit()
	if my_private_key_str != "" and my_invoice_address_str != "":
		sanity_checks()
	functions[sys.argv[1]](sys.argv[1])

if __name__ == '__main__':
	main()