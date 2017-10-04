
import os

# #HOST = '24.5.150.30'
# HOST = '10.0.0.21'
# HOST = 'localhost'


PROJECT_NAME = 'example_data' #'VOC2007' #'oxfordpets'
BASE_PATH = '' #'/bigguy/data' #'/Users/bfortuner/data'
PROJECT_PATH = os.path.join(BASE_PATH, PROJECT_NAME)
MEDIA_PATH = os.path.join(BASE_PATH, PROJECT_NAME, 'images')
print(MEDIA_PATH)
# DEFAULT_LABELS = (
#     'aeroplane', 'bicycle', 'bird', 'boat',
#     'bottle', 'bus', 'car', 'cat', 'chair',
#     'cow', 'diningtable', 'dog', 'horse',
#     'motorbike', 'person', 'pottedplant',
#     'sheep', 'sofa', 'train', 'tvmonitor')

DEFAULT_LABELS = (
    'aeroplane', 'biker', 'bird', 'boat',
    'bottle', 'bus', 'car', 'cat', 'chair',
    'cow', 'diningtable', 'dog', 'horse',
    'motorbike', 'pedestrian', 'pottedplant',
    'sheep', 'sofa', 'truck', 'trafficlight')

# PROJECT_LABELS = (
#     'car', 'motorbike', 'pedestrian', 'biker'
# )
PROJECT_LABELS = (
    'car', 'trafficlight', 'biker'
)

METRICS_FNAME = 'metrics.json'
FOLD_FNAME = 'labels.json'
PREDS_FNAME = 'predictions.json'
RANKINGS_FNAME = 'rankings.csv'

TRAIN = 'trn'
VAL = 'val'
TEST = 'tst'
UNLABELED = 'unlabeled'

IMG_EXT = '.jpg'

DEFAULT_WIDTH = 300
DEFAULT_HEIGHT = 300
BATCH_SIZE = 12
VAL_FOLD_RATIO = 0.2


class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID', 'password')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'password')
    AWS_REGION='us-west-1'

class ProdConfig(Config):
    ENDPOINT = 'http://labelml.wfcpkpjahu.us-west-1.elasticbeanstalk.com'
    DEBUG = False

class DevConfig(Config):
    ENDPOINT = 'http://localhost:5000'
    DEBUG = True

#config = globals()[os.getenv('LABELML_ENV', 'ProdConfig')]
env = os.getenv('LABELML_ENV', 'prod')
print ("ENV " + env)
if env == 'prod':
    ENDPOINT = ProdConfig.ENDPOINT
else:
    ENDPOINT = DevConfig.ENDPOINT

# ENDPOINT = 'http://labelml.wfcpkpjahu.us-west-1.elasticbeanstalk.com'
IMG_ENDPOINT = ENDPOINT + '/img'
print("IMG", IMG_ENDPOINT)