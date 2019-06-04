'''@描述: All Bot'''
import json, requests, time
from log import Logger
from selenium import webdriver

class ticket(object):
    def __init__(self, drivers, methods, jobinfos):
        self.driver = drivers
        self.jobinfo = jobinfos
        self.method = methods
        if(methods == "cron"):
            self.productID = jobinfos['product_id']
            self.package = jobinfos['package']
            self.mallID = jobinfos['mall_id']
            self.ticketPlatform = "ctm"
            self.jobid = "cron"
            self.botid = "999"
        else:
            self.jobid = jobinfos['id']
            self.botid = "1"
            self.mall_extra = json.loads(jobinfos['mall_extra'])
            self.ticketPlatform = self.mall_extra['ticketPlatform']

            if self.method == "order":
                takeJoburl = "https://api.coolsharp.com/ticket/takeJob?id=" + self.jobid + "&bot="  + self.botid + "&type=ticket"
                jobdata = requests.get(takeJoburl).json()
                self.titlename = jobdata['data']['title']
                self.content = json.loads(jobdata['data']['content'])
            if self.method == "wait_voucher":
                self.ticketNum = jobinfos['job_context']['ticket']
            if self.method == "gen_voucher":
                self.ticketVoucherUrl = jobinfos['job_context']['ticket_voucher_url']

        self.logger = Logger(filename=self.ticketPlatform, jobid=self.jobid, botid=self.botid, method=self.method, logger='ticket')
        
    def order(self):
        import botCTM
        dictmsg = {}
        reportJoburl = "https://api.coolsharp.com/ticket/reportJob?id="
        if (self.ticketPlatform == "ctm"):
            loginstatus = botCTM.loginCTM(self.driver, self.ticketPlatform)
            if loginstatus == True:
                self.logger.info("Start Order CTM")
                dictmsg = botCTM.botCTM(self.driver, self.jobid, self.botid, self.mall_extra, self.content, self.titlename)
                if dictmsg['status'] == 'success':
                    self.logger.info("Order CTM Success")
                    reportJoburl = reportJoburl + self.jobid + "&bot=" + self.botid + "&status=success&ticket=" + dictmsg['message'] + "&msg=ok&cost=" + dictmsg['cost'] + "&currency=" + dictmsg['currency']
                elif dictmsg['status'] == 'fail':
                    self.logger.error("Order CTM Fail")
                    self.driver.save_screenshot('./data/error/error_' + self.ticketPlatform + '_' + self.jobid + '.png')
                    reportJoburl = reportJoburl + self.jobid + "&bot=" + self.botid + "&status=fail&msg=" + dictmsg['message']
                requests.get(reportJoburl)
            else:
                self.logger.error("Login Fail")
            
    def wait_voucher(self):
        import botCTM
        if self.ticketPlatform == "ctm":
            loginstatus = botCTM.loginCTM(self.driver, self.ticketPlatform)
            if loginstatus == True:
                self.logger.info("Start get voucher url")
                voucherurl = botCTM.getVoucherUrl(self.driver, self.jobid, self.ticketPlatform, self.ticketNum)
                if voucherurl == False:
                    self.logger.error("Get voucher url Fail")
                else:
                    self.logger.info("Get voucher url Success VoucherUrl = " + voucherurl)
                    reportvoucherurl = 'https://api.coolsharp.com/ticket/reportVoucherUrl?id=' + self.jobid + '&bot=' + self.botid + '&voucherUrl=' + voucherurl
                    reportvoucher = requests.get(reportvoucherurl).json()
                    if reportvoucher['code'] == 0:
                        self.logger.info("Report Voucher Url Success")
                    else:
                        self.logger.error("Report Voucher Url Fail")
            else:
                self.logger.error("Login Fail")

    def gen_voucher(self):
        import convertPDF, uploadFile
        self.logger.info("Start convertPDF")
        convertPDF.convertPDF(self.driver, self.ticketVoucherUrl, self.jobid)
        reponse = uploadFile.uploadfile(self.jobid)
        if (reponse['code'] == 0):
            self.logger.info("Upload Success" + reponse['file'])
        else:
            self.logger.error("Upload Fail")
    
    def cron(self):
        import botCTM
        dictmsg = {}
        if self.ticketPlatform == "ctm":
            reportProducturl = "http://api.coolsharp.com/ticket/reportctmInfo?mallID="
            loginstatus = botCTM.loginCTM(self.driver, self.ticketPlatform)
            if loginstatus == True:
                self.logger.info("Check CTM Product")
                dictmsg = botCTM.cronCTM(self.driver, self.productID, self.package)
                if dictmsg['status'] == 'success':
                    self.logger.info("Check CTM Product Success")
                    reportProducturl = reportProducturl + self.mallID + "&status=success&msg=ok&cost=" + dictmsg['cost'] + "&currency=" + dictmsg['currency']
                elif dictmsg['status'] == 'fail':
                    self.logger.error("Check CTM Product Fail")
                    self.driver.save_screenshot('./data/error/error_' + self.ticketPlatform + '_' + self.mallID + '.png')
                    reportProducturl = reportProducturl + self.mallID + "&status=fail&msg=" + dictmsg['message']
                requests.get(reportProducturl)
            else:
                self.logger.error("Login Fail")


def getJoblist(filters, method, limit):
    url = 'https://api.coolsharp.com/ticket/getJobList?filter=' + filters + '&method=' + method + '&limit=' + limit
    try:
        text = requests.get(url)
        joblistinfo = text.json()
    except:
        return False
    return joblistinfo

def getctmInfo():
    url = 'http://api.coolsharp.com/ticket/getctmInfo'
    try:
        text = requests.get(url)
        jobctminfo = text.json()
    except:
        return False
    return jobctminfo

if __name__ == "__main__":
    driver = webdriver.Chrome("./data/driver/chromedriver.exe") # chromedriver 路徑
    idleTime = 120
    countTime = {
        "cron":0,
        "order":0,
        "wait_voucher":0,
        "gen_voucher":0
    }
    while True:
        for mkey in countTime.keys():
            tTime = countTime.get(mkey)
            if time.time() > tTime and mkey == "cron":
                jobctminfo = getctmInfo()
                if jobctminfo != False:
                    for index, jobinfos in enumerate(jobctminfo['jobs']):
                        tickets = ticket(driver, mkey, jobinfos)
                        getattr(tickets, mkey, 'No_Method')()
                    countTime['cron'] = time.time() +  0
            elif time.time() > tTime and mkey != "cron":
                joblistinfo = getJoblist(filters="ticket", method=mkey, limit="3")
                if joblistinfo != False and len(joblistinfo['jobs']) == 0:
                    if mkey == "order":
                        countTime['order'] = time.time() +  idleTime
                    if mkey == "wait_voucher":
                        countTime['wait_voucher'] = time.time() + idleTime
                    if mkey == "gen_voucher":
                        countTime['gen_voucher'] = time.time() + idleTime
                elif joblistinfo != False and len(joblistinfo['jobs']) > 0:
                    for index, jobinfos in enumerate(joblistinfo['jobs']):
                        tickets = ticket(driver, mkey, jobinfos)
                        getattr(tickets, mkey, 'No_Method')()
                        countTime[mkey] = time.time() + idleTime
                
                            
                