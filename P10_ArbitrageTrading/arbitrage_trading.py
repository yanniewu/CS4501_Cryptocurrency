# Yannie Wu, ylw4sj

from web3 import Web3
from web3.middleware import geth_poa_middleware
from hexbytes import HexBytes
import math

import arbitrage_config

# Initialize config file variables
idex_abi = arbitrage_config.idex_abi
itokencc_abi = arbitrage_config.itokencc_abi

account_address = arbitrage_config.config['account_address']
account_private_key = arbitrage_config.config['account_private_key']
connection_uri = arbitrage_config.config['connection_uri']
connection_is_ipc = arbitrage_config.config['connection_is_ipc']
price_eth = arbitrage_config.config['price_eth']
price_tc = arbitrage_config.config['price_tc']
max_eth_to_trade = arbitrage_config.config['max_eth_to_trade']
max_tc_to_trade = arbitrage_config.config['max_tc_to_trade']
gas_price = arbitrage_config.config['gas_price']
dex_addrs = arbitrage_config.config['dex_addrs']
tokencc_addr = arbitrage_config.config['tokencc_addr']
chainID = arbitrage_config.config['chainId']

def get_contract(w3, address, abi_spec):
	#print("dex_addr: ", address)
	address = Web3.to_checksum_address(address)
	contract = w3.eth.contract(address=address, abi=abi_spec)
	return contract

def get_f(contract):
    feeNumerator = contract.functions.feeNumerator().call()
    feeDenominator = contract.functions.feeDenominator().call()
    return 1 - feeNumerator/feeDenominator

def get_xyk(contract, token_contract):
    x = contract.functions.x().call()
    y = contract.functions.y().call()
    k = contract.functions.k().call()
    return x / (10 ** 18), y / (10 ** token_contract.functions.decimals().call()), k / (10 ** (18 + token_contract.functions.decimals().call()))

def set_qe(w3):
    return w3.eth.get_balance(account_address) / (10 ** 18)

def set_qt(token_contract):
    return get_balance(token_contract, account_address) / (10 ** token_contract.functions.decimals().call())

def get_balance(contract, addr):
    balance = contract.functions.balanceOf(addr).call()
    return balance

def get_holdings(q_e, q_t, p_e, p_t):
    return q_e * p_e + q_t * p_t

def delta_t(y_d, f, k_d, p_e, p_t):
    return y_d * (-1) + math.sqrt(f * k_d * p_e/p_t)

def delta_e(x_d, f, k_d, p_e, p_t):
    return x_d * (-1) + math.sqrt(f * k_d * p_t/p_e)

def holdings_after_ETH(q_t, f, y_d, k_d, x_d, delta_e, p_t, q_e, p_e, g):
    h_after = (q_t + f * y_d - f * k_d / (x_d + delta_e)) * p_t + (q_e - delta_e) * p_e - g * p_e 
    return h_after

def holdings_after_ETH2(q_e, f, y_d, k_d, x_d, delta_t):
    return ((q_e + f * x_d - f * (k_d / (y_d + delta_t))) - q_e)

def holdings_after_TC(q_e, f, x_d, k_d, y_d, delta_t, p_e, q_t, p_t, g):
    h_after = (q_e + f * x_d - f * k_d/(y_d + delta_t)) * p_e + (q_t - delta_t) * p_t - g * p_e
    return h_after

def holdings_after_TC2(q_t, f, y_d, k_d, x_d, delta_e):
    return ((q_t + f * y_d - f * (k_d / (x_d + delta_e))) - q_t)

def get_gas_fees(w3, gas):
	gwei_fees = gas * gas_price
	wei_fees = w3.to_wei(gwei_fees, 'gwei')
	gas_fees = float (w3.from_wei(wei_fees, 'ether'))
	return gas_fees

def create_transaction_transfer(w3, contract, my_address, dex_address, amount):
	transaction = contract.functions.transfer(Web3.to_checksum_address(dex_address), amount).build_transaction({
	    'gas': 2100000,
	    'chainId': chainID,
	    'gasPrice': w3.to_wei(gas_price, 'gwei'),
	    'from': my_address,
	    'nonce': w3.eth.get_transaction_count(my_address)
    })
	return transaction

def create_transaction(w3, my_address, dex_address, amount):
    transaction = {
	    'chainId': chainID,
	    'nonce': w3.eth.get_transaction_count(my_address),
	    'from': my_address,
	    'to': Web3.to_checksum_address(dex_address),
	    'value': w3.to_wei(amount, 'ether'),
	    'gas': 2100000,
	    'gasPrice': Web3.to_wei(gas_price, 'gwei')
    }
    return transaction

def main():

    # set up connection
	w3 = None 
	if connection_is_ipc:
		w3 = Web3(Web3.IPCProvider(connection_uri))
	else:
	    w3 = Web3(Web3.WebsocketProvider(connection_uri))
	w3.middleware_onion.inject(geth_poa_middleware, layer=0)
 
	eth_amount = 0
	tc_amount = 0
	fees = 0
	transaction_final = None

	token_contract = get_contract(w3, tokencc_addr, itokencc_abi)
	q_e, q_t = set_qe(w3), set_qt(token_contract)

	h_before = get_holdings(q_e, q_t, price_eth, price_tc)
	
	for dex_addr in dex_addrs:
        
		contract = get_contract(w3, dex_addr, idex_abi)
		f = get_f(contract)

		decimals = token_contract.functions.decimals().call()
		x,y,k = get_xyk(contract, token_contract)

		d_t = delta_t(y, f, k, price_eth, price_tc)
		d_e = delta_e(x, f, k, price_eth, price_tc)

		checksum_address = Web3.to_checksum_address(account_address)

		balance_tc = get_balance(token_contract, account_address)
		d_t = min(d_t, balance_tc)
		d_t = min(d_t, max_tc_to_trade)

		balance_eth = w3.eth.get_balance(account_address)
		d_e = min(d_e, balance_eth)
		d_e = min(d_e, max_eth_to_trade)

		if d_t > 0:

			gas_fees = get_gas_fees(w3, 117000)
			gas_fees_USD = gas_fees * price_eth 
			h_after_TC = holdings_after_TC(q_e, f, x, k, y, d_t, price_eth, q_t, price_tc, gas_fees)
            
			if h_after_TC > h_before:
				h_before = max(h_before, h_after_TC)
				eth_amount = holdings_after_ETH2(q_e, f, y, k, x, d_t) 
				tc_amount = d_t * (-1) 
				fees = gas_fees_USD
				transaction_final = create_transaction_transfer(w3, token_contract, checksum_address, dex_addr, int(d_t * 10 ** decimals))

		if d_e > 0:

			gas_fees = get_gas_fees(w3, 107000)
			gas_fees_USD = gas_fees * price_eth
			h_after_ETH = holdings_after_ETH(q_t, f, y, k, x, d_e, price_tc, q_e, price_eth, gas_fees)

			if h_after_ETH > h_before:
				h_before = max(h_before, h_after_ETH)
				tc_amount = holdings_after_TC2(q_t, f, y, k, x, d_e)                  
				eth_amount = d_e * (-1)  
				fees = gas_fees_USD           
				transaction_final = create_transaction(w3, checksum_address, dex_addr, d_e) 


	if eth_amount != 0 and tc_amount != 0:
		signed_txn = w3.eth.account.sign_transaction(transaction_final, private_key=account_private_key)
		ret = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

		q_e += eth_amount
		q_t += tc_amount

		w3.eth.wait_for_transaction_receipt(ret)

	q_e, q_t = set_qe(w3), set_qt(token_contract)
	h_after = get_holdings(q_e, q_t, price_eth, price_tc)

	arbitrage_config.output(eth_amount, tc_amount, fees, h_after)



if __name__ == "__main__":
    main()