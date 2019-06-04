'''
@描述: webpage 轉換成 pdf文件
@創建: 2018/08/22
'''
from selenium import webdriver
import uploadFile

def convertPDF(driver, voucherurl, jobid):
    import pdfkit
    options = { 'encoding':"UTF-8", 
                'no-background':None, 
                'exclude-from-outline':None,
                'margin-bottom': '10mm',
                'margin-top':'10mm'
                }
    config = pdfkit.configuration(wkhtmltopdf= r"./data/driver/wkhtmltopdf.exe") # wkhtmltopdf path
    #driver = webdriver.Chrome("./data/driver/chromedriver.exe") # chromedriver path
    driver.get(voucherurl)
    textcss = driver.find_element_by_xpath("//style[@media='screen']").get_attribute("outerHTML")
    textcss += '<style type="text/css">div{margin:auto;page-break-inside:avoid;}</style>'
    texthtml = driver.find_element_by_xpath("//div[@class='ticket-summary']").get_attribute("outerHTML") 
    texthtml += driver.find_element_by_xpath("//div[@class='mhl']").get_attribute("outerHTML")
    texthtml = textcss + texthtml
    pdfkit.from_string(texthtml,"./data/voucher/ticketVoucher_" + jobid + ".pdf",configuration=config,options=options)


# Test
#convertPDF('http://r.tour-mall.cn/AMU8CW9c754986ef84a59','7662')
#uploadFile.uploadfile('7662')
