import os
import shutil


src_image_dir = 'F:\earn\yolov8-pytorch-master\yolov8-pytorch-master\VOCdevkit\VOC2007\JPEGImages'


src_label_dir = 'F:\earn\yolov8-pytorch-master\yolov8-pytorch-master\VOCdevkit\VOC2007\Annotations'


dst_dir = r'F:\earn\yolov8-pytorch-master\yolov8-pytorch-master\VOCdevkit\VOC2007\renam'


if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)


counter = 1


for label_filename in os.listdir(src_label_dir):

    if label_filename.endswith('.xml'):

        base_name = os.path.splitext(label_filename)[0]


        src_image_path = os.path.join(src_image_dir, f'{base_name}.jpg')


        new_image_filename = f'{counter}.jpg'


        new_label_filename = f'{counter}.xml'


        dst_image_path = os.path.join(dst_dir, new_image_filename)
        shutil.copy(src_image_path, dst_image_path)


        src_label_path = os.path.join(src_label_dir, label_filename)
        dst_label_path = os.path.join(dst_dir, new_label_filename)
        shutil.copy(src_label_path, dst_label_path)

        # 递增计数器
        counter += 1

print('Dataset modification complete!')