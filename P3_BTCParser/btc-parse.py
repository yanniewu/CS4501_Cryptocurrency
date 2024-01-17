import sys
import math 
import json
from datetime import datetime
from hashlib import sha256

def read_file(n):
    global file_contents

    res = file_contents[:n]
    file_contents = file_contents[n:]
    return res

def compact_size(flag):
    global transaction_bytes

    b = read_file(1) # read first byte
    dec = int.from_bytes(b, 'little')

    if dec >= 0 and dec < 253:
        if flag:
            transaction_bytes += bytearray(b)
        return dec
    elif dec == 253:
        b = read_file(2)
        if flag:
            transaction_bytes += bytearray(b)
        return int.from_bytes(b, 'little')
    elif dec == 254:
        b = read_file(4)
        if flag:
            transaction_bytes += bytearray(b)
        return int.from_bytes(b, 'little')
    else:
        b = read_file(8)
        if flag:
            transaction_bytes += bytearray(b)
        return int.from_bytes(b, 'little')

class Block:
    def __init__(self, height):
        self.height = height
        self.version = None
        self.previous_hash = None
        self.merkle_hash = None
        self.timestamp = None
        self.timestamp_readable = None
        self.nbits = None
        self.nonce = None

        self.txn_count = None
        self.transactions = []
        
    def get_header(self):

        # Version
        b_array = bytearray(read_file(4))
        b_array.reverse()
        self.version = int.from_bytes(bytes(b_array), byteorder='big')

        # Previous hash
        b_array = bytearray(read_file(32))
        b_array.reverse()
        self.previous_hash = str(bytes(b_array).hex())

        # Merkle root hash
        b_array = bytearray(read_file(32))
        b_array.reverse()
        self.merkle_hash = str(bytes(b_array).hex())

        # Timestamp
        self.timestamp = int.from_bytes(read_file(4), 'little', signed=False)
        
        # Timestamp (readable)
        self.timestamp_readable = datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')

        # N bits
        b_array = bytearray(read_file(4))
        b_array.reverse()
        self.nbits = bytes(b_array).hex()
        
        # Nonce
        self.nonce = int.from_bytes(read_file(4), 'little', signed=False)


    def get_transaction(self):
        global transaction_bytes

        trans = Transaction()

        # Version
        b_array = bytearray(read_file(4))
        transaction_bytes += b_array
        b_array.reverse()
        trans.version = int.from_bytes(bytes(b_array), 'big')

        # Transaction input count
        trans.txn_in_count = compact_size(True)

        # Transaction inputs
        for _ in range(trans.txn_in_count):
            ti = TransactionInput()

            # Hash
            b_array = bytearray(read_file(32))
            transaction_bytes += b_array
            b_array.reverse()
            ti.txn_hash = str(bytes(b_array).hex())

            # Index
            b = read_file(4)
            ti.index = int.from_bytes(b,'little')
            transaction_bytes += bytearray(b)

            # Input script bytes
            ti.input_script_size = compact_size(True)

            # Input script signature
            b = read_file(ti.input_script_size)
            ti.input_script_bytes = b.hex()
            transaction_bytes += bytearray(bytes(b))

            # Sequence
            b = read_file(4)
            ti.sequence = int.from_bytes(b, 'little')
            transaction_bytes += bytearray(bytes(b))

            # Add transaction input
            trans.txn_inputs.append(ti)

        # Transaction output count
        trans.txn_out_count = compact_size(True)

        # Transaction outputs
        for _ in range(trans.txn_out_count):
            to = TransactionOutput()

            # Value
            b = read_file(8)
            to.satoshis = int.from_bytes(b, 'little')
            transaction_bytes += bytearray(bytes(b))

            # Output script bytes
            to.output_script_size = compact_size(True)

            # Output script signature
            b = read_file(to.output_script_size)
            to.output_script_bytes = b.hex()
            transaction_bytes += bytearray(b)

            # Add transaction output
            trans.txn_outputs.append(to)   

        # Lock time
        b = read_file(4)
        trans.lock_time = int.from_bytes(b, 'little')
        transaction_bytes += bytearray(b)
        transactions_merkle.append(bytes(transaction_bytes).hex())
        transaction_bytes.clear()

        return trans

class Transaction:
    def __init__(self):
        self.version = None
        self.txn_in_count = None
        self.txn_inputs = []
        self.txn_out_count = None
        self.txn_outputs = []
        self.lock_time = None

class TransactionOutput:
    def __init__(self):
        self.satoshis = None
        self.output_script_size = None
        self.output_script_bytes = None

class TransactionInput:
    def __init__(self):
        self.txn_hash = None
        self.index = None
        self.input_script_size = None
        self.input_script_bytes = None
        self.sequence = None

def get_block(height):
    bl = Block(height)
    bl.get_header()
    bl.txn_count = compact_size(False)
    for _ in range(bl.txn_count):
        bl.transactions.append(bl.get_transaction())       
    return bl

def validate_merkle_hash():
    global num_txn, merkle_tree

    hashes = []
    for i in range(len(transactions_merkle)):
        h = sha256(sha256(bytes.fromhex(transactions_merkle[i])).digest()).digest()
        hashes.append(h)

    length = 1 << (len(hashes) - 1).bit_length()

    if length > len(merkle_tree):
        while length > len(merkle_tree):
            merkle_tree += [None]
        for h in hashes:
            merkle_tree.append(h)
        if len(hashes) % 2 != 0:
            merkle_tree.append(hashes[-1])
    else:
        for h in hashes:
            merkle_tree.append(h) 

    for i in range(math.ceil(len(merkle_tree)/2)-1, 0, -1): # index of where to begin our concate hash
        merkle_tree[i] = sha256(sha256(merkle_tree[2*i]+merkle_tree[2*i+1]).digest()).digest()

    return merkle_tree[1]


#------- MAIN -------#
with open(sys.argv[1], "rb") as f:
    file_contents = f.read()
f.close()

merkle_hashes = []
merkle_tree = [None]
num_txn = 0
MAGIC_NUMBER= 3652501241 #0xd9b4bef9 = 3652501241365250124
transactions_merkle = []
transaction_bytes = []

all_blocks = []
height = 0
prev_hash = None

while len(file_contents.hex()) > 0:

    #--------- Get info ----------#
    # Preamble
    magic_num = int.from_bytes(read_file(4), 'little')
    size = int.from_bytes(read_file(4), 'little')
   
    # Header
    header = file_contents[:80]

    curr_block = get_block(height)
    all_blocks.append(curr_block)
    prev_block = all_blocks[height - 1]

    #--------- Validation ----------#
    # Error 1
    if magic_num != MAGIC_NUMBER:
        print("error 1 block " + str(height)) 
        exit()

    # Error 2
    if str(curr_block.version) != "1": 
        print("error 2 block " + str(height))
        exit()

    # Error 3
    curr_hash = ''.join(format(x, '02x') for x in reversed(bytearray(sha256(sha256(bytes.fromhex(bytearray(header).hex())).digest()).digest())))
    if prev_hash != None and str(curr_block.previous_hash) != str(prev_hash) : 
        print("error 3 block " + str(height))
        exit()

    # Error 4
    d1 = datetime.strptime(curr_block.timestamp_readable, "%Y-%m-%d %H:%M:%S%f") # error 4
    d2 = datetime.strptime(prev_block.timestamp_readable, "%Y-%m-%d %H:%M:%S%f")
    if height > 0 and (d2-d1).total_seconds()/3600.0 > 2:
        print("error 4 block " + str(height))
        exit()

    # Error 5
    for i in range(curr_block.txn_count): 
        if curr_block.transactions[i].version != 1:
            print("error 5 block " + str(height))
            exit()

    # Error 6
    merkle_hash = bytearray(validate_merkle_hash())
    merkle_hash.reverse()
    merkle_hash = ''.join(format(x, '02x') for x in merkle_hash)
    if merkle_hash != curr_block.merkle_hash.strip():
        print("error 6 block " + str(height))
        exit()

    prev_hash = curr_hash
    height += 1

    # Reset
    merkle_tree = [None]
    transaction_bytes = []
    transactions_merkle = []


#--------- Write to JSON ----------#
output_file = open(sys.argv[1] + ".json", mode='w')
json_obj = json.dumps({"blocks":all_blocks, "height": height}, default=lambda o: o.__dict__, indent=4)
output_file.write(json_obj)
output_file.close()

print("no errors " + str(height) + " blocks")