import os.path
import array
import datetime
import urllib2

from collections import namedtuple
from pyspark import SparkContext, since
from pyspark.mllib.common import JavaModelWrapper, callMLlibFunc, inherit_doc
from pyspark.mllib.util import JavaLoader, JavaSaveable
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating

def main():
    sc = SparkContext()
    try:
        a = datetime.datetime.now()
        model = MatrixFactorizationModel.load(sc, "target/howtocookollaborativeFilter")
        b = datetime.datetime.now()
        c = b - a
        print '========= Load Rating Model %d.%d =========' % (c.seconds, c.microseconds)
    except:
        print '========= Calc Ratings ========='
        ## CSV file contains user, product, rank each rows
        data = sc.textFile("file:///mnt/spark-workspace/recommendation/20190116_spark_30.data")
        # data = sc.textFile("file:///mnt/spark-workspace/recommendation/data.txt")
        # data = sc.textFile("data/mllib/als/test.data")
        ratings = data.map(lambda l: l.split(',')).map(lambda l: Rating(int(l[0]), int(l[1]), float(l[2])))
        # Build the recommendation model using Alternating Least Squares
        rank = 100
        numIterations = 10
        model = ALS.train(ratings, rank, numIterations)
        print '========= Calc Complete ========='
        '''
        # Evaluate the model on training data
        testdata = ratings.map(lambda p: (p[0], p[1]))
        predictions = model.predictAll(testdata).map(lambda r: ((r[0], r[1]), r[2]))

        ratesAndPreds = ratings.map(lambda r: ((r[0], r[1]), r[2])).join(predictions)
        MSE = ratesAndPreds.map(lambda r: (r[1][0] - r[1][1])**2).mean()
        print("@@@@ Mean Squared Error = " + str(MSE))
        '''
        model.save(sc, "target/howtocookollaborativeFilter")

    print '========= Prediction ========='

    a = datetime.datetime.now()
    # source = [(1497,13761,100), (1674,1112,2), (2160,22538,14), (2834,22418,18)]
    source = [(1497,13761), (1674,1112), (2160,22538), (2834,22418)]
    source_rdd = sc.parallelize(source)
    predictions = model.predictAll(source_rdd).map(lambda r: ((r[0], r[1]), r[2]))
    b = datetime.datetime.now()
    c = b - a
    print '========= Prediction cost: %d.%d =========' % (c.seconds, c.microseconds)
    print '####', predictions.take(4)


    ## Save and load model
    # model.save(sc, "target/howtocookollaborativeFilter")
    # sameModel = MatrixFactorizationModel.load(sc, "target/tmp/myCollaborativeFilter")

if __name__ == "__main__":

    content = urllib2.urlopen('https://www.google.com').read()
    print content
    # main()
