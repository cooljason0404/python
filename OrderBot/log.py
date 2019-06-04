'''
@描述：日誌輸入封裝
@創建：2018/08/17
'''
import time
import logging

class Logger():
    def __init__(self, filename, jobid, botid, method, logger):
        # log filename 
        self.filename = filename
        self.path = './data/log/' + method + '/' + time.strftime("%Y%m%d",time.localtime()) + '_' + filename + '.log'
        self.method = method
        self.jobid = jobid
        self.botid = botid
        self.defcontent = "[JobId:" + self.jobid + "] - "
        self.formatter = logging.Formatter('[%(asctime)s] - %(filename)s - %(module)s - %(funcName)s [Line:%(lineno)d] - [%(levelname)s] - %(message)s')
        
        # Create logger
        self.logger = logging.getLogger(logger)
        logging.Logger.manager.loggerDict.pop(logger)
        self.logger.handlers = []
        self.logger.removeHandler(self.logger.handlers)

        if not self.logger.handlers:
            self.handler = logging.FileHandler(self.path)
            self.logger.setLevel(logging.DEBUG)
            self.handler.setFormatter(self.formatter)
            self.logger.addHandler(self.handler)
            ch = logging.StreamHandler() 
            ch.setLevel(logging.INFO) 
            ch.setFormatter(self.formatter) 
            self.logger.addHandler(ch)

    # 重寫方法 AND 紀錄後清除logger
    def info(self,message=None):
        self.logger.info(self.defcontent + message)
        self.logger.removeHandler(self.logger.handlers)

    def debug(self,message=None):
        self.logger.debug(self.defcontent + message)
        self.logger.removeHandler(self.logger.handlers)

    def warning(self,message=None):
        self.logger.warning(self.defcontent + message)
        self.logger.removeHandler(self.logger.handlers)

    def error(self,message=None):
        self.logger.error(self.defcontent + message)
        self.logger.removeHandler(self.logger.handlers)

    def critical(self, message=None):
        self.logger.critical(self.defcontent + message)
        self.logger.removeHandler(self.logger.handlers)
    
    def getlog(self):
        return self.logger

if __name__ == "__main__":
    testlogger = Logger(filename="ddd", jobid="1", botid="1", method="order", logger="ticket")
    testlogger.info("YES")
    testlogger.info("YES")
    testlogger.info("YES")
    testlogger.info("YES")
    testlogger.info("YES")