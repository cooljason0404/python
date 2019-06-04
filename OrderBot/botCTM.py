'''@描述: CTM 訂購機器人'''
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
import time, json
from log import Logger
import sys

flag_bug = False

def loginCTM(driver, ticketPlatform):
    import cookie
    if flag_bug :
        # Account 測試
        username = ''
        password = ''
    else:   
        # Account 真實
        username = ''
        password = ''
    # Load logger
    loginlogger = Logger(ticketPlatform, jobid='login', botid='1', method='login', logger='login')

    #------------------------------------直接進入------------------------------------
    driver.get("http://www.travelmart.com.cn/hotelsearch.asp")
    if username in driver.page_source:
        loginlogger.info("login is success")
        return True
 
    #------------------------------------使用Cookie------------------------------------
    cookies = cookie.loadcookie(ticketPlatform)
    if cookies == 'fail':
        loginlogger.error("[cookie] Don't load cookie file")
    else:
        for text in cookies:
            driver.add_cookie(text)
        driver.refresh()
    
    driver.get("http://www.travelmart.com.cn/hotelsearch.asp")
    if username in driver.page_source:
        loginlogger.info("[cookie] sing in is success")
        return True
    else:
        # Fault inject cookie
        loginlogger.error("[cookie] sing in is fail")
        loginlogger.info("[account] go to sing in")

    #------------------------------------使用帳密登入------------------------------------
    import captchaIdentify, imageCrop
    driver.get("http://www.travelmart.com.cn/logout.asp")
    loginstatus = False
    try:
        driver.find_element_by_name('username').send_keys(username)
        driver.find_element_by_name('password').send_keys(password)   
    except:
        loginlogger.error("error NotFindElement Account")
        return loginstatus 

    loginlogger.info("Get Capthca code")
    # 取得驗證碼
    driver.save_screenshot('./data/cache/tmp_' + ticketPlatform + '.png')
    pass_code = driver.find_element_by_tag_name('img')
    left = pass_code.location['x']
    right = pass_code.location['x'] + pass_code.size['width']
    top = pass_code.location['y']
    bottom = pass_code.location['y'] + pass_code.size['height']
    imageCrop.imagepngCrop(ticketPlatform, './data/cache/tmp_' + ticketPlatform + '.png', left, top, right, bottom) # Crop Image
    captchanum = captchaIdentify.captchaIdentify(ticketPlatform) # 驗證碼辨識

    try:
        driver.find_element_by_name('verify').send_keys(captchanum)
        driver.find_element_by_name('smit').click()
    except:
        loginlogger.error("error NotFindElement")
        return loginstatus
        
    if username in driver.page_source: # Sing in success
        loginstatus = True
        loginlogger.info("Sucess")
        time.sleep(1)
        # Save cookie
        cookies = driver.get_cookies()
        cookie.savecookie(ticketPlatform, cookies)
        loginlogger.info("Save account cookie please waiting") 
    else:
        loginlogger.error("Fail")
    return loginstatus
            
def botCTM(driver, jobid, botid, mall_extra, content, titlename):
    dictmessage = {'message':'', 'status':'fail', 'cost':'0', 'currency':'USD'} # return infomation
    content['date'].split('/') # date format
    # Order information
    dictorderinfo = { 
        'productid':mall_extra['ticketPlatformParams'], 
        'bdt':content['date'].split('/')[0] + "-" + content['date'].split('/')[1] + "-" + content['date'].split('/')[2], 
        'emAmount':'1',
        'adultLN':content['last_name'], 
        'adultFN':content['first_name'], 
        'gender':'男', 
        'phone':content['tel'],
        'passport':content['passport'], 
        'countryCode':content['country_code'],
        'email':content['email']
    }
    ticketPlatform = mall_extra['ticketPlatform']

    # Load logger
    botctmlogger = Logger(ticketPlatform, jobid, botid, method='order', logger='botctm')
    botctmlogger.info("order start.")
    
    #-------------------------------Start Order-------------------------------------------
    # 檢查 產品ID 出發日 資訊是否取得
    if((dictorderinfo['productid']=="") or (dictorderinfo['bdt']=="")):
        botctmlogger.error("[Order Page] Productid or datetime error")
        dictmessage['message'] = 'Productid and datetime can not empty'
        return dictmessage['message']

    botctmlogger.info("Webdriver go to order page")
    #--------------------------------打開產品訂購頁--------------------------------
    url_list = {
        "old" : 'http://www.travelmart.com.cn/tourdetails.asp?id=',
        "new" : 'http://www.travelmart.com.cn/groundservice/detail.asp?id='
    }
    productType = ""
    for index in url_list.keys():
        url = url_list.get(index)
        productType = index
        if(index == "old"):
            url = url + dictorderinfo['productid'] + '&bdt=' + dictorderinfo['bdt']
        else:
            ticketPackage = mall_extra['ticketPackage']
            url = url + dictorderinfo['productid']
        driver.get(url)
        time.sleep(0.5)
        if dictorderinfo['productid'] in driver.page_source:
            break
    else:
        botctmlogger.error("[Order Page] fault")
        dictmessage['message'] = 'NotFindProduct'
        return dictmessage['message']
    
    botctmlogger.info("[Order Page] success")
    time.sleep(1)
    if(productType == "old"):
        #-----------------------------------------Step1----------------------------------------
        # 出發日判斷是否可訂票
        btd = driver.find_element_by_id('BDT').get_attribute('value')
        btdtext = btd.split(' ')[0]
        if (btdtext != dictorderinfo['bdt']):
            msg = "[Step1 Old] error Not have date"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
            return dictmessage

        try:
            Select(driver.find_element_by_id('emPrice')).select_by_value(dictorderinfo['emAmount'])# 成人票數 id=emPrice
        except:
            Select(driver.find_element_by_id('emPrice1')).select_by_value(dictorderinfo['emAmount'])# 小童

        # 抓取價格
        try:
            cost = driver.find_element_by_id('totalprice').text
            dictmessage['cost'] = cost
            botctmlogger.info("[Step1 Old] cost:" + dictmessage['cost'])
        except:
            botctmlogger.error("[Step1 Old] cost: Don't Find")
        
        try:
            currency_str = driver.find_element_by_id('submitTour').get_attribute('textContent')
            currency_list = ['USD','RMB','TWD']
            i = 0
            for index, currency_name in enumerate(currency_list) :
                if(currency_str.find(currency_name) != -1) :
                    i = index
                    break
            dictmessage['currency'] = currency_list[i]
            botctmlogger.info("[Step1 Old] currency:" + dictmessage['currency'])
        except:
            botctmlogger.error("[Step1 Old] currency: Don't Find")
        
        '''
        if flag_bug:
            dictmessage['message'] = 'SKE000288895'
            dictmessage['status'] = 'success'
            return dictmessage
            #sys.exit()
        '''

        try:
            driver.find_element_by_id('submit').submit() # Order Btn id=submit
        except:
            msg = "[Step1 Old] error NotFind Element"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
            return dictmessage

        if dictorderinfo['productid'] in driver.page_source:
            botctmlogger.info("[Step1] success")
        else:
            msg = "[Step1 Old] error"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
            return dictmessage

        
        #-----------------------------Step2 預定--------------------------------------------------
        # Name Gender cellphone
        time.sleep(0.5)
        try:
            driver.find_element_by_name('adultLastName').send_keys(dictorderinfo['adultLN'])
            driver.find_element_by_name('adultFirstName').send_keys(dictorderinfo['adultFN'])
            driver.find_element_by_name('AdultGender').send_keys(dictorderinfo['gender'])
        except:
            driver.find_element_by_name('childLastName').send_keys(dictorderinfo['adultLN'])
            driver.find_element_by_name('childFirstName').send_keys(dictorderinfo['adultFN'])
            driver.find_element_by_name('ChildGender').send_keys(dictorderinfo['gender'])
        try:
            driver.find_element_by_name('country_phone_area_no').clear()
            driver.find_element_by_name('country_phone_area_no').send_keys(dictorderinfo['countryCode'])
            driver.find_element_by_name('B2CTel').send_keys(dictorderinfo['phone'])
        except:
            msg = "[Step2 Old] error NotFindElement Phone"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
        try:
            driver.find_element_by_class_name('btn1').submit()
        except:
            msg = "[Step2 Old] error NotFindElement Submit"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
            return dictmessage

        botctmlogger.info("[Step2 Old] success")
        
        #------------------------------------------------Step3------------------------------------------------
        time.sleep(5)
        botctmlogger.info("[Step3 Old] success")

        #------------------------------------------------Step4------------------------------------------------
        # Check Order Success True
        try:
            dictmessage['message'] = driver.find_elements_by_partial_link_text('SKE')[0].text
        except:
            msg = "[Step4 Old] error NotFindElement"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
            return dictmessage     

    else:
        #NEW
        #------------------------------------------------Step1 查詢------------------------------------------------
        try:
            elements = driver.find_elements_by_tag_name('a')
            i = -1
            for index, element in enumerate(elements) :
                if(element.get_attribute('textContent') == ticketPackage):
                    i = index
                    break
            elements[i].click()
        except:
            msg = "[Step1 New] error Not have ticketPackage"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
            return dictmessage

        time.sleep(1)
        try:
            driver.execute_script('document.getElementById("price_calendar").removeAttribute("readonly")')
            driver.find_element_by_id('price_calendar').send_keys(dictorderinfo['bdt'])
        except:
            msg = "[Step1 New] error Not have date"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
            return dictmessage
        
        # 抓取價格
        time.sleep(1)
        try:
            Select(driver.find_elements_by_name("select-num")[0]).select_by_value("1")
            cost = driver.execute_script('var text = document.getElementsByName("price-P1")[0].textContent; return text;')
            dictmessage['cost'] = cost
            botctmlogger.info("[Step1 New] cost:" + dictmessage['cost'])
        except:
            botctmlogger.error("[Step1 New] cost: Don't Find")

        try:
            currency_str = driver.find_element_by_id('book-detail-area').get_attribute('textContent')
            currency_list = ['USD','RMB','TWD']
            i = 0
            for index, currency_name in enumerate(currency_list) :
                if(currency_str.find(currency_name) != -1) :
                    i = index
                    break
            dictmessage['currency'] = currency_list[i]
            botctmlogger.info("[Step1 New] currency:" + dictmessage['currency'])
        except:
            botctmlogger.error("[Step1 New] currency: Don't Find")
        time.sleep(1)
        # 確認
        try:
            driver.execute_script('document.getElementsByClassName("gs-product-booking-btn")[0].click();')
        except:
            msg = "[Step1 New] error NotFind Element"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
            return dictmessage
        time.sleep(1)

        #------------------------------------------------Step2 檢查------------------------------------------------
        if dictorderinfo['bdt'] in driver.page_source:
            botctmlogger.info("[Step1 New] success")
        else:
            botctmlogger.error("[Step1 New] error")
            dictmessage['message'] = '[Step1 New] error'
            return dictmessage

        # Step2 輸入名字email
        try:
            driver.find_element_by_name('isLeader1').click()
            driver.find_element_by_name('surnameEn').send_keys(dictorderinfo['adultLN'])
            driver.find_element_by_name('givenNameEn').send_keys(dictorderinfo['adultFN'])
            driver.find_element_by_name('leaderConfirmEmail').send_keys(dictorderinfo['email'])
        except:
            msg = "[Step2 New] 元素填放位置失敗"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
        #sys.exit()

        # Step2 確認點擊
        try:
            driver.find_element_by_class_name('submit-order-btn').click()
            time.sleep(1)
            driver.execute_script('document.getElementsByClassName("gs-product-booking-btn")[1].click();')
        except:
            msg = "[Step2 New] Submit Btn 找不到"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
            return dictmessage

        time.sleep(10)
        alertView = Alert(driver)
        if(alertView.text == "预定成功"):
            alertView.accept()
            botctmlogger.info("[Step2 New] 預定成功")
        else:
            alertView.accept()
            botctmlogger.error("[Step2 New] 預定失敗")


        time.sleep(3)
        #------------------------------------------------Step3------------------------------------------------
        # Check Order Success True
        if "SKE" in driver.page_source:
            # 取出訂單編號
            urlStr = driver.current_url
            dictmessage['message'] = urlStr.replace("http://www.travelmart.com.cn/otherorderdetail.asp?bno=", "");
        else:
            msg = "[Step3 New] 訂單失敗"
            botctmlogger.error(msg)
            dictmessage['message'] = msg
            return dictmessage

    #------------------------------------------------回傳訂單編號------------------------------------------------
    botctmlogger.info("訂單成功 訂單編號:" + dictmessage['message'])
    dictmessage['status'] = 'success'
    return dictmessage

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
        
def cronCTM(driver, productID, package):
    dictRepInfo = {'message':'', 'status':'fail', 'cost':'0', 'currency':'USD'} # return infomation
    
    url_list = [
        'http://www.travelmart.com.cn/tourdetails.asp?id=',
        'http://www.travelmart.com.cn/groundservice/detail.asp?id='
    ]
    key = 0;
    for index, url in enumerate(url_list):
        driver.get(url + productID)
        time.sleep(0.5)
        if productID in driver.page_source:
            key = index
            break
    else:
        dictRepInfo['message'] = "Don't Find proudct"
        return dictRepInfo

    
    # 抓取價格 && 貨幣名
    time.sleep(1)
    if key==0:
         # old
        try:
            cost = driver.find_element_by_id('totalprice')
            dictRepInfo['cost'] = cost.text
        except:
            dictRepInfo['message'] = "Don't Find cost"
            return dictRepInfo

        try:
            inContentfrom = driver.find_element_by_id('submitTour')
            currency_str = inContentfrom.get_attribute('textContent')
            currency_list = ['USD','RMB','TWD']
            i = 0
            for index, currency_name in enumerate(currency_list) :
                if(currency_str.find(currency_name) != -1) :
                    i = index
                    break
            dictRepInfo['currency'] = currency_list[i]
        except:
            dictRepInfo['message'] = "Don't Find currency"
            return dictRepInfo

    else:
        # new
        try:
            elements = driver.find_elements_by_tag_name('a')
            i = -1
            for index, element in enumerate(elements) :
                if(element.get_attribute('textContent') == package):
                    i = index
                    break
            elements[i].click()
        except:
            dictRepInfo['message'] = "Don't Find ticketPackage"

        time.sleep(1)
        try:
            driver.execute_script('document.getElementsByName("select-num")[0].value="1";')
            cost = driver.execute_script('var text = document.getElementsByName("price-P1")[0].textContent; return text;')
            dictRepInfo['cost'] = cost
        except:
            dictRepInfo['message'] = "Don't Find cost"
            return dictRepInfo

        try:
            inContentfrom = driver.find_element_by_id('book-detail-area')
            currency_str = inContentfrom.get_attribute('textContent')
            currency_list = ['USD','RMB','TWD']
            i = 0
            for index, currency_name in enumerate(currency_list) :
                if(currency_str.find(currency_name) != -1) :
                    i = index
                    break
            dictRepInfo['currency'] = currency_list[i]
            dictRepInfo['status'] = "success"
        except:
            dictRepInfo['message'] = "Don't Find currency"
            return dictRepInfo

    dictRepInfo['status'] = 'success'
    return dictRepInfo
    


# 單一測試
if __name__ == "__main__":
    mall_extra = {
        'ticketPlatformParams':'LXS012h082',
        'ticketPlatform':'ctm'
    }
    content = {
        'date':'2018/10/26',
        'last_name':'',
        'first_name':'',
        'tel':'',
        'passport': '0123456789',
        'country_code': '886'
    }
    driver = webdriver.Chrome("./data/driver/chromedriver.exe") # chromedriver 路徑
    check = loginCTM(driver,'ctm')
    if (check == True):
        botstatus = botCTM(driver, jobid='123', botid='1', mall_extra=mall_extra, content=content, titlename='LXS012h082')
    