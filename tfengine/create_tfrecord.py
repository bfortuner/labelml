import sys
sys.path.insert(0,'..')

import server.config as cfg
import server.utils.files

import tensorflow as tf
import pandas as pd
import os
import io
import json

from object_detection.utils import dataset_util
from collections import namedtuple, OrderedDict

from PIL import Image

flags = tf.app.flags
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')

FLAGS = flags.FLAGS

# TO-DO replace this with label map
def class_text_to_int(row_label):
    if row_label == 'car':
        return 1
    if row_label == 'pedestrian':
        return 2
    elif row_label == 'trafficlight':
        return 3
    elif row_label == 'biker':
        return 4
    elif row_label == 'truck':
        return 5
    else:
        print(row_label)
        None

total = 0

def create_tf_example(f_id, boxes, fpath):
  fname = os.path.join(fpath, f_id+'.jpg')
  statinfo = os.stat(fname)
  #print(fname)
  #print(statinfo.st_size)
  with tf.gfile.GFile(fname, 'rb') as fid:
      encoded_jpg = fid.read()

  encoded_jpg_io = io.BytesIO(encoded_jpg)
  image = Image.open(encoded_jpg_io)
  (width, height) = image.size
  #print("image.size")
  #print(image.size)
  #print(width,height)

  #print("widht,height %d %d" , (width,height))
  filename = f_id.encode('utf8')
  encoded_image_data = encoded_jpg # Encoded image bytes
  image_format = b'jpeg' # b'jpeg' or b'png'

  xmins = [] # List of normalized left x coordinates in bounding box (1 per box)
  xmaxs = [] # List of normalized right x coordinates in bounding box
             # (1 per box)
  ymins = [] # List of normalized top y coordinates in bounding box (1 per box)
  ymaxs = [] # List of normalized bottom y coordinates in bounding box
             # (1 per box)
  classes_text = [] # List of string class name of bounding box (1 per box)
  classes = [] # List of integer class id of bounding box (1 per box)

  for row in boxes:
        #print(row)
        xmin = row['xmin'] 
        ymin = row['ymin']
        xmax = row['xmax']
        ymax = row['ymax']

        xmins.append(float(xmin) / width)
        xmaxs.append(float(xmax) / width)
        ymins.append(float(ymin) / height)
        ymaxs.append(float(ymax) / height)
        classes_text.append(row['label'].encode('utf8'))
        classes.append(class_text_to_int(row['label']))

  #print(height)
  #print(width)
  #print(filename)
  #print(classes_text)
  #print(classes)
  #print(xmins)
  #print(xmaxs)
  tf_example = tf.train.Example(features=tf.train.Features(feature={
      'image/height': dataset_util.int64_feature(height),
      'image/width': dataset_util.int64_feature(width),
      'image/filename': dataset_util.bytes_feature(filename),
      'image/source_id': dataset_util.bytes_feature(filename),
      'image/encoded': dataset_util.bytes_feature(encoded_image_data),
      'image/format': dataset_util.bytes_feature(image_format),
      'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
      'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
      'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
      'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
      'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
      'image/object/class/label': dataset_util.int64_list_feature(classes),
  }))
  return tf_example


def create_tf_record(file_dict, dset, writer,writer_val):
    data = file_dict[dset]
    #ext = file_dict['file_ext']
    count = 0
    val = 0
    train = 0 
    ## TF record
    image_dir=cfg.MEDIA_PATH
    #image_dir=file_dict['inputs_dir']
    for f_id,data in data.items():
        count = count +1
        tf_example = create_tf_example(f_id, data['bboxes'], 
                                       image_dir)
        if not count % 5:
          writer_val.write(tf_example.SerializeToString())
          val = val +1
        else:
          writer.write(tf_example.SerializeToString())
          train = train +1

    print(count,dset)
    print('train',train)
    print('val',val)

def batch(writer,writer_val):
  fname = 'ground_truth_labels.json' #cfg.FOLD_FNAME
  json_name=os.path.join(cfg.PROJECT_PATH, fname)
  jsondata=server.utils.files.load_json(json_name)
  
  create_tf_record(jsondata, 'imgs', writer,writer_val)
  #create_tf_record(jsondata, 'val', writer_val)
  

def main(_):
  writer = tf.python_io.TFRecordWriter("train.record")
  writer_val = tf.python_io.TFRecordWriter("val.record")
  batch(writer,writer_val)
  writer.close()
  writer_val.close()

if __name__ == '__main__':
  tf.app.run()
