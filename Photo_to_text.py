import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance
import random, os

# Compatibility for Pillow resampling
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS

class PhotoToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo → Text Mosaic")

        self.bg_images = []
        self.text_images = []
        self.generated_img = None
        self.preview_tk = None

        # --- Top controls frame ---
        top = tk.Frame(root)
        top.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

        # left column
        left = tk.Frame(top)
        left.pack(side=tk.LEFT, anchor=tk.N)
        tk.Button(left, text="Load Background Images", command=self.load_bg_images).grid(row=0, column=0, sticky="ew", pady=2)
        self.bg_listbox = tk.Listbox(left, height=4, width=30)
        self.bg_listbox.grid(row=1, column=0, pady=2)
        tk.Button(left, text="Remove Selected BG", command=self.remove_bg_image).grid(row=2, column=0, sticky="ew", pady=2)

        tk.Button(left, text="Load Text Images", command=self.load_text_images).grid(row=3, column=0, sticky="ew", pady=2)
        self.text_listbox = tk.Listbox(left, height=4, width=30)
        self.text_listbox.grid(row=4, column=0, pady=2)
        tk.Button(left, text="Remove Selected Text", command=self.remove_text_image).grid(row=5, column=0, sticky="ew", pady=2)

        # middle column
        mid = tk.Frame(top)
        mid.pack(side=tk.LEFT, padx=12)
        tk.Label(mid, text="Text:").grid(row=0, column=0, sticky="w")
        self.text_entry = tk.Text(mid, width=20, height=4)
        self.text_entry.insert("1.0", "HELLO")
        self.text_entry.grid(row=1, column=0, pady=2, sticky="w")
        self.text_entry.bind("<Shift-Return>", self.shift_enter_newline)

        tk.Label(mid, text="Canvas W x H (px)").grid(row=2, column=0, sticky="w")
        whf = tk.Frame(mid); whf.grid(row=3, column=0, pady=2, sticky="w")
        self.canvas_w_entry = tk.Entry(whf, width=6); self.canvas_w_entry.pack(side=tk.LEFT)
        self.canvas_w_entry.insert(0, "1200")
        tk.Label(whf, text="×").pack(side=tk.LEFT, padx=4)
        self.canvas_h_entry = tk.Entry(whf, width=6); self.canvas_h_entry.pack(side=tk.LEFT)
        self.canvas_h_entry.insert(0, "800")
        tk.Label(mid, text="Font Size (px)").grid(row=4, column=0, sticky="w")
        self.font_size_entry = tk.Entry(mid, width=8)
        self.font_size_entry.insert(0, "300")
        self.font_size_entry.grid(row=5, column=0, pady=2, sticky="w")

        tk.Label(mid, text="Line Spacing (px)").grid(row=6, column=0, sticky="w")
        self.line_spacing_entry = tk.Entry(mid, width=8)
        self.line_spacing_entry.insert(0, "10")  # default 10 px spacing
        self.line_spacing_entry.grid(row=7, column=0, pady=2, sticky="w")

        # right column
        right = tk.Frame(top)
        right.pack(side=tk.LEFT, padx=12)
        tk.Label(right, text="Tile size (text px)").grid(row=0, column=0, sticky="w")
        self.tile_size_entry = tk.Entry(right, width=8)
        self.tile_size_entry.insert(0, "24")
        self.tile_size_entry.grid(row=1, column=0, pady=2, sticky="w")
        tk.Label(right, text="BG grid N (N×N tiles)").grid(row=2, column=0, sticky="w")
        self.bg_grid_entry = tk.Entry(right, width=8)
        self.bg_grid_entry.insert(0, "2")
        self.bg_grid_entry.grid(row=3, column=0, pady=2, sticky="w")
        tk.Label(right, text="BG color adjust").grid(row=4, column=0, sticky="w")
        self.bg_color_scale = tk.Scale(right, from_=0.1, to=2.0, resolution=0.1, orient="horizontal", length=140)
        self.bg_color_scale.set(1.0)
        self.bg_color_scale.grid(row=5, column=0, pady=2)
        tk.Label(right, text="Text color adjust").grid(row=6, column=0, sticky="w")
        self.text_color_scale = tk.Scale(right, from_=0.1, to=2.0, resolution=0.1, orient="horizontal", length=140)
        self.text_color_scale.set(1.0)
        self.text_color_scale.grid(row=7, column=0, pady=2)

        # generate/save buttons
        btns = tk.Frame(top)
        btns.pack(side=tk.RIGHT, anchor="n")
        tk.Button(btns, text="Generate", command=self.generate_image, width=12).pack(pady=4)
        tk.Button(btns, text="Save (png)", command=self.save_image, width=12).pack(pady=4)

        # preview area
        preview_frame = tk.Frame(root)
        preview_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.preview_canvas = tk.Canvas(preview_frame, bg="black")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        self.preview_canvas.bind("<Configure>", lambda e: self.update_preview())

    # ----------------- multi-line support -----------------
    def shift_enter_newline(self, event):
        self.text_entry.insert(tk.INSERT, "\n")
        return "break"

    # ----------------- file loaders -----------------
    def load_bg_images(self):
        files = filedialog.askopenfilenames(title="Select background tiles", filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not files: return
        for f in files:
            try:
                img = Image.open(f).convert("RGBA")
                self.bg_images.append(img)
                self.bg_listbox.insert(tk.END, os.path.basename(f))
            except: pass

    def load_text_images(self):
        files = filedialog.askopenfilenames(title="Select text tiles", filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not files: return
        for f in files:
            try:
                img = Image.open(f).convert("RGBA")
                self.text_images.append(img)
                self.text_listbox.insert(tk.END, os.path.basename(f))
            except: pass

    # ----------------- remove selected -----------------
    def remove_bg_image(self):
        sel = self.bg_listbox.curselection()
        if not sel: return
        for i in reversed(sel):
            del self.bg_images[i]
            self.bg_listbox.delete(i)

    def remove_text_image(self):
        sel = self.text_listbox.curselection()
        if not sel: return
        for i in reversed(sel):
            del self.text_images[i]
            self.text_listbox.delete(i)

    # ----------------- generation -----------------
    def generate_image(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        if not self.text_images or not text:
            messagebox.showerror("Error", "Please load text tiles and enter text.")
            return
        try:
            W = int(self.canvas_w_entry.get())
            H = int(self.canvas_h_entry.get())
            font_size = max(4,int(self.font_size_entry.get()))
            tile_size = max(1,int(self.tile_size_entry.get()))
            bg_grid = max(1,int(self.bg_grid_entry.get()))
            line_spacing = max(0,int(self.line_spacing_entry.get()))
        except:
            messagebox.showerror("Error","Check numeric inputs")
            return

        out = Image.new("RGBA",(W,H),(255,255,255,255))

        # background
        if self.bg_images:
            tile_w = W // bg_grid
            tile_h = H // bg_grid
            for y in range(bg_grid):
                for x in range(bg_grid):
                    tile = random.choice(self.bg_images).resize((tile_w,tile_h),RESAMPLE)
                    enhancer = ImageEnhance.Color(tile)
                    tile = enhancer.enhance(self.bg_color_scale.get())
                    out.paste(tile,(x*tile_w,y*tile_h),tile)

        # text mask
        mask = Image.new("L",(W,H),0)
        md = ImageDraw.Draw(mask)
        try: font = ImageFont.truetype("arial.ttf",font_size)
        except: font = ImageFont.load_default()

        # multi-line drawing with line spacing
        lines = text.splitlines()
        line_sizes = [md.textbbox((0,0), line, font=font) for line in lines]
        line_widths = [bbox[2]-bbox[0] for bbox in line_sizes]
        line_heights = [bbox[3]-bbox[1] for bbox in line_sizes]
        total_h = sum(line_heights) + line_spacing*(len(lines)-1)
        y_offset = (H - total_h)//2

        for i, line in enumerate(lines):
            x_offset = (W - line_widths[i])//2
            md.text((x_offset, y_offset), line, fill=255, font=font)
            y_offset += line_heights[i] + line_spacing

        mask_pixels = mask.load()

        # dynamic fill threshold based on tile size
        threshold = 0.2 if tile_size<=10 else 0.35 if tile_size<=30 else 0.5

        # fill text
        for y in range(0,H,tile_size):
            for x in range(0,W,tile_size):
                count=0
                for yy in range(tile_size):
                    for xx in range(tile_size):
                        if x+xx < W and y+yy < H:
                            if mask_pixels[x+xx,y+yy]>0: count+=1
                ratio = count/(tile_size*tile_size)
                if ratio>=threshold:
                    tile = random.choice(self.text_images).resize((tile_size,tile_size),RESAMPLE)
                    enhancer = ImageEnhance.Color(tile)
                    tile = enhancer.enhance(self.text_color_scale.get())
                    out.paste(tile,(x,y),tile)

        self.generated_img = out
        self.update_preview()

    # ----------------- preview -----------------
    def update_preview(self):
        if self.generated_img is None: return
        c_w = max(1,self.preview_canvas.winfo_width())
        c_h = max(1,self.preview_canvas.winfo_height())
        img_w,img_h = self.generated_img.size
        ratio = min(c_w/img_w, c_h/img_h)
        disp_w,disp_h = int(img_w*ratio), int(img_h*ratio)
        disp = self.generated_img.resize((disp_w,disp_h),RESAMPLE)
        self.preview_tk = ImageTk.PhotoImage(disp)
        self.preview_canvas.delete("all")
        x=(c_w-disp_w)//2
        y=(c_h-disp_h)//2
        self.preview_canvas.create_image(x,y,anchor="nw",image=self.preview_tk)

    # ----------------- save -----------------
    def save_image(self):
        if not self.generated_img:
            messagebox.showerror("Error","Generate image first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG","*.png")])
        if path:
            self.generated_img.save(path)
            messagebox.showinfo("Saved", f"Saved to: {path}")

if __name__=="__main__":
    root = tk.Tk()
    app = PhotoToTextApp(root)
    root.mainloop()
