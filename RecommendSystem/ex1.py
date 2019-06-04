import json

for num in range(10,20):
    print(num)


predictions_info = [(1,2,10),(1,3,80)]


json_predictions = json.dumps(predictions_info)
print(json_predictions)
'''
recipe_file = open("rating.data")
recipe_data = recipe_file.read()
recipe_file.close()
#recipe_list = recipe_data.split('\n')

recipe_data.map(lambda l: l.split(',')).map(lambda l: print(int(l[0]), int(l[1]), float(l[2])))


for index, rating in enumerate(recipe_list):
    list_rating = rating.split(',')
    try:
        if int(list_rating[2]) > 100:
            print(rating)
    except:
        print(rating)
'''


'''
## Logger init
abspath = os.path.dirname(os.path.abspath(__file__))
dirpath = abspath + '/log/prediction'
filepath = dirpath + '/' + time.strftime("%Y%m%d",time.localtime()) + '.log'
if(not os.path.isdir(dirpath)):
os.mkdir(dirpath)
formatter = "[%(asctime)s] - %(filename)s - %(funcName)s [Line:%(lineno)d] - [%(levelname)s] - %(message)s"
#logging.basicConfig(level=logging.DEBUG,format=formatter,datefmt='%m-%d %H:%M',handlers=[logging.FileHandler(filepath, 'w', 'utf-8'),])

formatter = logging.Formatter(formatter)
## logger
logger = logging.getLogger("prediction")
logger.setLevel(logging.DEBUG)


## console 
#console = logging.StreamHandler(sys.stdout)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)

## file
fileHandler = logging.FileHandler(filepath)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
'''