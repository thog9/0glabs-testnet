import os
import sys
import asyncio
import random
from web3 import Web3
from web3.exceptions import ContractLogicError
from eth_account import Account
from solcx import compile_source, install_solc, get_solc_version
from colorama import init, Fore, Style

# Khởi tạo colorama
init(autoreset=True)

# Constants
NETWORK_URLS = ['https://evmrpc-testnet.0g.ai']
CHAIN_ID = 16600
EXPLORER_URL = "https://chainscan-newton.0g.ai"
SOLC_VERSION = "0.8.19"  # Dùng phiên bản không có PUSH0

# Source code của CustomToken.sol
CONTRACT_SOURCE = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract CustomToken {
    string private _name;
    string private _symbol;
    uint8 private _decimals;
    uint256 private _totalSupply;
    address public owner;

    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    constructor(
        string memory name_,
        string memory symbol_,
        uint8 decimals_,
        uint256 totalSupply_
    ) {
        owner = msg.sender;
        _name = name_;
        _symbol = symbol_;
        _decimals = decimals_;
        _totalSupply = totalSupply_;
        _balances[address(this)] = totalSupply_;
        emit Transfer(address(0), address(this), totalSupply_);
    }

    function name() public view returns (string memory) {
        return _name;
    }

    function symbol() public view returns (string memory) {
        return _symbol;
    }

    function decimals() public view returns (uint8) {
        return _decimals;
    }

    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) public view returns (uint256) {
        return _balances[account];
    }

    function transfer(address to, uint256 amount) public returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }

    function allowance(address tokenOwner, address spender) public view returns (uint256) {
        return _allowances[tokenOwner][spender];
    }

    function approve(address spender, uint256 amount) public returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) public returns (bool) {
        uint256 currentAllowance = _allowances[from][msg.sender];
        require(currentAllowance >= amount, "ERC20: transfer amount exceeds allowance");
        _transfer(from, to, amount);
        _approve(from, msg.sender, currentAllowance - amount);
        return true;
    }

    function _transfer(address from, address to, uint256 amount) internal {
        require(from != address(0), "ERC20: transfer from the zero address");
        require(to != address(0), "ERC20: transfer to the zero address");
        require(_balances[from] >= amount, "ERC20: transfer amount exceeds balance");
        _balances[from] -= amount;
        _balances[to] += amount;
        emit Transfer(from, to, amount);
    }

    function _approve(address tokenOwner, address spender, uint256 amount) internal {
        require(tokenOwner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");
        _allowances[tokenOwner][spender] = amount;
        emit Approval(tokenOwner, spender, amount);
    }

    function sendToken(address recipient, uint256 amount) external onlyOwner {
        _transfer(address(this), recipient, amount);
    }
}
"""

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': 'DEPLOY TOKEN ERC20 - OG LABS TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallet': 'XỬ LÝ VÍ',
        'enter_name': 'Nhập tên token (VD: Thog Token):',
        'enter_symbol': 'Nhập ký hiệu token (VD: THOG):',
        'enter_decimals': 'Nhập số thập phân (mặc định 18):',
        'enter_supply': 'Nhập tổng cung (ví dụ: 1000000):',
        'preparing_tx': 'Chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'success': 'Triển khai thành công!',
        'failure': 'Triển khai thất bại',
        'address': 'Địa chỉ hợp đồng',
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
        'completed': 'HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'installing_solc': 'Đang cài đặt solc phiên bản {version}...',
        'solc_installed': 'Đã cài đặt solc phiên bản {version}',
        'no_balance': 'Số dư ví không đủ (cần ít nhất {required} A0GI)',
        'estimating_gas': 'Đang ước lượng gas...'
    },
    'en': {
        'title': 'DEPLOY ERC20 TOKEN - OG LABS TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallet': 'PROCESSING WALLET',
        'enter_name': 'Enter token name (e.g., Thog Token):',
        'enter_symbol': 'Enter token symbol (e.g., THOG):',
        'enter_decimals': 'Enter decimals (default 18):',
        'enter_supply': 'Enter total supply (e.g., 1000000):',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'success': 'Deployment successful!',
        'failure': 'Deployment failed',
        'address': 'Contract address',
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
        'completed': 'COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'installing_solc': 'Installing solc version {version}...',
        'solc_installed': 'Installed solc version {version}',
        'no_balance': 'Insufficient balance (need at least {required} A0GI)',
        'estimating_gas': 'Estimating gas...'
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

# Hàm kết nối Web3
def connect_web3(language: str = 'en'):
    for url in NETWORK_URLS:
        try:
            w3 = Web3(Web3.HTTPProvider(url))
            if w3.is_connected():
                print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} | Chain ID: {w3.eth.chain_id} | RPC: {url}{Style.RESET_ALL}")
                return w3
            else:
                print(f"{Fore.YELLOW}  ⚠ {LANG[language]['connect_error']} at {url}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['web3_error']} at {url}: {str(e)}{Style.RESET_ALL}")
    print(f"{Fore.RED}  ✖ Failed to connect to any RPC endpoint{Style.RESET_ALL}")
    sys.exit(1)

# Hàm kiểm tra và cài đặt solc
def ensure_solc_installed(language: str = 'en'):
    try:
        current_version = get_solc_version()
        if current_version != SOLC_VERSION:
            raise Exception("Phiên bản solc không khớp")
    except Exception:
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['installing_solc'].format(version=SOLC_VERSION)}{Style.RESET_ALL}")
        install_solc(SOLC_VERSION)
        print(f"{Fore.GREEN}  ✔ {LANG[language]['solc_installed'].format(version=SOLC_VERSION)}{Style.RESET_ALL}")

# Hàm biên dịch hợp đồng
def compile_contract(language: str = 'en'):
    ensure_solc_installed(language)
    compiled_sol = compile_source(CONTRACT_SOURCE, output_values=['abi', 'bin'], solc_version=SOLC_VERSION)
    contract_id, contract_interface = compiled_sol.popitem()
    return contract_interface['abi'], contract_interface['bin']

# Hàm triển khai hợp đồng
async def deploy_contract(w3: Web3, private_key: str, wallet_index: int, name: str, symbol: str, decimals: int, total_supply: int, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    try:
        # Biên dịch hợp đồng
        abi, bytecode = compile_contract(language)
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)

        # Kiểm tra số dư ví
        balance = w3.from_wei(w3.eth.get_balance(sender_address), 'ether')
        print(f"{Fore.YELLOW}  - Số dư hiện tại: {balance:.6f} A0GI{Style.RESET_ALL}")

        # Chuẩn bị giao dịch
        print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
        nonce = w3.eth.get_transaction_count(sender_address)
        total_supply_wei = w3.to_wei(total_supply, 'ether')

        # Ước lượng gas
        print(f"{Fore.CYAN}  > {LANG[language]['estimating_gas']}{Style.RESET_ALL}")
        try:
            estimated_gas = contract.constructor(name, symbol, decimals, total_supply_wei).estimate_gas({
                'from': sender_address
            })
            gas_limit = int(estimated_gas * 1.2)  # Tăng 20% giống ethers.js
            print(f"{Fore.YELLOW}  - Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}{Style.RESET_ALL}")
        except ContractLogicError as e:
            print(f"{Fore.RED}  ✖ Lỗi ước lượng gas: {str(e)} (Contract có thể không hợp lệ){Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ Không thể ước lượng gas: {str(e)}. Dùng gas mặc định: 4000000{Style.RESET_ALL}")
            gas_limit = 4000000  # Gas dự phòng

        # Kiểm tra số dư đủ cho gas không
        gas_price = w3.to_wei('0.1', 'gwei')  # Gas price cố định như ethers.js
        required_balance = w3.from_wei(gas_limit * gas_price, 'ether')
        if balance < required_balance:
            print(f"{Fore.RED}  ✖ {LANG[language]['no_balance'].format(required=required_balance)}{Style.RESET_ALL}")
            return None

        tx = contract.constructor(name, symbol, decimals, total_supply_wei).build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'gas': gas_limit,
            'gasPrice': gas_price
        })

        # Gửi giao dịch
        print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_link = f"{EXPLORER_URL}/tx/0x{tx_hash.hex()}"

        # Đợi receipt
        receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300))

        if receipt.status == 1:
            contract_address = receipt['contractAddress']
            print(f"{Fore.GREEN}  ✔ {LANG[language]['success']} | Tx: {tx_link}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    - {LANG[language]['address']}: {contract_address}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
            return contract_address
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Thất bại / Failed'}: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}    - Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
        return None

# Hàm chính
async def run_deploytoken(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    # Nhập thông tin token
    name = input(f"{Fore.YELLOW}  > {LANG[language]['enter_name']} {Style.RESET_ALL}").strip()
    symbol = input(f"{Fore.YELLOW}  > {LANG[language]['enter_symbol']} {Style.RESET_ALL}").strip()
    decimals_input = input(f"{Fore.YELLOW}  > {LANG[language]['enter_decimals']} {Style.RESET_ALL}").strip() or "18"
    total_supply_input = input(f"{Fore.YELLOW}  > {LANG[language]['enter_supply']} {Style.RESET_ALL}").strip()

    try:
        decimals = int(decimals_input)
        total_supply = int(total_supply_input)
        if decimals <= 0 or total_supply <= 0:
            raise ValueError
    except ValueError:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")
        return

    successful_deploys = 0
    total_wallets = len(private_keys)

    random.shuffle(private_keys)

    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{total_wallets})", Fore.MAGENTA)
        print()

        contract_address = await deploy_contract(w3, private_key, profile_num, name, symbol, decimals, total_supply, language)
        if contract_address:
            successful_deploys += 1
            with open('contractERC20.txt', 'a') as f:
                f.write(f"{contract_address}\n")
        
        if i < total_wallets:
            delay = random.uniform(10, 30)
            print(f"{Fore.YELLOW}  ℹ {'Tạm nghỉ' if language == 'vi' else 'Pausing'} {delay:.2f} {'giây' if language == 'vi' else 'seconds'}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_deploys, total=total_wallets)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_deploytoken('vi'))
