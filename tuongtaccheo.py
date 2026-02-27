import requests, json, random

from base_platform import BasePlatform, ReturnData, AccountData, ConfigData, JobData, SubmitData, ReceiveCoinData, TaskDescriptionData
from typing import List

class Tuongtaccheo(BasePlatform):
    def __init__(self, token: str):
        super().__init__(token)
        self.token_TTC = token
        self.base_url  = "https://tuongtaccheo.com"
        self.session = requests.Session()
        self.session.headers.update({
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
            "accept-language": "vi,en-US;q=0.9,en;q=0.8",
            "dnt": "1",
            "x-requested-with": "XMLHttpRequest",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        })
        self._tasks = [
            {"type": "likepostvipcheo", "label": "like post 1", 'group': self.TASK_TYPE_GROUP.REACT},
            {"type": "likepostvipre", "label": "like post 2", 'group': self.TASK_TYPE_GROUP.REACT},
            {"type": "camxucvipcheo", "label": "cảm xúc vip1", 'group': self.TASK_TYPE_GROUP.REACT},
            {"type": "camxucvipre", "label": "cảm xúc vip2", 'group': self.TASK_TYPE_GROUP.REACT},
            {"type": "camxuccheobinhluan", "label": "cảm xúc bình luận", 'group': self.TASK_TYPE_GROUP.REACT_CMT},
            {"type": "cmtcheo", "label": "comment", 'group': self.TASK_TYPE_GROUP.COMMENT},
            {"type": "subcheo", "label": "follow vip1", 'group': self.TASK_TYPE_GROUP.FOLLOW},
            {"type": "subcheofbvip", "label": "follow vip2", 'group': self.TASK_TYPE_GROUP.FOLLOW},
            {"type": "sharecheo", "label": "share", 'group': self.TASK_TYPE_GROUP.SHARE},
            {"type": "sharecheokemnoidung", "label": "share kèm nội dung", 'group': self.TASK_TYPE_GROUP.SHARE},
            {"type": "likepagecheo", "label": "like page", 'group': self.TASK_TYPE_GROUP.LIKE_PAGE},
            {"type": "thamgianhomcheo", "label": "tham gia page", 'group': self.TASK_TYPE_GROUP.JOIN_PAGE},
            {"type": "danhgiapage", "label": "đánh giá page", 'group': self.TASK_TYPE_GROUP.RATE_PAGE},
        ]

        self.cache_follow_id_data_list = []
    def get_all_tasks(self) -> List[TaskDescriptionData]:
        return [
            TaskDescriptionData(
                type=item['type'],
                label=item['label'],
            ) for item in self._tasks
        ]
    def login(self) -> ReturnData:
        """
        Đăng nhập vào hệ thống Tuongtaccheo (dùng Token - an toàn).
        Cookie PHPSESSID sẽ tự động được lưu vào session.

        Returns:
            {
                "status": "success",
                "data": {
                    "user": "pillrock",
                    "sodu": 2200,
                    ...
                }
            }
        """
        try:
            url = f"{self.base_url}/logintoken.php"
            data = {
                "access_token": self.token,
            }
            response = self.session.post(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            jsonR = response.json()
            if response.status_code == 200 and jsonR['status'] != 'fail':
                return ReturnData(
                    success=True,
                    data=AccountData(
                        user=jsonR['data']['user'],
                        xu=jsonR['data']['sodu'],
                    ),
                    msg="Đăng nhập thành công",
                )
            else:
                return ReturnData(
                    success=False,
                    error=f"{jsonR['mess']}",
                    msg="Đăng nhập thất bại",
                )
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")
            return None    
    
    def config(self, id: str) -> ReturnData:
        """
        Cấu hình (set nick) Facebook trên hệ thống Tuongtaccheo.
        Yêu cầu đã gọi dangNhap() trước để có cookie session.

        Args:
            type (str): Loại nhiệm vụ 
            id (str): đối với FB là id FB, tiktok, ytb là id trên nền tảng TTC, 

        Returns:
            str: Nội dung phản hồi từ server (text, không phải JSON)
                 Ví dụ: "1" = thành công, "0" hoặc rỗng = thất bại
        """
        # if type not in ['fb', 'tt', 'youtube']:
        #     return "Loại nhiệm vụ không hợp lệ"
        try:
            url = f"{self.base_url}/cauhinh/datnick.php"

            data = "iddat%5B%5D={}&loai={}".format(id, 'fb')

            headers = {
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "origin": "https://tuongtaccheo.com",
                "referer": "https://tuongtaccheo.com/cauhinh/facebook.php",
                
            }

            response = self.session.post(url, data=data, headers=headers)
            jsonR = response.json() # 1: True, 2: False
            if response.status_code == 200 and jsonR==1:
                return ReturnData(
                    success=True,
                    data=ConfigData(
                        id=id,
                    ),
                    msg="Cấu hình thành công",
                )
            else:
                return ReturnData(
                    success=False,
                    error=f"{jsonR}",
                    msg="Cấu hình thất bại",
                )
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")
            return ReturnData(
                success=False,
                error=f"{e}",
                msg="Cấu hình thất bại",
            )
    
    def get_job(self, index_task: int) -> ReturnData:
        """
        Lấy nhiệm vụ Facebook từ Tuongtaccheo.
        Yêu cầu đã gọi dangNhap() trước để có cookie session.

        Args:
            index_task (int): Chỉ số nhiệm vụ (0-based)

        Returns:
            Ví dụ:
            
        """
        try:
            task_info = self._tasks[index_task]
            headers = { 
                "accept": "application/json, text/javascript, */*; q=0.01",
                "origin": "https://tuongtaccheo.com",
                "referer": f"https://tuongtaccheo.com/kiemtien/{task_info['type']}/",
            }
            url = f"{self.base_url}/kiemtien/{task_info['type']}/getpost.php"
            response = self.session.get(url, headers=headers)
            jsonR = response.json()
            if response.status_code == 200 and 'error' not in jsonR:
                return ReturnData(
                    success=True,
                    data=[
                        JobData(
                            typeJob=task_info['type'],
                            idJob=item['idpost'],
                            idExecute=item.get('idfb') or item['idpost'],
                            typeExecute="LIKE" if task_info['type'] in ['likepostvipre', 'likepostvipcheo'] else item.get('loaicx') or None,
                            msgExecute=random.choice(json.loads(item.get('nd', []))) if item.get('nd') else None,
                            group=task_info['group']
                            
                        ) for item in jsonR
                    ],
                    msg="Lấy nhiệm vụ thành công",
                )
            else:
                return ReturnData(
                    success=False,
                    error=f"{response.text}",
                    msg="Lấy nhiệm vụ thất bại",
                    countdown=jsonR.get('countdown', 0)
                )
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")
            return ReturnData(
                success=False,
                error=f"{e}",
                msg="Lấy nhiệm vụ thất bại",
            )
    
    def submit(self, job: JobData) -> ReturnData:
        if 'subcheo' not in job.typeJob:
            return ReturnData(
                success=False,
                error="Không hỗ trợ loại nhiệm vụ này",
                msg="Không hỗ trợ loại nhiệm vụ này",
            )
        self.cache_job['follow'] += 1
        self.cache_follow_id_data_list.append(job.idJob)
        return ReturnData(
            success=True,
            data=SubmitData(
                cache=self.cache_job['follow']
            ),
            msg="Đã lưu vào cache, đủ cache sẽ tự động nhận xu",
        )
    
    def receive_coin(self, job: JobData) -> ReturnData:
        """
        Nhận xu từ Tuongtaccheo.
        Yêu cầu đã gọi dangNhap() trước để có cookie session.

        Returns:
            Ví dụ:
            {'error': 'Bạn chưa đánh giá đúng nội dung'}
            {'mess': 'Thành công, bạn được cộng 1000 xu'}
        """
        isReceiveCoinCache = 'subcheo' in job.typeJob
        if isReceiveCoinCache and self.cache_job['follow'] <= 10:
            return self.submit(job)

        try:
            headers = { 
                "accept": "application/json, text/javascript, */*; q=0.01",
                "origin": "https://tuongtaccheo.com",
                "referer": f"https://tuongtaccheo.com/kiemtien/{job.typeJob}/",
                "x-requested-with": "XMLHttpRequest",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
            }
            url = f"{self.base_url}/kiemtien/{job.typeJob}/nhantien.php"
            data = {
                "id": job.idJob if not isReceiveCoinCache else ",".join(self.cache_follow_id_data_list),
            }
            response = self.session.post(url, data=data, headers=headers)
            jsonR = response.json()
            if response.status_code == 200 and 'error' not in jsonR:
                loginRes = self.login()
                return ReturnData(
                    success=True,
                    data=ReceiveCoinData(
                        xu=loginRes.data.xu if loginRes.success else 0,
                        xu_them=jsonR['mess'].split("cộng")[1].strip(),
                        msg=jsonR['mess'],
                    ),
                    msg="Nhận xu thành công",
                )
            else:
                return ReturnData(
                    success=False,
                    error=f"{jsonR['error']}",
                    msg="Nhận xu thất bại",
                )
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")
            return ReturnData(
                success=False,
                error=f"{e}",
                msg="Nhận xu thất bại",
            )