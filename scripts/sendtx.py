import os
import sys
import asyncio
import random
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style
import aiohttp
from aiohttp_socks import ProxyConnector

# Khởi tạo colorama
init(autoreset=True)

# Độ rộng viền
BORDER_WIDTH = 80

# Constants
NETWORK_URL = "https://evmrpc-testnet.0g.ai"
CHAIN_ID = 80087
EXPLORER_URL = "https://chainscan-galileo.0g.ai/tx/0x"
IP_CHECK_URL = "https://api.ipify.org?format=json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}
CONFIG = {
    "PAUSE_BETWEEN_ATTEMPTS": [10, 30],
    "MAX_CONCURRENCY": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.001  # OG
}

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': '✨ GỬI GIAO DỊCH - 0G TESTNET ✨',
        'info': 'ℹ Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'enter_tx_count': '✦ NHẬP SỐ LƯỢNG GIAO DỊCH',
        'tx_count_prompt': 'Số giao dịch (mặc định 1): ',
        'selected': 'Đã chọn',
        'transactions': 'giao dịch',
        'enter_amount': '✦ NHẬP SỐ LƯỢNG OG',
        'amount_prompt': 'Số lượng OG (mặc định 0.000001, tối đa 999): ',
        'amount_unit': 'OG',
        'select_tx_type': '✦ CHỌN LOẠI GIAO DỊCH',
        'random_option': '1. Gửi đến địa chỉ ngẫu nhiên',
        'file_option': '2. Gửi đến địa chỉ từ file (address.txt)',
        'choice_prompt': 'Nhập lựa chọn (1 hoặc 2): ',
        'start_random': '✨ BẮT ĐẦU GỬI {tx_count} GIAO DỊCH NGẪU NHIÊN',
        'start_file': '✨ BẮT ĐẦU GỬI GIAO DỊCH ĐẾN {addr_count} ĐỊA CHỈ TỪ FILE',
        'processing_wallet': '⚙ XỬ LÝ VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ (cần ít nhất {required:.6f} OG cho giao dịch)',
        'transaction': 'Giao dịch',
        'to_address': 'Địa chỉ nhận',
        'sending': 'Đang gửi giao dịch...',
        'success': '✅ Giao dịch thành công!',
        'failure': '❌ Giao dịch thất bại',
        'timeout': '⏰ Giao dịch chưa xác nhận sau {timeout} giây, kiểm tra trên explorer',
        'sender': 'Người gửi',
        'receiver': 'Người nhận',
        'amount': 'Số lượng',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'invalid_number': 'Vui lòng nhập số hợp lệ',
        'tx_count_error': 'Số giao dịch phải lớn hơn 0',
        'amount_error': 'Số lượng phải lớn hơn 0 và không quá 999',
        'invalid_choice': 'Lựa chọn không hợp lệ',
        'connect_success': '✅ Thành công: Đã kết nối mạng 0G Testnet',
        'connect_error': '❌ Không thể kết nối RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ File pvkey.txt không tồn tại',
        'pvkey_empty': '❌ Không tìm thấy private key hợp lệ',
        'pvkey_error': '❌ Đọc pvkey.txt thất bại',
        'addr_not_found': '❌ File address.txt không tồn tại',
        'addr_empty': '❌ Không tìm thấy địa chỉ hợp lệ trong address.txt',
        'addr_error': '❌ Đọc address.txt thất bại',
        'invalid_addr': 'không phải địa chỉ hợp lệ, bỏ qua',
        'warning_line': '⚠ Cảnh báo: Dòng',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'proxy_error': '❌ Lỗi kết nối proxy: {error}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
    },
    'en': {
        'title': '✨ SEND TRANSACTION - 0G TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'enter_tx_count': '✦ ENTER NUMBER OF TRANSACTIONS',
        'tx_count_prompt': 'Number of transactions (default 1): ',
        'selected': 'Selected',
        'transactions': 'transactions',
        'enter_amount': '✦ ENTER AMOUNT OF OG',
        'amount_prompt': 'Amount of OG (default 0.000001, max 999): ',
        'amount_unit': 'OG',
        'select_tx_type': '✦ SELECT TRANSACTION TYPE',
        'random_option': '1. Send to random address',
        'file_option': '2. Send to addresses from file (address.txt)',
        'choice_prompt': 'Enter choice (1 or 2): ',
        'start_random': '✨ STARTING {tx_count} RANDOM TRANSACTIONS',
        'start_file': '✨ STARTING TRANSACTIONS TO {addr_count} ADDRESSES FROM FILE',
        'processing_wallet': '⚙ PROCESSING WALLET',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance (need at least {required:.6f} OG for transaction)',
        'transaction': 'Transaction',
        'to_address': 'Receiver address',
        'sending': 'Sending transaction...',
        'success': '✅ Transaction successful!',
        'failure': '❌ Transaction failed',
        'timeout': '⏰ Transaction not confirmed after {timeout} seconds, check on explorer',
        'sender': 'Sender',
        'receiver': 'Receiver',
        'amount': 'Amount',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'invalid_number': 'Please enter a valid number',
        'tx_count_error': 'Number of transactions must be greater than 0',
        'amount_error': 'Amount must be greater than 0 and not exceed 999',
        'invalid_choice': 'Invalid choice',
        'connect_success': '✅ Success: Connected to 0G Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'addr_not_found': '❌ address.txt file not found',
        'addr_empty': '❌ No valid addresses found in address.txt',
        'addr_error': '❌ Failed to read address.txt',
        'invalid_addr': 'is not a valid address, skipped',
        'warning_line': '⚠ Warning: Line',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'no_proxies': 'No proxies found in proxies.txt',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'proxy_error': '❌ Proxy connection error: {error}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
    }
}

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

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
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i}: {LANG[language]['invalid_addr']} - {key}{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Hàm đọc địa chỉ từ file address.txt
def load_addresses(file_path: str = "address.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['addr_not_found']}. Tạo file mới.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm địa chỉ nhận vào đây, mỗi địa chỉ trên một dòng\n# Ví dụ: 0x1234567890abcdef1234567890abcdef1234567890\n")
            return None
        
        addresses = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                addr = line.strip()
                if addr and not addr.startswith('#'):
                    if Web3.is_address(addr):
                        addresses.append(Web3.to_checksum_address(addr))
                    else:
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i}: {LANG[language]['invalid_addr']} - {addr}{Style.RESET_ALL}")
        
        if not addresses:
            print(f"{Fore.RED}  ✖ {LANG[language]['addr_empty']}{Style.RESET_ALL}")
            return None
        
        return addresses
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['addr_error']}: {str(e)}{Style.RESET_ALL}")
        return None

# Hàm đọc proxies từ proxies.txt
def load_proxies(file_path: str = "proxies.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Dùng không proxy.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm proxy vào đây, mỗi proxy trên một dòng\n# Ví dụ: socks5://user:pass@host:port hoặc http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not proxy.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Dùng không proxy.{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}{Style.RESET_ALL}")
        return proxies
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

# Hàm lấy IP công khai qua proxy
async def get_proxy_ip(proxy: str = None, language: str = 'en') -> str:
    try:
        if proxy:
            if proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')):
                connector = ProxyConnector.from_url(proxy)
            else:
                parts = proxy.split(':')
                if len(parts) == 4:  # host:port:user:pass
                    proxy_url = f"socks5://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
                    connector = ProxyConnector.from_url(proxy_url)
                elif len(parts) == 3 and '@' in proxy:  # user:pass@host:port
                    connector = ProxyConnector.from_url(f"socks5://{proxy}")
                else:
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['invalid_proxy'].format(proxy=proxy)}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
        else:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}{Style.RESET_ALL}")
        return LANG[language]['unknown']

# Hàm kết nối Web3
def connect_web3(language: str = 'en'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if not w3.is_connected():
            print(f"{Fore.RED}  ✖ {LANG[language]['connect_error']}{Style.RESET_ALL}")
            sys.exit(1)
        print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} │ Chain ID: {w3.eth.chain_id}{Style.RESET_ALL}")
        return w3
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['web3_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Hàm đợi receipt thủ công
async def wait_for_receipt(w3: Web3, tx_hash: str, max_wait_time: int = 300, language: str = 'en'):
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

# Tạo địa chỉ ngẫu nhiên với checksum
def get_random_address(w3: Web3):
    random_account = w3.eth.account.create()
    return random_account.address

# Hàm gửi giao dịch
async def send_transaction(w3: Web3, private_key: str, to_address: str, amount: float, wallet_index: int, tx_index: int, total_tx: int, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            nonce = w3.eth.get_transaction_count(sender_address)
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))

            # Ước lượng gas
            try:
                estimated_gas = w3.eth.estimate_gas({
                    'from': sender_address,
                    'to': to_address,
                    'value': w3.to_wei(amount, 'ether')
                })
                gas_limit = int(estimated_gas * 1.2)
                print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}{Style.RESET_ALL}")
            except Exception as e:
                gas_limit = 30000
                print(f"{Fore.YELLOW}  - Không thể ước lượng gas: {str(e)}. Dùng gas mặc định: {gas_limit}{Style.RESET_ALL}")

            balance = w3.from_wei(w3.eth.get_balance(sender_address), 'ether')
            required_balance = w3.from_wei(gas_limit * gas_price + w3.to_wei(amount, 'ether'), 'ether')
            if balance < required_balance:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=required_balance)}: {balance:.6f} OG{Style.RESET_ALL}")
                return False

            tx = {
                'nonce': nonce,
                'to': to_address,
                'value': w3.to_wei(amount, 'ether'),
                'gas': gas_limit,
                'gasPrice': gas_price,
                'chainId': CHAIN_ID,
            }

            print(f"{Fore.CYAN}  > {LANG[language]['sending']}{Style.RESET_ALL}")
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=300, language=language)

            if receipt is None:
                print(f"{Fore.YELLOW}  {LANG[language]['timeout'].format(timeout=300)} - Tx: {tx_link}{Style.RESET_ALL}")
                return True
            elif receipt.status == 1:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['success']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['sender']}: {sender_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['receiver']}: {to_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['amount']}: {amount:.6f} {LANG[language]['amount_unit']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['balance']}: {w3.from_wei(w3.eth.get_balance(sender_address), 'ether'):.6f} {LANG[language]['amount_unit']}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
                return False
        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} | Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  ⚠ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} | Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
            return False

# Hàm nhập số lượng giao dịch
def get_tx_count(language: str = 'en') -> int:
    print_border(LANG[language]['enter_tx_count'], Fore.YELLOW)
    while True:
        try:
            tx_count_input = input(f"{Fore.YELLOW}  > {LANG[language]['tx_count_prompt']}{Style.RESET_ALL}")
            tx_count = int(tx_count_input) if tx_count_input.strip() else 1
            if tx_count <= 0:
                print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['tx_count_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['selected']}: {tx_count} {LANG[language]['transactions']}{Style.RESET_ALL}")
                return tx_count
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

# Hàm nhập số lượng OG
def get_amount(language: str = 'en') -> float:
    print_border(LANG[language]['enter_amount'], Fore.YELLOW)
    while True:
        try:
            amount_input = input(f"{Fore.YELLOW}  > {LANG[language]['amount_prompt']}{Style.RESET_ALL}")
            amount = float(amount_input) if amount_input.strip() else 0.000001
            if 0 < amount <= 999:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['selected']}: {amount} {LANG[language]['amount_unit']}{Style.RESET_ALL}")
                return amount
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['amount_error']}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

# Gửi giao dịch đến địa chỉ ngẫu nhiên
async def send_to_random_addresses(w3: Web3, amount: float, tx_count: int, private_key: str, wallet_index: int, language: str = 'en'):
    successful_txs = 0
    
    for tx_iter in range(tx_count):
        print(f"{Fore.CYAN}  > {LANG[language]['transaction']} {tx_iter + 1}/{tx_count}{Style.RESET_ALL}")
        to_address = get_random_address(w3)
        if await send_transaction(w3, private_key, to_address, amount, wallet_index, tx_iter + 1, tx_count, language):
            successful_txs += 1
        if tx_iter < tx_count - 1:
            delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()
    
    return successful_txs

# Gửi giao dịch đến địa chỉ từ file
async def send_to_file_addresses(w3: Web3, amount: float, addresses: list, private_key: str, wallet_index: int, language: str = 'en'):
    successful_txs = 0
    
    for addr_iter, to_address in enumerate(addresses, 1):
        print(f"{Fore.CYAN}  > {LANG[language]['to_address']} {addr_iter}/{len(addresses)}{Style.RESET_ALL}")
        if await send_transaction(w3, private_key, to_address, amount, wallet_index, addr_iter, len(addresses), language):
            successful_txs += 1
        if addr_iter < len(addresses):
            delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()
    
    return successful_txs

# Hàm xử lý từng ví
async def process_wallet(index: int, profile_num: int, private_key: str, proxy: str, w3: Web3, choice: str, tx_count: int, amount: float, language: str):
    total_wallets = CONFIG.get('TOTAL_WALLETS', 1)
    print_border(
        f"{LANG[language]['processing_wallet']} {profile_num} ({index + 1}/{total_wallets})",
        Fore.MAGENTA
    )
    print()

    # Display proxy info
    public_ip = await get_proxy_ip(proxy, language)
    proxy_display = proxy if proxy else LANG[language]['no_proxy']
    print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

    print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
    eth_balance = float(w3.from_wei(w3.eth.get_balance(Account.from_key(private_key).address), 'ether'))
    if eth_balance < CONFIG['MINIMUM_BALANCE']:
        print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=CONFIG['MINIMUM_BALANCE'])}: {eth_balance:.6f} OG{Style.RESET_ALL}")
        return 0

    if choice == '1':
        print_border(LANG[language]['start_random'].format(tx_count=tx_count), Fore.CYAN)
        result = await send_to_random_addresses(w3, amount, tx_count, private_key, index, language)
    else:
        addresses = load_addresses('address.txt', language)
        if not addresses:
            return 0
        print_border(LANG[language]['start_file'].format(addr_count=len(addresses)), Fore.CYAN)
        result = await send_to_file_addresses(w3, amount, addresses, private_key, index, language)
    
    print_separator(Fore.GREEN if result > 0 else Fore.RED)
    return result

# Hàm chính
async def run_sendtx(language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    proxies = load_proxies('proxies.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    tx_count = get_tx_count(language)
    amount = get_amount(language)
    print_separator()

    while True:
        print_border(LANG[language]['select_tx_type'], Fore.YELLOW)
        print(f"{Fore.GREEN}    ├─ {LANG[language]['random_option']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    └─ {LANG[language]['file_option']}{Style.RESET_ALL}")
        choice = input(f"{Fore.YELLOW}  > {LANG[language]['choice_prompt']}{Style.RESET_ALL}").strip()

        if choice in ['1', '2']:
            break
        print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        print()

    successful_txs = 0
    total_wallets = len(private_keys)
    failed_attempts = 0
    CONFIG['TOTAL_WALLETS'] = total_wallets
    CONFIG['MAX_CONCURRENCY'] = min(CONFIG['MAX_CONCURRENCY'], total_wallets)

    random.shuffle(private_keys)
    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    async def limited_task(index, profile_num, private_key, proxy):
        nonlocal successful_txs, failed_attempts
        async with semaphore:
            result = await process_wallet(index, profile_num, private_key, proxy, w3, choice, tx_count, amount, language)
            if result > 0:
                successful_txs += result
                failed_attempts = 0
            else:
                failed_attempts += 1
                if failed_attempts >= 3:
                    print(f"{Fore.RED}  ✖ Dừng xử lý ví {profile_num}: Quá nhiều giao dịch thất bại liên tiếp{Style.RESET_ALL}")
                    return
            if index < total_wallets - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
                print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)

    tasks = []
    for i, (profile_num, private_key) in enumerate(private_keys):
        proxy = proxies[i % len(proxies)] if proxies else None
        tasks.append(limited_task(i, profile_num, private_key, proxy))

    await asyncio.gather(*tasks, return_exceptions=True)

    total_txs = (tx_count if choice == '1' else len(load_addresses('address.txt', language) or [0])) * len(private_keys)
    print()
    print_border(
        f"{LANG[language]['completed'].format(successful=successful_txs, total=total_txs)}",
        Fore.GREEN
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_sendtx('vi'))
