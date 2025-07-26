# Uniswap V3 Simple Swap on Arbitrum

A Python script that performs token swaps on Uniswap V3 using the Arbitrum network. This script swaps USDC for ARB tokens with built-in slippage protection and transaction confirmation.

## Features

- **Token Swap**: Swaps USDC to ARB using Uniswap V3 on Arbitrum
- **Quote Fetching**: Gets accurate swap quotes before execution
- **Slippage Protection**: Built-in 0.2% slippage tolerance
- **User Confirmation**: Prompts for confirmation before executing trades
- **Transaction Monitoring**: Waits for transaction confirmations

## Prerequisites

- Python 3.7+
- USDC balance on Arbitrum network
- Private key with sufficient ETH for gas fees
- Environment file with private key

## Installation

1. Install required packages:
```bash
pip install web3 python-dotenv requests
```

2. Set up environment file at `./.env`:
```
PRIVATE=your_private_key_here
```

3. Ensure you have the required ABI files:
   - `quoter.json` - Uniswap V3 QuoterV2 ABI
   - `erc20.json` - Standard ERC20 token ABI  
   - `router.json` - Uniswap V3 Router ABI

## Configuration

Update the following variables in `main.py`:

- `user_address`: Your wallet address
- `amount`: Amount of USDC to swap (default: 1 USDC)
- `FEE`: Pool fee tier (default: 500 = 0.05%)

## Smart Contract Addresses

- **QuoterV2**: `0x61fFE014bA17989E743c5F6cB21bF9697530B21e`
- **Router**: `0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45`
- **USDC**: `0xaf88d065e77c8cC2239327C5EDb3A432268e5831`
- **ARB**: `0x912CE59144191C1204E64559FE8253a0e49E6548`

## Usage

Run the script:
```bash
python main.py
```

The script will:
1. Connect to Arbitrum RPC
2. Get current gas price
3. Fetch a quote for the swap
4. Display quote and slippage information
5. Prompt for user confirmation
6. Approve router to spend USDC
7. Execute the swap transaction
8. Display transaction results

## Safety Features

- **Slippage Protection**: 0.2% slippage tolerance
- **User Confirmation**: Manual approval required before execution
- **Transaction Monitoring**: Waits for confirmations before proceeding
- **Gas Price Adjustment**: Uses 110% of current gas price for faster execution

## Risk Warning

This script involves real cryptocurrency transactions. Always:
- Test with small amounts first
- Verify all addresses and parameters
- Keep your private key secure
- Understand the risks of automated trading

## License

Use at your own risk. No warranty provided.
