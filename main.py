import os
import sys
import asyncio
from colorama import init, Fore, Style
import inquirer

# Khởi tạo colorama
init(autoreset=True)

# Độ rộng viền cố định
BORDER_WIDTH = 80

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."  # Cắt dài và thêm "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

# Hàm hiển thị banner
def _banner():
    banner = r"""


░█████╗░░██████╗░  ░██████╗░░█████╗░██╗░░░░░██╗██╗░░░░░███████╗░█████╗░  ██╗░░░██╗██████╗░
██╔══██╗██╔════╝░  ██╔════╝░██╔══██╗██║░░░░░██║██║░░░░░██╔════╝██╔══██╗  ██║░░░██║╚════██╗
██║░░██║██║░░██╗░  ██║░░██╗░███████║██║░░░░░██║██║░░░░░█████╗░░██║░░██║  ╚██╗░██╔╝░█████╔╝
██║░░██║██║░░╚██╗  ██║░░╚██╗██╔══██║██║░░░░░██║██║░░░░░██╔══╝░░██║░░██║  ░╚████╔╝░░╚═══██╗
╚█████╔╝╚██████╔╝  ╚██████╔╝██║░░██║███████╗██║███████╗███████╗╚█████╔╝  ░░╚██╔╝░░██████╔╝
░╚════╝░░╚═════╝░  ░╚═════╝░╚═╝░░╚═╝╚══════╝╚═╝╚══════╝╚══════╝░╚════╝░  ░░░╚═╝░░░╚═════╝░


    """
    print(f"{Fore.GREEN}{banner:^80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
    print_border("0G LABs TESTNET", Fore.GREEN)
    print(f"{Fore.YELLOW}│ {'Liên hệ / Contact'}: {Fore.CYAN}https://t.me/thog099{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}│ {'Replit'}: {Fore.CYAN}Thog{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}│ {'Channel Telegram'}: {Fore.CYAN}https://t.me/thogairdrops{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

# Hàm xóa màn hình
def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Các hàm giả lập cho các lệnh mới
async def run_faucettokens(language: str):
    from scripts.faucettokens import run_faucettokens as faucettokens_run
    await faucettokens_run(language)
    
async def run_swaptoken(language: str):
    from scripts.swaptoken import run_swaptoken as swaptoken_run
    await swaptoken_run(language)

async def run_storagescan(language: str):
    from scripts.storagescan import run_storagescan as storagescan_run
    await storagescan_run(language)

async def run_conftnft(language: str):
    from scripts.conftnft import run_conftnft as conftnft_run
    await conftnft_run(language)

async def run_domain(language: str):
    from scripts.domain import run_domain as domain_run
    await domain_run(language)

async def run_mintaura(language: str):
    from scripts.mintaura import run_mintaura as mintaura_run
    await mintaura_run(language)

async def run_mintnerzo(language: str):
    from scripts.mintnerzo import run_mintnerzo as mintnerzo_run
    await mintnerzo_run(language)

async def run_sendtx(language: str):
    from scripts.sendtx import run_sendtx as sendtx_run
    await sendtx_run(language)

async def run_deploytoken(language: str):
    from scripts.deploytoken import run_deploytoken as deploytoken_run
    await deploytoken_run(language)

async def run_sendtoken(language: str):
    from scripts.sendtoken import run_sendtoken as sendtoken_run
    await sendtoken_run(language)

async def run_nftcollection(language: str):
    from scripts.nftcollection import run_nftcollection as nftcollection_run
    await nftcollection_run(language)

async def cmd_exit(language: str):
    messages = {"vi": "Đang thoát...", "en": "Exiting..."}
    print_border(messages[language], Fore.GREEN)
    sys.exit(0)

# Danh sách lệnh menu
SCRIPT_MAP = {
    "faucettokens": run_faucettokens,
    "swaptoken": run_swaptoken,
    "storagescan": run_storagescan,
    "conftnft": run_conftnft,
    "domain": run_domain,
    "mintaura": run_mintaura,
    "mintnerzo": run_mintnerzo,
    "sendtx": run_sendtx,
    "deploytoken": run_deploytoken,
    "sendtoken": run_sendtoken,
    "nftcollection": run_nftcollection,
    "exit": cmd_exit
}

# Danh sách script và thông báo theo ngôn ngữ
def get_available_scripts(language):
    scripts = {
        'vi': [
            {"name": "1. Faucet tokens [USDT, ETH, BTC] -> zer0 ØG │ 0G Galileo Testnet", "value": "faucettokens"},
            {"name": "2. Swap token ngẫu nhiên trên zer0 ØG │ 0G Galileo Testnet", "value": "swaptoken"},
            {"name": "3. Deploy Storagescan File │ 0G Galileo Testnet", "value": "storagescan"},
            {"name": "4. Mint ConftApp Galileo Drift (GD) │ 0G Galileo Testnet", "value": "conftnft"},
            {"name": "5. Mint Domain │ 0G Galileo Testnet", "value": "domain"},
            
            #{"name": "5. Mint Aura - Panda 0G (PG) │ 0G Galileo Testnet", "value": "mintaura"},
            #{"name": "6. Mint Nerzo - 0G OG (NERZO-0GOG) │ 0G Galileo Testnet", "value": "mintnerzo"},
            
            {"name": "6. Gửi TX ngẫu nhiên hoặc File (address.txt) │ 0G Galileo Testnet", "value": "sendtx"},
            {"name": "7. Deploy Token smart-contract │ 0G Galileo Testnet", "value": "deploytoken"},
            {"name": "8. Gửi Token ERC20 ngẫu nhiên hoặc File (addressERC20.txt) │ 0G Galileo Testnet", "value": "sendtoken"},
            {"name": "9. Deploy NFT - Quản lý bộ sưu tập NFT [ Tạo | Mint | Đốt ] | 0G Galileo Testnet", "value": "nftcollection"},
            {"name": "10. Thoát", "value": "exit"},
        ],
        'en': [
            {"name": "1. Faucet tokens [USDT, ETH, BTC] -> zer0 ØG │ 0G Galileo Testnet", "value": "faucettokens"},
            {"name": "2. Swap tokens randomly on zer0 ØG │ 0G Galileo Testnet", "value": "swaptoken"},
            {"name": "3. Deploy Storagescan File │ 0G Galileo Testnet", "value": "storagescan"},
            {"name": "4. Mint ConftApp Galileo Drift (GD) │ 0G Galileo Testnet", "value": "conftnft"},
            {"name": "5. Mint Domain │ 0G Galileo Testnet", "value": "domain"},
            
            #{"name": "5. Mint Aura - Panda 0G (PG) │ 0G Galileo Testnet", "value": "mintaura"},
            #{"name": "6. Mint Nerzo - 0G OG (NERZO-0GOG) │ 0G Galileo Testnet", "value": "mintnerzo"},
            
            {"name": "6. Send Random TX or File (address.txt) │ 0G Galileo Testnet", "value": "sendtx"},
            {"name": "7. Deploy Token smart-contract │ 0G Galileo Testnet", "value": "deploytoken"},
            {"name": "8. Send ERC20 Token Random or File (addressERC20.txt) │ 0G Galileo Testnet", "value": "sendtoken"},
            {"name": "9. Deploy NFT - Manage NFT Collection [ Create | Mint | Burn ] | 0G Galileo Testnet", "value": "nftcollection"},
            {"name": "10. Exit", "value": "exit"},
        ]
    }
    return scripts[language]

def run_script(script_func, language):
    """Chạy script bất kể nó là async hay không."""
    if asyncio.iscoroutinefunction(script_func):
        asyncio.run(script_func(language))
    else:
        script_func(language)

def select_language():
    while True:
        _clear()
        _banner()
        print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
        print_border("CHỌN NGÔN NGỮ / SELECT LANGUAGE", Fore.YELLOW)
        questions = [
            inquirer.List('language',
                          message=f"{Fore.CYAN}Vui lòng chọn / Please select:{Style.RESET_ALL}",
                          choices=[("1. Tiếng Việt", 'vi'), ("2. English", 'en')],
                          carousel=True)
        ]
        answer = inquirer.prompt(questions)
        if answer and answer['language'] in ['vi', 'en']:
            return answer['language']
        print(f"{Fore.RED}❌ {'Lựa chọn không hợp lệ / Invalid choice':^76}{Style.RESET_ALL}")

def main():
    _clear()
    _banner()
    language = select_language()

    messages = {
        "vi": {
            "running": "Đang thực thi: {}",
            "completed": "Đã hoàn thành: {}",
            "error": "Lỗi: {}",
            "press_enter": "Nhấn Enter để tiếp tục...",
            "menu_title": "MENU CHÍNH",
            "select_script": "Chọn script để chạy"
        },
        "en": {
            "running": "Running: {}",
            "completed": "Completed: {}",
            "error": "Error: {}",
            "press_enter": "Press Enter to continue...",
            "menu_title": "MAIN MENU",
            "select_script": "Select script to run"
        }
    }

    while True:
        _clear()
        _banner()
        print(f"{Fore.YELLOW}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
        print_border(messages[language]["menu_title"], Fore.YELLOW)
        print(f"{Fore.CYAN}│ {messages[language]['select_script'].center(BORDER_WIDTH - 4)} │{Style.RESET_ALL}")

        available_scripts = get_available_scripts(language)
        questions = [
            inquirer.List('script',
                          message=f"{Fore.CYAN}{messages[language]['select_script']}{Style.RESET_ALL}",
                          choices=[script["name"] for script in available_scripts],
                          carousel=True)
        ]
        answers = inquirer.prompt(questions)
        if not answers:
            continue

        selected_script_name = answers['script']
        selected_script_value = next(script["value"] for script in available_scripts if script["name"] == selected_script_name)

        script_func = SCRIPT_MAP.get(selected_script_value)
        if script_func is None:
            print(f"{Fore.RED}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(f"{'Chưa triển khai / Not implemented'}: {selected_script_name}", Fore.RED)
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
            continue

        try:
            print(f"{Fore.CYAN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["running"].format(selected_script_name), Fore.CYAN)
            run_script(script_func, language)
            print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["completed"].format(selected_script_name), Fore.GREEN)
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
        except Exception as e:
            print(f"{Fore.RED}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["error"].format(str(e)), Fore.RED)
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")

if __name__ == "__main__":
    main()
