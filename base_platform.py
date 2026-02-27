from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Optional, Union

@dataclass
class AccountData:
    user: str
    xu: int

@dataclass
class JobData:
    typeJob: str
    idJob: str
    idExecute: str
    typeExecute: str = None
    msgExecute: str = None
    group: str = None
    
@dataclass
class ConfigData: 
    id: str

@dataclass
class SubmitData:
    cache: int

@dataclass
class ReceiveCoinData:
    xu: int
    msg: str
    job_success: Optional[int] = None
    xu_them: Optional[str] = None

@dataclass
class ReturnData:
    success: bool
    data: Optional[Union[AccountData, List[JobData], ConfigData, SubmitData, ReceiveCoinData]] = None
    error: Optional[str] = None
    msg: Optional[str] = None
    countdown: Optional[int] = None

@dataclass
class TaskDescriptionData:
    type: str
    label: str
    group: str = None
    
class TaskTypeGroup:
    REACT     = 'REACT'
    REACT_CMT = 'REACT_CMT'
    SHARE     = 'SHARE'
    FOLLOW    = 'FOLLOW'
    COMMENT   = 'COMMENT'
    LIKE_PAGE = 'LIKE_PAGE'
    JOIN_PAGE = 'JOIN_PAGE'
    RATE_PAGE = 'RATE_PAGE'
    

class BasePlatform(ABC):

    TASK_TYPE_GROUP = TaskTypeGroup

    def __init__(self, token: str):
        self.token = token
        self.cache_job = {
            "follow": 0,
            "page": 0
        }

    @abstractmethod
    def login(self) -> ReturnData:
        pass

    @abstractmethod
    def config(self, id: str) -> ReturnData:
        pass

    @abstractmethod
    def get_all_tasks(self) -> List[TaskDescriptionData]:
        pass

    @abstractmethod
    def get_job(self, index_task: int) -> ReturnData:
        pass

    @abstractmethod
    def submit(self, job: JobData) -> ReturnData:
        pass

    @abstractmethod
    def receive_coin(self, job: JobData) -> ReturnData:
        pass