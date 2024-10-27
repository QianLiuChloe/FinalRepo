# Ultralytics YOLO 🚀, AGPL-3.0 license

import itertools
from glob import glob
from math import ceil
from pathlib import Path

import cv2
from PIL import Image
from tqdm import tqdm
import numpy as np
from ultralytics.data.utils import exif_size, img2label_paths
from ultralytics.utils.checks import check_requirements
check_requirements("shapely")
from shapely.geometry import Polygon

import numpy as np

def normalize_to_center_wh_with_class(polygons):
    """
    Convert polygon coordinates to center point and dimensions (h, w) with class.

    Args:
        polygons (np.ndarray): Polygon coordinates with class, shape (n, 9).
                               Format: [class, x1, y1, x2, y2, x3, y3, x4, y4]

    Returns:
        np.ndarray: Center point and dimensions with class, shape (n, 5).
                    Format: [class, cx, cy, width, height]
    """
    # Extract the class column
    classes = polygons[:, 0]

    # Reshape the polygons to (n, 4, 2) for easier manipulation
    polygons_coords = polygons[:, 1:].reshape(-1, 4, 2)

    # Calculate the minimum and maximum x and y coordinates
    min_x = np.min(polygons_coords[:, :, 0], axis=1)
    max_x = np.max(polygons_coords[:, :, 0], axis=1)
    min_y = np.min(polygons_coords[:, :, 1], axis=1)
    max_y = np.max(polygons_coords[:, :, 1], axis=1)

    # Calculate the center point (cx, cy)
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2

    # Calculate the width and height
    width = max_x - min_x
    height = max_y - min_y

    # Stack the results to form the output array
    center_wh = np.stack([classes, cx, cy, width, height], axis=-1)

    return center_wh


def center_to_vertex(boxes):
    """
    将中心点、宽度和高度的矩形转换为四个顶点的坐标形式。

    Args:
        boxes (np.ndarray): 形状为 (N, 5)，其中每个元素是 [类别, cx, cy, width, height]。

    Returns:
        np.ndarray: 形状为 (N, 9)，其中每个元素是 [类别, x1, y1, x2, y2, x3, y3, x4, y4]。
    """
    classes = boxes[:, 0]
    cx, cy, w, h = (boxes[:, i] for i in range(1, 5))

    # 计算四个顶点
    x1 = cx - w / 2
    y1 = cy - h / 2
    x2 = cx + w / 2
    y2 = cy - h / 2
    x3 = cx + w / 2
    y3 = cy + h / 2
    x4 = cx - w / 2
    y4 = cy + h / 2

    # 合并类别和顶点坐标
    vertices = np.stack([x1, y1, x2, y2, x3, y3, x4, y4], axis=-1)
    return np.hstack([classes[:, None], vertices])


def bbox_iof(polygon1, bbox2, eps=1e-6):
    """
    Calculate Intersection over Foreground (IoF) between polygons and bounding boxes.

    Args:
        polygon1 (np.ndarray): Polygon coordinates, shape (n, 9).
        bbox2 (np.ndarray): Bounding boxes, shape (m, 4).
        eps (float, optional): Small value to prevent division by zero. Defaults to 1e-6.

    Returns:
        (np.ndarray): IoF scores, shape (n, m).

    Note:
        Polygon format: [类别, x1, y1, x2, y2, x3, y3, x4, y4].
        Bounding box format: [x_min, y_min, x_max, y_max].
    """
    # 提取多边形的顶点坐标（忽略类别）
    polygon1_vertices = polygon1[:, 1:].reshape(-1, 4, 2)

    # 计算 polygon1 的边界框
    lt_point = np.min(polygon1_vertices, axis=-2)  # left-top
    rb_point = np.max(polygon1_vertices, axis=-2)  # right-bottom
    bbox1 = np.concatenate([lt_point, rb_point], axis=-1)

    # 扩展维度以便广播
    lt = np.maximum(bbox1[:, None, :2], bbox2[None, :, :2])
    rb = np.minimum(bbox1[:, None, 2:], bbox2[None, :, 2:])
    wh = np.clip(rb - lt, 0, np.inf)
    h_overlaps = wh[..., 0] * wh[..., 1]

    # 将 bbox2 转换为多边形格式
    left, top, right, bottom = (bbox2[..., i] for i in range(4))
    polygon2 = np.stack([left, top, right, top, right, bottom, left, bottom], axis=-1).reshape(-1, 4, 2)

    # 创建 Shapely 多边形
    sg_polys1 = [Polygon(p) for p in polygon1_vertices]
    sg_polys2 = [Polygon(p) for p in polygon2]

    # 初始化重叠面积数组
    n, m = len(sg_polys1), len(sg_polys2)
    overlaps = np.zeros((n, m))

    # 计算交集面积
    for i in range(n):
        for j in range(m):
            if h_overlaps[i, j] > 0:
                overlaps[i, j] = sg_polys1[i].intersection(sg_polys2[j]).area

    # 计算并集面积
    unions = np.array([p.area for p in sg_polys1], dtype=np.float32)[:, None]

    # 防止除零错误
    unions = np.clip(unions, eps, np.inf)

    # 计算 IoF
    outputs = overlaps / unions

    return outputs


def load_yolo_dota(data_root, split="train"):
    """
    Load DOTA dataset.

    Args:
        data_root (str): Data root.
        split (str): The split data set, could be train or val.

    Notes:
        The directory structure assumed for the DOTA dataset:
            - data_root
                - images
                    - train
                    - val
                - labels
                    - train
                    - val
    """
    assert split in {"train", "val"}, f"Split must be 'train' or 'val', not {split}."
    im_dir = Path(data_root) / "images"
    assert im_dir.exists(), f"Can't find {im_dir}, please check your data root."
    im_files = glob(str(Path(data_root) / "images" / "*"))
    lb_files = img2label_paths(im_files)
    annos = []
    for im_file, lb_file in zip(im_files, lb_files):
        w, h = exif_size(Image.open(im_file))
        with open(lb_file) as f:
            lb = [x.split() for x in f.read().strip().splitlines() if len(x)]
            lb = np.array(lb, dtype=np.float32)
        annos.append(dict(ori_size=(h, w), label=lb, filepath=im_file))
    return annos


def get_windows(im_size, crop_sizes=(1024,), gaps=(200,), im_rate_thr=0.6, eps=0.01):
    """
    Get the coordinates of windows.

    Args:
        im_size (tuple): Original image size, (h, w).
        crop_sizes (List[int]): Crop size of windows.
        gaps (List[int]): Gap between crops.
        im_rate_thr (float): Threshold of windows areas divided by image ares.
        eps (float): Epsilon value for math operations.
    """
    h, w = im_size
    windows = []
    for crop_size, gap in zip(crop_sizes, gaps):
        assert crop_size > gap, f"invalid crop_size gap pair [{crop_size} {gap}]"
        step = crop_size - gap

        xn = 1 if w <= crop_size else ceil((w - crop_size) / step + 1)
        xs = [step * i for i in range(xn)]
        if len(xs) > 1 and xs[-1] + crop_size > w:
            xs[-1] = w - crop_size

        yn = 1 if h <= crop_size else ceil((h - crop_size) / step + 1)
        ys = [step * i for i in range(yn)]
        if len(ys) > 1 and ys[-1] + crop_size > h:
            ys[-1] = h - crop_size

        start = np.array(list(itertools.product(xs, ys)), dtype=np.int64)
        stop = start + crop_size
        windows.append(np.concatenate([start, stop], axis=1))
    windows = np.concatenate(windows, axis=0)

    im_in_wins = windows.copy()
    im_in_wins[:, 0::2] = np.clip(im_in_wins[:, 0::2], 0, w)
    im_in_wins[:, 1::2] = np.clip(im_in_wins[:, 1::2], 0, h)
    im_areas = (im_in_wins[:, 2] - im_in_wins[:, 0]) * (im_in_wins[:, 3] - im_in_wins[:, 1])
    win_areas = (windows[:, 2] - windows[:, 0]) * (windows[:, 3] - windows[:, 1])
    im_rates = im_areas / win_areas
    if not (im_rates > im_rate_thr).any():
        max_rate = im_rates.max()
        im_rates[abs(im_rates - max_rate) < eps] = 1
    return windows[im_rates > im_rate_thr]


def get_window_obj(anno, windows, iof_thr=0.7):
    """Get objects for each window."""
    h, w = anno["ori_size"]

    label = anno["label"]
    if len(label):
        # 将中心点格式转换为顶点格式
        label_vertex = center_to_vertex(label)

        # 将归一化坐标转换为绝对坐标
        label_vertex[:, 1::2] *= w
        label_vertex[:, 2::2] *= h


        # 计算 IoF 分数
        iofs = bbox_iof(label_vertex, windows)
    
        # 获取每个窗口内的对象
        window_objs = []
        for i in range(len(windows)):
            window_label = label_vertex[iofs[:, i] >= iof_thr]
            window_objs.append(window_label)
        return window_objs
    else:
        return [np.zeros((0, 5), dtype=np.float32) for _ in range(len(windows))]


def crop_and_save(anno, windows, window_objs, im_dir, lb_dir, allow_background_images=False):
    """
    Crop images and save new labels.

    Args:
        anno (dict): Annotation dict, including `filepath`, `label`, `ori_size` as its keys.
        windows (list): A list of windows coordinates.
        window_objs (list): A list of labels inside each window.
        im_dir (str): The output directory path of images.
        lb_dir (str): The output directory path of labels.
        allow_background_images (bool): Whether to include background images without labels.
    """
    im = cv2.imread(anno["filepath"])
    name = Path(anno["filepath"]).stem
    for i, window in enumerate(windows):
        x_start, y_start, x_stop, y_stop = window.tolist()
        new_name = f"{name}{x_stop - x_start}{x_start}{y_start}"
        patch_im = im[y_start:y_stop, x_start:x_stop]
        ph, pw = patch_im.shape[:2]

        label = window_objs[i]
        if len(label) or allow_background_images:
            cv2.imwrite(str(Path(im_dir) / f"{new_name}.jpg"), patch_im)
        if len(label):
            label[:, 1::2] -= x_start
            label[:, 2::2] -= y_start
            label[:, 1::2] /= pw
            label[:, 2::2] /= ph
            label = normalize_to_center_wh_with_class(label)
            with open(Path(lb_dir) / f"{new_name}.txt", "w") as f:
                for lb in label:
                    formatted_coords = [f"{coord:.6g}" for coord in lb[1:]]
                    f.write(f"{int(lb[0])} {' '.join(formatted_coords)}\n")


def split_images_and_labels(data_root, save_dir, split="train", crop_sizes=(1024,), gaps=(200,)):
    im_dir = Path(save_dir) / "images" 
    im_dir.mkdir(parents=True, exist_ok=True)
    lb_dir = Path(save_dir) / "labels" 
    lb_dir.mkdir(parents=True, exist_ok=True)

    annos = load_yolo_dota(data_root, split=split)
    for anno in tqdm(annos, total=len(annos), desc=split):
        windows = get_windows(anno["ori_size"], crop_sizes, gaps)
        window_objs = get_window_obj(anno, windows)
        crop_and_save(anno, windows, window_objs, str(im_dir), str(lb_dir))


def split_trainval(data_root, save_dir, crop_size=1024, gap=200, rates=(1.0)):
    crop_sizes, gaps = [], []
    for r in rates:
        crop_sizes.append(int(crop_size / r))
        gaps.append(int(gap / r))
    for split in ["train"]:
        split_images_and_labels(data_root, save_dir, split, crop_sizes, gaps)