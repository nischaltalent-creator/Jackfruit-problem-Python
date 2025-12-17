import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def open_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if not file_path:
        return

    img = Image.open(file_path).convert("RGB")
    pixels = np.array(img.getdata())
    total_pixels = pixels.shape[0]

    # Strict dominance classification
    r, g, b = pixels[:, 0], pixels[:, 1], pixels[:, 2]
    red_mask   = (r > g) & (r > b)
    green_mask = (g > r) & (g > b)
    blue_mask  = (b > r) & (b > g)
    neutral_mask = ~(red_mask | green_mask | blue_mask)

    red_pixels     = int(np.sum(red_mask))
    green_pixels   = int(np.sum(green_mask))
    blue_pixels    = int(np.sum(blue_mask))
    neutral_pixels = int(np.sum(neutral_mask))

    status_text.set(f"Opened: {file_path}")

    # Clear previous content frames
    for widget in left_panel.winfo_children():
        widget.destroy()
    for widget in right_panel.winfo_children():
        widget.destroy()

    # Thumbnail (left panel, row 0)
    thumb = img.copy()
    thumb.thumbnail((220, 220))
    thumb_tk = ImageTk.PhotoImage(thumb)
    thumb_label = tk.Label(left_panel, image=thumb_tk, bg=gui_bg)
    thumb_label.image = thumb_tk
    thumb_label.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

    # Swatches and counts (left panel, row 1)
    swatch_frame = tk.Frame(left_panel, bg=gui_bg)
    swatch_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
    left_panel.grid_columnconfigure(0, weight=1)

    header = tk.Label(swatch_frame, text="Dominant pixel counts", font=("Arial", 14, "bold"),
                      bg=gui_bg, fg="white")
    header.pack(anchor="w", pady=(0, 6))

    def add_swatch(frame, color_hex, text):
        row = tk.Frame(frame, bg=gui_bg)
        row.pack(fill="x", expand=True, pady=6, anchor="w")
        swatch = tk.Canvas(row, width=30, height=30, bg=gui_bg, highlightthickness=0)
        swatch.create_oval(2, 2, 28, 28, fill=color_hex, outline=color_hex)
        swatch.pack(side="left", padx=10)
        label = tk.Label(row, text=text, font=("Arial", 12), bg=gui_bg, fg="white", anchor="w")
        label.pack(side="left", padx=10, fill="x", expand=True)

    add_swatch(swatch_frame, "#e53935", f"Red-dominant: {red_pixels}")
    add_swatch(swatch_frame, "#43a047", f"Green-dominant: {green_pixels}")
    add_swatch(swatch_frame, "#1e88e5", f"Blue-dominant: {blue_pixels}")
    add_swatch(swatch_frame, "#9e9e9e", f"Neutral/Gray: {neutral_pixels}")

    # Bar chart (right panel, row 0)
    fig, ax = plt.subplots(figsize=(5.5, 4.2))
    categories = ["Red", "Green", "Blue", "Neutral"]
    values = [red_pixels, green_pixels, blue_pixels, neutral_pixels]
    colors = ["#e53935", "#43a047", "#1e88e5", "#9e9e9e"]

    ax.bar(categories, values, color=colors)
    ax.set_title("Pixel count by dominant channel", fontsize=12, fontweight="bold", color="white")
    ax.set_ylabel("Pixels", color="white")
    ax.tick_params(axis='x', colors="white")
    ax.tick_params(axis='y', colors="white")
    fig.patch.set_facecolor(gui_bg)
    ax.set_facecolor(gui_bg)
    for i, v in enumerate(values):
        ax.text(i, v, f"{v}", ha="center", va="bottom", fontsize=10, color="white")
    fig.tight_layout()

    bar_canvas = FigureCanvasTkAgg(fig, master=right_panel)
    bar_canvas.draw()
    bar_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    right_panel.grid_rowconfigure(0, weight=1)
    right_panel.grid_columnconfigure(0, weight=1)

def exit_app():
    root.quit()

# GUI setup
root = tk.Tk()
root.title("RGB Pixellator")
root.geometry("1000x750")

# Use a softer shade of black/charcoal gray
gui_bg = "#121212"
status_bg = "#1e1e1e"

root.configure(bg=gui_bg)

# Menu bar
menubar = tk.Menu(root, tearoff=0)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Open image", command=open_image)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_app)
menubar.add_cascade(label="File", menu=file_menu)
root.config(menu=menubar)

# Title
title_label = tk.Label(
    root, text="RGB Pixellator", font=("Helvetica", 24, "bold"), bg=gui_bg, fg="white"
)
title_label.pack(pady=20)

# Open button (white background)
open_button = tk.Button(
    root, text="Open image", command=open_image,
    font=("Arial", 14, "bold"), bg="white", fg="black",
    activebackground="#ddd", padx=20, pady=10
)
open_button.pack(pady=10)

# Main content frame (grid layout)
content = tk.Frame(root, bg=gui_bg)
content.pack(pady=20, fill="both", expand=True)

# Two panels: left for thumbnail + swatches, right for bar chart
left_panel = tk.Frame(content, bg=gui_bg)
right_panel = tk.Frame(content, bg=gui_bg)

left_panel.grid(row=0, column=0, sticky="nsew")
right_panel.grid(row=0, column=1, sticky="nsew")

content.grid_columnconfigure(0, weight=1, minsize=360)
content.grid_columnconfigure(1, weight=2)
content.grid_rowconfigure(0, weight=1)

# Status bar
status_text = tk.StringVar()
status_label = tk.Label(
    root, textvariable=status_text, font=("Arial", 10),
    bg=status_bg, fg="white", anchor="w"
)
status_label.pack(side="bottom", fill="x")

root.mainloop()