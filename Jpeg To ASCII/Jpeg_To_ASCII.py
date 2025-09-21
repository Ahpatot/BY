"""
Image to ASCII Converter - GUI (Tkinter + Pillow)

How to run:
1) Create a virtualenv (optional) and install Pillow:
   pip install Pillow
2) Run:
   python image_to_ascii.py

Features:
- Open an image file
- Set output width (characters)
- Choose character set (dense or sparse)
- Invert brightness mapping
- Preview original image and ASCII output (monospaced)
- Save ASCII to .txt or copy to clipboard

This is a single-file script intended as a starting point. You can
package it with pyinstaller if you want a standalone executable.

"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import io
import sys

# Character sets from dark->light
CHAR_SETS = {
    'Standard (dense)': "@%#*+=-:. ",
    'Blocks (very dense)': "@#S%?*+;:,. ",
    'Simple (sparse)': "@OXx+-. "
}

DEFAULT_WIDTH = 100

def map_pixels_to_ascii(image, width=DEFAULT_WIDTH, chars="@%#*+=-:. ", invert=False):
    # Convert to grayscale
    gray = image.convert('L')
    original_width, original_height = gray.size

    # Approximate character aspect ratio: characters are taller than wide; adjust height
    aspect_ratio = 0.55  # tweak this for better proportions
    new_width = max(1, int(width))
    new_height = max(1, int(aspect_ratio * original_height * (new_width / original_width)))

    resized = gray.resize((new_width, new_height))
    pixels = list(resized.getdata())

    if invert:
        pixels = [255 - p for p in pixels]

    # Map pixel to char
    scale = (len(chars) - 1) / 255
    ascii_chars = [chars[int(p * scale)] for p in pixels]

    # Group into lines
    lines = ["".join(ascii_chars[i:i+new_width]) for i in range(0, len(ascii_chars), new_width)]
    return "\n".join(lines)


class ImageToAsciiApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Image → ASCII Converter')
        self.root.geometry('1000x700')
        self.image = None
        self.tk_preview = None

        self._build_ui()

    def _build_ui(self):
        # Top frame for controls
        ctrl_frame = ttk.Frame(self.root, padding=8)
        ctrl_frame.pack(side=tk.TOP, fill=tk.X)

        open_btn = ttk.Button(ctrl_frame, text='Open Image', command=self.open_image)
        open_btn.pack(side=tk.LEFT)

        ttk.Label(ctrl_frame, text='Width:').pack(side=tk.LEFT, padx=(10,0))
        self.width_var = tk.IntVar(value=DEFAULT_WIDTH)
        width_spin = ttk.Spinbox(ctrl_frame, from_=10, to=400, textvariable=self.width_var, width=6)
        width_spin.pack(side=tk.LEFT)

        ttk.Label(ctrl_frame, text='Charset:').pack(side=tk.LEFT, padx=(10,0))
        self.charset_var = tk.StringVar(value='Standard (dense)')
        charset_menu = ttk.OptionMenu(ctrl_frame, self.charset_var, 'Standard (dense)', *CHAR_SETS.keys())
        charset_menu.pack(side=tk.LEFT)

        self.invert_var = tk.BooleanVar(value=False)
        invert_cb = ttk.Checkbutton(ctrl_frame, text='Invert', variable=self.invert_var)
        invert_cb.pack(side=tk.LEFT, padx=(10,0))

        convert_btn = ttk.Button(ctrl_frame, text='Convert', command=self.convert)
        convert_btn.pack(side=tk.LEFT, padx=(10,0))

        save_btn = ttk.Button(ctrl_frame, text='Save ASCII', command=self.save_ascii)
        save_btn.pack(side=tk.LEFT, padx=(10,0))

        copy_btn = ttk.Button(ctrl_frame, text='Copy to Clipboard', command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=(10,0))

        # Main panes: left = original preview, right = ascii text
        main_pane = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_pane, width=350)
        right_frame = ttk.Frame(main_pane)

        main_pane.add(left_frame, weight=1)
        main_pane.add(right_frame, weight=3)

        # Left: image preview
        ttk.Label(left_frame, text='Original Image Preview').pack(anchor=tk.W)
        self.canvas = tk.Canvas(left_frame, bg='#222', height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Right: ASCII output
        top_right = ttk.Frame(right_frame)
        top_right.pack(fill=tk.X)
        ttk.Label(top_right, text='ASCII Output (monospace)').pack(anchor=tk.W)

        txt_frame = ttk.Frame(right_frame)
        txt_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.ascii_text = tk.Text(txt_frame, wrap=tk.NONE, font=('Courier', 6), bg='#111', fg='#e6e6e6')
        self.ascii_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        yscroll = ttk.Scrollbar(txt_frame, orient=tk.VERTICAL, command=self.ascii_text.yview)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.ascii_text['yscrollcommand'] = yscroll.set

        xscroll = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=self.ascii_text.xview)
        xscroll.pack(fill=tk.X)
        self.ascii_text['xscrollcommand'] = xscroll.set

        # Footer
        footer = ttk.Frame(self.root, padding=6)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        self.status = tk.StringVar(value='Ready')
        ttk.Label(footer, textvariable=self.status).pack(side=tk.LEFT)

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.bmp;*.gif'), ('All files', '*.*')])
        if not path:
            return
        try:
            img = Image.open(path).convert('RGB')
            self.image = img
            self.show_preview(img)
            self.status.set(f'Loaded: {path}')
        except Exception as e:
            messagebox.showerror('Error', f'Unable to open image:\n{e}')

    def show_preview(self, pil_image):
        # Resize preview to canvas size while keeping aspect
        canvas_w = max(200, self.canvas.winfo_width() or 300)
        canvas_h = max(200, self.canvas.winfo_height() or 300)
        img = pil_image.copy()
        img.thumbnail((canvas_w, canvas_h))
        self.tk_preview = ImageTk.PhotoImage(img)
        self.canvas.delete('all')
        self.canvas.create_image(canvas_w//2, canvas_h//2, image=self.tk_preview, anchor=tk.CENTER)

    def convert(self):
        if not self.image:
            messagebox.showwarning('No image', 'Please open an image first.')
            return
        width = self.width_var.get()
        charset = CHAR_SETS.get(self.charset_var.get(), CHAR_SETS['Standard (dense)'])
        invert = bool(self.invert_var.get())
        try:
            ascii_art = map_pixels_to_ascii(self.image, width=width, chars=charset, invert=invert)
            self.ascii_text.delete('1.0', tk.END)
            self.ascii_text.insert(tk.END, ascii_art)
            self.status.set('Conversion complete')
        except Exception as e:
            messagebox.showerror('Conversion error', str(e))

    def save_ascii(self):
        content = self.ascii_text.get('1.0', tk.END).rstrip()
        if not content:
            messagebox.showwarning('Empty', 'No ASCII content to save. Convert an image first.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.status.set(f'Saved ASCII to: {path}')
        except Exception as e:
            messagebox.showerror('Save error', str(e))

    def copy_to_clipboard(self):
        content = self.ascii_text.get('1.0', tk.END).rstrip()
        if not content:
            messagebox.showwarning('Empty', 'No ASCII content to copy. Convert an image first.')
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status.set('ASCII copied to clipboard')
        except Exception as e:
            messagebox.showerror('Clipboard error', str(e))


if __name__ == '__main__':
    root = tk.Tk()
    app = ImageToAsciiApp(root)
    # If the window is resized, refresh preview
    def on_resize(event):
        if app.image:
            app.show_preview(app.image)
    root.bind('<Configure>', on_resize)
    root.mainloop()
