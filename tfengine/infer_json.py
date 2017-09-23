import numpy as np
import os
import io
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import json
import math


import sys
sys.path.insert(0,'..')

import server.config as cfg
import server.utils.files


from collections import defaultdict
from io import StringIO
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from PIL import Image

from object_detection.utils import label_map_util

from object_detection.utils import visualization_utils as vis_util


PATH_TO_CKPT = "./tl_inference/frozen_inference_graph.pb"
PATH_TO_LABELS = "./output.pbtxt"
NUM_CLASSES = 5
IMAGE_SIZE = (12, 8)


detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')

def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)


label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


sess = None

with detection_graph.as_default():
    sess=tf.Session(graph=detection_graph)

    # Definite input and output Tensors for detection_graph
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    # Each box represents a part of the image where a particular object was detected.
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

def changelabel(label):
  if (label=='traffic_light_red'):
     return 'red'
  if (label=='traffic_light_green'):
     return 'green'
  if (label=='traffic_light_yellow'):
     return 'yellow'
  return label

def predict(f_id,image,data):
      #image = Image.open(image_path)
      # the array based representation of the image will be used later in order to prepare the
      # result image with boxes and labels on it.
      #image_np = load_image_into_numpy_array(image)
      image_np = np.array(image)  
      # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
      image_np_expanded = np.expand_dims(image_np, axis=0)
      # Actual detection.
      (boxes, scores, classes, num) = sess.run(
          [detection_boxes, detection_scores, detection_classes, num_detections],
          feed_dict={image_tensor: image_np_expanded})
      # Visualization of the results of a detection.
      #print((scores))
      min_score_thresh=0.001
      #vis_util.visualize_boxes_and_labels_on_image_array(
      #    image_np,
      #    np.squeeze(boxes),
      #    np.squeeze(classes).astype(np.int32),
      #    np.squeeze(scores),
      #    category_index,
      #    use_normalized_coordinates=True,
      #    min_score_thresh=min_score_thresh,
      #    line_thickness=4)
      '''
        "1478019952686311006": {
            "img_id": "1478019952686311006",
            "bboxes": [
                {
                    "label": "pedestrian",
                    "score": 0.326338529586792,
                    "xmin": 1725.1727294921875,
                    "ymin": 484.7314453125,
                    "xmax": 1812.0869140625,
                    "ymax": 718.4708862304688
                }
            ]
        },
      '''
      
      data[fid] = {
               'img_id' : fid,
               'bboxes' : []
           }
      #data['filename']=fname
      #data['folder']=folder
      #data['creator']='synthetic'
      (width,height) =  image.size
      #data['image_w_h']= image.size
      #data['objects']=[]
      scores2=np.squeeze(scores)
      boxes2=np.squeeze(boxes)
      classes2=np.squeeze(classes).astype(np.int32)
      print(boxes2)
      #print(scores2,boxes2) 
      boxes=[]
      for i in range(boxes2.shape[0]):
         if scores2 is None or scores2[i] > min_score_thresh:
                  box = tuple(boxes2[i].tolist())
                  if classes2[i] in category_index.keys():
                     class_name = category_index[classes2[i]]['name']
                  print(box)
                  x = int(round(box[1]*width))
                  y = int(round(box[0]*height))
                  x2 = int(round(box[3]*width))
                  y2 = int(round(box[2]*height))
                  onebox = {
                    "label": class_name,
                    "score": scores2[i],
                    "xmin": x,
                    "ymin": y,
                    "xmax": x2,
                    "ymax": y2,
                  }
                  boxes.append(onebox)
      data[fid]['bboxes']=boxes
      print(boxes)
      #jsondata=json.dumps(data)
      #print(jsondata)







def processVideo(input_video,output):
  clip1 = VideoFileClip(input_video)
  print("about to predict on video",input_video)
  out_clip = clip1.fl_image(predict)
  out_clip.write_videofile(output,audio=False)


def processJSON():
  json_name=os.path.join(cfg.PROJECT_PATH,cfg.FOLD_FNAME)
  data=server.utils.files.load_json(json_name)
  data = data['unlabeled']

  jsonpredictions = {
    "metrics": None,
    "dset": "tst",
    "imgs": {}
  }
  count = 0

  for f_id in data.keys():
           count = count +1
           with tf.gfile.GFile( os.path.join(cfg.MEDIA_PATH, f_id+'.jpg') , 'rb') as fid:
              encoded_jpg = fid.read()
              encoded_jpg_io = io.BytesIO(encoded_jpg)
              image = Image.open(encoded_jpg_io)
              d=jsonpredictions['imgs']
              predict(f_id,image,d)

  server.utils.files.save_json('./predictions.json',jsonpredictions)
if __name__ == '__main__':
   processJSON()




