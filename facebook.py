from FacebookAPI import FacebookAPI
from base_platform import JobData

class FacebookTool(FacebookAPI):

    def login(self):
        return self.info()

    def do_social(self, job: JobData):
        if job.group == "REACT":
            return self.reaction(job.idExecute, job.typeExecute)
        elif job.group == "COMMENT":
            return self.comment(job.idExecute, job.msgExecute)
        elif job.group == "SHARE":
            return self.share(job.idExecute)
        elif job.group == "SHARE_WITH_MESSAGE":
            return self.share_with_message(job.idExecute, job.msgExecute)
        elif job.group == "FOLLOW":
            return self.follow(job.idExecute)
        elif job.group == "JOIN_PAGE":
            return self.join_page(job.idExecute)
        elif job.group == "RATE_PAGE":
            return self.rate_page(job.idExecute, job.msgExecute)
        else:
            return False