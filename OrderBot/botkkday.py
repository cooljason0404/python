'''@描述: All Bot ex1'''
import json, requests, time
from log import Logger
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

def loginKKday(driver):
    username = ""
    password = ""
    loginurl = "https://www.kkday.com/zh-tw/"
    logouturl = "https://www.kkday.com/zh-tw/member/logout?backurl=https://www.kkday.com/zh-tw"
    driver.get(logouturl)
    driver.get(loginurl)
    try:
        driver.find_element_by_id("btn-account-login").click()
    except:
        pass
    time.sleep(0.5)
    try:
        driver.find_element_by_id("loginEmail").send_keys(username)
        driver.find_element_by_id("loginPassword").send_keys(password)
    except:
        pass
    driver.find_element_by_id("loginBtn").click()
    try:
        driver.find_element_by_id("header-main-sidenav-button")
        loginstatus = True
    except:
        loginstatus = False
    return loginstatus

def botKKday(driver, dictinfo):
    # Load logger
    botkkdaylogger = Logger(filename='kkday', jobid='1', botid='1', method='order', logger='botkkday')
    botkkdaylogger.info("order start.")

    producturl = "https://www.kkday.com/zh-tw/product/4885"
    driver.get(producturl)

    # Step 1
    driver.execute_script("$('.has-datepicker').removeAttr('readonly')") # 移除readonly
    try:
        driver.find_element_by_class_name('has-datepicker').send_keys(dictinfo['dpdate'])
        driver.find_element_by_class_name('has-datepicker').send_keys(Keys.ENTER)
        driver.find_element_by_class_name('has-datepicker').click()
        driver.find_element_by_xpath('//td[contains(@class,"start-date") and contains(@class,"end-date")]').click()
    except:
        botkkdaylogger.error("Step1 depaturedate")
    time.sleep(0.5)
    try:
        driver.find_elements_by_class_name('select-option')[0].click()
    except:
        botkkdaylogger.error("Step1 NotFindSelectButton")
    time.sleep(0.5)
    driver.find_elements_by_class_name('icon-plus')[0].click()
    time.sleep(0.5)
    driver.find_element_by_xpath('//*[@id="booking-bar"]/div/div[1]/div[3]/button[2]').click()

    # Step 2 填寫旅客資料
    driver.find_element_by_id('board1_btn').click()
    try:
        driver.find_element_by_xpath('//*[@id="board2"]/div[2]/div[1]/div[2]/div[1]/div/input').send_keys(dictinfo['Firstname'])
        driver.find_element_by_xpath('//*[@id="board2"]/div[2]/div[1]/div[2]/div[2]/div/input').send_keys(dictinfo['Lastname'])
        selectgender = Select(driver.find_element_by_xpath('//*[@id="board2"]/div[2]/div[1]/div[2]/div[3]/div/select'))
        selectgender.select_by_value(dictinfo['gender'])
    except:
        botkkdaylogger.error("Step2 NotFind travel input")

    try:
        driver.execute_script("$('.has-datepicker').removeAttr('readonly')")
        driver.find_element_by_class_name('has-datepicker').send_keys(dictinfo['borndate'])
        driver.find_element_by_class_name('has-datepicker').send_keys(Keys.ENTER)
        driver.find_element_by_class_name('has-datepicker').click()
        driver.find_element_by_class_name('end-date').click()
    except:
        botkkdaylogger.error("Step2 NotFindBorndate")
    time.sleep(0.5)
    try:
        driver.find_element_by_xpath('//*[@id="board2"]/div[2]/div[1]/div[4]/div/div/input').send_keys(dictinfo['passport'])
        driver.find_element_by_id('board2_btn').click()
    except:
        botkkdaylogger.error("Step2 NotFindElements")
    
    driver.find_element_by_name('payment').click()
    time.sleep(0.5)
    try:
        driver.find_element_by_xpath('//*[@id="board3"]/div[2]/ul/li[1]/div[2]/div[2]/div/div/input').send_keys('XXXX') # 持可人
        driver.find_element_by_xpath('//*[@id="board3"]/div[2]/ul/li[1]/div[2]/div[3]/div[1]/div/input').send_keys('1234123412341234') # 信用卡號碼
        driver.find_element_by_xpath('//*[@id="board3"]/div[2]/ul/li[1]/div[2]/div[3]/div[2]/div/input').send_keys('05/22') # 有效期限
        driver.find_element_by_xpath('//*[@id="board3"]/div[2]/ul/li[1]/div[2]/div[3]/div[3]/div/input').send_keys('144') # CSV/CVV
        #driver.find_element_by_class_name('btn-primary').click()
        return True
    except:
        pass

if __name__=="__main__":
    driver = webdriver.Chrome("./data/driver/chromedriver.exe") # chromedriver 路徑
    dictinfo = {
        'Firstname':'',
        'Lastname':'',
        'borndate':'',
        'dpdate':'2018/09/20',
        'gender':'M',
        'passport':'1234567890'
    }
    if loginKKday(driver) == True:
        driver.maximize_window()
        orderstatus = botKKday(driver, dictinfo)
        print(orderstatus)
    else:
        print(False)
    