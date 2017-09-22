import os
import numpy as np
import pandas as pd

import constants as c


def get_metadata_df(fpath):
    return pd.read_csv(fpath, header=0, names=['id','labels'])


def get_labels_to_idxs(label_names):
    return {v:k for k,v in enumerate(label_names)}


def get_idxs_to_labels(label_names):
    return {k:v for k,v in enumerate(label_names)}


def convert_tags_to_one_hots(tags, label_names, delim=' '):
    label_to_idx = get_labels_to_idxs(label_names)
    idxs = [label_to_idx[o] for o in tags.split(delim)]
    onehot = np.zeros((len(label_names),), dtype=np.float32)
    onehot[idxs] = 1
    return onehot


def get_one_hots_from_tags(tags, label_names):
    onehots = np.zeros( (0, len(label_names)) )
    for tag in tags:
        onehot = convert_tags_to_one_hots(tags, label_names)
        onehots = np.append(onehots, np.array([onehot]), axis=0)
    return onehots


def get_fpaths_targs_from_label_fold(fold, dset, label_type='labels'):
    label_names = fold['label_names']
    onehots = np.zeros( (0, len(label_names)) )
    fpaths = []
    for id_ in fold[dset].keys():
        entry = fold[dset][id_]
        fpath = os.path.join(fold['inputs_dir'], id_ + fold['file_ext'])
        if dset not in [c.TEST, c.UNLABELED]:
            onehot = convert_tags_to_one_hots(' '.join(entry[label_type]), label_names)
            onehots = np.append(onehots, np.array([onehot]), axis=0)
        fpaths.append(fpath)
    return fpaths, onehots


def get_one_hots_array(meta_fpath, label_names):
    meta_df = get_metadata_df(meta_fpath)
    onehots = np.zeros( (0, len(label_names)) )
    for _, row in meta_df.iterrows():
        onehot = convert_tags_to_one_hots(row[1], label_names)
        onehots = np.append(onehots, np.array([onehot]), axis=0)
    return onehots


def get_tags_by_id(meta_df, id_):
    tags = list(meta_df[meta_df['id'] == id_]['labels'].values)
    return tags


def get_tags_from_fold(meta_fpath, fold, dset):
    meta_df = get_metadata_df(meta_fpath)
    all_tags = []
    for _, name in enumerate(fold[dset]):
        tags = meta_df[meta_df['id'] == name]['labels'].values[0]
        all_tags.append(tags)
    return all_tags


def get_one_hots_from_fold(meta_fpath, fold, dset, label_names):
    meta_df = get_metadata_df(meta_fpath)
    onehots = np.zeros( (0, len(label_names)) )
    for _, name in enumerate(fold[dset]):
        tags = meta_df[meta_df['id'] == name]['labels'].values[0]
        onehot = convert_tags_to_one_hots(tags, label_names)
        onehots = np.append(onehots, np.array([onehot]), axis=0)
    return onehots


def get_label_idx_by_name(label, label_names):
    return label_names.index(label)


def get_tags_from_preds(preds, label_names):
    tags = []
    for _, pred in enumerate(preds):
        tag_str = ' '.join(convert_one_hot_to_tags(pred, label_names))
        tags.append(tag_str)
    return tags


def convert_one_hot_to_tags(onehot, label_names):
    tags = []
    for idx, val in enumerate(onehot):
        if val == 1:
            tags.append(label_names[idx])
    return tags