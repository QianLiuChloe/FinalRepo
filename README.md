
# Building Drawing Information Extraction and Estimation Tool

An automated tool developed to streamline the extraction of information and perform estimations from construction drawings in PDF format.

## Project Overview

This tool is designed to help users efficiently analyze and quantify data from architectural drawings, focusing on dimensions, quantities, and other essential metrics for construction components. It aims to enhance workflow efficiency, reduce manual errors, and provide accurate data for project cost management.

### Key Features
- **Drawing Conversion**: Splits multi-page PDF files into single-page PDFs and converts them to image format (JPG) for further processing.
- **Drawing Analysis**:
  - **Table Segmentation**: Detects table areas in drawings using YOLOv8 and separates tables for individual analysis.
  - **Text Extraction**: Extracts text from tables using PaddleOCR and exports results to Excel format.
  - **Component Dimension Parsing**: Parses dimensional data, calculates volumes, and updates the extracted table.
  - **Quantity Recognition**: Identifies and counts specific components (e.g., footings) using YOLO technology.
  - **Table Merging**: Combines extracted data and component counts into a final report table for comprehensive analysis.

## Installation Requirements

### Hardware
- **OS**: Windows 10 or 11
- **CPU**: Intel Core i5 (13th generation) or higher
- **RAM**: Minimum of 64GB
- **Graphics Card**: NVIDIA Graphics Card
- **Storage**: 1TB of free disk space

### Software
- **Anaconda**: Latest version
- **Pycharm/VS Code**: Latest version

### Setup
1. **Install Required Software**:
   - Anaconda: [Download](https://www.anaconda.com/download/success)
   - PyCharm: [Download](https://www.jetbrains.com/pycharm/download/?section=windows) (VS Code can also be used)
2. **Clone the Repository**:
   ```bash
   git clone https://github.com/QianLiuChloe/FinalRepo.git
   ```
   Place the project folder in disk D and rename it to `integrated_ui` for seamless setup.
3. **Configure CUDA and Conda Environment**:
   - CUDA: Version 11.1 ([Download](https://developer.nvidia.com/cuda-11.1.0-download-archive))
   - CuDNN: Version 8.05 for CUDA 11.1 ([Download](https://developer.nvidia.com/rdp/cudnn-archive))
   - Conda Environment:
     ```bash
     conda env create –file YOURPATH/environment.yml
     ```
     Replace `YOURPATH` with the project's path.

## Usage Instructions

### Step 1: PDF Conversion
1. Run `DrawingConverter.py`.
2. Choose the file path and output path.
3. Convert multi-page PDFs into single-page files and JPG images.

### Step 2: Drawing Analysis
1. Place JPG files in the `source` folder.
2. Run `mainwindow.py` and upload the drawings.
3. Start the analysis and follow on-screen instructions for table extraction, processing, and merging.

### Testing Examples
Examples for typical input and output cases are provided in the user manual for guidance.


## Acknowledgments
University of South Australia, Group: 2024-SP5-02
