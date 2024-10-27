
import time
import cv2
import numpy as np
from PIL import Image
from yolo import YOLO


if __name__ == "__main__":
    yolo = YOLO()

    mode = "predict"

    crop            = True
    count           = False

    video_path      = 0
    video_save_path = ""
    video_fps       = 25.0

    test_interval   = 100
    fps_image_path  = "img/street.jpg"
    #-------------------------------------------------------------------------#

    #-------------------------------------------------------------------------#
    img = r"D:\integrated_ui\source\52af8f71a7db8c6ead1b26da90184c5.jpg"
    dir_save_path   = "img_out"
    #-------------------------------------------------------------------------#

    #-------------------------------------------------------------------------#
    heatmap_save_path = "model_data/heatmap_vision.png"

    simplify        = True
    onnx_save_path  = "model_data/models.onnx"

    if mode == "predict":

        try:
            image = Image.open(img)
        except:
            print('Open Error! Try again!')
        else:
            r_image = yolo.detect_image(image, crop = crop, count=count)


    elif mode == "export_onnx":
        yolo.convert_to_onnx(simplify, onnx_save_path)
        
    else:
        raise AssertionError("Please specify the correct mode: 'predict', 'video', 'fps', 'heatmap', 'export_onnx', 'dir_predict'.")
