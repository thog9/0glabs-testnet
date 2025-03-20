# 0G Labs Testnet Automation Scripts

This repository contains a collection of Python scripts designed to automate various tasks on the 0G Labs Testnet, including faucet claiming, token swapping, contract deployment, transaction sending, and NFT minting. These scripts are integrated with a central `main.py` file for streamlined execution, supporting multiple private keys and a user-friendly CLI interface.

## Features Overview

### General Features

- **Multi-Account Support**: Reads private keys from `pvkey.txt` to perform actions across multiple accounts.
- **Colorful CLI**: Uses `colorama` for visually appealing output with colored text and borders.
- **Asynchronous Execution**: Built with `asyncio` for efficient blockchain interactions.
- **Error Handling**: Comprehensive error catching for blockchain transactions and RPC issues.
- **Bilingual Support**: Supports both Vietnamese and English output based on user selection.

### Included Scripts

#### 1. `faucettokens.py` - Faucet ETH/BTC/USDT
- **Description**: Claims ETH, BTC, or USDT tokens from the 0G Labs Testnet faucet (requires A0GI balance).
- **Features**:
  - Random delays (10-30 seconds) between claims.
  - Detailed transaction logs with explorer links.
- **Usage**: Select from `main.py` menu.

#### 2. `swaptoken.py` - Swap Tokens
- **Description**: Swaps tokens (USDT, ETH, BTC) randomly or manually on the 0G Labs Testnet swap router.
- **Features**:
  - Supports random or manual swap pairs (e.g., USDT -> ETH).
  - User inputs for swap count and amount (default: 0.1 token).
  - Random delays (10-30 seconds) between swaps.
- **Usage**: Select from `main.py` menu, choose swap type and parameters.

#### 3. `storagescan.py` - Deploy Storage Scan
- **Description**: Deploys a storage scan file to the 0G Labs Testnet.
- **Features**:
  - Random value between 0.000005-0.00001 A0GI.
  - Retries on failure (up to 3 attempts).
  - Random delays (10-30 seconds) between deploys.
- **Usage**: Select from `main.py` menu.

#### 4. `conftnft.py` - Mint ConftApp Miner's Legacy NFT
- **Description**: Mints the ConftApp Miner's Legacy (MINERS) NFT on 0G Labs Testnet.
- **Features**:
  - Checks NFT balance to avoid duplicate minting.
  - Requires 0.005 A0GI per mint.
  - Random delays (10-30 seconds) between mints.
- **Usage**: Select from `main.py` menu.

#### 5. `domain.py` - Mint Domain
- **Description**: Mints a domain on the 0G Labs Testnet.
- **Features**:
  - Automates domain minting for multiple wallets.
  - Random delays (10-30 seconds) between mints.
- **Usage**: Select from `main.py` menu.

#### 6. `mintaura.py` - Mint Aura - Panda 0G (PG)
- **Description**: Mints the Aura - Panda 0G (PG) NFT on 0G Labs Testnet.
- **Features**:
  - Checks for existing mints to avoid duplicates.
  - Random delays (10-30 seconds) between mints.
- **Usage**: Select from `main.py` menu.

#### 7. `mintnerzo.py` - Mint Nerzo - 0G OG (NERZO-0GOG)
- **Description**: Mints the Nerzo - 0G OG (NERZO-0GOG) NFT for 0.005 A0GI.
- **Features**:
  - Checks NFT balance and A0GI balance (min 0.006 A0GI).
  - Random delays (10-30 seconds) between mints.
  - Detailed transaction logs with explorer links.
- **Usage**: Select from `main.py` menu.

#### 8. `sendtx.py` - Send Transactions
- **Description**: Sends A0GI transactions to random addresses or from `address.txt`.
- **Features**:
  - User-configurable transaction count and amount (default: 0.000001 A0GI).
  - Random delays (10-30 seconds) between transactions.
  - Detailed transaction logs with explorer links.
- **Usage**: Select from `main.py` menu, input transaction count and amount.

#### 9. `deploytoken.py` - Deploy ERC-20 Token Contract
- **Description**: Deploys a custom ERC-20 token smart contract on 0G Labs Testnet.
- **Features**:
  - User inputs for token name, symbol, decimals, and total supply.
  - Random delays (10-30 seconds) between deployments.
- **Usage**: Select from `main.py` menu, provide token details.

#### 10. `sendtoken.py` - Send ERC-20 Tokens
- **Description**: Transfers ERC-20 tokens to random addresses or from `addressERC20.txt`.
- **Features**:
  - User inputs for contract address and amount.
  - Random delays (10-30 seconds) between transfers.
  - Detailed transaction logs with explorer links.
- **Usage**: Select from `main.py` menu, input contract address and amount.

## Prerequisites

- **Python 3.8+**
- **Dependencies**: Install via `pip install -r requirements.txt` (ensure `web3.py`, `colorama`, `asyncio`, and `eth-account` are included).
- **pvkey.txt**: Add private keys (one per line) for wallet automation.
- **address.txt / addressERC20.txt**: Optional files for specifying recipient addresses.

## Installation

1. **Clone this repository:**
- Open cmd or Shell, then run the command:
```sh
git clone https://github.com/thog9/0glabs-testnet.git
```
```sh
cd 0glabs-testnet
```
2. **Install Dependencies:**
- Open cmd or Shell, then run the command:
```sh
pip install -r requirements.txt
```
3. **Prepare Input Files:**
- Open the `pvkey.txt`: Add your private keys (one per line) in the root directory.
```sh
nano pvkey.txt 
```
- Open the `address.txt`(optional): Add recipient addresses (one per line) for `sendtx.py`, `faucetstt.py`, `deploytoken.py`, `sendtoken.py`.
```sh
nano address.txt 
```
```sh
nano addressERC20.txt
```
```sh
nano addressFaucet.txt
```
```sh
nano contractERC20.txt
```
4. **Run:**
- Open cmd or Shell, then run command:
```sh
python main.py
```
- Choose a language (Vietnamese/English).

## Contact

- **Telegram**: [thog099](https://t.me/thog099)
- **Channel**: [thogairdrops](https://t.me/thogairdrops)
- **Replit**: Thog
