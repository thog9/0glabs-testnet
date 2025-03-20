import os
import sys
import asyncio
import random
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style

# Khởi tạo colorama
init(autoreset=True)

# Constants
NETWORK_URLS = ['https://evmrpc-testnet.0g.ai']
CHAIN_ID = 16600
EXPLORER_URL = "https://chainscan-newton.0g.ai"

# ABI của CustomToken.sol (khớp với hợp đồng trong deploytoken.py)
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "name_", "type": "string"},
            {"internalType": "string", "name": "symbol_", "type": "string"},
            {"internalType": "uint8", "name": "decimals_", "type": "uint8"},
            {"internalType": "uint256", "name": "totalSupply_", "type": "uint256"}
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "spender", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "from", "type": "address"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "transferFrom",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "tokenOwner", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "sendToken",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': 'SEND TOKEN ERC20 - OG LABS TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallet': 'XỬ LÝ VÍ',
        'enter_contract': 'Nhập địa chỉ hợp đồng ERC20 (contractERC20.txt):',
        'enter_amount': 'Nhập số lượng token gửi:',
        'choose_destination': 'Chọn phương thức gửi token:',
        'option_random': '1. Gửi ngẫu nhiên',
        'option_file': '2. Gửi từ file addressERC20.txt',
        'input_prompt': 'Nhập lựa chọn của bạn (1 hoặc 2):',
        'invalid_choice': 'Lựa chọn không hợp lệ',
        'no_addresses': 'Không tìm thấy địa chỉ trong addressERC20.txt',
        'preparing_tx': 'Chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'success': 'Gửi token thành công!',
        'failure': 'Gửi token thất bại',
        'address': 'Địa chỉ ví',
        'destination': 'Địa chỉ nhận',
        'amount': 'Số lượng',
        'gas': 'Gas',
        'block': 'Khối',
        'error': 'Lỗi',
        'invalid_number': 'Vui lòng nhập số hợp lệ',
        'connect_success': 'Thành công: Đã kết nối mạng OG LABS Testnet',
        'connect_error': 'Không thể kết nối RPC',
        'web3_error': 'Kết nối Web3 thất bại',
        'pvkey_not_found': 'File pvkey.txt không tồn tại',
        'pvkey_empty': 'Không tìm thấy private key hợp lệ',
        'pvkey_error': 'Đọc pvkey.txt thất bại',
        'invalid_key': 'không hợp lệ, bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'completed': 'HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG'
    },
    'en': {
        'title': 'SEND ERC20 TOKEN - OG LABS TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallet': 'PROCESSING WALLET',
        'enter_contract': 'Enter ERC20 contract address (contractERC20.txt):',
        'enter_amount': 'Enter token amount to send:',
        'choose_destination': 'Choose token sending method:',
        'option_random': '1. Send randomly',
        'option_file': '2. Send from addressERC20.txt',
        'input_prompt': 'Enter your choice (1 or 2):',
        'invalid_choice': 'Invalid choice',
        'no_addresses': 'No addresses found in addressERC20.txt',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'success': 'Token sent successfully!',
        'failure': 'Token sending failed',
        'address': 'Wallet address',
        'destination': 'Destination address',
        'amount': 'Amount',
        'gas': 'Gas',
        'block': 'Block',
        'error': 'Error',
        'invalid_number': 'Please enter a valid number',
        'connect_success': 'Success: Connected to OG LABS Testnet',
        'connect_error': 'Failed to connect to RPC',
        'web3_error': 'Web3 connection failed',
        'pvkey_not_found': 'pvkey.txt file not found',
        'pvkey_empty': 'No valid private keys found',
        'pvkey_error': 'Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'completed': 'COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL'
    }
}

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=80):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

# Hàm hiển thị phân cách
def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * 80}{Style.RESET_ALL}")

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

# Hàm đọc địa chỉ từ file addressERC20.txt
def load_addresses(file_path: str = "addressERC20.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_addresses']}. Tạo file mới.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm địa chỉ nhận token vào đây, mỗi địa chỉ trên một dòng\n# Ví dụ: 0x1234567890abcdef1234567890abcdef1234567890\n")
            return []
        
        addresses = []
        with open(file_path, 'r') as f:
            for line in f:
                addr = line.strip()
                if addr and not addr.startswith('#') and Web3.is_address(addr):
                    addresses.append(Web3.to_checksum_address(addr))
        
        if not addresses:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_addresses']}{Style.RESET_ALL}")
        return addresses
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

# Hàm kết nối Web3
def connect_web3(language: str = 'en'):
    for url in NETWORK_URLS:
        try:
            w3 = Web3(Web3.HTTPProvider(url))
            if w3.is_connected():
                print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} │ Chain ID: {w3.eth.chain_id} │ RPC: {url}{Style.RESET_ALL}")
                return w3
            else:
                print(f"{Fore.YELLOW}  ⚠ {LANG[language]['connect_error']} at {url}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['web3_error']} at {url}: {str(e)}{Style.RESET_ALL}")
    print(f"{Fore.RED}  ✖ Failed to connect to any RPC endpoint{Style.RESET_ALL}")
    sys.exit(1)

# Hàm gửi token ERC20
async def send_token(w3: Web3, private_key: str, wallet_index: int, contract_address: str, destination: str, amount: float, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    try:
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=CONTRACT_ABI)
        decimals = contract.functions.decimals().call()
        amount_wei = int(amount * 10 ** decimals)

        balance = w3.from_wei(w3.eth.get_balance(sender_address), 'ether')
        print(f"{Fore.YELLOW}  - Số dư hiện tại: {balance:.6f} A0GI{Style.RESET_ALL}")

        print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
        nonce = w3.eth.get_transaction_count(sender_address)
        gas_price = w3.to_wei('0.1', 'gwei')

        try:
            estimated_gas = contract.functions.sendToken(Web3.to_checksum_address(destination), amount_wei).estimate_gas({
                'from': sender_address
            })
            gas_limit = int(estimated_gas * 1.2)
            print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ Không thể ước lượng gas: {str(e)}. Dùng gas mặc định: 200000{Style.RESET_ALL}")
            gas_limit = 200000

        required_balance = w3.from_wei(gas_limit * gas_price, 'ether')
        if balance < required_balance:
            print(f"{Fore.RED}  ✖ Insufficient balance for gas (Need: {required_balance:.6f} A0GI){Style.RESET_ALL}")
            return False

        tx = contract.functions.sendToken(Web3.to_checksum_address(destination), amount_wei).build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'gas': gas_limit,
            'gasPrice': gas_price
        })

        print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_link = f"{EXPLORER_URL}/tx/0x{tx_hash.hex()}"

        receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))

        if receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ {LANG[language]['success']} │ Tx: {tx_link}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['address']}: {sender_address}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['destination']}: {destination}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['amount']}: {amount:.4f} Token{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']} │ Tx: {tx_link}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Thất bại / Failed'}: {str(e)}{Style.RESET_ALL}")
        return False

# Hàm chính
async def run_sendtoken(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    w3 = connect_web3(language)
    print()

    # Nhập thông tin giao dịch
    print(f"{Fore.YELLOW}  ➤ {LANG[language]['enter_contract']} {Style.RESET_ALL}", end="")
    contract_address = input().strip()
    print(f"{Fore.YELLOW}  ➤ {LANG[language]['enter_amount']} {Style.RESET_ALL}", end="")
    amount_input = input().strip()

    try:
        amount = float(amount_input)
        if amount <= 0:
            raise ValueError
    except ValueError:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")
        return

    # Chọn cách gửi token với giao diện đẹp hơn
    print()
    print(f"{Fore.CYAN}  ✦ {LANG[language]['choose_destination']}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}    ├─ {LANG[language]['option_random']}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}    └─ {LANG[language]['option_file']}{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}  ➤ {LANG[language]['input_prompt']} {Style.RESET_ALL}", end="")
    choice = input().strip()

    destinations = []
    if choice == '1':
        # Gửi ngẫu nhiên
        for _ in range(len(private_keys)):  # Tạo số lượng địa chỉ bằng số ví
            new_account = w3.eth.account.create()
            destinations.append(new_account.address)
    elif choice == '2':
        # Đọc từ file
        destinations = load_addresses('addressERC20.txt', language)
        if not destinations:
            return
    else:
        print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        return

    successful_sends = 0
    total_wallets = len(private_keys)

    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        print()
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{len(private_keys)})", Fore.MAGENTA)
        print()

        # Chọn địa chỉ nhận tương ứng hoặc ngẫu nhiên nếu ít hơn số ví
        destination = destinations[i-1] if i-1 < len(destinations) else random.choice(destinations)

        if await send_token(w3, private_key, profile_num, contract_address, destination, amount, language):
            successful_sends += 1
        
        if i < len(private_keys):
            delay = random.uniform(10, 30)
            print(f"{Fore.YELLOW}  ℹ {'Tạm nghỉ' if language == 'vi' else 'Pausing'} {delay:.2f} {'giây' if language == 'vi' else 'seconds'}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_sends, total=total_wallets)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_sendtoken('vi'))  # Ngôn ngữ mặc định là Tiếng Việt
