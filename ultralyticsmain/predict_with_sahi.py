
import argparse
from pathlib import Path

import cv2
import pandas as pd
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

from ultralyticsmain.ultralytics.utils.files import increment_path
from ultralyticsmain.ultralytics.utils.plotting import Annotator, colors


class SAHIInference:
    """Runs YOLOv8 and SAHI for object detection on images with options to view, save, and track results."""

    def __init__(self):
        """Initializes the SAHIInference class for performing sliced inference using SAHI with YOLOv8 models."""
        self.detection_model = None
        self.category_counts = {}

    def load_model(self, weights):
        """Loads a YOLOv8 model with specified weights for object detection using SAHI."""
        yolov8_model_path = f"{weights}"
        # download_yolov8s_model(yolov8_model_path)
        self.detection_model = AutoDetectionModel.from_pretrained(
            model_type="yolov8", model_path=yolov8_model_path, confidence_threshold=0.3, device="cpu"
        )


    def inference(
            self, weights="yolov8n.pt", source=None, view_img=False, save_img=False, exist_ok=False, track=False
    ):
        """
        Run object detection on a single image using YOLOv8 and SAHI.

        Args:
            weights (str): Model weights path.
            source (str): Path to the image file.
            view_img (bool): Show results.
            save_img (bool): Save results.
            exist_ok (bool): Overwrite existing files.
            track (bool): Enable object tracking with SAHI
        """
        if source is None:
            raise ValueError("The 'source' argument must be provided for a single image.")


        save_dir = increment_path(Path("ultralytics_results_with_sahi") , exist_ok)
        save_dir.mkdir(parents=True, exist_ok=True)


        self.load_model(weights)


        img_path = Path(source)
        frame = cv2.imread(str(img_path))
        if frame is None:
            print(f"Error reading image: {img_path}")
            return


        self.category_counts = {}


        annotator = Annotator(frame)  # Initialize annotator for plotting detection and tracking results


        results = get_sliced_prediction(
            frame,
            self.detection_model,
            slice_height=512,
            slice_width=512,
            overlap_height_ratio=0.2,
            overlap_width_ratio=0.2,
        )
        detection_data = [
            (det.category.name, det.category.id, (det.bbox.minx, det.bbox.miny, det.bbox.maxx, det.bbox.maxy))
            for det in results.object_prediction_list
        ]


        for det in detection_data:
            annotator.box_label(det[2], label=str(det[0]), color=colors(int(det[1]), True))


            if det[0] not in self.category_counts:
                self.category_counts[det[0]] = 0
            self.category_counts[det[0]] += 1


        if view_img:
            cv2.imshow(f"Detection: {img_path.name}", frame)
            cv2.waitKey(0)  # Wait until a key is pressed
            cv2.destroyAllWindows()  # Close the window after a key press


        if save_img:
            output_path = str(save_dir / f"{img_path.stem}_result{img_path.suffix}")
            cv2.imwrite(output_path, frame)
            print(f"Saved to: {output_path}")


        df = pd.DataFrame(list(self.category_counts.items()), columns=["Category", "Count"])
        excel_path = str(save_dir / f"{img_path.stem}_category_counts.xlsx")
        df.to_excel(excel_path, index=False)
        print(f"Category counts for {img_path.name} saved to: {excel_path}")

    def parse_opt(self):
        """Parse command line arguments."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--weights", type=str, default=r"D:\integrated_ui\ultralytics-main\runs\res\weights\best.pt", help="initial weights path")
        parser.add_argument("--source", type=str, default=r"D:\integrated_ui\ultralytics-main\raw.v1i.yolov8\demo", help="video file path")
        parser.add_argument("--view-img", action="store_true", help="show results")
        parser.add_argument("--save-img", default=True, help="save results")
        parser.add_argument("--exist-ok", action="store_true", help="existing project/name ok, do not increment")
        return parser.parse_args()


if __name__ == "__main__":
    inference = SAHIInference()
    inference.inference(**vars(inference.parse_opt()))