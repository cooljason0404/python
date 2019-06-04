'''
@描述: 圖像剪裁
@創建: 2018/08/14
'''
from PIL import Image

def imagepngCrop(ticketPlatform, filename, left, top, right, bottom):
    imagepng = Image.open(filename)
    imagejpg = imagepng.crop((left, top, right, bottom))
    imagejpg.convert("RGB").save('./data/cache/captcha_' + ticketPlatform + '.jpg', 'JPEG')