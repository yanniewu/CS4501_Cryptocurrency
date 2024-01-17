#!/usr/bin/python3

# This is the homework submission file for the BTC Scripting homework, which
# can be found at http://aaronbloomfield.github.io/ccc/hws/btcscript.  That
# page describes how to fill in this program.

from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
from bitcoin import SelectParams
from bitcoin.core import CMutableTransaction
from bitcoin.core.script import *
from bitcoin.core import x


#------------------------------------------------------------
# Do not touch: change nothing in this section!

# ensure we are using the bitcoin testnet and not the real bitcoin network
SelectParams('testnet')

# The address that we will pay our tBTC to -- do not change this!
tbtc_return_address = CBitcoinAddress('mohjSavDdQYHRYXcS3uS6ttaHP8amyvX78') # https://testnet-faucet.com/btc-testnet/

# The address that we will pay our BCY to -- do not change this!
bcy_dest_address = CBitcoinAddress('mgBT4ViPjTTcbnLn9SFKBRfGtBGsmaqsZz')

# Yes, we want to broadcast transactions
broadcast_transactions = True

# Ensure we don't call this directly
if __name__ == '__main__':
    print("This script is not meant to be called directly -- call bitcoinctl.py instead")
    exit()


#------------------------------------------------------------
# Setup: your information

# Your UVA userid
userid = 'ylw4sj'

# Enter the BTC private key and invoice address from the setup 'Testnet Setup'
# section of the assignment.  
my_private_key_str = "cScmiduS9S1V1CgtqDZqyHnHtLtySS4gCeka99mAM6jWKVUuWWqx"
my_invoice_address_str = "my5mHJaeWWKmu7yzET1k5TEidEUSVoHqvD"

# Enter the transaction ids (TXID) from the funding part of the 'Testnet
# Setup' section of the assignment.  Each of these was provided from a faucet
# call.  And obviously replace the empty string in the list with the first
# one you botain..
txid_funding_list = ["476d8f18e25513b8f1beedecb581e535aa3f118fbda95059c2652707b0d5400e"]

# These conversions are so that you can use them more easily in the functions
# below -- don't change these two lines.
if my_private_key_str != "":
    my_private_key = CBitcoinSecret(my_private_key_str)
    my_public_key = my_private_key.pub


#------------------------------------------------------------
# Utility function(s)

# This function will create a signature of a given transaction.  The
# transaction itself is passed in via the first three parameters, and the key
# to sign it with is the last parameter.  The parameters are:
# - txin: the transaction input of the transaction being signed; type: CMutableTxIn
# - txout: the transaction output of the transaction being signed; type: CMutableTxOut
# - txin_scriptPubKey: the pubKey script of the transaction being signed; type: list
# - private_key: the private key to sign the transaction; type: CBitcoinSecret
def create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, private_key):
    tx = CMutableTransaction([txin], [txout])
    sighash = SignatureHash(CScript(txin_scriptPubKey), tx, 0, SIGHASH_ALL)
    return private_key.sign(sighash) + bytes([SIGHASH_ALL])


#------------------------------------------------------------
# Testnet Setup: splitting coins

# The transaction ID that is to be split -- the assumption is that it is the
# transaction hash, above, that funded your account with tBTC.  You may have
# to split multiple UTXOs, so if you are splitting a different faucet
# transaction, then change this appropriately. It must have been paid to the
# address that corresponds to the private key above
txid_split = txid_funding_list[0]

# After all the splits, you should have around 10 (or more) UTXOs, all for the
# amount specified in this variable. That amount should not be less than
# 0.0001 BTC, and can be greater.  It will make your life easier if each
# amount is a negative power of 10, but that's not required.
#split_amount_to_split = 0.01249056
split_amount_to_split = 0.001

# How much BTC is in that UTXO; look this up on https://live.blockcypher.com
# to get the correct amount.
#split_amount_after_split = 0.001
split_amount_after_split = 0.0001

# How many UTXO indices to split it into -- you should not have to change
# this!  Note that it will actually split into one less, and use the last one
# as the transaction fee.
split_into_n = int(split_amount_to_split/split_amount_after_split)

# The transaction IDs obtained after successfully splitting the tBTC.
txid_split_list = ["37855d88e4b7310fec72c660b3521e93bc61203c55719da8cc8d26937f378b34"]


#------------------------------------------------------------
# Global settings: some of these will need to be changed for EACH RUN

# The transaction ID that is being redeemed for the various parts herein --
# this should be the result of the split transaction, above; thus, the
# default is probably sufficient.
txid_utxo = txid_split_list[0]

# This is likely not needed.  The bitcoinctl.py will take a second
# command-line parmaeter, which will override this value.  You should use the
# second command-line parameter rather than this variable. The index of the
# UTXO that is being spent -- note that these indices are indexed from 0.
# Note that you will have to change this for EACH run, as once a UTXO index
# is spent, it can't be spent again.  If there is only one index, then this
# should be set to 0.
utxo_index = -1

# How much tBTC to send -- this should be LESS THAN the amount in that
# particular UTXO index -- if it's not less than the amount in the UTXO, then
# there is no miner fee, and it will not be mined into a block.  Setting it
# to 90% of the value of the UTXO index is reasonable.  Note that the amount
# in a UTXO index is split_amount_to_split / split_into_n.
send_amount = split_amount_after_split * 0.9


#------------------------------------------------------------
# Part 1: P2PKH transaction

# This defines the pubkey script (aka output script) for the transaction you
# are creating.  This should be a standard P2PKH script.  The parameter is:
# - address: the address this transaction is being paid to; type:
#   P2PKHBitcoinAddress
def P2PKH_scriptPubKey(address):
    return [ 
            OP_DUP, 
            OP_HASH160, 
            address, 
            OP_EQUALVERIFY, 
            OP_CHECKSIG
           ]

# This function provides the sigscript (aka input script) for the transaction
# that is being redeemed.  This is for a standard P2PKH script.  The
# parameters are:
# - txin: the transaction input of the UTXO being redeemed; type:
#   CMutableTxIn
# - txout: the transaction output of the UTXO being redeemed; type:
#   CMutableTxOut
# - txin_scriptPubKey: the pubKey script (aka output script) of the UTXO being
#   redeemed; type: list
# - private_key: the private key of the redeemer of the UTXO; type:
#   CBitcoinSecret
def P2PKH_scriptSig(txin, txout, txin_scriptPubKey, private_key):
    
    signature = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, private_key)
    
    priv_key = CBitcoinSecret(str(private_key))
    public_key = priv_key.pub
    
    return [ 
            signature,
            public_key
           ]

# The transaction hash received after the successful execution of this part
txid_p2pkh = "d40c03544f6f9235b83fb618ef9233fcc6c126c25b0a4fecf7a3e1f50a6e29e6"


#------------------------------------------------------------
# Part 2: puzzle transaction

# These two values are constants that you should choose -- they should be four
# digits long.  They need to allow for only integer solutions to the linear
# equations specified in the assignment.
puzzle_txn_p = 4934 # p = 2x + y
puzzle_txn_q = 3672 # q = x + y

# These are the solutions to the linear equations specified in the homework
# assignment.  You can use an online linear equation solver to find the
# solutions.
puzzle_txn_x = 1262
puzzle_txn_y = 2410

# This function provides the pubKey script (aka output script) that requres a
# solution to the above equations to redeem this UTXO.
def puzzle_scriptPubKey():
    return [
            OP_2DUP,
            OP_OVER,
            OP_ADD,
            OP_ADD,
            puzzle_txn_p,
            OP_EQUALVERIFY,
            OP_ADD,
            puzzle_txn_q,
            OP_EQUAL
           ]

# This function provides the sigscript (aka input script) for the transaction
# that you are redeeming.  It should only provide the two values x and y, but
# in the order of your choice.
def puzzle_scriptSig():
    return [ 
            puzzle_txn_x,
            puzzle_txn_y
           ]

# The transaction hash received after successfully submitting the first
# transaction above (part 2a)
txid_puzzle_txn1 = "f6ca8586af87dbaf1fbaf779a9dcf02550dd951fe63afb8ccfa146da5ef4cce0"

# The transaction hash received after successfully submitting the second
# transaction above (part 2b)
txid_puzzle_txn2 = "ac7fd88fc7bc322660672d5c744499d197b3a2d7e7524f8ab20cdd2ed15e5ead"


#------------------------------------------------------------
# Part 3: Multi-signature transaction

# These are the public and private keys that need to be created for alice,
# bob, and charlie
alice_private_key_str = "cVkGWHuXy1piFMRn7A77TjhB1nQ7B9AfT8bM2Le1ipN1MLA5Dtqn"
alice_invoice_address_str = "mgCo2EDjWsPVmD9pqWX2Qgywg7if9E52DZ"
bob_private_key_str = "cTtt3Ynva6uSEeD66Chm7TS4tZebuHxYhYLtRGsDpdpieGHW1aH9"
bob_invoice_address_str = "n2TtofGMj9327gUFsAUXe7Tztmtr42E4wK"
charlie_private_key_str = "cVn3owPXC2fGSheNHCBxaEmVGSNssEY6g4bZUdUwxWMEYg9rPFqn"
charlie_invoice_address_str = "mw38fyc986ztY2tbvxwM1CSUZANkXowAiF"

# These three lines convert the above strings into the type that is usable in
# a script -- you should NOT modify these lines.
if alice_private_key_str != "":
    alice_private_key = CBitcoinSecret(alice_private_key_str)
if bob_private_key_str != "":
    bob_private_key = CBitcoinSecret(bob_private_key_str)
if charlie_private_key_str != "":
    charlie_private_key = CBitcoinSecret(charlie_private_key_str)

# This function provides the pubKey script (aka output script) that will
# require multiple different keys to allow redeeming this UTXO.  It MUST use
# the OP_CHECKMULTISIGVERIFY opcode.  While there are no parameters to the
# function, you should use the keys above for alice, bob, and charlie, as
# well as your own key.
def multisig_scriptPubKey():
    return [ 
            my_private_key.pub,
            OP_CHECKSIGVERIFY,
            alice_private_key.pub,
            bob_private_key.pub,
            charlie_private_key.pub,
            OP_3,                     
            OP_CHECKMULTISIGVERIFY, 
            OP_1  
           ]

# This function provides the sigScript (aka input script) that can redeem the
# above transaction.  The parameters are the same as for P2PKH_scriptSig
# (), above.  You also will need to use the keys for alice, bob, and charlie,
# as well as your own key.  The private key parameter used is the global
# my_private_key.
def multisig_scriptSig(txin, txout, txin_scriptPubKey):
    bank_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, my_private_key)
    alice_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, alice_private_key)
    bob_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, bob_private_key)
    charlie_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, charlie_private_key)
    return [ 
            OP_0,
            alice_sig,
            bob_sig,
            charlie_sig,
            OP_3,
            bank_sig
           ]

# The transaction hash received after successfully submitting the first
# transaction above (part 3a)
txid_multisig_txn1 = "6bc0be8134b75dd7d53e65e3e4e625daa2a540d9ad001652c7fe2b42661bde4e"

# The transaction hash received after successfully submitting the second
# transaction above (part 3b)
txid_multisig_txn2 = "22e46fd7db81970c60b2a3a1211695997d842191657733734896ef289173ef1b"


#------------------------------------------------------------
# Part 4: cross-chain transaction

# This is the API token obtained after creating an account on
# https://accounts.blockcypher.com/.  This is optional!  But you may want to
# keep it here so that everything is all in once place.
blockcypher_api_token = "2bf1e254ffe34d59abd1d7470b8d89fa"

# These are the private keys and invoice addresses obtained on the BCY test
# network.
my_private_key_bcy_str = "196c41de1fb9ed2e39ff68f48469214ef11880d4947d4d670fede983651da163"
my_invoice_address_bcy_str = "C7vnTNLwfb5hMdnXW4jS8MsTfgGq8B37a3"
bob_private_key_bcy_str = "2c4e2964c8679f95ea8f90af71f67901371db27cb5906f2dd13275cbb70643ef"
bob_invoice_address_bcy_str = "BxQU8AH4jvDshXYam9vzgkqXtxvfrfkQiQ"

# This is the transaction hash for the funding transaction for Bob's BCY
# network wallet.
txid_bob_bcy_funding = "eb1ac79aa78f122f628544cb130a9197aea2a2c7596b9ded540f82c95bb5b8e1"

# This is the transaction hash for the split transaction for the trasnaction
# above.
txid_bob_bcy_split = "36de2eb4908439266131c53ee8067de4bf3f82d9218ac9c2d9a82e7a699d8a71"

# This is the secret used in this atomic swap.  It needs to be between 1 million
# and 2 billion.
atomic_swap_secret = 1234567890

# This function provides the pubKey script (aka output script) that will set
# up the atomic swap.  This function is run by both Alice (aka you) and Bob,
# but on different networks (tBTC for you/Alice, and BCY for Bob).  This is
# used to create TXNs 1 and 3, which are described at
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/xchainpt1.
def atomicswap_scriptPubKey(public_key_sender, public_key_recipient, hash_of_secret):
    return [ 
            OP_IF,
            OP_HASH160,
            hash_of_secret,
            OP_EQUALVERIFY,
            public_key_recipient,
            OP_CHECKSIG,
            OP_ELSE,
            public_key_sender,
            OP_CHECKSIGVERIFY,
            public_key_recipient,
            OP_CHECKSIG,
            OP_ENDIF
           ]

# This is the ScriptSig that the receiver will use to redeem coins.  It's
# provided in full so that you can write the atomicswap_scriptPubKey()
# function, above.  This creates the "normal" redeeming script, shown in steps 5 and 6 at 
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/atomicsteps.
def atomcswap_scriptSig_redeem(sig_recipient, secret):
    return [
        sig_recipient, secret, OP_TRUE,
    ]

# This is the ScriptSig for sending coins back to the sender if unredeemed; it
# is provided in full so that you can write the atomicswap_scriptPubKey()
# function, above.  This is used to create TXNs 2 and 4, which are
# described at
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/xchainpt1.  In
# practice, this would be time-locked in the future -- it would include a
# timestamp and call OP_CHECKLOCKTIMEVERIFY.  Because the time can not be
# known when the assignment is written, and as it will vary for each student,
# that part is omitted.
def atomcswap_scriptSig_refund(sig_sender, sig_recipient):
    return [
        sig_recipient, sig_sender, OP_FALSE,
    ]

# The transaction hash received after successfully submitting part 4a
txid_atomicswap_alice_send_tbtc = "15eaaf20dc8ec6ced52dd3f9f427064b37f7b8ae780b7177c0619713003ffb81"

# The transaction hash received after successfully submitting part 4b
txid_atomicswap_bob_send_bcy = "8d14c938925f6084db6e8a40c9349b39b5925f56d0ecc8518b54ea618844a3b2"

# The transaction hash received after successfully submitting part 4c
txid_atomicswap_alice_redeem_bcy = "06fac45e39972861f490e601bfda53b1a55aa607d45e62a24100a463e622c09c"

# The transaction hash received after successfully submitting part 4d
txid_atomicswap_bob_redeem_tbtc = "1aaf067c8e901a563195295a54af9ff1495122deeb5f40c26c46b1f3fe4b9c49"


#------------------------------------------------------------
# part 5: return everything to the faucet

# nothing to fill in here, as we are going to look at the balance of
# `my_invoice_address_str` to verify that you've completed this part.

# Ran python3 bitcoinctl.py part1 for UTXO=9,10