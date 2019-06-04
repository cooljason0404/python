'''測試wait voucher'''
import requests, json, time
import cookie
from log import Logger
from selenium import webdriver

def getVoucherUrl(driver, waitJobid, ticketPlatform, ticketNum):
    # Load logger
    voucherlogger = Logger(ticketPlatform, waitJobid, botid='1', method='wait_voucher', logger='waitVoucher').getlog()
    voucherlogger.info("wait_vocher jobid=" + waitJobid)
    voucherlogger.info("order ticketplatform=" + ticketPlatform)
    voucherlogger.info("wait_vocher ticketNumber=" + ticketNum)

    singleorderurl = 'http://www.travelmart.com.cn/singleOrder.asp?id='
    try:
        driver.get(singleorderurl + ticketNum)
    except:
        voucherlogger.error("Don't open singleorderurl")
        return False

    try:
        voucherurl = driver.find_element_by_link_text('查看打印凭证').get_attribute('href')
    except:
        voucherlogger.error("[Voucherurl] don't find element")
        return False
        
    return voucherurl

