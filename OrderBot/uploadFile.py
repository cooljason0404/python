'''
@描述:Upload File
@創建:2018/08/22
'''
import requests

def uploadfile(jobid):
    url = 'https://api.coolsharp.com/ticket/reportGenerateVoucherJob'
    data = {'id':jobid, 'bot':'1'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    files = {'voucher' : ('file', open("./data/voucher/ticketVoucher_" + jobid + ".pdf", 'rb'), "application/pdf", headers)}
    reponse = requests.post(url, data=data, files=files)
    reponsetext = reponse.json()
    return reponsetext