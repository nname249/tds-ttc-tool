import requests

from base_platform import BasePlatform, ReturnData, AccountData, ConfigData, JobData, SubmitData, ReceiveCoinData, TaskDescriptionData
from typing import List

class Traodoisub(BasePlatform):
    def __init__(self, token: str):
        super().__init__(token)
        self.base_url  = "https://traodoisub.com/api"

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
        })      
        self._TIMEOUT = 15

        self._tasks = [
            {"type": "facebook_reaction", "label": "Thả cảm xúc", "group": self.TASK_TYPE_GROUP.REACT},
            {"type": "facebook_reaction2", "label": "Thả cảm xúc 2", "group": self.TASK_TYPE_GROUP.REACT},
            {"type": "facebook_reactioncmt", "label": "Thả cảm xúc cmt", "group": self.TASK_TYPE_GROUP.REACT_CMT},
            {"type": "facebook_share", "label": "Chia sẻ", "group": self.TASK_TYPE_GROUP.SHARE},
            {"type": "facebook_follow", "label": "Theo dõi", "group": self.TASK_TYPE_GROUP.FOLLOW},
            {"type": "facebook_page", "label": "Tham gia page", "group": self.TASK_TYPE_GROUP.JOIN_PAGE},
        ]

    def get_all_tasks(self) -> List[TaskDescriptionData]:
        return [
            TaskDescriptionData(
                type=item['type'],
                label=item['label'],
                group=item['group']
            ) for item in self._tasks
        ]
    
    def login(self) -> ReturnData:
        try:
            url = f"{self.base_url}/"
            payload = {
                "fields": "profile",
                "access_token": self.token,
            }
            response = self.session.get(url, params=payload, timeout=self._TIMEOUT)
            jsonData = response.json()
            if 'error' not in jsonData:
                return ReturnData(
                    success=True,
                    data=AccountData(
                        user=jsonData['data']['user'],
                        xu=jsonData['data']['xu'],
                    ),
                    msg="Đăng nhập thành công",
                )
            else:
                return ReturnData(
                    success=False,
                    error=f"HTTP {response.status_code}",
                    msg="Đăng nhập thất bại",
                )
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")
            return ReturnData(
                success=False,
                error=str(e),
                msg="Đăng nhập thất bại",
            )    

    def config(self, id: str) -> ReturnData:
        try:
            # https://traodoisub.com/api/?fields=run&id={{idfb}}&access_token={{TDS_token}}
            url = f"{self.base_url}/"
            payload = {
                "fields": "run",
                "id": id,
                "access_token": self.token,
            }
            response = self.session.get(url, params=payload, timeout=self._TIMEOUT)
            jsonR = response.json()
            if 'error' not in jsonR:
                return ReturnData(
                    success=True,
                    data=ConfigData(
                        id=jsonR['data']['id'],
                    ),
                    msg="Cấu hình thành công!",
                )
            else:
                return ReturnData(
                    success=False,
                    error=jsonR['error'],
                    msg="Cấu hình thất bại",
                )
        except Exception as e:
            return ReturnData(
                success=False,
                error=str(e),
                msg="Cấu hình thất bại",
            )
    def get_job(self, index_task: int) -> ReturnData:
        """
        Args:
            fields (str): facebook_reaction, facebook_reaction2, facebook_reactioncmt, facebook_share, facebook_follow, facebook_page
            type (str): Áp dụng cho: facebook_reaction, facebook_reaction2, facebook_reactioncmt. Các thông số bao gồm:

                ALL: lấy tất cả loại cảm xúc
                LIKE: lấy nguyên loại là like, tương tự thay LOVE, WOW, HAHA, ANGRY, SAD
                Lấy nhiều loại cùng lúc tùy chọn: LOVE,WOW các loại ngăn cách nhau bởi dấu phẩy
        Returns:
            {
                "cache": 0,
                "data": [
                    {
                        "id": "100064877612993_980823404090238",
                        "code": "WSE9W9VGJQFP5TG28RC5",
                        "type": "LIKE"
                    }
                ]
            }
        """
        try:
            # https://traodoisub.com/api/?fields={{fields}}&access_token={{TDS_token}}&type={{type}}
            url = f"{self.base_url}/"
            task_info = self._tasks[index_task]
            payload = {
                "fields": task_info['type'],
                "access_token": self.token,
                "type": "ALL",
            }
            response = self.session.get(url, params=payload, timeout=self._TIMEOUT)
            jsonR = response.json()
            if 'error' not in jsonR:
                job_list = [
                    JobData(
                        typeJob=task_info['type'],
                        idJob=item['code'],
                        idExecute=item['id'],
                        typeExecute=item['type'],
                        group=task_info['group']
                    ) for item in jsonR.get('data', [])
                ] 
                return ReturnData(
                    success=True,
                    data=job_list,
                    msg="Lấy nhiệm vụ thành công",
                )
            else:
                return ReturnData(
                    success=False,
                    error=f"{jsonR['error']}",
                    msg="Lấy nhiệm vụ thất bại",
                    countdown=jsonR.get('countdown', 0)
                )
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")
            return ReturnData(
                success=False,
                error=str(e),
                msg="Lấy nhiệm vụ thất bại",
            )
            
    def submit(self, job: JobData) -> ReturnData:
        """
        Args:
            type (str): Loại nhiệm vụ
            id (str): code nhiệm vụ

        áp dụng với 'facebook_follow', 'facebook_page'

        Returns:
            {
                "cache":1     //cache là số nhiệm vụ chưa nhận xu, trên 4 nhiệm vụ có thể nhận xu
            }
        """
        try:
            # https://traodoisub.com/api/coin/?type={{type}}&id={{id_job}}&access_token={{TDS_token}}
            url = f"{self.base_url}/coin/"

            payload = {
                "type": f'{job.typeJob}_cache',
                "id": job.idJob,
                "access_token": self.token,
            }
            response = self.session.get(url, params=payload, timeout=self._TIMEOUT)
            jsonR = response.json()
            if jsonR['msg'] == 'Thành công' and response.status_code == 200: 

                # Tăng cache
                self.cache_job["follow" if job.typeJob == "facebook_follow" else 'page'] = jsonR['cache']

                return ReturnData(
                    success=True,
                    data=SubmitData(
                        cache=jsonR['cache'],
                    ),
                    msg="Đã lưu NV vào cache, đủ cache sẽ tự động nhận xu",
                )
            else:
                return ReturnData(
                    success=False,
                    error=f"HTTP {response.status_code}",
                    msg="Gửi duyệt NV thất bại",
                )
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")
            return ReturnData(
                success=False,
                error=str(e),
                msg="Gửi duyệt NV thất bại",
            )
    
    def receive_coin(self, job: JobData) -> ReturnData:
        """
        Args:
            type (str): Loại nhiệm vụ
            id (str): code nhiệm vũ đã làm. Riêng facebook_follow, facebook_page mặc định là facebook_api

        áp dụng với TYPE_NHIEMVU_FB['facebook_follow'], TYPE_NHIEMVU_FB['facebook_page']

        Returns:
            {
                "success": 200,
                "data": {
                    "xu": 560274200,
                    "job_success": 2,
                    "xu_them": 4200,
                    "msg": "+4200 Xu"
                }
            }
        """
        if (job.typeJob == 'facebook_follow' and self.cache_job['follow'] <= 4) or (job.typeJob == 'facebook_page' and self.cache_job['page'] <= 4):
            return self.submit(job)
            
        try:
            # https://traodoisub.com/api/coin/?type={{type}}&id={{id_job}}&access_token={{TDS_token}}
            url = f"{self.base_url}/coin/"
            payload = {
                "type": job.typeJob,
                "id": job.idJob if job.typeJob not in ['facebook_follow', 'facebook_page'] else 'facebook_api',
                "access_token": self.token,
            }
            response = self.session.get(url, params=payload, timeout=self._TIMEOUT)
            jsonR = response.json()
            if 'error' not in jsonR and response.status_code == 200 :
                data = jsonR['data']

                return ReturnData(
                    success=True,
                    data=ReceiveCoinData(
                        xu=data.get('xu', 0),
                        job_success=data.get('job_success', 0),
                        xu_them=data.get('xu_them', ''),
                        msg=data.get('msg', ''),
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
                error=str(e),
                msg="Nhận xu thất bại",
            )