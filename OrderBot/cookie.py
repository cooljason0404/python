'''
@描述: Load and Save Cookie
@創建: 2018/08/17
'''
import json

def loadcookie (ticketPlatform):
    try:
        cookiefile = open('./data/cookie/cookie_' + ticketPlatform +'.txt')
        cookie = cookiefile.read()
        cookie = json.loads(cookie)
        cookiefile.close()
        return cookie
    except:
        return "fail"

def savecookie (tickePlatform, cookie):
    cookiefile = open('./data/cookie/cookie_' + tickePlatform + '.txt', 'w')
    cookiefile.write(json.dumps(cookie))
    cookiefile.close