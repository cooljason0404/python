import json, requests, time, os, sys
import urllib, urllib2
from collections import namedtuple
from pyspark import SparkContext, since
from pyspark.mllib.common import JavaModelWrapper, callMLlibFunc, inherit_doc
from pyspark.mllib.util import JavaLoader, JavaSaveable
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating
from log import Logger

def runPredictionJob(logger, version_num):
    abspath = os.path.dirname(os.path.abspath(__file__))
    version_num = str(version_num).strip()
    # check model
    if (not os.path.isdir(abspath + "/model/" + version_num + "/howtocookollaborativeFilter")):
        logger.error("no search %d model"%int(version_num))
        return False
    
    # Recipe
    try:
        # recipe_network = requests.get(api_url_recipe)
        # with open('./train/recipe_prediction.data', "w") as code:
        #     code.write(recipe_network.content)
        recipe_file = open(abspath + "/train/" + version_num + "/recipe.data")
        recipe_data = recipe_file.read()
        recipe_file.close()
        recipe_list = recipe_data.split('\n')
    except:
        logger.error("no get recoipe data maybe no job queue")
        time.sleep(60)
        return False

    # device id
    api_url = 'http://api.coolsharp.com.tw/recommend/predictionJob'
    try:
        device_get = requests.get(api_url)
        device_data = device_get.json()
    except:
        logger.error("no get device ids data maybe no job queue")
        time.sleep(60)
        return False

    device_ids = device_data['user_ids']
    threshold = device_data['threshold']
    
    if device_data['c'] != 1 or device_ids == False:
        logger.error("no get device ids data")
        time.sleep(60)
        return False

    # Load model
    sc = SparkContext()
    try:
        model = MatrixFactorizationModel.load(sc, "file://" + abspath + "/model/" + version_num + "/howtocookollaborativeFilter")
    except:
        logger.error("no load model")
        return False
    
    source = []
    for index, device_id in enumerate(device_ids):
        for key, recipe_id in enumerate(recipe_list):
            if(recipe_id != '' and device_id != ''):
                source.append((int(device_id),int(recipe_id)))
    source_rdd = sc.parallelize(source)
    predictions = model.predictAll(source_rdd).map(lambda r: (r[0], r[1], r[2]))
    predictions_info = predictions.collect()

    predictions_output = predictionDataRule(logger, device_ids, predictions_info)
    output = [device_ids, predictions_output]
    sc.stop()
    logger.info("Success runPredictionJob")
    return output

def predictionDataRule(logger, device_ids, prediction_data):
    # Top 100  
    outputData = []
    for key, device_id in enumerate(device_ids):
        temp = []
        for index, prediction in enumerate(prediction_data):
            if(device_id == prediction[0]):
                temp.append(prediction)

        logger.debug(str(device_id) + " Count => " + str(len(temp)))
        count = len(temp)
        if(count > 0):
            temp.sort(key = sortSource, reverse = True)
            for index, value in enumerate(temp):
                if(index < 100):
                    outputData.append(value)

            block = count / 10
            for i in range(1,10):
                index = block * i - 1
                for before_index in range(index-5, index):
                    outputData.append(temp[before_index])
                for after_index in range(index+1, index+6):
                    outputData.append(temp[after_index])
            for i in range(count-10, count):
                outputData.append(temp[i])

    logger.debug("runPredictionJob Count => " + str(len(outputData)))  
    return outputData

def sortSource(elem):
     return elem[2]

def reportPredictionJob(logger, predictions):
    api_url = 'http://api.coolsharp.com.tw/recommend/reportPrediction'
    user_ids = []
    for index, user_id in enumerate(predictions[0]):
        user_ids.append(str(user_id))
    user_ids_str = ','.join(user_ids)
 
    # post
    output_data = { 'user_ids' : user_ids_str, 'predictions' : json.dumps(predictions[1]) }
    output_data_urlencode = urllib.urlencode(output_data)
    reposone = urllib2.Request(url = api_url, data = output_data_urlencode)
    reposone_data = urllib2.urlopen(reposone)
    info = reposone_data.read()
    logger.info(info)

def checkModelVersion(logger):
    abspath = os.path.dirname(os.path.abspath(__file__))
    try:
        version_file_mnt = open('/mnt/cifs/model/version.json')
        version_num_mnt = version_file_mnt.readline()
        version_file_mnt.close()
        version_num_mnt = str(version_num_mnt).strip()
        if(os.path.isdir(abspath + '/model/' + version_num_mnt)):
            return version_num_mnt
        else:
            logger.error("version change, synchronous")
            synchronous()
            return False
    except:
        return False

def synchronous():
    abspath = os.path.dirname(os.path.abspath(__file__))
    lock_file_path = '/mnt/cifs/synchronous.lock'
    while True:
        if (not os.path.isfile(lock_file_path)):
            os.system('rsync -vzrtopg --progress --delete /mnt/cifs/train ' + abspath)
            os.system('rsync -vzrtopg --progress --delete /mnt/cifs/model ' + abspath)
            break

if __name__ == "__main__":
    logger = Logger(work="prediction")
    logger1 = Logger(work="")
    while True: 
        version_num = checkModelVersion(logger)
        if version_num != False :
            latest_time = time.time()
            predictions = runPredictionJob(logger, version_num)
            latest_time = time.time() - latest_time
            if predictions != False :
                logger1.info("Prediction time : " + str(latest_time))
                reportPredictionJob(logger, predictions)
        else:
            break
