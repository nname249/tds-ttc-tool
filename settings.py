
class BotSettings:
    def __init__(self):
        self.total_s = None
        self.time_each_s = None
        self.countdown_s = None
        self.countdown_time = None
        self.change_acc_s = None
    
    def set_total_s(self, total_s: int):
        self.total_s = total_s
    
    def set_time_each_s(self, time_each_s: int):
        self.time_each_s = time_each_s
    
    def set_countdown_s(self, countdown_s: int):
        self.countdown_s = countdown_s
    
    def set_countdown_time(self, countdown_time: int):
        self.countdown_time = countdown_time
    
    def set_change_acc_s(self, change_acc_s: int):
        self.change_acc_s = change_acc_s