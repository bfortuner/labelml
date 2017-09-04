
import os

ENDPOINT = 'http://24.5.150.30:5000'
#ENDPOINT = 'http://10.0.0.21:5000'
IMG_ENDPOINT = ENDPOINT + '/image'

PROJECT_PATH = '/bigguy/data/dogscats'
MEDIA_PATH = PROJECT_PATH + '/datasets/inputs/trn_jpg'
LABEL_PATH = os.path.join(PROJECT_PATH, 'labels') 
PROJECT_NAME = 'test_project'
PROJECT_PATH = os.path.join(LABEL_PATH, PROJECT_NAME)
METADATA_FPATH = os.path.join(PROJECT_PATH, 'metadata.csv')

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
