'''
@描述: 驗證碼辨識 載入神經網路模型
@創建: 2018/08/14
'''
from keras.models import load_model, Model
import numpy as np
from PIL import Image

def to_text(int):
    dic10 = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9}
    text = []
    text.append(list(dic10.keys())[list(dic10.values()).index(int)])
    return "".join(text)

def captchaIdentify(ticketPlatform):   
    model = load_model("./data/model/model_" + ticketPlatform + ".hdf5") # load 建立好的模型
    prediction = model.predict(np.stack([np.array(Image.open('./data/cache/captcha_' + ticketPlatform + '.jpg'))/255.0]))
    answer = ""
    for predict in prediction:
        answer += to_text(np.argmax(predict[0]))
    return answer