# 🖼️ JPEG to ASCII Converter (GUI)

A simple Python GUI tool that converts JPEG (and other image formats) into ASCII art.

## 🚀 Features
- Open JPEG, PNG, BMP images
- Adjustable output width
- Custom character sets
- Invert brightness option
- Save ASCII art to `.txt`

## 🛠️ Installation
Clone the repo and install dependencies:
```bash
git clone https://github.com/yourusername/jpeg-to-ascii.git
cd jpeg-to-ascii
pip install -r requirements.txt

Photo → Text Mosaic

Turn your text into a beautiful mosaic using your own images for both background and text tiles. Fully interactive GUI tool built in Python with Tkinter and Pillow.

Features

Text to Image Mosaic: Transform any text into a mosaic of images.

Custom Background: Use multiple images for the background and adjust their grid and color intensity.

Text Tiles: Fill your text with custom images and adjust their color and size.

Multi-line Text Support: Supports multi-line text with Shift+Enter.

Adjustable Canvas Size: Set any width and height for your output image.

Line Spacing: Control the vertical spacing between lines of text.

Live Preview: See your mosaic directly in the app before saving.

Save to PNG: Export your creations easily.

Installation

Make sure you have Python 3.x installed.

Install required packages:

pip install pillow

Usage

Run the app:

python Photo_to_text.py


Load background images and text tile images.

Enter your text. Use Shift+Enter for line breaks.

Adjust:

Canvas width & height

Font size

Tile size for text

Background grid size

Line spacing

Color adjustment sliders for both text and background

Click Generate to preview your mosaic.

Click Save to export as PNG.

Supported Formats

Images: PNG, JPG, JPEG, BMP

Notes

Large canvas sizes and small tile sizes may take longer to generate.

Font fallback: If arial.ttf is not found, the default PIL font is used.
