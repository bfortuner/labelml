import os
from pathlib import Path
import time
import pandas as pd
from collections import namedtuple, OrderedDict

import utils.files
import config as cfg


DEFAULT_COLS = ['id','labels','model_labels']


def get_fpath(proj_name, fname):
    return os.path.join(cfg.LABEL_PATH, proj_name, fname)


def init_dataset(name, input_dir, file_ext, label_names=None):
    fpaths, ids = utils.files.get_paths_to_files(input_dir, strip_ext=True)
    label_names = [] if label_names is None else label_names
    fold = {
        'name': name,
        'file_ext': file_ext,
        'inputs_dir': input_dir,
        'label_names': sorted(label_names),
        'trn': {},
        'val': {},
        'tst': {}, #auditing purposes
        'unlabeled': {}, #these need to be queried and popped by key
        'metrics': {},
        'created': time.strftime("%m/%d/%Y %H:%M:%S", time.localtime())
    }
    for id_ in ids:
        fold['unlabeled'][id_] = id_
    os.makedirs(os.path.join(cfg.LABEL_PATH, name), exist_ok=True)
    # Path(get_fpath(name, cfg.METRICS_FNAME)).touch()
    # Path(get_fpath(name, cfg.PREDS_FNAME)).touch()
    utils.files.save_json(get_fpath(name, cfg.FOLD_FNAME), fold)
    return fold


def make_entry(labels=None, model_labels=None, model_probs=None):
    labels = [] if labels is None else labels
    model_labels = [] if model_labels is None else model_labels
    model_probs = [] if model_probs is None else model_probs
    return {
        'labels': labels,
        'model_labels': model_labels,
        'model_probs': model_probs,
    }


def add_or_update_entry(fold, dset, id_, entry):
    print("Adding or updating entry")
    fold[dset][id_] = entry


def move_unlabeled_to_labeled(fold, dset, id_, entry):
    print("Moving unlabeled to labeled")
    add_or_update_entry(fold, dset, id_, entry)
    del fold['unlabeled'][id_]


def load_fold(name):
    fpath = get_fpath(name, cfg.FOLD_FNAME)
    return utils.files.load_json(fpath)

def save_fold(fold):
    fpath = get_fpath(fold["name"], cfg.FOLD_FNAME)
    return utils.files.save_json(fpath, fold)    


def img_url(fname):
    return cfg.IMG_ENDPOINT + '/{:s}'.format(fname + cfg.IMG_EXT)


def get_img_count(fold, dset):
    return len(fold[dset].keys())


def load_metrics(fpath):
    if os.path.isfile(fpath):
        return utils.files.load_json(fpath)
    return {
        "experiments":{}, 
        "latest":{},
        "counts":{}
    }


def get_metrics(project_name):
    metrics = load_metrics(get_fpath(
        project_name, cfg.METRICS_FNAME))
    return { 
        "accuracy": metrics['latest']['Accuracy'],
        "loss": metrics['latest']['Loss'],
        "counts": metrics["counts"]
    }


def get_img_count(fold, dset):
    return len(fold[dset].keys())


def get_img_counts(proj_name):
    fold = load_fold(proj_name)
    return {
        cfg.TRAIN: get_img_count(fold, cfg.TRAIN),
        cfg.VAL: get_img_count(fold, cfg.VAL),
        cfg.TEST: get_img_count(fold, cfg.TEST),
        cfg.UNLABELED: get_img_count(fold, cfg.UNLABELED)
    }


def load_counts(fpath):
    if os.path.isfile(fpath):
        return utils.files.load_json(fpath)
    return {
        "experiments":{}, 
        "latest":{},
        "counts":{}
    }


def update_counts(project_name):
    counts = get_img_counts(project_name)
    metrics_fpath = get_fpath(
        project_name, cfg.METRICS_FNAME)
    metrics = load_metrics(metrics_fpath)
    metrics["counts"] = counts
    utils.files.save_json(metrics_fpath, metrics)
    return metrics



# Pandas 

def init_dataset_df(meta_fpath, input_dir):
    fpaths, ids = utils.files.get_paths_to_files(input_dir, strip_ext=True)
    data = []
    for id_ in ids:
        data.append([id_,'',''])
    df = pd.DataFrame(data, columns=DEFAULT_COLS)
    df = df.set_index('id')
    save_metadata_df(df, meta_fpath)
    return df

def save_metadata_df(df, fpath):
    df.to_csv(fpath, index=True, columns=DEFAULT_COLS[1:])


def get_row_by_id(df, id_):
    if id_ in df.index:
        return df.loc[id_]
    return None


def insert_or_append_df(df, id_, values):
    df.loc[id_] = values
    return df


def load_metadata_df(fpath):
    df = pd.read_csv(fpath, header=0, 
                     names=DEFAULT_COLS, index_col=DEFAULT_COLS[0])
    df = df.fillna(value='')
    return df