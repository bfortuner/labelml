import os
import random
from collections import namedtuple, OrderedDict
import pandas as pd
from graphql import (
    GraphQLField, GraphQLNonNull, GraphQLArgument,
    GraphQLObjectType, GraphQLList, GraphQLBoolean, GraphQLString,
    GraphQLSchema, GraphQLInt, GraphQLFloat
)

import config as cfg
import data

Image = namedtuple('Image', 'id project src thumbnail thumbnailWidth thumbnailHeight \
                            tags caption modelTags modelProbs')
Metrics = namedtuple('Metrics', 'accuracy loss counts')
Counts = namedtuple('Counts', 'trn val tst unlabeled')
ImageList = namedtuple('ImageList', 'images') 
BoundingBox = namedtuple('BoundingBox', 'label coords')
Coords = namedtuple('Coords', 'bl br tl tr')
ObjDetectImage = namedtuple('ObjDetectImage', 'id project src boundingBoxes') 


CoordsType = GraphQLObjectType(
    name='Coords',
    fields= {
        'bl': GraphQLField(
            GraphQLNonNull(GraphQLInt),
        ),
        'br': GraphQLField(
            GraphQLNonNull(GraphQLInt),
        ),
        'tl': GraphQLField(
            GraphQLNonNull(GraphQLInt),
        ),
        'tr': GraphQLField(
            GraphQLNonNull(GraphQLInt),
        )
    }
)


BoundingBoxType = GraphQLObjectType(
    name='BoundingBox',
    fields= {
        'label': GraphQLField(
            GraphQLNonNull(GraphQLString),
        ),
        'coords': GraphQLField(
            GraphQLNonNull(CoordsType),
        ),
    }
)


ObjDetectImageType = GraphQLObjectType(
    name='ObjDetectImage',
    fields= {
        'id': GraphQLField(
            GraphQLNonNull(GraphQLString),
        ),
        'project': GraphQLField(
            GraphQLNonNull(GraphQLString),
        ),
        'src': GraphQLField(
            GraphQLString
        ),
        'boundingBoxes': GraphQLField(
            GraphQLList(BoundingBoxType)
        )
    }
)


ImageType = GraphQLObjectType(
    name='Image',
    fields= {
        'id': GraphQLField(
            GraphQLNonNull(GraphQLString),
        ),
        'project': GraphQLField(
            GraphQLNonNull(GraphQLString),
        ),
        'src': GraphQLField(
            GraphQLString
        ),
        'thumbnail': GraphQLField(
            GraphQLString
        ),
        'thumbnailWidth': GraphQLField(
            GraphQLInt
        ),
        'thumbnailHeight': GraphQLField(
            GraphQLInt
        ),
        'caption': GraphQLField(
            GraphQLString
        ),
        'tags': GraphQLField(
            GraphQLList(GraphQLString)
        ),
        'modelTags': GraphQLField(
            GraphQLList(GraphQLString)
        ),
        'modelProbs': GraphQLField(
            GraphQLList(GraphQLFloat)
        )
    }
)

CountsType = GraphQLObjectType(
    name='Counts',
    fields= {
        'trn': GraphQLField(
            GraphQLNonNull(GraphQLInt),
        ),
        'val': GraphQLField(
            GraphQLNonNull(GraphQLInt),
        ),
        'tst': GraphQLField(
            GraphQLInt,
        ),
        'unlabeled': GraphQLField(
            GraphQLNonNull(GraphQLInt),
        )
    }
)

MetricsType = GraphQLObjectType(
    name='Metrics',
    fields= {
        'accuracy': GraphQLField(
            GraphQLNonNull(GraphQLFloat),
        ),
        'loss': GraphQLField(
            GraphQLNonNull(GraphQLFloat),
        ),
        'counts': GraphQLField(
            CountsType
        ),
    }
)

ImageListType = GraphQLObjectType(
    name='ImageList',
    fields= {
        'images': GraphQLField(
            GraphQLList(ImageType)
        ),
    }
)


def make_unlabeled_img(project, id_):
    return Image(
        id=id_,
        project=project,
        src=data.img_url(id_),
        thumbnail=data.img_url(id_),
        thumbnailWidth=cfg.DEFAULT_WIDTH,
        thumbnailHeight=cfg.DEFAULT_HEIGHT,
        tags=[],
        caption=id_,
        modelTags=[],
        modelProbs=[]
    )


def make_image(id_, fold, dset):
    if dset == cfg.UNLABELED:
        return make_unlabeled_img(fold['name'], id_)
    img_meta = fold[dset][id_]
    tags = [] if img_meta is None else img_meta['labels']
    mdl_tags = [] if img_meta is None else img_meta['model_labels']
    mdl_probs = [] if img_meta is None else img_meta['model_probs']
    return Image(
        id=id_,
        project=fold['name'],
        src=data.img_url(id_),
        thumbnail=data.img_url(id_),
        thumbnailWidth=cfg.DEFAULT_WIDTH,
        thumbnailHeight=cfg.DEFAULT_HEIGHT,
        tags=tags,
        caption=id_,
        modelTags=mdl_tags,
        modelProbs=mdl_probs
    )



# const LABELS = [
#   {value: 'volvo', color: 'red'},
#   {value: 'saab', color: 'green'},
#   {value: 'opel', color: 'blue'},
#   {value: 'audi', color: 'orange'}
# ]

# const COLORS = {
#     'volvo':'red',
#     'saab':'green',
#     'opel':'blue',
#     'audi':'orange'
# }

SHAPE1 = {
    'coords': {
        'bl': {'x': 145, 'y': 149},
        'br': {'x': 269, 'y': 149},
        'tl': {'x': 145, 'y': 46.99},
        'tr': {'x': 269, 'y': 46.99}
    },
    'id': "s93pmd89nl",
    'label': "volvo"
}

SHAPE2 = {
    'coords': {
        'bl': {'x': 361, 'y': 353},
        'br': {'x': 603, 'y': 353},
        'tl': {'x': 361, 'y': 255},
        'tr': {'x': 603, 'y': 255}
    },
    'id': "asddddsss",
    'label': "opel"
}

TEST_IMG = {
    'id': 'test_id',
    'project': 'test_project',
    'src': 'http://www.nature.org/cs/groups/webcontent/@photopublic/documents/media/bluebird-640x400-1.jpg',
    'boundingBoxes': [
        SHAPE1, 
        SHAPE2
    ]
}

def make_obj_detect_image(id_, proj_name, bbs):
    bbs = [] if bbs is None else bbs
    return ObjDetectImage(
        id=id_,
        project=proj_name,
        src=data.img_url(id_),
        boundingBoxes=[]
    )


def get_metrics(project_name):
    metrics = data.get_metrics(project_name)
    m = Metrics(
        accuracy=metrics['accuracy'],
        loss=metrics['loss'],
        counts=Counts(
            trn=metrics['counts']['trn'],
            val=metrics['counts']['val'],
            tst=0 if 'tst' not in metrics['counts'] else metrics['counts']['tst'],
            unlabeled=metrics['counts']['unlabeled']                                    
        )
    )
    return m


def get_random_batch(proj_name, dset, shuffle=False, limit=20):
    fold = data.load_fold(proj_name)
    ids = list(fold[dset].keys())
    if shuffle:
        random.shuffle(ids)
    image_data = []
    for id_ in ids[:limit]:
        image_data.append(make_image(id_, fold, dset))
    return image_data


def get_ranked_batch(proj_name, dset, limit=cfg.BATCH_SIZE):
    fold = data.load_fold(proj_name)
    preds_df = pd.read_csv(
        data.get_fpath(proj_name, cfg.RANKINGS_FNAME), 
                       index_col=0)
    i = 0
    image_data = []
    for id_, row in preds_df.iterrows():
        if i > limit:
            return image_data
        if id_ in fold[dset]:
            image_data.append(make_image(
                id_, fold, dset))
            i += 1
    return image_data


def get_image_list(proj_name, dset=cfg.UNLABELED):
    if os.path.exists(data.get_fpath(proj_name, cfg.RANKINGS_FNAME)):
        image_data = get_ranked_batch(proj_name, dset)
    else:
        image_data = get_random_batch(
            proj_name, dset, shuffle=True)
    return ImageList(images=image_data)


def get_random_dset(val_ratio=cfg.VAL_FOLD_RATIO):
    if random.random() <= val_ratio:
        return cfg.VAL
    return cfg.TRAIN


def save_image_data(fold, id_, tags, dset=None, 
                    model_tags=None, model_probs=None):
    dset = get_random_dset() if dset is None else dset
    entry = data.make_entry(tags, model_tags, model_probs)
    data.move_unlabeled_to_labeled(fold, dset, id_, entry)
    data.save_fold(fold)
    data.update_counts(fold["name"])



def get_obj_detect_image(project, id_):
    fold = data.load_fold(project)
    return make_obj_detect_image(id_, fold, dset)


def get_next_obj_detect_image(project):
    return make_obj_detect_image(project)


def update_obj_detect_image(project, id_, img):
    pass


def get_image(project, id_, dset=cfg.UNLABELED):
    fold = data.load_fold(project)
    return make_image(id_, fold, dset)


def get_images(image_list):
    return map(get_image, image_list.images)


def get_image_single(id_, dset=cfg.UNLABELED):
    print('get image single')
    fold = data.load_fold(cfg.FOLD_FPATH)
    return make_image(id_, fold, dset)


def update_tags(id_, project, tags):
    print('updating tags', id_, project, tags)
    if len(tags) > 0:
        fold = data.load_fold(project)
        print(fold.keys())
        save_image_data(fold, id_, tags)


QueryRootType = GraphQLObjectType(
    name='Query',
    fields=lambda: {
        'image': GraphQLField(
            ImageType,
            args={
                'id': GraphQLArgument(GraphQLString)
            },
            resolver=lambda root, args, *_: get_image_single(
                args.get('id')
            ),
        ),
        'nextObjDetectImage': GraphQLField(
            ObjDetectImageType,
            args={
                'project': GraphQLArgument(GraphQLString)
            },
            resolver=lambda root, args, *_: get_next_obj_detect_image(
                args.get('project')
            ),
        ),
        'objDetectImage': GraphQLField(
            ObjDetectImageType,
            args={
                'id': GraphQLArgument(GraphQLString),
                'project': GraphQLArgument(GraphQLString)
            },
            resolver=lambda root, args, *_: get_obj_detect_image(
                args.get('id'), args.get('project')
            ),
        ),
        'imageList': GraphQLField(
            ImageListType,
            args={
                'project': GraphQLArgument(GraphQLString)
            },
            resolver=lambda root, args, *_: get_image_list(
                args.get('project')
            ),
        ),
        'metrics': GraphQLField(
            MetricsType,
            args={
                'project': GraphQLArgument(GraphQLString)
            },
            resolver=lambda root, args, *_: get_metrics(
                args.get('project')
            ),
        )
    }
)


MutationRootType = GraphQLObjectType(
    name='Mutation',
    fields=lambda: {
        'addImage': GraphQLField(
            ImageType,
            args={
                'project': GraphQLArgument(GraphQLString), 
                'src': GraphQLArgument(GraphQLString),
                'userLabels': GraphQLArgument(GraphQLList(GraphQLString)),
                'modelLabels': GraphQLArgument(GraphQLList(GraphQLString))
            },
            resolver=lambda root, args, *_: add_image(
                args.get('project'), args.get('src'), 
                args.get('tags'), args.get('modelTags'))
        ),
        'updateImageTags': GraphQLField(
            ImageType,
            args={
                'id': GraphQLArgument(GraphQLString),
                'project': GraphQLArgument(GraphQLString),
                'tags': GraphQLArgument(GraphQLList(GraphQLString))
            },
            resolver=lambda root, args, *_: update_tags(
                args.get('id'), args.get('project'), args.get('tags'))
        ),
        # 'updateObjDetectLabels': GraphQLField(
        #     ObjDetectImageType,
        #     args={
        #         'id': GraphQLArgument(GraphQLString),
        #         'project': GraphQLArgument(GraphQLString),
        #         'boundingBoxes': GraphQLArgument(GraphQLList(BoundingBoxType))
        #     },
        #     resolver=lambda root, args, *_: update_obj_detect_image(
        #         args.get('id'), args.get('project'), args.get('boundingBoxes'))
        # ),
    }
)

Schema = GraphQLSchema(QueryRootType, MutationRootType)

# if not os.path.exists(cfg.FOLD_FPATH):
#     _ = data.init_dataset(cfg.MEDIA_PATH, cfg.FOLD_FPATH)