from ultralytics.data.split_data import split_trainval


split_trainval(
    data_root=r"C:\Users\fan\Desktop\yolov11\ultralytics-main\raw.v1i.yolov8\train",
    save_dir="./dataset",
    rates=[1.0],
    gap=200,
    crop_size=640
)