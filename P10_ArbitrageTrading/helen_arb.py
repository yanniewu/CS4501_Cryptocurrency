from web3 import Web3
from hexbytes import HexBytes
import arbitrage_config
import math

config = arbitrage_config.config

idex_abi = arbitrage_config.idex_abi

itokencc_abi = arbitrage_config.itokencc_abi

account_address = config['account_address']
account_private_key = config['account_private_key']
connection_is_ipc = config['connection_is_ipc']
connection_uri = config['connection_uri']
price_eth = config['price_eth']
price_tc = config['price_tc']
dex_addrs = config['dex_addrs']
tokencc_addr = config['tokencc_addr']
max_eth_to_trade = config['max_eth_to_trade']
max_tc_to_trade = config['max_tc_to_trade']
gas_price = config['gas_price']
chain_id = config['chainId']

transactions = []
keep_track = []

def profit(h_before, h_after):
    return (h_after - h_before)


def hAfter(trade, q_e, q_t, p_e, p_t, f, x_d, y_d, k_d, g):
    if trade == "tc":
        amt = d_tc(y_d, f, k_d, p_t, p_e)
        return (q_e + f * x_d - f * (k_d/(y_d+amt)))* p_e+(q_t - amt)*p_t- g* p_e
    elif(trade == "eth"): 
        amt = d_eth(x_d, f, k_d, p_t, p_e)
        return (q_t + f * y_d - f * (k_d/(x_d+amt)))* p_t+(q_e - amt)*p_e- g* p_e 
    else:
        return "didn't input eth or tc for trade"
    
# def hAfter2(trade, q_e, q_t, p_e, p_t, f, x_d, y_d, k_d, g):
#     if trade == "eth":
#         amt = d_tc2(y_d, f, k_d, p_e, p_t)
#         return (q_e + f * x_d - f * k_d/(y_d+amt))* p_e+(q_t - amt)*p_t- g* p_e
#     elif(trade == "tc"): #trade == "eth"
#         amt = d_eth2(x_d, f, k_d, p_t, p_e)
#         return (q_t + f * y_d - f * k_d/(x_d+amt))* p_t+(q_e - amt)*p_e- g* p_e 
#     else:
#         return "didn't input eth or tc for trade"

def hBefore(q_e, q_t, p_e, p_t):
    return q_e * p_e + q_t * p_t

def gweiToEth(gwei):
    return gwei * 0.000000001

def d_tc(y_d, f, k_d, p_t, p_e):
    return -y_d + math.sqrt(f * k_d* p_e/p_t)

def d_eth(x_d, f, k_d, p_t, p_e):
    return -x_d + math.sqrt(f * k_d* p_t/p_e)

# def d_tc2(y_d, f, k_d, p_t, p_e):
#     return -y_d - math.sqrt(f * k_d* p_e/p_t)

# def d_eth2(x_d, f, k_d, p_t, p_e):
#     return -x_d - math.sqrt(f * k_d* p_t/p_e)

def calculateDexTrade(token_contract, dex, w3):
    checksum_addr = w3.to_checksum_address(account_address)
    dex_addr = w3.to_checksum_address(dex_addrs[dex])
    dex_contract = w3.eth.contract(address = dex_addr, abi = idex_abi)
    

    tc_balance = token_contract.functions.balanceOf(account_address).call() / (10 ** token_contract.functions.decimals().call())
    tc_balance = 0
    # print(tc_balance)

    eth_balance = w3.eth.get_balance(account_address)/(10**18)
    eth_balance = 11
    # print(eth_balance)
    
    h_before = hBefore(eth_balance, tc_balance, price_eth,price_tc)
    # print(h_before)

    
    x = dex_contract.functions.x().call() / (10 ** 18)
    y = dex_contract.functions.y().call() / (10 ** token_contract.functions.decimals().call())
    k = x*y

    f = 1 - dex_contract.functions.feeNumerator().call()/dex_contract.functions.feeDenominator().call()

    # h_after_tc = hAfter("tc", eth_balance, tc_balance, price_eth, price_tc, f, x, y, k, gweiToEth(117000))
    # h_after_eth = hAfter("eth",  eth_balance, tc_balance, price_eth, price_tc, f, x, y, k, gweiToEth(107000))
    # h_after_tc2 = hAfter2("tc", eth_balance, tc_balance, price_eth, price_tc, f, x, y, k, gweiToEth(117000))
    # h_after_eth2 = hAfter2("eth", eth_balance, tc_balance, price_eth, price_tc, f, x, y, k, gweiToEth(107000))

    delta_eth = d_eth(x,f,k,price_tc,price_eth) # ignore negative deltas only calculate h after of the postivie deltas
    delta_tc = d_tc(y,f,k,price_tc,price_eth)

    # print(delta_eth, delta_tc)

    amt_trade = 0

    if delta_eth > delta_tc and eth_balance > 0:
        if delta_eth < max_eth_to_trade:
            amt_trade = int(delta_eth)
        else:
            amt_trade = int(max_eth_to_trade)
            delta_eth = int(max_eth_to_trade)

    # print(w3.to_wei(amt_trade, 'ether'))
        txn = {
                'nonce': w3.eth.get_transaction_count(checksum_addr),
                'to': dex_addr,
                'from': checksum_addr,
                'value': w3.to_wei(amt_trade, 'ether'),
                'gas': 800000,
                'gasPrice': w3.to_wei('10', 'gwei'),
                'chainId': chain_id,
            }
        gas = 107000 * gas_price * (10**9) / (10**18)
        h_after = hAfter("eth",eth_balance,tc_balance,price_eth, price_tc, f, x, y, k, gas)
        # print(h_after)
        cur_holdings = eth_balance * price_eth + tc_balance * price_tc

        profit = 0 
        # print(cur_holdings, h_after)
        if(h_after > cur_holdings):
            profit = h_after - h_before
            keep_track.append((profit, "eth", delta_eth, gas))
            transactions.append(txn)
            # print(h_before, h_after)
        else:
            keep_track.append((0, "eth",delta_eth, gas))
            transactions.append(txn)
        # print(amt_trade, profit)
    elif delta_tc > delta_eth and tc_balance > 0:
        if delta_tc < max_tc_to_trade:
            amt_trade = int(delta_tc)
        else:
            amt_trade = int(max_tc_to_trade) * (10 ** token_contract.functions.decimals().call())
            delta_tc = int(max_tc_to_trade)
        txn = token_contract.functions.transfer(dex_addr, amt_trade).build_transaction({
                'gas': 800000,
                'gasPrice': w3.to_wei('10', 'gwei'),
                'from': checksum_addr,
                'nonce': w3.eth.get_transaction_count(checksum_addr),
                'chainId': chain_id,
                })
        
        gas = 117000 * gas_price * (10**9) / (10**18)
        h_after = hAfter("tc", eth_balance, tc_balance, price_eth, price_tc, f, x, y, k, gas)
        

        cur_holdings = eth_balance * price_eth + tc_balance * price_tc
        
        if h_after > cur_holdings:
            profit = h_after - h_before
            keep_track.append((profit,"tc", delta_tc, gas))
            transactions.append(txn)
        else:
            keep_track.append((0,"tc",delta_tc, gas))
            transactions.append(txn)

def main():
    if connection_is_ipc:
        w3 = Web3(Web3.IPCProvider(connection_uri))
    else:
        w3 = Web3(Web3.WebsocketProvider('wss://andromeda.cs.virginia.edu/geth'))
    
    from web3.middleware import geth_poa_middleware
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    checksum_addr = w3.to_checksum_address(account_address)
    
    token_contract = w3.eth.contract(address = tokencc_addr, abi = itokencc_abi) #????
    decimals = token_contract.functions.decimals().call()

    eth_balance = w3.eth.get_balance(checksum_addr) / (10**18)
    tc_balance = token_contract.functions.balanceOf(checksum_addr).call() / (10 ** token_contract.functions.decimals().call())


    for dex in range(len(dex_addrs)):
        calculateDexTrade(token_contract, dex, w3)

    max_trade = max(keep_track)
    txn_id = keep_track.index(max_trade)
    
    # print(keep_track)
    orig_eth = w3.eth.get_balance(checksum_addr) / (10**18)
    orig_tc = tc_balance
    # if(max_trade[3] == "none"):
    #     print()
    

    if max_trade[0] <= 0:
        holdings = price_eth* eth_balance + price_tc * tc_balance
        arbitrage_config.output(0,0,max_trade[3]*price_eth, holdings)
    else:
        gas_fees = max_trade[3] * price_eth
        signed_txn = w3.eth.account.sign_transaction(transactions[txn_id], private_key=account_private_key)
        ret = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        if max_trade[1] == "eth":
            eth = -1*max_trade[2]
            tc = token_contract.functions.balanceOf(checksum_addr).call() / (10 ** token_contract.functions.decimals().call()) - orig_tc
        elif max_trade[1] == "tc":
            tc = -1*max_trade[2]
            eth = w3.eth.get_balance(checksum_addr) / (10**18) - orig_eth
        
        eth_balance = w3.eth.get_balance(checksum_addr) / (10**18)
        tc_balance = token_contract.functions.balanceOf(checksum_addr).call() / (10 ** token_contract.functions.decimals().call())
        cur_holdings = eth_balance * price_eth + tc_balance*price_tc
        arbitrage_config.output(eth, tc, gas_fees,cur_holdings )

    


if __name__ == "__main__":
    main()
