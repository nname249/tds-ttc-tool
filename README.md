# TDS-TTC-TOOL

Công cụ hỗ trợ chạy nhiệm vụ trên các nền tảng [Trao Đổi Sub](https://traodoisub.com/) và [Tương Tác Chéo](https://tuongtaccheo.com/) bằng Python

## Tính năng chính
- Hỗ trợ nền tảng [Trao Đổi Sub](https://traodoisub.com/) (TDS) và [Tương Tác Chéo](https://tuongtaccheo.com/) (TTC)
- Chạy bằng Cookies Facebook (chạy nhiều được, đổi acc luân phiên)
- Môi trường terminal
- Lưu Token, Cookies và cấu hình thời gian vào file `config.json`

## Hình ảnh minh họa
| ![Banner](https://sf-static.upanhlaylink.com/img/image_20260228e3d2771575bb03ed4608e6ae777cc27d.jpg) | ![Token & Cookies](https://sf-static.upanhlaylink.com/img/image_20260228a4e4156a0120696d90f0ddc65adcb994.jpg) | ![Setup & Running](https://sf-static.upanhlaylink.com/img/image_2026022896911bfce22f6da6fc7840eef0a50675.jpg) |
| :---: | :---: | :---: |
| *Giao diện chính* | *Token & Cookies* | *Setup & Running* |

## Hướng dẫn cài đặt
1. Đảm bảo máy tính đã cài đặt Python (3.8+).
2. Tải về mã nguồn
- Sử dụng Git
```powershell
git clone https://github.com/nname249/tds-ttc-tool.git
```
- Hoặc tải file zip về giải nén
3. Cài đặt các thư viện cần thiết:
```powershell
pip install -r requirements.txt
```

## Cách chạy tool
Mở Terminal tại thư mục dự án và chạy lệnh:
```powershell
python main.py
```

## Lưu ý
- Không chia sẻ file `config.json` cho người khác vì nó chứa Token và Cookies của bạn
- Các thiết lập về thời gian nghỉ và số lượng nhiệm vụ có thể chỉnh sửa trực tiếp trong Tool hoặc qua file `config.json`
- Thiết lập thời gian chờ giữa mỗi nhiệm vụ trên 15s để tránh bị checkpoint (nên chạy từ 2 acc trở lên để đổi acc luân phiên)


-- tool không có bất kỳ chức năng nào liên quan đến việc lấy token, cookies, hay bất kỳ thông tin cá nhân nào của người dùng. Tất cả thông tin cá nhân của người dùng đều được lưu trữ cục bộ trên máy tính của người dùng-- tool chỉ là công cụ hỗ trợ người dùng chạy nhiệm vụ trên các nền tảng đã nêu. Tác giả không chịu trách nhiệm về bất kỳ hậu quả nào xảy ra khi sử dụng tool này--