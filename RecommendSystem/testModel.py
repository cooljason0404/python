import os
from collections import namedtuple
from pyspark import SparkContext, since
from pyspark.mllib.common import JavaModelWrapper, callMLlibFunc, inherit_doc
from pyspark.mllib.util import JavaLoader, JavaSaveable
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating


if __name__ == "__main__":
    abspath = os.path.dirname(os.path.abspath(__file__))

    version_file_client = open('./model/version.json')
    version_num_client = version_file_client.readline()
    version_file_client.close()

    sc = SparkContext()
    print('========= Load Rating Model =========')
    model = MatrixFactorizationModel.load(sc, "file://" + abspath + "/model/" + version_num_client + "/howtocookollaborativeFilter")


    print('========= Prediction =========')
    source = [(1497,13761), (1674,1112), (2160,22538), (2834,22418)]
    source_rdd = sc.parallelize(source)
    print(source_rdd.collect())
    predictions = model.predictAll(source_rdd).map(lambda r: ((r[0], r[1]), r[2]))

    print('#### ANS ####\n', predictions.collect())