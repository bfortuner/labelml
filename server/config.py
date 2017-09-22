
import os

#HOST = '24.5.150.30'
#HOST = '10.0.0.21'
HOST = 'localhost'
ENDPOINT = 'http://{:s}:5000'.format(HOST)
IMG_ENDPOINT = ENDPOINT + '/img'

PROJECT_NAME = 'udacity' #'VOC2007' #'oxfordpets'
BASE_PATH = '/Users/bfortuner/data'
PROJECT_PATH = os.path.join(BASE_PATH, PROJECT_NAME)
MEDIA_PATH = os.path.join(BASE_PATH, PROJECT_NAME, 'images')
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

PROJECT_LABELS = (
    'car', 'motorbike', 'pedestrian', 'biker'
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
