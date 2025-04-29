import os
import sys
import asyncio
import random
import time
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
ROUTER_ADDRESS = "0x16a811adc55A99b4456F62c54F12D3561559a268"
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

# Token configurations
TOKENS = {
    "USDT": {"address": "0xA8F030218d7c26869CADd46C5F10129E635cD565", "decimals": 18},
    "BTC": {"address": "0x6dc29491a8396Bd52376b4f6dA1f3E889C16cA85", "decimals": 18},
    "ETH": {"address": "0x2619090fcfDB99a8CCF51c76C9467F7375040eeb", "decimals": 18},
}

# Maximum uint256 for unlimited approve
MAX_UINT256 = 2**256 - 1

# ERC20 ABI
ERC20_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "address", "name": "", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# Router ABI
ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "internalType": "struct ISwapRouter.ExactInputSingleParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function",
    }
]

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': '✨ SWAP TOKEN - 0G TESTNET ✨',
        'info': 'ℹ Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'select_swap_type': '✦ CHỌN KIỂU SWAP',
        'random_option': '1. Swap token ngẫu nhiên',
        'manual_option': '2. Swap token thủ công',
        'choice_prompt': 'Nhập lựa chọn (1 hoặc 2): ',
        'enter_swap_count': '✦ NHẬP SỐ LƯỢNG SWAP',
        'swap_count_prompt': 'Số lần swap (mặc định 1): ',
        'enter_amount': '✦ NHẬP SỐ LƯỢNG TOKEN SWAP',
        'amount_prompt': 'Số lượng token (mặc định 0.1): ',
        'select_manual_swap': '✦ CHỌN CẶP SWAP THỦ CÔNG',
        'start_random': '✨ BẮT ĐẦU {swap_count} SWAP NGẪU NHIÊN',
        'start_manual': '✨ BẮT ĐẦU SWAP THỦ CÔNG',
        'processing_wallet': '⚙ XỬ LÝ VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ (cần ít nhất {required:.6f} OG hoặc token cho giao dịch)',
        'swap': 'Swap',
        'approving': 'Đang approve token...',
        'swapping': 'Đang thực hiện swap...',
        'success': '✅ Swap thành công!',
        'failure': '❌ Swap thất bại',
        'timeout': '⏰ Giao dịch chưa xác nhận sau {timeout} giây, kiểm tra trên explorer',
        'address': 'Địa chỉ ví',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} SWAP THÀNH CÔNG',
        'completed_all': '🏁 HOÀN THÀNH: {successful}/{total} VÍ SWAP THÀNH CÔNG',
        'error': 'Lỗi',
        'invalid_number': 'Vui lòng nhập số hợp lệ',
        'swap_count_error': 'Số lần swap phải lớn hơn 0',
        'amount_error': 'Số lượng token phải lớn hơn 0',
        'invalid_choice': 'Lựa chọn không hợp lệ',
        'connect_success': '✅ Thành công: Đã kết nối mạng 0G Testnet',
        'connect_error': '❌ Không thể kết nối RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ File pvkey.txt không tồn tại',
        'pvkey_empty': '❌ Không tìm thấy private key hợp lệ',
        'pvkey_error': '❌ Đọc pvkey.txt thất bại',
        'invalid_key': 'không hợp lệ, bỏ qua',
        'warning_line': '⚠ Cảnh báo: Dòng',
        'no_balance': '❌ Không đủ số dư token hoặc OG để swap',
        'selected': 'Đã chọn',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'proxy_error': '❌ Lỗi kết nối proxy: {error}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
        'manual_swap_options': {
            1: '1. Swap USDT -> ETH',
            2: '2. Swap ETH -> USDT',
            3: '3. Swap USDT -> BTC',
            4: '4. Swap BTC -> USDT',
            5: '5. Swap BTC -> ETH',
            6: '6. Swap ETH -> BTC',
        },
        'manual_swap_prompt': 'Chọn cặp swap (1-6): ',
    },
    'en': {
        'title': '✨ SWAP TOKEN - 0G TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'select_swap_type': '✦ SELECT SWAP TYPE',
        'random_option': '1. Random token swap',
        'manual_option': '2. Manual token swap',
        'choice_prompt': 'Enter choice (1 or 2): ',
        'enter_swap_count': '✦ ENTER NUMBER OF SWAPS',
        'swap_count_prompt': 'Number of swaps (default 1): ',
        'enter_amount': '✦ ENTER TOKEN AMOUNT TO SWAP',
        'amount_prompt': 'Token amount (default 0.1): ',
        'select_manual_swap': '✦ SELECT MANUAL SWAP PAIR',
        'start_random': '✨ STARTING {swap_count} RANDOM SWAPS',
        'start_manual': '✨ STARTING MANUAL SWAP',
        'processing_wallet': '⚙ PROCESSING WALLET',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance (need at least {required:.6f} OG or token for transaction)',
        'swap': 'Swap',
        'approving': 'Approving token...',
        'swapping': 'Performing swap...',
        'success': '✅ Swap successful!',
        'failure': '❌ Swap failed',
        'timeout': '⏰ Transaction not confirmed after {timeout} seconds, check on explorer',
        'address': 'Wallet address',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} SWAPS SUCCESSFUL',
        'completed_all': '🏁 COMPLETED: {successful}/{total} WALLETS SWAPPED SUCCESSFULLY',
        'error': 'Error',
        'invalid_number': 'Please enter a valid number',
        'swap_count_error': 'Number of swaps must be greater than 0',
        'amount_error': 'Token amount must be greater than 0',
        'invalid_choice': 'Invalid choice',
        'connect_success': '✅ Success: Connected to 0G Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': '⚠ Warning: Line',
        'no_balance': '❌ Insufficient token or OG balance for swap',
        'selected': 'Selected',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'no_proxies': 'No proxies found in proxies.txt',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'proxy_error': '❌ Proxy connection error: {error}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
        'manual_swap_options': {
            1: '1. Swap USDT -> ETH',
            2: '2. Swap ETH -> USDT',
            3: '3. Swap USDT -> BTC',
            4: '4. Swap BTC -> USDT',
            5: '5. Swap BTC -> ETH',
            6: '6. Swap ETH -> BTC',
        },
        'manual_swap_prompt': 'Select swap pair (1-6): ',
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

# Hàm approve token
async def approve_token(w3: Web3, private_key: str, token_address: str, spender: str, amount: int, language: str = 'en'):
    account = Account.from_key(private_key)
    token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
    
    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            allowance = token_contract.functions.allowance(account.address, spender).call()
            if allowance >= amount:
                print(f"{Fore.GREEN}  ✔ Đã có allowance đủ cho {spender}{Style.RESET_ALL}")
                return True

            nonce = w3.eth.get_transaction_count(account.address)
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))
            try:
                estimated_gas = token_contract.functions.approve(spender, MAX_UINT256).estimate_gas({'from': account.address})
                gas_limit = int(estimated_gas * 1.2)
                print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}{Style.RESET_ALL}")
            except Exception as e:
                gas_limit = 150000
                print(f"{Fore.YELLOW}  - Không thể ước lượng gas: {str(e)}. Dùng gas mặc định: {gas_limit}{Style.RESET_ALL}")

            balance = w3.from_wei(w3.eth.get_balance(account.address), 'ether')
            required_balance = w3.from_wei(gas_limit * gas_price, 'ether')
            if balance < required_balance:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=required_balance)}{Style.RESET_ALL}")
                return False

            tx = token_contract.functions.approve(spender, MAX_UINT256).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'chainId': CHAIN_ID,
            })

            print(f"{Fore.CYAN}  > {LANG[language]['approving']}{Style.RESET_ALL}")
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=300, language=language)

            if receipt is None:
                print(f"{Fore.YELLOW}  {LANG[language]['timeout'].format(timeout=300)} - Tx: {tx_link}{Style.RESET_ALL}")
                return True
            elif receipt.status == 1:
                print(f"{Fore.GREEN}  ✔ Approve thành công │ Tx: {tx_link}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ✖ Approve thất bại │ Tx: {tx_link}{Style.RESET_ALL}")
                return False
        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print(f"{Fore.RED}  ✖ Approve thất bại: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  ⚠ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ Approve thất bại: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
            return False

# Hàm swap token
async def swap_tokens(w3: Web3, private_key: str, token_in: str, token_out: str, amount_in: int, token_in_symbol: str, token_out_symbol: str, language: str = 'en'):
    account = Account.from_key(private_key)
    router_contract = w3.eth.contract(address=Web3.to_checksum_address(ROUTER_ADDRESS), abi=ROUTER_ABI)

    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            # Kiểm tra số dư token
            token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_in), abi=ERC20_ABI)
            balance = token_contract.functions.balanceOf(account.address).call()
            if balance < amount_in:
                print(f"{Fore.RED}  ✖ {LANG[language]['no_balance']} (Cần: {amount_in / 10**TOKENS[token_in_symbol]['decimals']:.6f} {token_in_symbol}, Có: {balance / 10**TOKENS[token_in_symbol]['decimals']:.6f} {token_in_symbol}){Style.RESET_ALL}")
                return False

            # Approve token
            if not await approve_token(w3, private_key, token_in, ROUTER_ADDRESS, amount_in, language):
                return False

            # Chuẩn bị tham số swap
            swap_params = {
                "tokenIn": Web3.to_checksum_address(token_in),
                "tokenOut": Web3.to_checksum_address(token_out),
                "fee": 3000,  # 0.3%
                "recipient": account.address,
                "deadline": int(time.time()) + 1800,  # 30 phút
                "amountIn": amount_in,
                "amountOutMinimum": 0,
                "sqrtPriceLimitX96": 0,
            }

            nonce = w3.eth.get_transaction_count(account.address)
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))
            try:
                estimated_gas = router_contract.functions.exactInputSingle(swap_params).estimate_gas({'from': account.address})
                gas_limit = int(estimated_gas * 1.2)
                print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}{Style.RESET_ALL}")
            except Exception as e:
                gas_limit = 300000
                print(f"{Fore.YELLOW}  - Không thể ước lượng gas: {str(e)}. Dùng gas mặc định: {gas_limit}{Style.RESET_ALL}")

            balance = w3.from_wei(w3.eth.get_balance(account.address), 'ether')
            required_balance = w3.from_wei(gas_limit * gas_price, 'ether')
            if balance < required_balance:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=required_balance)}{Style.RESET_ALL}")
                return False

            tx = router_contract.functions.exactInputSingle(swap_params).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'chainId': CHAIN_ID,
            })

            print(f"{Fore.CYAN}  > {LANG[language]['swapping']}{Style.RESET_ALL}")
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=300, language=language)

            if receipt is None:
                print(f"{Fore.YELLOW}  {LANG[language]['timeout'].format(timeout=300)} - Tx: {tx_link}{Style.RESET_ALL}")
                return True
            elif receipt.status == 1:
                amount_out = receipt.logs[0].data[-32:]  # Lấy amountOut từ log
                amount_out = int.from_bytes(amount_out, 'big')
                print(f"{Fore.GREEN}  ✔ {LANG[language]['success']} │ Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['address']}: {account.address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - Số lượng vào: {amount_in / 10**TOKENS[token_in_symbol]['decimals']:.6f} {token_in_symbol} | {LANG[language]['balance']}: {(token_contract.functions.balanceOf(account.address).call() / 10**TOKENS[token_in_symbol]['decimals']):.6f} {token_in_symbol}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - Số lượng ra: {amount_out / 10**TOKENS[token_out_symbol]['decimals']:.6f} {token_out_symbol} | {LANG[language]['balance']}: {(w3.eth.contract(address=Web3.to_checksum_address(token_out), abi=ERC20_ABI).functions.balanceOf(account.address).call() / 10**TOKENS[token_out_symbol]['decimals']):.6f} {token_out_symbol}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']} │ Tx: {tx_link}{Style.RESET_ALL}")
                return False
        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print(f"{Fore.RED}  ✖ Swap thất bại: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  ⚠ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ Swap thất bại: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
            return False

# Hàm nhập số lượng swap
def get_swap_count(language: str = 'en') -> int:
    print_border(LANG[language]['enter_swap_count'], Fore.YELLOW)
    while True:
        try:
            swap_count_input = input(f"{Fore.YELLOW}  > {LANG[language]['swap_count_prompt']}{Style.RESET_ALL}")
            swap_count = int(swap_count_input) if swap_count_input.strip() else 1
            if swap_count <= 0:
                print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['swap_count_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['selected']}: {swap_count} swaps{Style.RESET_ALL}")
                return swap_count
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

# Hàm nhập số lượng token swap
def get_swap_amount(language: str = 'en') -> float:
    print_border(LANG[language]['enter_amount'], Fore.YELLOW)
    while True:
        try:
            amount_input = input(f"{Fore.YELLOW}  > {LANG[language]['amount_prompt']}{Style.RESET_ALL}")
            amount = float(amount_input) if amount_input.strip() else 0.1
            if amount <= 0:
                print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['amount_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['selected']}: {amount} token{Style.RESET_ALL}")
                return amount
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

# Hàm hiển thị số dư
def display_balances(w3: Web3, account_address: str, language: str = 'en'):
    print(f"{Fore.YELLOW}  - {LANG[language]['balance']} USDT: {(w3.eth.contract(address=Web3.to_checksum_address(TOKENS['USDT']['address']), abi=ERC20_ABI).functions.balanceOf(account_address).call() / 10**18):.6f}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  - {LANG[language]['balance']} ETH: {(w3.eth.contract(address=Web3.to_checksum_address(TOKENS['ETH']['address']), abi=ERC20_ABI).functions.balanceOf(account_address).call() / 10**18):.6f}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  - {LANG[language]['balance']} BTC: {(w3.eth.contract(address=Web3.to_checksum_address(TOKENS['BTC']['address']), abi=ERC20_ABI).functions.balanceOf(account_address).call() / 10**18):.6f}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  - {LANG[language]['balance']} OG: {(w3.from_wei(w3.eth.get_balance(account_address), 'ether')):.6f}{Style.RESET_ALL}")

# Swap ngẫu nhiên
async def random_swap(w3: Web3, private_key: str, swap_count: int, amount: float, wallet_index: int, language: str = 'en'):
    account = Account.from_key(private_key)
    successful_swaps = 0
    
    for swap_num in range(swap_count):
        print(f"{Fore.CYAN}  > {LANG[language]['swap']} {swap_num + 1}/{swap_count}{Style.RESET_ALL}")
        
        # Hiển thị số dư
        display_balances(w3, account.address, language)
        
        # Lấy danh sách token có số dư
        token_balances = {}
        for symbol, token_data in TOKENS.items():
            contract = w3.eth.contract(address=Web3.to_checksum_address(token_data['address']), abi=ERC20_ABI)
            balance = contract.functions.balanceOf(account.address).call()
            token_balances[symbol] = balance
        
        tokens_with_balance = [symbol for symbol, balance in token_balances.items() if balance > 0]
        if not tokens_with_balance:
            print(f"{Fore.RED}  ✖ {LANG[language]['no_balance']}{Style.RESET_ALL}")
            break

        token_in_symbol = random.choice(tokens_with_balance)
        token_in_address = TOKENS[token_in_symbol]["address"]
        balance = token_balances[token_in_symbol]
        amount_in = int(amount * 10**TOKENS[token_in_symbol]["decimals"])
        if balance < amount_in:
            print(f"{Fore.RED}  ✖ {LANG[language]['no_balance']} (Cần: {amount}, Có: {balance / 10**TOKENS[token_in_symbol]['decimals']:.6f} {token_in_symbol}){Style.RESET_ALL}")
            break

        if token_in_symbol == "USDT":
            token_out_symbol = random.choice(["ETH", "BTC"])
        else:
            token_out_symbol = "USDT"
        token_out_address = TOKENS[token_out_symbol]["address"]

        if await swap_tokens(w3, private_key, token_in_address, token_out_address, amount_in, token_in_symbol, token_out_symbol, language):
            successful_swaps += 1
        
        if swap_num < swap_count - 1:
            delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()
    
    return successful_swaps

# Swap thủ công
async def manual_swap(w3: Web3, private_key: str, wallet_index: int, language: str = 'en'):
    account = Account.from_key(private_key)
    
    print_border(LANG[language]['select_manual_swap'], Fore.YELLOW)
    for i in range(1, 7):
        print(f"{Fore.GREEN}    ├─ {LANG[language]['manual_swap_options'][i]}{Style.RESET_ALL}" if i < 6 else 
              f"{Fore.GREEN}    └─ {LANG[language]['manual_swap_options'][i]}{Style.RESET_ALL}")
    
    while True:
        try:
            choice = int(input(f"{Fore.YELLOW}  > {LANG[language]['manual_swap_prompt']}{Style.RESET_ALL}"))
            if choice in range(1, 7):
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_number']}{Style.RESET_ALL}")

    pairs = {
        1: ("USDT", "ETH"), 2: ("ETH", "USDT"), 3: ("USDT", "BTC"),
        4: ("BTC", "USDT"), 5: ("BTC", "ETH"), 6: ("ETH", "BTC")
    }
    token_in_symbol, token_out_symbol = pairs[choice]
    token_in_address = TOKENS[token_in_symbol]["address"]
    token_out_address = TOKENS[token_out_symbol]["address"]

    # Hiển thị số dư trước khi nhập lượng token
    print_separator()
    display_balances(w3, account.address, language)
    
    # Nhập số lượng token
    amount = get_swap_amount(language)
    amount_in = int(amount * 10**TOKENS[token_in_symbol]["decimals"])

    contract = w3.eth.contract(address=Web3.to_checksum_address(token_in_address), abi=ERC20_ABI)
    balance = contract.functions.balanceOf(account.address).call()
    if balance < amount_in:
        print(f"{Fore.RED}  ✖ {LANG[language]['no_balance']} (Cần: {amount}, Có: {balance / 10**TOKENS[token_in_symbol]['decimals']:.6f} {token_in_symbol}){Style.RESET_ALL}")
        return 0
    
    success = await swap_tokens(w3, private_key, token_in_address, token_out_address, amount_in, token_in_symbol, token_out_symbol, language)
    return 1 if success else 0

# Hàm xử lý từng ví
async def process_wallet(index: int, profile_num: int, private_key: str, proxy: str, w3: Web3, language: str, choice: str, swap_count: int, amount: float):
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
        print_border(LANG[language]['start_random'].format(swap_count=swap_count), Fore.CYAN)
        result = await random_swap(w3, private_key, swap_count, amount, index, language)
    else:
        print_border(LANG[language]['start_manual'], Fore.CYAN)
        result = await manual_swap(w3, private_key, index, language)
    
    print_separator(Fore.GREEN if result > 0 else Fore.RED)
    return result

# Hàm chính
async def run_swaptoken(language: str = 'vi'):
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

    while True:
        print_border(LANG[language]['select_swap_type'], Fore.YELLOW)
        print(f"{Fore.GREEN}    ├─ {LANG[language]['random_option']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    └─ {LANG[language]['manual_option']}{Style.RESET_ALL}")
        choice = input(f"{Fore.YELLOW}  > {LANG[language]['choice_prompt']}{Style.RESET_ALL}").strip()

        if choice in ['1', '2']:
            break
        print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        print()

    if choice == '1':
        swap_count = get_swap_count(language)
        amount = get_swap_amount(language)
    else:
        swap_count = 1  # Thủ công chỉ swap 1 lần mỗi ví
        amount = None  # Sẽ nhập sau khi chọn cặp

    print_separator()

    successful_wallets = 0
    total_wallets = len(private_keys)
    failed_attempts = 0
    CONFIG['TOTAL_WALLETS'] = total_wallets
    CONFIG['MAX_CONCURRENCY'] = min(CONFIG['MAX_CONCURRENCY'], total_wallets)

    random.shuffle(private_keys)
    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    async def limited_task(index, profile_num, private_key, proxy):
        nonlocal successful_wallets, failed_attempts
        async with semaphore:
            result = await process_wallet(index, profile_num, private_key, proxy, w3, language, choice, swap_count, amount)
            if result > 0:
                successful_wallets += 1
                failed_attempts = 0
            else:
                failed_attempts += 1
                if failed_attempts >= 3:
                    print(f"{Fore.RED}  ✖ {LANG[language]['no_balance'].format(wallet=profile_num)}{Style.RESET_ALL}")
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
        f"{LANG[language]['completed_all'].format(successful=successful_wallets, total=total_wallets)}",
        Fore.GREEN
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_swaptoken('vi'))
