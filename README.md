Photo → Text Mosaic

Transform your text into beautiful mosaics using your own images for background and text tiles. Fully interactive GUI tool built with Python Tkinter and Pillow.

Features

Text to Mosaic – Create text using your chosen images.

Custom Background – Use multiple background images with adjustable grid and color intensity.

Text Tile Images – Fill your text with images, adjusting color and size.

Multi-Line Text Support – Use Shift+Enter for line breaks.

Adjustable Line Spacing – Control vertical spacing between lines.

Custom Canvas Size – Define width and height of the output image.

Live Preview – See the mosaic in-app before saving.

Save to PNG – Easily export creations.

Installation
git clone https://github.com/yourusername/photo-to-text.git
cd photo-to-text
pip install pillow

Usage

Run the app:

python Photo_to_text.py


Load background images and text tile images.

Enter your text (use Shift+Enter for new lines).

Adjust settings:

Canvas width & height

Font size

Tile size for text

Background grid size

Line spacing

Color adjustments for text and background

Click Generate to preview the mosaic.

Click Save to export as PNG.

Supported Formats

PNG, JPG, JPEG, BMP

Notes

Large canvas sizes with small tile sizes may take longer to generate.

Font fallback: If arial.ttf is not found, a default PIL font is used.
