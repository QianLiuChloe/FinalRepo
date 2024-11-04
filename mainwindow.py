import sys
import os
from pathlib import Path

import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'ultralyticsmain'))
import shutil

import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
from yolov8_crop.yolo import YOLO as Crop_yolo
from PaddleOCR.paddleocr import PPStructure, draw_structure_result, save_structure_res
import cv2
from excel import process_excel
from ultralyticsmain.predict_with_sahi import SAHIInference


class ComponentRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Component recognition and generation of component tables")

        self.save_folder = os.path.join(os.getcwd(), r"./output")


        self.root.minsize(800, 600)


        self.upload_button = Button(root, text="Upload Drawing", command=self.upload_drawing, width=20, height=5)
        self.upload_button.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')


        self.recognize_button = Button(root, text="Start ", command=self.recognize_components, state=tk.DISABLED,
                                       width=20, height=5)
        self.recognize_button.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')


        self.extract_table_button = Button(root, text="Extract a table", command=self.extract_table, state=tk.DISABLED,
                                           width=20, height=5)
        self.extract_table_button.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')


        self.excel_table_button = Button(root, text="Process Excel Table", command=self._process_excel, state=tk.DISABLED,
                                         width=20, height=5)
        self.excel_table_button.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')


        self.sahi_table_button = Button(root, text="SAHI inference", command=self.sahi_infer, state=tk.DISABLED,
                                        width=20, height=5)
        self.sahi_table_button.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')


        self.combine_table_button = Button(root, text="combine", command=self.combine, state=tk.DISABLED,
                                           width=20, height=5)
        self.combine_table_button.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')


        self.result_text = Text(root, height=20, width=40, font=("Arial", 12), wrap=tk.WORD)  # 添加 wrap=WORD 使得文本自动换行
        self.result_text.grid(row=0, column=3, rowspan=4, padx=10, pady=10, sticky='nsew', columnspan=2)


        self.preview_image_label = Label(root,relief=tk.SUNKEN)
        self.preview_image_label.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        self.model_crop = Crop_yolo()
        self.table_engine = PPStructure(show_log=False)
        self.inference = SAHIInference()

        self.image_path = ""

    def upload_drawing(self):

        self.image_path = filedialog.askopenfilename(
            initialdir=os.path.join(os.getcwd(), "source"),
            title="Choose Drawing",
            filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*"))
        )

        if self.image_path:
            try:
                image = Image.open(self.image_path)
                image.thumbnail((600, 750))
                photo = ImageTk.PhotoImage(image)
                self.preview_image_label.config(image=photo)
                self.preview_image_label.image = photo


                self.recognize_button.config(state=tk.NORMAL)


                self.result_text.insert(tk.END, "The drawing has been successfully uploaded.\n")

            except Exception as e:
                messagebox.showerror("Error", f"Can not open the file: {e}")

                self.recognize_button.config(state=tk.DISABLED)

    def recognize_components(self):
        if os.path.exists('./img_crop'):
            shutil.rmtree('./img_crop')
        try:
            image = Image.open(self.image_path)
            r_image, infos = self.model_crop.detect_image(image, crop=True, count=True)
            r_image.thumbnail((750, 600))
            photo = ImageTk.PhotoImage(r_image)
            self.preview_image_label.config(image=photo)
            self.preview_image_label.image = photo


            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Result is below:\n{str(infos)}")


            self.extract_table_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Recognition failed: {e}")

            self.extract_table_button.config(state=tk.DISABLED)

    def extract_table(self):
        if os.path.exists(self.save_folder):
            shutil.rmtree(self.save_folder)
        try:
            save_folder = self.save_folder
            img_path = filedialog.askopenfilename(
                initialdir=os.path.join(os.getcwd(), "img_crop"),
                title="Choose Table",
                filetypes=(("PNG files", "*.png"), ("All files", "*.*"))
            )
            if not img_path:
                return
            img = cv2.imread(img_path)
            result = self.table_engine(img)
            save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])


            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"save result in {save_folder}\n")
            self.result_text.insert(tk.END, str(result))
            self.excel_table_button.config(state=tk.NORMAL)  # 启用处理 Excel 按钮

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while extracting the table.: {e}")
            self.excel_table_button.config(state=tk.DISABLED)  # 如果提取失败，禁用处理 Excel 按钮

    def _process_excel(self):
        if os.path.exists("process_excel"):
            shutil.rmtree(r"E:\FinalRepo\process_excel")
        os.makedirs(r"E:\FinalRepo\process_excel")
        all_infos = []
        res = os.listdir(self.save_folder)
        for i in res:
            detail = os.listdir(os.path.join(self.save_folder, i))
            detail = [f for f in detail if f.lower().endswith('.xlsx')]
            # print(detail)
            for r in detail:
                file_path = os.path.join(os.path.join(self.save_folder, i), r)
                try:

                    print(f"Processing document: {file_path}")

                    news = process_excel(file_path,
                                         os.path.join(r"E:\FinalRepo\process_excel", r))
                    all_infos.append(news)
                except Exception as e:
                    messagebox.showerror("Error", f"File: {i} An error occurred while processing the document: {e}")


        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"{all_infos}")
        self.sahi_table_button.config(state=tk.NORMAL)

    def sahi_infer(self):

        try:
            args = {
                "weights": r"E:\FinalRepo\ultralyticsmain\runs\res\weights\best.pt",
                "source": self.image_path,
                "view_img": False,
                'save_img': False,
                'exist_ok': True,
            }
            self.inference.inference(**args)
            self.result_text.insert(tk.END, "SAHI reasoning completed。\n")
            self.combine_table_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Failure of SAHI inference: {e}")

    def combine(self):


        df1 = pd.read_excel(os.path.join(r'.\process_excel', os.listdir(r'.\process_excel')[0]))  # Table 1
        df2 = pd.read_excel(
            os.path.join(r'.\ultralytics_results_with_sahi', os.listdir(r'.\ultralytics_results_with_sahi')[0]))  # Table2


        df2.iloc[:, 0] = df2.iloc[:, 0].str.upper()


        quantity_dict = df2.groupby(df2.columns[0])[df2.columns[1]].sum().to_dict()


        df1['Number'] = 0


        for idx, row in df1.iterrows():
            component_name = row[df1.columns[0]].upper()

            if component_name in quantity_dict:
                df1.at[idx, 'Number'] = quantity_dict[component_name]


        df1.to_excel(f"{Path(os.listdir('process_excel')[0]).name}", index=False)
        self.result_text.insert(tk.END, "Table merging complete,del process_excel and ultralytics_results_with_sahi.\n")
        shutil.rmtree(r'.\process_excel')
        shutil.rmtree(r'.\ultralytics_results_with_sahi')


if __name__ == "__main__":
    root = tk.Tk()
    app = ComponentRecognitionApp(root)
    root.mainloop()