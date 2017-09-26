#
# Make the inference file 
#
rm -rf tl_inference
mkdir tl_inference
python object_detection/export_inference_graph.py \
    --input_type image_tensor \
    --pipeline_config_path ./faster_rcnn_resnet101_coco.config \
    --trained_checkpoint_prefix ./checkpoint/model.ckpt-100 \
    --output_directory tl_inference
