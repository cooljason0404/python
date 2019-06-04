import requests, time
import os, shutil
from collections import namedtuple
from pyspark import SparkContext, since
from pyspark.mllib.common import JavaModelWrapper, callMLlibFunc, inherit_doc
from pyspark.mllib.util import JavaLoader, JavaSaveable
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating
from log import Logger

def runTrainJob(logger ,version_code):
    sc = SparkContext()
    abspath = os.path.dirname(os.path.abspath(__file__))
    try:
        data = sc.textFile("file://" + abspath + "/train/" + version_code + "/rating.data");
    except:
        logger.error("[error] no get recoipe data maybe no job queue")
        return False
     
    ratings = data.map(lambda l: l.split(',')).map(lambda l: Rating(int(l[0]), int(l[1]), float(l[2])))
    rank = 100
    numIterations = 15
    model = ALS.train(ratings, rank, numIterations)
    model.save(sc, abspath + "/model/" + version_code + "/coolsharpollaborativeFilter")

    version_file = open(abspath + '/model/version.json', 'w')
    version_file.write(version_code)
    version_file.close()
    
    sc.stop()
    return True

def version(logger):
    api_url = "http://api.coolsharp.com.tw/recommend/versionV2"
    try:
        version_get = requests.get(api_url)
        version_data = version_get.json()
    except:
        logger.error("version api error")
        time.sleep(60)
        return False
    
    if(version_data['c'] != 1):
        logger.error("version api fail")
        time.sleep(60)
        return False
    
    result = version_data['result']
    latest = str(result['latest'])

    api_download_url = {
        'recipe' : result[latest]['recipes'], 
        'rating' : result[latest]['train']
    }
    data = {
        'version' : latest,
        'url' : api_download_url
    }
    return data

def downloadData(version_code, api_download_url):
    abspath = os.path.dirname(os.path.abspath(__file__))
    dirpath = abspath + '/train/' + version_code
    if(not os.path.isdir(dirpath)):
        # create dir
        os.mkdir(dirpath)

        # get data
        for filename in api_download_url.keys():
            url = api_download_url.get(filename)
            r = requests.get(url)
            # save local
            with open(dirpath + '/' + filename + '.data', "w") as code:
                code.write(r.content)

        # record version
        version_file = open(abspath + '/train/version.json', 'w')
        version_file.write(version_code)
        version_file.close()

        return True
    else:
        time.sleep(60)
        return False


def synchronous():
    abspath = os.path.dirname(os.path.abspath(__file__))
    lock_file_path = '/mnt/cifs/synchronous.lock'
    lock_file = open(lock_file_path, 'w')
    lock_file.close()
    os.system('rsync -vzrtopg --progress --delete ' + abspath + '/train /mnt/cifs')
    os.system('rsync -vzrtopg --progress --delete ' + abspath + '/model /mnt/cifs')
    try:
        os.remove(lock_file_path)
    except OSError as e:
        print(e)

def deleteOldData(version_code):
    abspath = os.path.dirname(os.path.abspath(__file__))
    trainList = os.listdir(abspath + '/train/')
    for dirname in trainList:
        if(dirname != 'version.json' and dirname != version_code):
            shutil.rmtree(abspath + '/train/' + dirname)

    modelList = os.listdir(abspath + '/model/')
    for dirname in modelList:
        if(dirname != 'version.json' and dirname != version_code): 
            shutil.rmtree(abspath + '/model/' + dirname)
    

if __name__ == "__main__":
    logger = Logger(work="train")
    logger1 = Logger(work="")
    while True:
        latest_version = version(logger)
        if(latest_version != False):
            latest_version_code = latest_version['version']
            logger.info("latest version code : " + latest_version_code)
            if(downloadData(latest_version_code, latest_version['url'])):
                latest_time = time.time()
                if(runTrainJob(logger, latest_version_code)):
                    latest_time = time.time() - latest_time
                    logger1.info("Train time : " + str(latest_time))
                deleteOldData(latest_version_code)
                synchronous()