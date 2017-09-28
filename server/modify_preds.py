import os
import utils.files
import config as cfg


fpath = os.path.join(cfg.PROJECT_PATH, cfg.PREDS_FNAME)
preds = utils.files.load_json(fpath)
print(preds.keys())

new_preds = {
    'metrics': preds['metrics'],
    'dset': preds['dset'],
    'imgs': {}
}

for id_,img in preds['imgs'].items():
    record = {
        "img_id": id_,
        "annotations": []
    }
    for box in img['bboxes']:
        anno_id = utils.files.gen_unique_id()
        box['points'] = []
        box['annoId'] = anno_id
        box['id'] = utils.files.gen_unique_id()
        record['annotations'].append({
            "id": anno_id,
            "label": box['label'],
            "bbox": box,
            "polygon": None
        })
        new_preds['imgs'][id_] = record


print(new_preds['imgs'][list(new_preds['imgs'].keys())[5]])

utils.files.save_json(fpath, new_preds)

