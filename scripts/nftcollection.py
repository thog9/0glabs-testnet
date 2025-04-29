import os
import sys
import asyncio
import random
from web3 import Web3
from eth_account import Account
from solcx import compile_source, install_solc, get_solc_version
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
SOLC_VERSION = "0.8.19"
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
    "MINIMUM_BALANCE": 0.001
}

# NFT Contract Source Code
NFT_CONTRACT_SOURCE = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract NFTCollection {
    address public owner;
    string public name;
    string public symbol;
    uint256 public maxSupply;
    uint256 public totalSupply;

    mapping(uint256 => address) private _owners;
    mapping(address => uint256) private _balances;
    mapping(uint256 => string) private _tokenURIs;

    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Mint(address indexed to, uint256 indexed tokenId, string tokenURI);
    event Burn(address indexed from, uint256 indexed tokenId);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the contract owner");
        _;
    }

    modifier tokenExists(uint256 tokenId) {
        require(_owners[tokenId] != address(0), "Token doesn't exist");
        _;
    }

    constructor(string memory _name, string memory _symbol, uint256 _maxSupply) {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        maxSupply = _maxSupply;
        totalSupply = 0;
    }

    function mint(address to, uint256 tokenId, string memory tokenURI) public onlyOwner {
        require(to != address(0), "Cannot mint to zero address");
        require(_owners[tokenId] == address(0), "Token already exists");
        require(totalSupply < maxSupply, "Maximum supply reached");

        _owners[tokenId] = to;
        _balances[to]++;
        _tokenURIs[tokenId] = tokenURI;
        totalSupply++;

        emit Transfer(address(0), to, tokenId);
        emit Mint(to, tokenId, tokenURI);
    }

    function burn(uint256 tokenId) public tokenExists(tokenId) {
        address tokenOwner = _owners[tokenId];
        require(msg.sender == tokenOwner || msg.sender == owner, "Not authorized to burn");

        delete _tokenURIs[tokenId];
        delete _owners[tokenId];
        _balances[tokenOwner]--;
        totalSupply--;

        emit Transfer(tokenOwner, address(0), tokenId);
        emit Burn(tokenOwner, tokenId);
    }

    function tokenURI(uint256 tokenId) public view tokenExists(tokenId) returns (string memory) {
        return _tokenURIs[tokenId];
    }

    function ownerOf(uint256 tokenId) public view tokenExists(tokenId) returns (address) {
        return _owners[tokenId];
    }

    function balanceOf(address _owner) public view returns (uint256) {
        require(_owner != address(0), "Zero address has no balance");
        return _balances[_owner];
    }
}
"""

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': '✨ QUẢN LÝ NFT - 0G TESTNET ✨',
        'info': 'ℹ Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'processing_wallet': '⚙ XỬ LÝ VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ (cần ít nhất {required:.6f} OG cho giao dịch)',
        'select_option': '✦ CHỌN HÀNH ĐỘNG',
        'option_deploy': '1. Tạo bộ sưu tập NFT (Deploy)',
        'option_mint': '2. Đúc NFT (Mint)',
        'option_burn': '3. Đốt NFT (Burn)',
        'choice_prompt': 'Nhập lựa chọn (1, 2 hoặc 3): ',
        'invalid_choice': 'Lựa chọn không hợp lệ',
        'enter_name': 'Nhập tên bộ sưu tập NFT (VD: Thog NFT): ',
        'enter_symbol': 'Nhập ký hiệu bộ sưu tập (VD: THOG): ',
        'enter_max_supply': 'Nhập tổng cung tối đa (VD: 999): ',
        'enter_token_id': 'Nhập Token ID: ',
        'enter_token_uri': 'Nhập Token URI (VD: ipfs://..., để trống nếu không cần): ',
        'preparing_tx': 'Đang chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'deploy_success': '✅ Tạo bộ sưu tập NFT thành công!',
        'mint_success': '✅ Đúc NFT thành công!',
        'burn_success': '✅ Đốt NFT thành công!',
        'failure': '❌ Thất bại',
        'timeout': '⏰ Giao dịch chưa xác nhận sau {timeout} giây, kiểm tra trên explorer',
        'address': 'Địa chỉ ví',
        'contract_address': 'Địa chỉ hợp đồng',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư OG',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'invalid_number': 'Vui lòng nhập số hợp lệ',
        'invalid_address': 'Địa chỉ hợp đồng không hợp lệ',
        'no_contract_found': 'Không tìm thấy hợp đồng NFT cho ví này trong contractNFT.txt',
        'connect_success': '✅ Thành công: Đã kết nối mạng 0G Testnet',
        'connect_error': '❌ Không thể kết nối RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ File pvkey.txt không tồn tại',
        'pvkey_empty': '❌ Không tìm thấy private key hợp lệ',
        'pvkey_error': '❌ Đọc pvkey.txt thất bại',
        'invalid_key': 'không hợp lệ, bỏ qua',
        'warning_line': '⚠ Cảnh báo: Dòng',
        'installing_solc': 'Đang cài đặt solc phiên bản {version}...',
        'solc_installed': 'Đã cài đặt solc phiên bản {version}',
        'estimating_gas': 'Đang ước lượng gas...',
        'gas_estimation_failed': 'Không thể ước lượng gas',
        'default_gas_used': 'Sử dụng gas mặc định: {gas}',
        'tx_rejected': 'Giao dịch bị từ chối bởi mạng',
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
        'title': '✨ NFT MANAGEMENT - 0G TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'processing_wallet': '⚙ PROCESSING WALLET',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance (need at least {required:.6f} OG for transaction)',
        'select_option': '✦ SELECT ACTION',
        'option_deploy': '1. Create NFT Collection (Deploy)',
        'option_mint': '2. Mint NFT',
        'option_burn': '3. Burn NFT',
        'choice_prompt': 'Enter choice (1, 2, or 3): ',
        'invalid_choice': 'Invalid choice',
        'enter_name': 'Enter NFT collection name (e.g., Thog NFT): ',
        'enter_symbol': 'Enter collection symbol (e.g., THOG): ',
        'enter_max_supply': 'Enter maximum supply (e.g., 999): ',
        'enter_token_id': 'Enter Token ID: ',
        'enter_token_uri': 'Enter Token URI (e.g., ipfs://..., leave blank if not needed): ',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'deploy_success': '✅ NFT collection created successfully!',
        'mint_success': '✅ NFT minted successfully!',
        'burn_success': '✅ NFT burned successfully!',
        'failure': '❌ Failed',
        'timeout': '⏰ Transaction not confirmed after {timeout} seconds, check on explorer',
        'address': 'Wallet address',
        'contract_address': 'Contract address',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'OG Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'invalid_number': 'Please enter a valid number',
        'invalid_address': 'Invalid contract address',
        'no_contract_found': 'No NFT contract found for this wallet in contractNFT.txt',
        'connect_success': '✅ Success: Connected to 0G Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': '⚠ Warning: Line',
        'installing_solc': 'Installing solc version {version}...',
        'solc_installed': 'Installed solc version {version}',
        'estimating_gas': 'Estimating gas...',
        'gas_estimation_failed': 'Failed to estimate gas',
        'default_gas_used': 'Using default gas: {gas}',
        'tx_rejected': 'Transaction rejected by network',
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
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key}{Style.RESET_ALL}")
        
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

# Hàm đọc địa chỉ hợp đồng từ contractNFT.txt dựa trên index
def load_contract_address(index: int, language: str = 'en') -> str:
    try:
        file_path = "contractNFT.txt"
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: contractNFT.txt không tồn tại{Style.RESET_ALL}")
            return None
        
        contracts = []
        with open(file_path, 'r') as f:
            for line in f:
                addr = line.strip()
                if addr and not addr.startswith('#') and Web3.is_address(addr):
                    contracts.append(Web3.to_checksum_address(addr))
        
        if not contracts:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: Không tìm thấy hợp đồng trong contractNFT.txt{Style.RESET_ALL}")
            return None
        
        if index < len(contracts):
            return contracts[index]
        else:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_contract_found']}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return None

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

# Hàm kiểm tra và cài đặt solc
def ensure_solc_installed(language: str = 'en'):
    try:
        current_version = get_solc_version()
        if str(current_version) != SOLC_VERSION:
            raise Exception("Phiên bản solc không khớp")
    except Exception:
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['installing_solc'].format(version=SOLC_VERSION)}{Style.RESET_ALL}")
        install_solc(SOLC_VERSION)
        print(f"{Fore.GREEN}  ✔ {LANG[language]['solc_installed'].format(version=SOLC_VERSION)}{Style.RESET_ALL}")

# Hàm biên dịch hợp đồng
def compile_contract(language: str = 'en'):
    ensure_solc_installed(language)
    compiled_sol = compile_source(NFT_CONTRACT_SOURCE, output_values=['abi', 'bin'], solc_version=SOLC_VERSION)
    contract_id, contract_interface = compiled_sol.popitem()
    return contract_interface['abi'], contract_interface['bin']

# Hàm đợi receipt thủ công
async def wait_for_receipt(w3: Web3, tx_hash: str, max_wait_time: int = 180, language: str = 'en'):
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
        
        await asyncio.sleep(5)

# Hàm triển khai hợp đồng NFT
async def deploy_nft(w3: Web3, private_key: str, wallet_index: int, name: str, symbol: str, max_supply: int, proxy: str = None, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

            print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
            eth_balance = float(w3.from_wei(w3.eth.get_balance(sender_address), 'ether'))
            if eth_balance < CONFIG['MINIMUM_BALANCE']:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=CONFIG['MINIMUM_BALANCE'])}: {eth_balance:.6f} OG{Style.RESET_ALL}")
                return None

            abi, bytecode = compile_contract(language)
            contract = w3.eth.contract(abi=abi, bytecode=bytecode)

            print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
            nonce = w3.eth.get_transaction_count(sender_address)
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))

            tx = contract.constructor(name, symbol, max_supply).build_transaction({
                'from': sender_address,
                'nonce': nonce,
                'chainId': CHAIN_ID,
                'gasPrice': gas_price
            })

            print(f"{Fore.CYAN}  > {LANG[language]['estimating_gas']}{Style.RESET_ALL}")
            try:
                estimated_gas = contract.constructor(name, symbol, max_supply).estimate_gas({'from': sender_address})
                gas_limit = int(estimated_gas * 1.2)
                tx['gas'] = gas_limit
                print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}{Style.RESET_ALL}")
            except Exception as e:
                tx['gas'] = 5000000
                print(f"{Fore.YELLOW}  - {LANG[language]['gas_estimation_failed']}: {str(e)}. {LANG[language]['default_gas_used'].format(gas=5000000)}{Style.RESET_ALL}")

            required_balance = w3.from_wei(tx['gas'] * tx['gasPrice'], 'ether')
            if eth_balance < required_balance:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=required_balance)}: {eth_balance:.6f} OG{Style.RESET_ALL}")
                return None

            print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=300, language=language)

            if receipt is None:
                print(f"{Fore.YELLOW}  {LANG[language]['timeout'].format(timeout=300)} - Tx: {tx_link}{Style.RESET_ALL}")
                return None
            elif receipt.status == 1:
                contract_address = receipt['contractAddress']
                print(f"{Fore.GREEN}  ✔ {LANG[language]['deploy_success']} | Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['address']}: {sender_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['contract_address']}: {contract_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['balance']}: {eth_balance:.6f} OG{Style.RESET_ALL}")
                return {'address': contract_address, 'abi': abi}
            else:
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.RED}    - {LANG[language]['tx_rejected']}{Style.RESET_ALL}")
                return None
        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} | Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  ⚠ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} | Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
            return None

# Hàm đúc NFT
async def mint_nft(w3: Web3, private_key: str, wallet_index: int, contract_address: str, token_id: int, token_uri: str, proxy: str = None, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

            print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
            eth_balance = float(w3.from_wei(w3.eth.get_balance(sender_address), 'ether'))
            if eth_balance < CONFIG['MINIMUM_BALANCE']:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=CONFIG['MINIMUM_BALANCE'])}: {eth_balance:.6f} OG{Style.RESET_ALL}")
                return False

            contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=compile_contract(language)[0])

            print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
            nonce = w3.eth.get_transaction_count(sender_address)
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))

            tx = contract.functions.mint(sender_address, token_id, token_uri).build_transaction({
                'from': sender_address,
                'nonce': nonce,
                'chainId': CHAIN_ID,
                'gasPrice': gas_price
            })

            print(f"{Fore.CYAN}  > {LANG[language]['estimating_gas']}{Style.RESET_ALL}")
            try:
                estimated_gas = contract.functions.mint(sender_address, token_id, token_uri).estimate_gas({'from': sender_address})
                gas_limit = int(estimated_gas * 1.2)
                tx['gas'] = gas_limit
                print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}{Style.RESET_ALL}")
            except Exception as e:
                tx['gas'] = 300000
                print(f"{Fore.YELLOW}  - {LANG[language]['gas_estimation_failed']}: {str(e)}. {LANG[language]['default_gas_used'].format(gas=300000)}{Style.RESET_ALL}")

            required_balance = w3.from_wei(tx['gas'] * tx['gasPrice'], 'ether')
            if eth_balance < required_balance:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=required_balance)}: {eth_balance:.6f} OG{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=180, language=language)

            if receipt is None:
                print(f"{Fore.YELLOW}  {LANG[language]['timeout'].format(timeout=180)} - Tx: {tx_link}{Style.RESET_ALL}")
                return False
            elif receipt.status == 1:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['mint_success']} | Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['address']}: {sender_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - Token ID: {token_id}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - Token URI: {token_uri if token_uri else 'None'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['balance']}: {eth_balance:.6f} OG{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.RED}    - {LANG[language]['tx_rejected']}{Style.RESET_ALL}")
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

# Hàm đốt NFT
async def burn_nft(w3: Web3, private_key: str, wallet_index: int, contract_address: str, token_id: int, proxy: str = None, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

            print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
            eth_balance = float(w3.from_wei(w3.eth.get_balance(sender_address), 'ether'))
            if eth_balance < CONFIG['MINIMUM_BALANCE']:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=CONFIG['MINIMUM_BALANCE'])}: {eth_balance:.6f} OG{Style.RESET_ALL}")
                return False

            contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=compile_contract(language)[0])

            print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
            nonce = w3.eth.get_transaction_count(sender_address)
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))

            tx = contract.functions.burn(token_id).build_transaction({
                'from': sender_address,
                'nonce': nonce,
                'chainId': CHAIN_ID,
                'gasPrice': gas_price
            })

            print(f"{Fore.CYAN}  > {LANG[language]['estimating_gas']}{Style.RESET_ALL}")
            try:
                estimated_gas = contract.functions.burn(token_id).estimate_gas({'from': sender_address})
                gas_limit = int(estimated_gas * 1.2)
                tx['gas'] = gas_limit
                print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}{Style.RESET_ALL}")
            except Exception as e:
                tx['gas'] = 300000
                print(f"{Fore.YELLOW}  - {LANG[language]['gas_estimation_failed']}: {str(e)}. {LANG[language]['default_gas_used'].format(gas=300000)}{Style.RESET_ALL}")

            required_balance = w3.from_wei(tx['gas'] * tx['gasPrice'], 'ether')
            if eth_balance < required_balance:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=required_balance)}: {eth_balance:.6f} OG{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=180, language=language)

            if receipt is None:
                print(f"{Fore.YELLOW}  {LANG[language]['timeout'].format(timeout=180)} - Tx: {tx_link}{Style.RESET_ALL}")
                return False
            elif receipt.status == 1:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['burn_success']} | Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['address']}: {sender_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - Token ID: {token_id}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    - {LANG[language]['balance']}: {eth_balance:.6f} OG{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.RED}    - {LANG[language]['tx_rejected']}{Style.RESET_ALL}")
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

# Hàm xử lý từng ví
async def process_wallet(index: int, profile_num: int, private_key: str, proxy: str, w3: Web3, action: str, params: dict, language: str):
    total_wallets = CONFIG.get('TOTAL_WALLETS', 1)
    print_border(
        f"{LANG[language]['processing_wallet']} {profile_num} ({index + 1}/{total_wallets})",
        Fore.MAGENTA
    )
    print()

    if action == 'deploy':
        result = await deploy_nft(w3, private_key, profile_num, params['name'], params['symbol'], params['max_supply'], proxy, language)
        if result:
            with open('contractNFT.txt', 'a') as f:
                f.write(f"{result['address']}\n")
        return bool(result)
    elif action in ('mint', 'burn'):
        contract_address = load_contract_address(index, language)
        if not contract_address:
            print(f"{Fore.RED}  ✖ {LANG[language]['no_contract_found']}{Style.RESET_ALL}")
            return False
        params['contract_address'] = contract_address
        if action == 'mint':
            result = await mint_nft(w3, private_key, profile_num, params['contract_address'], params['token_id'], params['token_uri'], proxy, language)
        else:  # burn
            result = await burn_nft(w3, private_key, profile_num, params['contract_address'], params['token_id'], proxy, language)
        return result
    return False

# Hàm chính
async def run_nftcollection(language: str = 'vi'):
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

    print_border(LANG[language]['select_option'], Fore.YELLOW)
    print(f"{Fore.GREEN}    ├─ {LANG[language]['option_deploy']}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}    ├─ {LANG[language]['option_mint']}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}    └─ {LANG[language]['option_burn']}{Style.RESET_ALL}")
    choice = input(f"{Fore.YELLOW}  > {LANG[language]['choice_prompt']}{Style.RESET_ALL}").strip()

    params = {}
    if choice == '1':  # Deploy
        action = 'deploy'
        params['name'] = input(f"{Fore.YELLOW}  > {LANG[language]['enter_name']}{Style.RESET_ALL}").strip()
        params['symbol'] = input(f"{Fore.YELLOW}  > {LANG[language]['enter_symbol']}{Style.RESET_ALL}").strip() or "NFT"
        max_supply_input = input(f"{Fore.YELLOW}  > {LANG[language]['enter_max_supply']}{Style.RESET_ALL}").strip()
        try:
            params['max_supply'] = int(max_supply_input)
            if params['max_supply'] <= 0:
                raise ValueError
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")
            return
    elif choice == '2':  # Mint
        action = 'mint'
        token_id_input = input(f"{Fore.YELLOW}  > {LANG[language]['enter_token_id']}{Style.RESET_ALL}").strip()
        try:
            params['token_id'] = int(token_id_input)
            if params['token_id'] < 0:
                raise ValueError
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")
            return
        params['token_uri'] = input(f"{Fore.YELLOW}  > {LANG[language]['enter_token_uri']}{Style.RESET_ALL}").strip() or ""
    elif choice == '3':  # Burn
        action = 'burn'
        token_id_input = input(f"{Fore.YELLOW}  > {LANG[language]['enter_token_id']}{Style.RESET_ALL}").strip()
        try:
            params['token_id'] = int(token_id_input)
            if params['token_id'] < 0:
                raise ValueError
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")
            return
    else:
        print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        return

    successful_ops = 0
    total_wallets = len(private_keys)
    failed_attempts = 0
    CONFIG['TOTAL_WALLETS'] = total_wallets
    CONFIG['MAX_CONCURRENCY'] = min(CONFIG['MAX_CONCURRENCY'], total_wallets)

    random.shuffle(private_keys)
    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    async def limited_task(index, profile_num, private_key, proxy):
        nonlocal successful_ops, failed_attempts
        async with semaphore:
            result = await process_wallet(index, profile_num, private_key, proxy, w3, action, params, language)
            if result:
                successful_ops += 1
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
        f"{LANG[language]['completed'].format(successful=successful_ops, total=total_wallets)}",
        Fore.GREEN
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_nftcollection('vi'))
