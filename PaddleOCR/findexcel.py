import cv2
from paddleocr import PaddleOCR
from paddleocr import PPStructure,save_structure_res
import os
# 2. 初始化PaddleOCR实例
ocr = PaddleOCR(use_angle_cls=True, lang='en')
table_engine = PPStructure(table=False, ocr=False, show_log=True)
# 3. 读取并分析输入图像
image_path = './out/1.png'
save_folder = './output'
img = cv2.imread(image_path)
result = table_engine(img)
save_structure_res(result, save_folder, os.path.basename(image_path).split('.')[0])
# result = ocr.ocr(image_path, cls=True)
print(result)

# 4. 提取表格区域坐标
table_regions = []
for line in result:
    box = line[0]
    text = line[1][0]
    if 'Table' in text:
        x1, y1 = box[0]
        x2, y2 = box[2]
        table_regions.append((x1, y1, x2-x1, y2-y1))

# 5. 根据坐标裁剪出表格区域并保存
image = cv2.imread(image_path)
for i, region in enumerate(table_regions):
    x, y, w, h = [int(x) for x in region]
    table_image = image[y:y+h, x:x+w]
    cv2.imwrite(f'table_{i}.jpg', table_image)