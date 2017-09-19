
import os

#ENDPOINT = 'http://24.5.150.30:5000'
ENDPOINT = 'http://localhost:5000'
IMG_ENDPOINT = ENDPOINT + '/img'

PROJECT_NAME = 'VOC2007' #'oxfordpets'
BASE_PATH = '/Users/bfortuner/data' #'/Users/bfortuner/workplace/data/VOC2007'
PROJECT_PATH = os.path.join(BASE_PATH, PROJECT_NAME)
MEDIA_PATH = os.path.join(BASE_PATH, PROJECT_NAME, 'images')
DEFAULT_LABELS = (
    'aeroplane', 'bicycle', 'bird', 'boat',
    'bottle', 'bus', 'car', 'cat', 'chair',
    'cow', 'diningtable', 'dog', 'horse',
    'motorbike', 'person', 'pottedplant',
    'sheep', 'sofa', 'train', 'tvmonitor')

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
