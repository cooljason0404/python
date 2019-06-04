import time, os
import sys
import logging
import traceback

class Logger():
    def __init__(self, work):
        abspath = os.path.dirname(os.path.abspath(__file__))
        dirpath = abspath + '/log/' + work
        logger = "Spark"

        # log filename 
        filepath = dirpath + '/' + time.strftime("%Y%m%d",time.localtime()) + '.log'
        self.formatter = logging.Formatter('[%(asctime)s] - %(filename)s - %(module)s - %(funcName)s [Line:%(lineno)d] - [%(levelname)s] - %(message)s')

        if(not os.path.isdir(dirpath)):
            os.mkdir(dirpath)
        
        # Create logger
        self.logger = logging.getLogger(logger)
        logging.Logger.manager.loggerDict.pop(logger)
        self.logger.handlers = []
        self.logger.removeHandler(self.logger.handlers)

        if(not self.logger.handlers):
            self.handler = logging.FileHandler(filepath)
            self.logger.setLevel(logging.DEBUG)
            self.handler.setFormatter(self.formatter)
            self.logger.addHandler(self.handler)
            ch = logging.StreamHandler(sys.stdout) 
            ch.setLevel(logging.DEBUG) 
            ch.setFormatter(self.formatter) 
            self.logger.addHandler(ch)

    def info(self,message=None):
        self.logger.info(message)
        self.logger.removeHandler(self.logger.handlers)

    def debug(self,message=None):
        self.logger.debug(message)
        self.logger.removeHandler(self.logger.handlers)

    def warning(self,message=None):
        self.logger.warning(message)
        self.logger.removeHandler(self.logger.handlers)

    def error(self,message=None):
        self.logger.error(message)
        self.logger.removeHandler(self.logger.handlers)

    def critical(self, message=None):
        self.logger.critical(message)
        self.logger.removeHandler(self.logger.handlers)
    
    def getlog(self):
        return self.logger

if __name__ == "__main__":
    testlogger = Logger(work="ddd")
    while True:
        testlogger.error("YES")
        testlogger.info("YES")
        testlogger.info("YES")
        testlogger.info("YES")
        testlogger.info("YES")