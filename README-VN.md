# Script Tự Động 0G Labs Testnet

Kho lưu trữ này chứa một bộ sưu tập các script Python được thiết kế để tự động hóa nhiều tác vụ trên 0G Labs Testnet, bao gồm nhận token từ faucet, hoán đổi token, triển khai hợp đồng, gửi giao dịch và mint NFT. Các script này được tích hợp với file `main.py` trung tâm để thực thi dễ dàng, hỗ trợ nhiều khóa riêng tư và giao diện CLI thân thiện với người dùng.

## Tính Năng Tổng Quan

### Tính Năng Chung

- **Hỗ Trợ Nhiều Tài Khoản**: Đọc khóa riêng tư từ `pvkey.txt` để thực hiện hành động trên nhiều tài khoản.
- **CLI Màu Sắc**: Sử dụng `colorama` để hiển thị đầu ra hấp dẫn với văn bản và viền màu.
- **Thực Thi Bất Đồng Bộ**: Được xây dựng với `asyncio` để tương tác blockchain hiệu quả.
- **Xử Lý Lỗi**: Bắt lỗi toàn diện cho các giao dịch blockchain và vấn đề RPC.
- **Hỗ Trợ Song Ngữ**: Hỗ trợ đầu ra bằng cả tiếng Việt và tiếng Anh dựa trên lựa chọn của người dùng.

### Các Script Bao Gồm

#### 1. `faucettokens.py` - Nhận ETH/BTC/USDT từ Faucet
- **Mô Tả**: Nhận ETH, BTC hoặc USDT từ faucet của 0G Labs Testnet (yêu cầu số dư A0GI).
- **Tính Năng**:
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần nhận.
  - Nhật ký giao dịch chi tiết với liên kết explorer.
- **Cách Dùng**: Chọn từ menu `main.py`.

#### 2. `swaptoken.py` - Hoán Đổi Token
- **Mô Tả**: Hoán đổi token (USDT, ETH, BTC) ngẫu nhiên hoặc thủ công trên router swap của 0G Labs Testnet.
- **Tính Năng**:
  - Hỗ trợ hoán đổi ngẫu nhiên hoặc thủ công (ví dụ: USDT -> ETH).
  - Người dùng nhập số lần hoán đổi và số lượng (mặc định: 0.1 token).
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần hoán đổi.
- **Cách Dùng**: Chọn từ menu `main.py`, chọn kiểu hoán đổi và thông số.

#### 3. `storagescan.py` - Triển Khai Storage Scan
- **Mô Tả**: Triển khai file storage scan lên 0G Labs Testnet.
- **Tính Năng**:
  - Giá trị ngẫu nhiên từ 0.000005-0.00001 A0GI.
  - Thử lại khi thất bại (tối đa 3 lần).
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần triển khai.
- **Cách Dùng**: Chọn từ menu `main.py`.

#### 4. `conftnft.py` - Mint NFT ConftApp Miner's Legacy
- **Mô Tả**: Mint NFT ConftApp Miner's Legacy (MINERS) trên 0G Labs Testnet.
- **Tính Năng**:
  - Kiểm tra số dư NFT để tránh mint trùng lặp.
  - Yêu cầu 0.005 A0GI mỗi lần mint.
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần mint.
- **Cách Dùng**: Chọn từ menu `main.py`.

#### 5. `domain.py` - Mint Domain
- **Mô Tả**: Mint domain trên 0G Labs Testnet.
- **Tính Năng**:
  - Tự động hóa mint domain cho nhiều ví.
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần mint.
- **Cách Dùng**: Chọn từ menu `main.py`.

#### 6. `mintaura.py` - Mint Aura - Panda 0G (PG)
- **Mô Tả**: Mint NFT Aura - Panda 0G (PG) trên 0G Labs Testnet.
- **Tính Năng**:
  - Kiểm tra mint hiện có để tránh trùng lặp.
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần mint.
- **Cách Dùng**: Chọn từ menu `main.py`.

#### 7. `mintnerzo.py` - Mint Nerzo - 0G OG (NERZO-0GOG)
- **Mô Tả**: Mint NFT Nerzo - 0G OG (NERZO-0GOG) với chi phí 0.005 A0GI.
- **Tính Năng**:
  - Kiểm tra số dư NFT và A0GI (tối thiểu 0.006 A0GI).
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần mint.
  - Nhật ký giao dịch chi tiết với liên kết explorer.
- **Cách Dùng**: Chọn từ menu `main.py`.

#### 8. `sendtx.py` - Gửi Giao Dịch
- **Mô Tả**: Gửi giao dịch A0GI đến địa chỉ ngẫu nhiên hoặc từ `address.txt`.
- **Tính Năng**:
  - Số giao dịch và số lượng do người dùng cấu hình (mặc định: 0.000001 A0GI).
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các giao dịch.
  - Nhật ký giao dịch chi tiết với liên kết explorer.
- **Cách Dùng**: Chọn từ menu `main.py`, nhập số giao dịch và số lượng.

#### 9. `deploytoken.py` - Triển Khai Hợp Đồng Token ERC-20
- **Mô Tả**: Triển khai hợp đồng thông minh ERC-20 tùy chỉnh trên 0G Labs Testnet.
- **Tính Năng**:
  - Người dùng nhập tên token, ký hiệu, số thập phân và tổng cung.
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần triển khai.
- **Cách Dùng**: Chọn từ menu `main.py`, cung cấp chi tiết token.

#### 10. `sendtoken.py` - Gửi Token ERC-20
- **Mô Tả**: Chuyển token ERC-20 đến địa chỉ ngẫu nhiên hoặc từ `addressERC20.txt`.
- **Tính Năng**:
  - Người dùng nhập địa chỉ hợp đồng và số lượng.
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần chuyển.
  - Nhật ký giao dịch chi tiết với liên kết explorer.
- **Cách Dùng**: Chọn từ menu `main.py`, nhập địa chỉ hợp đồng và số lượng.

## Yêu Cầu

- **Python 3.8+**
- **Phụ Thuộc**: Cài đặt qua `pip install -r requirements.txt` (bao gồm `web3.py`, `colorama`, `asyncio`, và `eth-account`).
- **pvkey.txt**: Thêm khóa riêng tư (mỗi khóa một dòng) để tự động hóa ví.
- **address.txt / addressERC20.txt**: File tùy chọn để chỉ định địa chỉ nhận.

## Cài Đặt

1. **Clone this repository:**
- Open cmd or Shell, then run the command:
```sh
git clone https://github.com/thog9/Somnia-testnet.git
```
```sh
cd Somnia-testnet
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
- Chọn ngôn ngữ (Tiếng Việt/Tiếng Anh) và chọn script từ menu.

## Liên Hệ

- **Telegram**: [thog099](https://t.me/thog099)
- **Kênh Telegram**: [thogairdrops](https://t.me/thogairdrops)
- **Replit**: Thog




