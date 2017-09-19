import os
import random
from collections import namedtuple, OrderedDict
import pandas as pd
from graphql import (
    GraphQLField, GraphQLNonNull, GraphQLArgument,
    GraphQLObjectType, GraphQLList, GraphQLBoolean, GraphQLString,
    GraphQLSchema, GraphQLInt, GraphQLFloat, GraphQLInputObjectType,
    GraphQLInputObjectField
)

import config as cfg
import data

Image = namedtuple('Image', 'id project src thumbnail thumbnailWidth thumbnailHeight \
                            tags caption modelTags modelProbs')
Metrics = namedtuple('Metrics', 'accuracy loss counts')
Counts = namedtuple('Counts', 'trn val tst unlabeled')
ImageList = namedtuple('ImageList', 'images') 
BoundingBox = namedtuple('BoundingBox', 'id label xmin ymin xmax ymax')
ObjDetectImage = namedtuple('ObjDetectImage', 'id project src bboxes') 
ObjDetectLabelOpts = namedtuple('ObjDetectLabelOpts', 'labels') 
ColorLabel = namedtuple('ColorLabel', 'value color') 


BoundingBoxType = GraphQLObjectType(
    name='BoundingBox',
    fields= {
        'id': GraphQLField(
            GraphQLNonNull(GraphQLString),
        ),
        'label': GraphQLField(
            GraphQLNonNull(GraphQLString),
        ),
        'xmin': GraphQLField(
            GraphQLNonNull(GraphQLInt),
        ),
        'ymin': GraphQLField(
            GraphQLNonNull(GraphQLInt),
        ),
        'xmax': GraphQLField(
            GraphQLNonNull(GraphQLInt),
        ),
        'ymax': GraphQLField(
            GraphQLNonNull(GraphQLInt),
        )
    }
)

BoundingBoxInputType = GraphQLInputObjectType(
    name='BoundingBoxInput',
    fields= {
        'id': GraphQLInputObjectField(
            GraphQLNonNull(GraphQLString),
        ),
        'label': GraphQLInputObjectField(
            GraphQLNonNull(GraphQLString),
        ),
        'xmin': GraphQLInputObjectField(
            GraphQLNonNull(GraphQLInt),
        ),
        'ymin': GraphQLInputObjectField(
            GraphQLNonNull(GraphQLInt),
        ),
        'xmax': GraphQLInputObjectField(
            GraphQLNonNull(GraphQLInt),
        ),
        'ymax': GraphQLInputObjectField(
            GraphQLNonNull(GraphQLInt),
        )
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
        'bboxes': GraphQLField(
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


ColorLabelType = GraphQLObjectType(
    name='ColorLabel',
    fields= {
        'value': GraphQLField(
            GraphQLNonNull(GraphQLString),
        ),
        'color': GraphQLField(
            GraphQLNonNull(GraphQLString),
        )
    }
)


ObjDetectLabelOptsType = GraphQLObjectType(
    name='ObjDetectLabelOpts',
    fields= {
        'labels': GraphQLField(
            GraphQLList(ColorLabelType)
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


def make_obj_detect_label_opt(label):
    return ColorLabel(
        value=label['value'],
        color=label['color']
    )


def get_obj_detect_label_opts(project):
    labels = data.get_obj_detect_label_opts(project)
    print("LBS", labels)
    opts = []
    for label in labels:
        opts.append(make_obj_detect_label_opt(label))
    print("OPTS", opts)
    return ObjDetectLabelOpts(
        labels=opts)


def get_obj_detect_img(id_, project):
    img = data.load_obj_detect_img(id_, project)
    return make_obj_detect_image(id_, project, img)


def make_bounding_boxes(bbList):
    bbs = []
    for box in bbList:
        bbs.append(
            BoundingBox(
                id=box["id"],
                label=box["label"],
                xmin=box["xmin"],
                ymin=box["ymin"],
                xmax=box["xmax"],
                ymax=box["ymax"] 
            )
        )
    return bbs


def make_obj_detect_image(id_, project, img):
    src = data.make_url(project, data.id_to_fname(id_))
    bbs = [] if img is None else img['bboxes']
    return ObjDetectImage(
        id=id_,
        project=project,
        src=src,
        bboxes=make_bounding_boxes(bbs)
    )


def get_metrics(project_name):
    metrics = data.get_metrics(project_name)
    return Metrics(
        accuracy=metrics['accuracy'],
        loss=metrics['loss'],
        counts=Counts(
            trn=metrics['counts']['trn'],
            val=metrics['counts']['val'],
            tst=(0 if 'tst' not in metrics['counts'] 
                 else metrics['counts']['tst']),
            unlabeled=metrics['counts']['unlabeled']                                    
        )
    )


def get_next_obj_detect_img(project, currentId=None, dset=cfg.UNLABELED, 
                            include_preds=True):
    fold = data.load_fold(project)
    ids = list(fold[dset].keys())
    random.shuffle(ids)
    img = data.load_obj_detect_img(ids[0], project, include_preds)
    print(img)
    return make_obj_detect_image(ids[0], project, img)


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


def save_obj_detect_image(id_, project, bbs, dset=None):
    dset = get_random_dset() if dset is None else dset
    entry = data.make_obj_detect_entry(bbs)
    fold = data.load_fold(project)
    if id_ in fold[cfg.UNLABELED]:
        data.move_unlabeled_to_labeled(fold, dset, id_, entry)
    else:
        for dset in [cfg.VAL, cfg.TRAIN]:
            if id_ in fold[dset]:
                fold[dset][id_] = entry
                break
    data.save_fold(fold)
    # data.update_counts(fold["name"])


def get_image(project, id_, dset=cfg.UNLABELED):
    fold = data.load_fold(project)
    return make_image(id_, fold, dset)


def get_images(image_list):
    return map(get_image, image_list.images)


def get_image_single(project, id_, dset=cfg.UNLABELED):
    fpath = data.get_fpath(proj_name, cfg.FOLD_FNAME)
    fold = data.load_fold(fpath)
    return make_image(id_, fold, dset)


def update_tags(id_, project, tags):
    if len(tags) > 0:
        fold = data.load_fold(project)
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
                'project': GraphQLArgument(GraphQLString),
                'currentId': GraphQLArgument(GraphQLString)
            },
            resolver=lambda root, args, *_: get_next_obj_detect_img(
                args.get('project'), args.get('currentId')
            ),
        ),
        'objDetectImage': GraphQLField(
            ObjDetectImageType,
            args={
                'id': GraphQLArgument(GraphQLString),
                'project': GraphQLArgument(GraphQLString)
            },
            resolver=lambda root, args, *_: get_obj_detect_img(
                args.get('id'), args.get('project')
            ),
        ),
        'objDetectLabelOpts': GraphQLField(
            ObjDetectLabelOptsType,
            args={
                'project': GraphQLArgument(GraphQLString)
            },
            resolver=lambda root, args, *_: get_obj_detect_label_opts(
                args.get('project')
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
        'saveObjDetectImage': GraphQLField(
            ObjDetectImageType,
            args={
                'id': GraphQLArgument(GraphQLString),
                'project': GraphQLArgument(GraphQLString),
                'bboxes': GraphQLArgument(GraphQLList(BoundingBoxInputType))
            },
            resolver=lambda root, args, *_: save_obj_detect_image(
                args.get('id'), args.get('project'), args.get('bboxes'))
        ),
    }
)

Schema = GraphQLSchema(QueryRootType, MutationRootType)


# Init test project
fold_fpath = data.get_fpath(cfg.PROJECT_NAME, cfg.FOLD_FNAME)
if not os.path.exists(fold_fpath):
    _ = data.init_dataset(cfg.PROJECT_NAME, cfg.MEDIA_PATH, 
                          cfg.IMG_EXT, cfg.DEFAULT_LABELS)