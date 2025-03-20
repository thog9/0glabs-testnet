import os
import sys
import asyncio
import random
import time
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style

# Khởi tạo colorama
init(autoreset=True)

# Độ rộng viền
BORDER_WIDTH = 80

# Constants
NETWORK_URL = "https://evmrpc-testnet.0g.ai"
CHAIN_ID = 16600
EXPLORER_URL = "https://chainscan-newton.0g.ai/tx/0x"
STORAGE_SCAN_CONTRACT = "0x0460aA47b41a66694c0a73f667a1b795A5ED3556"

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': '✨ DEPLOY STORAGE SCAN - OG LABS TESTNET ✨',
        'info': 'ℹ Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallet': '⚙ XỬ LÝ VÍ',
        'start_deploy': '✨ BẮT ĐẦU DEPLOY STORAGE SCAN',
        'deploying': 'Đang deploy Storage Scan...',
        'success': '✅ Deploy Storage Scan thành công!',
        'failure': '❌ Deploy Storage Scan thất bại',
        'timeout': '⏰ Giao dịch chưa xác nhận sau {timeout} giây, kiểm tra explorer',
        'address': 'Địa chỉ ví',
        'value': 'Giá trị',
        'gas': 'Gas',
        'block': 'Khối',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} DEPLOY THÀNH CÔNG',
        'error': 'Lỗi',
        'retrying': '🔄 Thử lại sau lỗi...',
        'connect_success': '✅ Thành công: Đã kết nối mạng OG Labs Testnet',
        'connect_error': '❌ Không thể kết nối RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ File pvkey.txt không tồn tại',
        'pvkey_empty': '❌ Không tìm thấy private key hợp lệ',
        'pvkey_error': '❌ Đọc pvkey.txt thất bại',
        'no_balance': '❌ Không đủ số dư A0GI để deploy',
        'balance': 'Số dư A0GI',
    },
    'en': {
        'title': '✨ DEPLOY STORAGE SCAN - OG LABS TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallet': '⚙ PROCESSING WALLET',
        'start_deploy': '✨ STARTING STORAGE SCAN DEPLOY',
        'deploying': 'Deploying Storage Scan...',
        'success': '✅ Storage Scan deployed successfully!',
        'failure': '❌ Storage Scan deployment failed',
        'timeout': '⏰ Transaction not confirmed after {timeout} seconds, check explorer',
        'address': 'Wallet address',
        'value': 'Value',
        'gas': 'Gas',
        'block': 'Block',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} DEPLOYS SUCCESSFUL',
        'error': 'Error',
        'retrying': '🔄 Retrying after error...',
        'connect_success': '✅ Success: Connected to OG Labs Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'no_balance': '❌ Insufficient A0GI balance for deployment',
        'balance': 'A0GI Balance',
    }
}

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}╔{'═' * (width - 2)}╗{Style.RESET_ALL}")
    print(f"{color}║{padded_text}║{Style.RESET_ALL}")
    print(f"{color}╚{'═' * (width - 2)}╝{Style.RESET_ALL}")

# Hàm hiển thị phân cách
def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

# Hàm kiểm tra private key hợp lệ
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

# Hàm đọc private keys từ file pvkey.txt
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
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['error']}: Dòng {i} - {key} không hợp lệ{Style.RESET_ALL}")
        
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
            print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} | Chain ID: {w3.eth.chain_id}{Style.RESET_ALL}")
            return w3
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['connect_error']}{Style.RESET_ALL}")
            sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['web3_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Hàm deploy Storage Scan với retry
async def deploy_storage_scan(w3: Web3, private_key: str, wallet_index: int, language: str = 'en', max_retries: int = 3):
    account = Account.from_key(private_key)
    
    for attempt in range(max_retries):
        try:
            # Kiểm tra số dư A0GI
            balance = w3.from_wei(w3.eth.get_balance(account.address), 'ether')
            print(f"{Fore.YELLOW}  - {LANG[language]['balance']}: {balance:.6f}{Style.RESET_ALL}")
            if balance == 0:
                print(f"{Fore.RED}  ✖ {LANG[language]['no_balance']}{Style.RESET_ALL}")
                return False

            # Tạo random bytes (32 bytes)
            content_hash = bytes([random.randint(0, 255) for _ in range(32)])

            # Tạo payload giống giao dịch thành công
            data = (
                "0xef3e12dc" +
                "0000000000000000000000000000000000000000000000000000000000000020" +
                "0000000000000000000000000000000000000000000000000000000000000014" +
                "0000000000000000000000000000000000000000000000000000000000000060" +
                "0000000000000000000000000000000000000000000000000000000000000080" +
                "0000000000000000000000000000000000000000000000000000000000000000" +
                "0000000000000000000000000000000000000000000000000000000000000001" +
                content_hash.hex() +
                "0000000000000000000000000000000000000000000000000000000000000000"
            )

            # Giá trị ngẫu nhiên giữa 0.000005 và 0.00001 ETH
            random_value = random.uniform(0.000005, 0.00001)
            value_wei = w3.to_wei(random_value, 'ether')

            # Chuẩn bị giao dịch
            gas_price = w3.to_wei('0.5', 'gwei')  # Tăng gas price lên 0.5 gwei
            nonce = w3.eth.get_transaction_count(account.address, 'latest')

            tx_params = {
                'from': account.address,
                'to': Web3.to_checksum_address(STORAGE_SCAN_CONTRACT),
                'value': value_wei,
                'data': data,
                'nonce': nonce,
                'chainId': CHAIN_ID,
                'gasPrice': gas_price,
            }

            # Ước lượng gas
            try:
                estimated_gas = w3.eth.estimate_gas(tx_params)
                gas_limit = int(estimated_gas * 1.5)  # Tăng gas limit lên 1.5x
                print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}{Style.RESET_ALL}")
            except:
                gas_limit = 250000  # Gas mặc định cao hơn
                print(f"{Fore.YELLOW}  - Không thể ước lượng gas, dùng mặc định: {gas_limit}{Style.RESET_ALL}")

            tx_params['gas'] = gas_limit

            # Kiểm tra số dư đủ cho gas và value
            required_balance = w3.from_wei(gas_limit * gas_price + value_wei, 'ether')
            if balance < required_balance:
                print(f"{Fore.RED}  ✖ {LANG[language]['no_balance']} (Cần: {required_balance:.6f} A0GI, Có: {balance:.6f} A0GI){Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}  > {LANG[language]['deploying']}{Style.RESET_ALL}")
            signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
            receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300))  # Tăng timeout lên 300 giây

            if receipt.status == 1:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['success']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['address']}: {account.address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['value']}: {w3.from_wei(value_wei, 'ether'):.6f} A0GI{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - Tx: {tx_link}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
                return False

        except Exception as e:
            if 'not in the chain after' in str(e):
                print(f"{Fore.YELLOW}  ⏰ {LANG[language]['timeout'].format(timeout=300)} - [{tx_link}]{Style.RESET_ALL}")
                # Kiểm tra trạng thái giao dịch sau timeout
                try:
                    receipt = w3.eth.get_transaction_receipt(tx_hash)
                    if receipt and receipt.status == 1:
                        print(f"{Fore.GREEN}  ✔ {LANG[language]['success']} (xác nhận muộn){Style.RESET_ALL}")
                        return True
                except:
                    pass
                if attempt < max_retries - 1:
                    delay = random.uniform(10, 20)
                    print(f"{Fore.RED}  ✖ {LANG[language]['retrying']} ({attempt + 1}/{max_retries}) sau lỗi timeout{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
                    continue
            else:
                delay = random.uniform(10, 30)
                print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}. {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}...{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                return False

# Hàm chính
async def run_storagescan(language: str = 'en'):
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    w3 = connect_web3(language)
    print_separator()

    total_deploys = len(private_keys)
    successful_deploys = 0

    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{len(private_keys)})", Fore.MAGENTA)
        print()
        
        print_border(LANG[language]['start_deploy'], Fore.CYAN)
        if await deploy_storage_scan(w3, private_key, i, language):
            successful_deploys += 1
        
        if i < len(private_keys):
            delay = random.uniform(10, 30)
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()

    print_border(LANG[language]['completed'].format(successful=successful_deploys, total=total_deploys), Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_storagescan('vi'))  # Ngôn ngữ mặc định là Tiếng Việt, đổi thành 'en' nếu muốn tiếng Anh
