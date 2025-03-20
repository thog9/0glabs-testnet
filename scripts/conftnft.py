import os
import sys
import asyncio
import random
from web3 import Web3
from web3.exceptions import ContractLogicError
from eth_account import Account
from colorama import init, Fore, Style

# Khởi tạo colorama
init(autoreset=True)

# Constants
NETWORK_URL = 'https://lightnode-json-rpc-0g.grandvalleys.com'
CHAIN_ID = 16600
EXPLORER_URL = "https://chainscan-newton.0g.ai"
CONFT_NFT_ADDRESS = "0x9059cA87Ddc891b91e731C57D21809F1A4adC8D9"
MAX_WAIT_TIME = 300  # Thời gian tối đa đợi receipt (5 phút)

# ABI cho NFT contract
NFT_ABI = [
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "owner", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "mintPrice", "type": "function", "inputs": [], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "mint", "type": "function", "inputs": [], "outputs": [], "stateMutability": "payable"}
]

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': '✨ MINT CONFT NFT - OG LABS TESTNET ✨',
        'info': 'ℹ Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallet': '⚙ XỬ LÝ VÍ',
        'checking_balance': 'Đang kiểm tra số dư NFT...',
        'has_nft': 'Ví này đã mint Miners Legacy (MINERS)! Không thực hiện lại',
        'no_balance': 'Số dư ví không đủ để mint (cần ít nhất {price} A0GI)',
        'preparing_tx': 'Đang chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'waiting_tx': 'Đang đợi xác nhận giao dịch...',
        'success': '✅ Mint Miners Legacy (MINERS) thành công!',
        'failure': '❌ Mint Miners Legacy (MINERS) thất bại',
        'timeout': '⚠ Đã hết thời gian đợi ({timeout} giây), kiểm tra giao dịch trên explorer...',
        'address': 'Địa chỉ ví',
        'gas': 'Gas',
        'block': 'Khối',
        'connect_success': '✅ Thành công: Đã kết nối mạng OG LABS Testnet',
        'connect_error': '❌ Không thể kết nối RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ File pvkey.txt không tồn tại',
        'pvkey_empty': '❌ Không tìm thấy private key hợp lệ',
        'pvkey_error': '❌ Đọc pvkey.txt thất bại',
        'invalid_key': 'không hợp lệ, bỏ qua',
        'warning_line': '⚠ Cảnh báo: Dòng',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG'
    },
    'en': {
        'title': '✨ MINT CONFT NFT - OG LABS TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallet': '⚙ PROCESSING WALLET',
        'checking_balance': 'Checking NFT balance...',
        'has_nft': 'This wallet has already minted Miners Legacy (MINERS)! Skipping',
        'no_balance': 'Insufficient balance to mint (need at least {price} A0GI)',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'waiting_tx': 'Waiting for transaction confirmation...',
        'success': '✅ Successfully minted Miners Legacy (MINERS)!',
        'failure': '❌ Failed to mint Miners Legacy (MINERS)',
        'timeout': '⚠ Timeout after {timeout} seconds, check transaction on explorer...',
        'address': 'Wallet address',
        'gas': 'Gas',
        'block': 'Block',
        'connect_success': '✅ Success: Connected to OG LABS Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': '⚠ Warning: Line',
        'completed': '🏁 COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL'
    }
}

# Hàm UI
def print_border(text: str, color=Fore.CYAN, width=80):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}╔{'═' * (width - 2)}╗{Style.RESET_ALL}")
    print(f"{color}║{padded_text}║{Style.RESET_ALL}")
    print(f"{color}╚{'═' * (width - 2)}╝{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * 80}{Style.RESET_ALL}")

# Hàm kiểm tra private key
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

# Hàm đọc private keys từ pvkey.txt
def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm private keys vào đây, mỗi key trên một dòng\n# Ví dụ: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
            sys.exit(1)
        
        valid_keys = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                key = line.strip()
                if key and not key.startswith('#'):
                    if is_valid_private_key(key):
                        if not key.startswith('0x'):
                            key = '0x' + key
                        valid_keys.append((i, key))
                    else:
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i}: {LANG[language]['invalid_key']} - {key}{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Hàm kết nối Web3
def connect_web3(language: str = 'en'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if w3.is_connected():
            print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} | Chain ID: {w3.eth.chain_id} | RPC: {NETWORK_URL}{Style.RESET_ALL}")
            return w3
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['connect_error']} at {NETWORK_URL}{Style.RESET_ALL}")
            sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['web3_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Hàm đợi receipt thủ công
async def wait_for_receipt(w3: Web3, tx_hash: str, max_wait_time: int, language: str = 'en'):
    start_time = asyncio.get_event_loop().time()
    while True:
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return receipt
        except Exception:
            pass
        
        elapsed_time = asyncio.get_event_loop().time() - start_time
        if elapsed_time > max_wait_time:
            return None
        
        await asyncio.sleep(5)  # Kiểm tra mỗi 5 giây

# Hàm mint Conft NFT
async def mint_conft_nft(w3: Web3, private_key: str, wallet_index: int, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    try:
        nft_contract = w3.eth.contract(address=Web3.to_checksum_address(CONFT_NFT_ADDRESS), abi=NFT_ABI)
        
        print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
        nft_balance = nft_contract.functions.balanceOf(sender_address).call()
        if nft_balance >= 1:
            print(f"{Fore.GREEN}  ✔ {LANG[language]['has_nft']}{Style.RESET_ALL}")
            return True

        mint_price = nft_contract.functions.mintPrice().call()
        balance = w3.from_wei(w3.eth.get_balance(sender_address), 'ether')
        print(f"{Fore.YELLOW}  - Số dư hiện tại: {balance:.6f} A0GI{Style.RESET_ALL}")

        print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
        nonce = w3.eth.get_transaction_count(sender_address)
        gas_price = w3.to_wei('0.1', 'gwei')  # Gas price cố định

        # Ước lượng gas
        try:
            estimated_gas = nft_contract.functions.mint().estimate_gas({
                'from': sender_address,
                'value': mint_price
            })
            gas_limit = int(estimated_gas * 1.2)  # Tăng 20%
            print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ Không thể ước lượng gas: {str(e)}. Dùng gas mặc định: 500000{Style.RESET_ALL}")
            gas_limit = 500000

        required_balance = w3.from_wei(gas_limit * gas_price + mint_price, 'ether')
        if balance < required_balance:
            print(f"{Fore.RED}  ✖ {LANG[language]['no_balance'].format(price=required_balance)}{Style.RESET_ALL}")
            return False

        tx = nft_contract.functions.mint().build_transaction({
            'from': sender_address,
            'value': mint_price,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'gas': gas_limit,
            'gasPrice': gas_price
        })

        print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_link = f"{EXPLORER_URL}/tx/0x{tx_hash.hex()}"

        print(f"{Fore.CYAN}  > {LANG[language]['waiting_tx']}{Style.RESET_ALL}")
        receipt = await wait_for_receipt(w3, tx_hash, MAX_WAIT_TIME, language)

        if receipt is None:
            print(f"{Fore.YELLOW}  {LANG[language]['timeout'].format(timeout=MAX_WAIT_TIME)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    - Tx: {tx_link}{Style.RESET_ALL}")
            return True
        elif receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ {LANG[language]['success']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    - {LANG[language]['address']}: {sender_address}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    - Tx: {tx_link}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
            return False

    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Thất bại / Failed'}: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}    - Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
        return False

# Hàm chính
async def run_conftnft(language: str = 'en'):
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    w3 = connect_web3(language)
    print()

    successful_mints = 0
    total_wallets = len(private_keys)

    random.shuffle(private_keys)  # Xáo trộn danh sách ví để xử lý ngẫu nhiên

    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{total_wallets})", Fore.MAGENTA)
        print()

        if await mint_conft_nft(w3, private_key, profile_num, language):
            successful_mints += 1
        
        if i < total_wallets:
            delay = random.uniform(10, 30)  # Tạm nghỉ ngẫu nhiên 10-30 giây giữa các ví
            print(f"{Fore.YELLOW}  {'Tạm nghỉ' if language == 'vi' else 'Pausing'} {delay:.2f} {'giây' if language == 'vi' else 'seconds'}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()

    print_border(f"{LANG[language]['completed'].format(successful=successful_mints, total=total_wallets)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_conftnft('vi'))
