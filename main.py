from typing import List
import time, random

from base_platform import BasePlatform
from traodoisub import Traodoisub
from tuongtaccheo import Tuongtaccheo

from FacebookAPI import FacebookAPI
from account import AccountPool
from settings import BotSettings
from utils import Utils


class MainTool:
    def __init__(self,  platform: BasePlatform, 
                        acc_pool: AccountPool,
                        settings: BotSettings,
                        indexes_job: List[int]):

        self.platform = platform
        self.acc_pool = acc_pool
        self.settings = settings
        self.indexes_job = indexes_job

        self.is_running = False
        self._total_job = 0
        self._acc_job_count = 0
        self._success_job = 0
        self._fail_job = 0



    def start(self):

        Utils.gach()

        #show thôn tin acc fb
        login_fb_response = self.acc_pool.current.login() 
        Utils.show_info_facebook(login_fb_response.get('id',''), login_fb_response.get('name',''))

        # Cấu hình acc vào nền tảng
        stop = Utils.loading("Đang cấu hình tài khoản...")
        config_response = self.platform.config(self.acc_pool.current.actor_id)
        stop()
        if (not config_response.success):
            Utils.log(f"Cấu hình thất bại: {config_response.error}", "Lỗi")
            return
        Utils.log(f"Cấu hình thành công", "Thành công")

        self.is_running = True
        is_attempt_get_job = 0
        last_index_job = -1
        # Vòng lặp chính
        while self.is_running:
            random_index_job = random.choice(self.indexes_job)
            while random_index_job == last_index_job and len(self.indexes_job) > 1:
                random_index_job = random.choice(self.indexes_job)
            last_index_job = random_index_job

            # Lấy nhiệm vụ
            stop = Utils.loading("Đang lấy nhiệm vụ...")
            jobs_response = self.platform.get_job(random_index_job)
            stop()
            if not jobs_response.success:
                is_attempt_get_job += 1
                if(is_attempt_get_job > 3):
                    Utils.log(f"Lấy nhiệm vụ thất bại: {jobs_response.error}", "Lỗi")
                    if jobs_response.countdown:
                        Utils.delay(jobs_response.countdown)
                        is_attempt_get_job = 0
                continue
            Utils.gach()
            Utils.log(f"Lấy được {len(jobs_response.data)} nhiệm vụ [{self.platform.get_all_tasks()[random_index_job].label}]", "Thành công")
            
            for job in jobs_response.data:

                #đổi acc nếu đến lượt
                if self._should_change_acc():
                    stop = Utils.loading("Đang đổi acc...")
                    self._switch_account()
                    stop()
                    break

                #thời gian nghỉ giữa mỗi nhiệm vụ
                Utils.delay(self.settings.time_each_s)
                
                #lỗi quá nhiều (>70%) -> dừng
                if self._total_job > 20 and (self._fail_job / self._total_job) > 0.7:
                    Utils.log(f"Lỗi quá nhiều ({self._fail_job / self._total_job * 100}%)", "Lỗi")
                    self.stop()
                
                #hoàn thành tổng NV -> dừng
                if self._total_job == self.settings.total_s:
                    Utils.log(f"Đã hoàn thành {self.settings.total_s} nhiệm vụ", "Thành công")
                    self.stop()

                self._total_job += 1
                self._acc_job_count += 1
                #làm nhiệm vụ
                stop = Utils.loading("Đang tương tác Facebook...")
                isDone = self.acc_pool.current.do_social(job)
                stop()
                if not isDone:
                    self._fail_job += 1
                    Utils.show_job_fail(self._fail_job, job.typeExecute, job.idExecute, "Tương tác thất bại")
                    continue

                #nhận xu nếu thao tác facebook ok
                Utils.delay(1)
                stop = Utils.loading("Đang nhận xu...")
                recieve_coin_response = self.platform.receive_coin(job)
                stop()
                data = recieve_coin_response.data
                if not recieve_coin_response.success:
                    self._fail_job += 1
                    Utils.show_job_fail(self._fail_job, job.typeExecute, job.idExecute, recieve_coin_response.error)
                    continue

                self._success_job += 1
                Utils.show_job_success(self._success_job, job.typeExecute, job.idExecute, data.xu_them or data.msg, data.xu)
                
                #sau khi làm được N nhiệm vụ thì nghỉ ngơi
                if self._success_job != 0 and self._success_job % self.settings.countdown_s == 0:
                    Utils.log(f"Đã làm {self._success_job} nhiệm vụ, nghỉ ngơi {self.settings.countdown_time}s", "Thông tin")
                    Utils.delay(self.settings.countdown_time)
            
    def _switch_account(self) -> bool:
        new_acc = None
        isSuccess = False
        while (not isSuccess):
            new_acc = self.acc_pool.next
            Utils.gach()
            login_fb_response = new_acc.login()
            Utils.show_info_facebook(login_fb_response.get('id',''), login_fb_response.get('name',''))
            config_response = self.platform.config(new_acc.actor_id)
            if (not config_response.success):
                Utils.log(f"Cấu hình thất bại: {config_response.error}", "Lỗi")
                continue
            isSuccess = True
            self._acc_job_count = 0
            Utils.log(f"Cấu hình thành công", "Thành công")
    def _should_change_acc(self) -> bool:
        return self._acc_job_count >= self.settings.change_acc_s

    def stop(self):
        self.is_running = False   
        print(f"Tổng nhiệm vụ đã làm: {self._total_job}")
        print(f"Thành công: {self._success_job}")
        print(f"Thất bại: {self._fail_job}")


if __name__ == "__main__":
    platform = None

    Utils.show_banner()

    Utils.show_tools()
    choice = Utils.input_choice("Chọn nền tảng", ["1", "2"])
    if choice == "1":
        platform = Traodoisub
    elif choice == "2":
        platform = Tuongtaccheo

    #load configs trong file config.json
    configs = Utils.load_config()

    list_tokens = Utils.show_config_tokens(configs)
    choice = Utils.input_choice("n: nhập token mới, y: chọn token trong file", ["y", "n"])
    if choice == "n":
        input_token = Utils.input_text("Nhập TOKEN: ")
        platform = platform(input_token)
    elif choice == "y":
        input_token = Utils.input_choice("Nhập số để chọn token trong file")
        platform = platform(list_tokens[int(input_token)-1].get("token", ""))

    #định nghĩa object nền tảng
    stop = Utils.loading("Đang đăng nhập...")
    login_response = platform.login()
    stop()
    if not login_response.success:
        Utils.log(f"{login_response.msg}", "Lỗi")
        exit()
    Utils.log(f"{login_response.msg}", "Thành công")
    Utils.show_info_platform(login_response.data.user, login_response.data.xu)

    #lưu token vào config
    isInsert = True
    for item in list_tokens:
        if item.get("token", "") == platform.token:
            isInsert = False
            break
    if isInsert:
        list_tokens.append({
            "user": login_response.data.user,
            "token": platform.token
        })
    configs["tokens"] = list_tokens
    Utils.save_config(configs)

    list_cookies = Utils.show_config_cookies(configs)
    __cookies = []
    choice = Utils.input_choice("n: nhập cookie mới, y: chọn cookie trong file", ["y", "n"])
    if choice == "n":
        input_cookie = Utils.input_text("Nhập COOKIE (nhấn enter để dừng nhập): ")
        while input_cookie != "":
            __cookies.append(input_cookie)
            input_cookie = Utils.input_text("Nhập COOKIE (nhấn enter để dừng nhập): ")
    elif choice == "y":
        input_cookie = Utils.input_choice("Nhập số để chọn cookie trong file (cách nhau bởi dấu cách)", [str(i) for i in range(1, len(list_cookies)+1)])
        for i in input_cookie:
            __cookies.append(list_cookies[int(i)-1])
    
    #lưu cookies
    for cookie in __cookies:
        c_user_new = Utils.extract_c_user(cookie)
        if not c_user_new:
            Utils.log(f'Cookie không hợp lệ hoặc không tìm thấy c_user: {cookie[:20]}...', "Lỗi")
            continue
            
        isInsert = True
        for item in list_cookies:
            c_user_old = Utils.extract_c_user(item)
            if c_user_new == c_user_old:
                isInsert = False
                break
        
        if isInsert:
            list_cookies.append(cookie)
            
    configs["cookies"] = list_cookies
    Utils.save_config(configs)
    
    #khởi tạo acc pool
    stop = Utils.loading("Đang tải danh sách tài khoản Facebook...")
    acc_pool = AccountPool(__cookies)
    stop()

    #show task của nền tảng
    Utils.show_tasks(platform.get_all_tasks())
    choice = Utils.input_choice("Chọn nhiệm vụ (chọn nhiều thì cách nhau bởi dấu cách)", [str(i) for i in range(1, len(platform.get_all_tasks())+1)])
    list_tasks_index = [int(i)-1 for i in choice]

    #khởi tạo settings
    settings = BotSettings()
    current_settings = Utils.show_settings(configs)
    choice = Utils.input_choice("n: nhập settings mới, y: sử dụng settings trên", ["y", "n"])
    
    if choice == "n":
        settings.set_total_s(int(Utils.input_text("Nhập tổng số nhiệm vụ")))
        settings.set_time_each_s(int(Utils.input_text("Nhập thời gian nghỉ giữa mỗi nhiệm vụ (giây)")))
        settings.set_countdown_s(int(Utils.input_text("Làm bao nhiêu nhiệm vụ thì nghỉ ngơi")))
        settings.set_countdown_time(int(Utils.input_text("Nhập thời gian nghỉ ngơi (giây)")))
        settings.set_change_acc_s(int(Utils.input_text("Làm bao nhiêu nhiệm vụ thì đổi acc")))
        
        # Lưu vào config nếu người dùng muốn
        configs["settings"] = {
            "total_s": settings.total_s,
            "time_each_s": settings.time_each_s,
            "countdown_s": settings.countdown_s,
            "countdown_time": settings.countdown_time,
            "change_acc_s": settings.change_acc_s
        }
        Utils.save_config(configs)
        Utils.log("Đã lưu cài đặt mới vào file cấu hình.", "Thành công")
            
    elif choice == "y":
        if current_settings:
            settings.set_total_s(current_settings.get("total_s", 0))
            settings.set_time_each_s(current_settings.get("time_each_s", 0))
            settings.set_countdown_s(current_settings.get("countdown_s", 0))
            settings.set_countdown_time(current_settings.get("countdown_time", 0))
            settings.set_change_acc_s(current_settings.get("change_acc_s", 0))
            Utils.log("Đã áp dụng cài đặt từ file cấu hình.", "Thông tin")
        else:
            Utils.log("Không có cấu hình để sử dụng! Vui lòng nhập mới.", "Lỗi")
            exit()

    tool = MainTool(platform=platform, 
                    acc_pool=acc_pool, 
                    settings=settings, 
                    indexes_job=list_tasks_index)
    tool.start()
   