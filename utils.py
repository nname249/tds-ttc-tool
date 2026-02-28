import time, os, json
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.status import Status
from rich.markup import escape


class Utils:
    console = Console()

    @staticmethod
    def extract_c_user(cookie):
        """
        Trích xuất c_user từ chuỗi cookie một cách an toàn
        """
        match = re.search(r'c_user=(\d+)', cookie)
        return match.group(1) if match else None

    @staticmethod
    def gach():
        """
        In ra dòng kẻ ngang màu vàng (45 dấu -)
        """
        Utils.console.print("[yellow]" + "-" * 45 + "[/yellow]")

    @staticmethod
    def show_banner():
        banner_text = """
 ██████╗  █████╗ ████████╗     ██████╗  ██████╗ 
 ██╔══██╗██╔══██╗╚══██╔══╝    ██╔═████╗██╔══██╗
 ██║  ██║███████║   ██║       ██║██╔██║╚██████║
 ██║  ██║██╔══██║   ██║       ████╔╝██║ ╚═══██║
 ██████╔╝██║  ██║   ██║       ╚██████╔╝ ██████╔╝
 ╚═════╝ ╚═╝  ╚═╝   ╚═╝        ╚═════╝  ╚═════╝ 
        """
        Utils.console.print(Panel(
            Text(banner_text, style="bold cyan"),
            title="[bold yellow]TDS/TTC TOOL[/bold yellow]",
            subtitle="[bold green]by nname249[/bold green]",
            border_style="bright_magenta"
        ))

    @staticmethod
    def log(msg, type="Thông tin"):
        color = "white"
        if type == "Thông tin": color = "bold blue"
        elif type == "Cảnh báo": color = "bold yellow"
        elif type == "Lỗi": color = "bold red"
        elif type == "Thành công": color = "bold green"
        
        Utils.console.print(f"[{color}]\[{type}][/{color}] | {msg}")

    @staticmethod
    def show_job_success(num_counter, job_type, idExecute, reward, total_coin):
        timestamp = time.strftime("%H:%M:%S")
        Utils.console.print(
            f"[bold green][{num_counter}][/bold green] [grey50]\[{timestamp}][/grey50] | "
            f"[bold bright_cyan]{job_type.upper()}[/bold bright_cyan] | "
            f"[bold plum1]{idExecute}[/bold plum1] | "
            f"[bold yellow]{reward}[/bold yellow] | "
            f"[bold dark_slate_gray2]Tổng: {total_coin:,} xu[/bold dark_slate_gray2]"
        )

    @staticmethod
    def show_job_fail(num_counter, job_type, idExecute, error):
        timestamp = time.strftime("%H:%M:%S")
        Utils.console.print(
            f"[bold deep_pink2][{num_counter}] [grey50]\[{timestamp}][/grey50] | "
            f"{job_type.upper()} | "
            f"{idExecute} | "
            f"Lỗi: {error}[/bold deep_pink2]"
        )

    @staticmethod
    def show_tasks(tasks):
        """
        In ra danh sách các nhiệm vụ từ List[TaskDescriptionData] dùng Panel
        """
        task_list_str = ""
        for idx, task in enumerate(tasks, 1):
            task_list_str += f"[bold cyan][{idx}][/bold cyan] [white]{task.label}[/white]\n"
        
        Utils.console.print(Panel(
            task_list_str.strip(),
            title="[bold yellow]DANH SÁCH NHIỆM VỤ[/bold yellow]",
            border_style="bright_blue",
            expand=False
        ))

    @staticmethod
    def show_tools():
        """
        Hiển thị danh sách các nền tảng hỗ trợ
        """
        tools_str = "[bold cyan][1][/bold cyan] Trao Đổi Sub (TDS)\n" \
                    "[bold cyan][2][/bold cyan] Tương Tác Chéo (TTC)"
        
        Utils.console.print(Panel(
            tools_str,
            title="[bold yellow]CHỌN NỀN TẢNG[/bold yellow]",
            border_style="bright_blue",
            expand=False
        ))

    @staticmethod
    def input_text(prompt_msg):
        """
        Nhập liệu văn bản với giao diện đẹp
        """
        return Utils.console.input(f"[bold green]</>[/bold green] [bold white]{prompt_msg}: [/bold white]").strip()

    @staticmethod
    def clear_screen():
        """
        Xóa màn hình console
        """
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def input_choice(prompt_msg, choices=None):
        """
        Nhập lựa chọn từ danh sách (hỗ trợ nhập đơn hoặc nhiều cách nhau bởi dấu cách)
        Nếu choices là None, cho phép nhập bất kỳ giá trị nào không trống.
        """
        while True:
            val = Utils.input_text(prompt_msg)
            input_list = [item for item in val.split(" ") if item.strip()]
            
            if not input_list:
                Utils.log("Vui lòng không để trống!", "Cảnh báo")
                continue

            if choices is None:
                return input_list[0] if len(input_list) == 1 else input_list

            if all(item in choices for item in input_list):
                return input_list[0] if len(input_list) == 1 else input_list
            
            Utils.log(f"Lựa chọn không hợp lệ! Vui lòng chọn trong: {', '.join(choices)}", "Cảnh báo")

    @staticmethod
    def load_config(file_path="config.json"):
        """
        Đọc cấu hình từ file JSON
        """
        if not os.path.exists(file_path):
            # Tạo file mẫu nếu chưa có
            default_config = {
                "tokens": [],
                "settings": {
                    "total_s": 100,
                    "time_each_s": 10,
                    "countdown_s": 10,
                    "countdown_time": 120,
                    "change_acc_s": 5
                },
                "cookies": []
            }
            Utils.save_config(default_config, file_path)
            return default_config
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            Utils.log(f"Lỗi đọc file config: {e}", "ERROR")
            return None

    @staticmethod
    def save_config(data, file_path="config.json"):
        """
        Lưu cấu hình vào file JSON
        """
        try:
            directory = os.path.dirname(file_path)
            
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            Utils.log(f"Lỗi lưu file config: {e}", "ERROR") 
            return False

    @staticmethod
    def show_config_tokens(config):
        """
        Hiển thị danh sách token tìm thấy trong file config và trả về list tokens
        """
        tokens = config.get("tokens", [])
        if not tokens:
            Utils.log("Không tìm thấy token nào trong file cấu hình!")
            return []

        token_list_str = ""
        for idx, item in enumerate(tokens, 1):
            user = item.get("user", "N/A")
            token_truncated = f"{item.get('token', '')[:10]}...{item.get('token', '')[-10:]}"
            token_list_str += f"[bold cyan][{idx}][/bold cyan] [green]{user:10}[/green] | [white]{token_truncated}[/white]\n"
        
        Utils.console.print(Panel(
            token_list_str.strip(),
            title="[bold yellow]TOKEN TÌM THẤY TRONG FILE CẤU HÌNH[/bold yellow]",
            border_style="bright_blue",
            expand=False
        ))
        
        return tokens

    @staticmethod
    def show_config_cookies(config):
        """
        Hiển thị danh sách cookie tìm thấy trong file config và trả về list cookies
        """
        cookies = config.get("cookies", [])
        if not cookies:
            Utils.log("Không tìm thấy cookie nào trong file cấu hình!")
            return []

        cookie_list_str = ""
        for idx, cookie in enumerate(cookies, 1):
            # Trích xuất user id từ cookie
            user_id = Utils.extract_c_user(cookie) or "N/A"
            
            cookie_truncated = f"{cookie[:10]}...{cookie[-10:]}"
            cookie_list_str += f"[bold cyan][{idx}][/bold cyan] [green]{user_id:15}[/green] | [white]{cookie_truncated}[/white]\n"
        
        Utils.console.print(Panel(
            cookie_list_str.strip(),
            title="[bold yellow]COOKIE TÌM THẤY TRONG FILE CẤU HÌNH[/bold yellow]",
            border_style="bright_blue",
            expand=False
        ))
        
        return cookies

    @staticmethod
    def show_settings(config):
        """
        Hiển thị cài đặt hiện tại trong file config
        """
        settings = config.get("settings", {})
        if not settings:
            Utils.log("Không tìm thấy cài đặt nào trong file cấu hình!")
            return None

        settings_str = f"[bold green]1. Tổng số nhiệm vụ cần làm:[/bold green] [white]{settings.get('total_s', 0)}[/white]\n" \
                       f"[bold green]2. Thời gian nghỉ giữa mỗi nhiệm vụ:[/bold green] [white]{settings.get('time_each_s', 0)}s[/white]\n" \
                       f"[bold green]3. Làm bao nhiêu nhiệm vụ thì nghỉ ngơi:[/bold green] [white]{settings.get('countdown_s', 0)}[/white]\n" \
                       f"[bold green]4. Thời gian nghỉ ngơi:[/bold green] [white]{settings.get('countdown_time', 0)}s[/white]\n" \
                       f"[bold green]5. Làm bao nhiêu nhiệm vụ thì chuyển sang tài khoản khác:[/bold green] [white]{settings.get('change_acc_s', 0)}[/white]"
        
        Utils.console.print(Panel(
            settings_str,
            title="[bold yellow]CÀI ĐẶT HIỆN TẠI[/bold yellow]",
            border_style="bright_blue",
            expand=False
        ))
        return settings

    @staticmethod
    def show_info_platform(user, xu):
        """
        Hiển thị thông tin tài khoản và số dư trên nền tảng
        """
        info_str = f"[bold green]User:[/bold green] [bold white]{user}[/bold white]\n" \
                   f"[bold green]Xu:[/bold green] [bold white]{int(xu):,} xu[/bold white]"
        
        Utils.console.print(Panel(
            info_str,
            title="[bold yellow]THÔNG TIN NỀN TẢNG[/bold yellow]",
            border_style="bright_blue",
            expand=False
        ))

    @staticmethod
    def show_info_facebook(fb_id, fb_name):
        """
        Hiển thị thông tin tài khoản Facebook đang chạy (ID và Tên) dạng hàng ngang
        """
        Utils.console.print(f"[bold yellow]\[[/bold yellow][bold green]{fb_id}[/bold green][bold yellow]][/bold yellow] [bold white]|[/bold white] [bold plum1]{fb_name}[/bold plum1]")

    @staticmethod
    def delay(seconds):
        with Utils.console.status(f"[bold yellow]Chờ...", spinner="line") as status:
            for i in range(seconds, 0, -1):
                status.update(f"[bold yellow]Chờ: [bold cyan]{i}s[/bold cyan] ...")
                time.sleep(1)

    @staticmethod
    def loading(msg="Đang xử lý..."):
        """
        Bắt đầu hiệu ứng loading và trả về hàm stop.
        Cách dùng:
            stop = Utils.loading("Đang login")
            # làm gì đó...
            stop()
        """
        status = Utils.console.status(f"[bold yellow]{msg}", spinner="line")
        status.start()
        return status.stop