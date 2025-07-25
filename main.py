from web3 import Web3
import json
import requests
import os
import time
from dotenv import find_dotenv
from dotenv import load_dotenv

env_file = find_dotenv("put .env file in a path")
load_dotenv(env_file)
PRIVATE= os.environ.get("PRIVATE")

# Step 1: Setup Web3
web3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))


# Step 2: Load ABIs and Define Contracts
with open('quoter.json') as f:
    QUOTER_ABI = json.load(f)

with open('erc20.json') as f:
    ERC20_ABI = json.load(f)

with open('router.json') as f:
    ROUTER_V3_ABI = json.load(f)

# Correct Arbitrum addresses - Use official Uniswap V3 QuoterV2
QUOTER_CONTRACT_ADDRESS = web3.to_checksum_address('0x61fFE014bA17989E743c5F6cB21bF9697530B21e')  # Official Uniswap V3 QuoterV2 on Arbitrum
QUOTER_CONTRACT = web3.eth.contract(address=QUOTER_CONTRACT_ADDRESS, abi=QUOTER_ABI)

BASE_TOKEN_ADDRESS = web3.to_checksum_address('0xaf88d065e77c8cC2239327C5EDb3A432268e5831')  # USDC on Arbitrum
BASE_TOKEN_CONTRACT = web3.eth.contract(address=BASE_TOKEN_ADDRESS, abi=ERC20_ABI)

ROUTER_V3_ADDRESS = web3.to_checksum_address('0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45')  # Uniswap V3 Router on Arbitrum
ROUTER_CONTRACT = web3.eth.contract(address=ROUTER_V3_ADDRESS, abi=ROUTER_V3_ABI)

# Step 3: Define Constants
DESIRE_TOKEN_ADDRESS = web3.to_checksum_address('0x912CE59144191C1204E64559FE8253a0e49E6548')
FEE = 500  # 0.05% fee (most common USDC/ARB pool fee tier)
amount = 1
amount_in_wei = int(amount * 10 ** 6)  # USDC has 6 decimals, not 18
user_address = "public"# Replace with your actual wallet address
private_key =   PRIVATE

# Step 4: Get Gas Price
gas_price = int(web3.eth.gas_price * 1.1) # Fetch the current gas price from the network
print(f"Current Gas Price: {gas_price}")

# Step 5: Get a Quote using correct struct format
quote_params = {
    'tokenIn': BASE_TOKEN_ADDRESS,
    'tokenOut': DESIRE_TOKEN_ADDRESS,
    'amountIn': amount_in_wei,
    'fee': FEE,
    'sqrtPriceLimitX96': 0
}

quote = QUOTER_CONTRACT.functions.quoteExactInputSingle(quote_params).call()
print("Quote Object Received", quote)
print(f"Quote received in human readable format: {quote[0] / 10**18} ARB")
acceptable_slippage_human_readable = (quote[0] / 10**18) * 0.999
acceptable_slippage_wei = int(acceptable_slippage_human_readable * 10**18)
print("The defined slippage is:", acceptable_slippage_human_readable)
print("The defined slippage in wei:", acceptable_slippage_wei)


# Step 5.5: User Confirmation Before Proceeding
quote_human_readable = quote[0] / 10**18
acceptable_slippage_human_readable = quote_human_readable * 0.998
acceptable_slippage_wei = int(acceptable_slippage_human_readable * 10**18)
print(f"Quote received: {quote_human_readable:.6f} ARB")
print(f"Acceptable Slippage: {acceptable_slippage_human_readable:.6f} ARB")
user_input = input("Proceed with the transaction? (yes/no): ").strip().lower()
if user_input != "yes":
    print("Transaction canceled.")
    exit()

# Step 6: Approve Router to Spend Tokens
amount_to_approve = int((amount+1) * 10**6)  # USDC has 6 decimals
tx = BASE_TOKEN_CONTRACT.functions.approve(
    ROUTER_V3_ADDRESS, amount_to_approve
).build_transaction({
    'from': user_address,
    'gas': 1000000,  # ✅ Correct gas limit for approval
    'gasPrice': gas_price,
    'nonce': web3.eth.get_transaction_count(user_address),
})

# Step 7: Sign & Send Approval Transaction
signed_tx = web3.eth.account.sign_transaction(tx, private_key)
tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
print(f"Approval TX Hash: {web3.to_hex(tx_hash)}")

# Wait for approval to be confirmed
print("Waiting for approval confirmation...")
approval_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
if approval_receipt.status == 1:
    print("✅ Approval confirmed!")
else:
    print("❌ Approval failed!")
    exit()

# Step 8: Perform the Swap
swap_tx = ROUTER_CONTRACT.functions.exactInputSingle({
    'tokenIn': BASE_TOKEN_ADDRESS,
    'tokenOut': DESIRE_TOKEN_ADDRESS,
    'fee': FEE,
    'recipient': user_address,
    'deadline': int(time.time()) + 600,  # 10-minute deadline from now
    'amountIn': amount_in_wei,
    'amountOutMinimum': acceptable_slippage_wei,  # Accept any output amount (adjust if needed)
    'sqrtPriceLimitX96': 0  # No price limit
}).build_transaction({
    'from': user_address,
    'gas': 1000000,  
    'gasPrice': gas_price,
    'nonce': web3.eth.get_transaction_count(user_address),
})
signed_swap_tx = web3.eth.account.sign_transaction(swap_tx, private_key)
swap_tx_hash = web3.eth.send_raw_transaction(signed_swap_tx.raw_transaction)
print(f"Swap TX Hash: {web3.to_hex(swap_tx_hash)}")

# Wait for swap confirmation
print("Waiting for swap confirmation...")
swap_receipt = web3.eth.wait_for_transaction_receipt(swap_tx_hash, timeout=120)
if swap_receipt.status == 1:
    print("✅ Swap successful!")
    print(f"Gas used: {swap_receipt.gasUsed}")
else:
    print("❌ Swap failed!")
    print(f"Gas used: {swap_receipt.gasUsed}")
