import subprocess
import json
import os
from dotenv import load_dotenv
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3 import Web3, middleware, Account
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware

# connect Web3
w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
# enable PoA middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
from constants import BTC, ETH, BTCTEST 
 
# Create a function called `derive_wallets`
def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    command = f"php ./derive -g --mnemonic=\"{mnemonic}\" --cols=all --coin={coin} --numderive{depth} --format=json" 
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {
    ETH: derive_wallets(coin=ETH),
    BTCTEST:derive_wallets(coin=BTCTEST)
}

print(coins)
# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin==ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin==BTCTEST:
        return PrivateKeyTestnet(priv_key)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin==ETH:
        value=w3.toWei(amount, "ether")
        gasEstimate = w3.eth.estimateGas(
        {"from": account.address, "to": recipient, "value": value}
    )
        return {
            "from": account.address,
            "to": recipient,
            "value": value,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
            "chainID": w3.eth.chain_id
        }

    if coin==BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])
    
    

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    if coin==ETH:
        tx = create_tx(coin, account.address, to, amount)
        signed_tx = account.signTransaction(tx)
        return w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    
    elif coin==BTCTEST:
        tx = create_tx(coin, account, to, amount)
        signed_tx = account.sign_transaction(tx)
        return NetworkAPI.broadcast_tx_testnet(signed_tx)