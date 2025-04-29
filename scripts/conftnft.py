import os
import sys
import asyncio
import random
from web3 import Web3
from web3.exceptions import ContractLogicError
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
CONFT_NFT_ADDRESS = "0xFC79f0EaC5bEcf21fDcf037bAdb977b2b43DE497"
IP_CHECK_URL = "https://api.ipify.org?format=json"
MAX_WAIT_TIME = 300  # Thời gian tối đa đợi receipt (5 phút)
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
    "MINIMUM_BALANCE": 0.03  # OG (bao gồm phí mint và gas)
}

# ABI cho NFT contract
NFT_ABI = [
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "owner", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"},
    {"name": "mint", "type": "function", "inputs": [], "outputs": [], "stateMutability": "payable"}
]

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': '✨ MINT GALILEO DRIFT (GD) NFT - 0G TESTNET ✨',
        'info': 'ℹ Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'processing_wallet': '⚙ XỬ LÝ VÍ',
        'checking_balance': 'Đang kiểm tra số dư NFT...',
        'has_nft': 'Ví này đã mint Galileo Drift (GD)! Không thực hiện lại',
        'no_balance': 'Số dư ví không đủ để mint (cần ít nhất {price} OG)',
        'preparing_tx': 'Đang chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'waiting_tx': 'Đang đợi xác nhận giao dịch...',
        'success': '✅ Mint Galileo Drift (GD) thành công!',
        'failure': '❌ Mint Galileo Drift (GD) thất bại',
        'timeout': '⚠ Đã hết thời gian đợi ({timeout} giây), kiểm tra giao dịch trên explorer...',
        'address': 'Địa chỉ ví',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư OG',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': '✅ Thành công: Đã kết nối mạng 0G Testnet',
        'connect_error': '❌ Không thể kết nối RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ File pvkey.txt không tồn tại',
        'pvkey_empty': '❌ Không tìm thấy private key hợp lệ',
        'pvkey_error': '❌ Đọc pvkey.txt thất bại',
        'invalid_key': 'không hợp lệ, bỏ qua',
        'warning_line': '⚠ Cảnh báo: Dòng',
        'stop_wallet': 'Dừng xử lý ví {wallet}: Quá nhiều giao dịch thất bại liên tiếp',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'proxy_error': '❌ Lỗi kết nối proxy: {error}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
    },
    'en': {
        'title': '✨ MINT GALILEO DRIFT (GD) NFT - 0G TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'processing_wallet': '⚙ PROCESSING WALLET',
        'checking_balance': 'Checking NFT balance...',
        'has_nft': 'This wallet has already minted Galileo Drift (GD)! Skipping',
        'no_balance': 'Insufficient balance to mint (need at least {price} OG)',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'waiting_tx': 'Waiting for transaction confirmation...',
        'success': '✅ Successfully minted Galileo Drift (GD)!',
        'failure': '❌ Failed to mint Galileo Drift (GD)',
        'timeout': '⚠ Timeout after {timeout} seconds, check transaction on explorer...',
        'address': 'Wallet address',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'OG Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'connect_success': '✅ Success: Connected to 0G Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': '⚠ Warning: Line',
        'stop_wallet': 'Stopping wallet {wallet}: Too many consecutive failed transactions',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'no_proxies': 'No proxies found in proxies.txt',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'proxy_error': '❌ Proxy connection error: {error}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
    }
}

# Hàm hiển thị viền đẹp
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

# Kiểm tra private key hợp lệ
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

# Đọc private keys từ pvkey.txt
def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add private keys here, one per line\n# Example: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
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
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key[:10]}...{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Đọc proxies từ proxies.txt
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

# Lấy IP công khai qua proxy
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

# Kết nối Web3
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

# Hàm mint Galileo Drift NFT
async def mint_conft_nft(w3: Web3, private_key: str, wallet_index: int, proxy: str = None, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            # Display proxy info
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

            nft_contract = w3.eth.contract(address=Web3.to_checksum_address(CONFT_NFT_ADDRESS), abi=NFT_ABI)
            
            print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
            nft_balance = nft_contract.functions.balanceOf(sender_address).call()
            if nft_balance >= 1:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['has_nft']}{Style.RESET_ALL}")
                return True

            mint_price = w3.to_wei(0.03, 'ether')  # Phí mint cố định 0.03 OG
            balance = w3.from_wei(w3.eth.get_balance(sender_address), 'ether')
            print(f"{Fore.YELLOW}  - Số dư hiện tại: {balance:.6f} OG{Style.RESET_ALL}")

            print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
            nonce = w3.eth.get_transaction_count(sender_address)
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))  # Tăng nhẹ gas price

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
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

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
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  ⚠ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)}{Style.RESET_ALL}")
            return False

# Hàm xử lý từng ví
async def process_wallet(index: int, profile_num: int, private_key: str, proxy: str, w3: Web3, language: str):
    total_wallets = CONFIG.get('TOTAL_WALLETS', 1)
    print_border(
        f"{LANG[language]['processing_wallet']} {profile_num} ({index + 1}/{total_wallets})",
        Fore.MAGENTA
    )
    print()

    result = await mint_conft_nft(w3, private_key, profile_num, proxy, language)
    print_separator(Fore.GREEN if result else Fore.RED)
    return result

# Hàm chính
async def run_conftnft(language: str = 'vi'):
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

    successful_mints = 0
    total_wallets = len(private_keys)
    failed_attempts = 0
    CONFIG['TOTAL_WALLETS'] = total_wallets
    CONFIG['MAX_CONCURRENCY'] = min(CONFIG['MAX_CONCURRENCY'], total_wallets)

    random.shuffle(private_keys)
    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    async def limited_task(index, profile_num, private_key, proxy):
        nonlocal successful_mints, failed_attempts
        async with semaphore:
            result = await process_wallet(index, profile_num, private_key, proxy, w3, language)
            if result:
                successful_mints += 1
                failed_attempts = 0
            else:
                failed_attempts += 1
                if failed_attempts >= 3:
                    print(f"{Fore.RED}  ✖ {LANG[language]['stop_wallet'].format(wallet=profile_num)}{Style.RESET_ALL}")
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

    print()
    print_border(
        f"{LANG[language]['completed'].format(successful=successful_mints, total=total_wallets)}",
        Fore.GREEN
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_conftnft('vi'))
