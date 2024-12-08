import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image_path = filedialog.askopenfilename()
        self.image = Image.open(self.image_path)
        self.tk_image = ImageTk.PhotoImage(self.image)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        self.end_x, self.end_y = (event.x, event.y)
        self.save_cropped_image()

    def save_cropped_image(self):
        if self.start_x and self.start_y and self.end_x and self.end_y:
            box = (self.start_x, self.start_y, self.end_x, self.end_y)
            cropped_image = self.image.crop(box)
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if save_path:
                cropped_image.save(save_path)

if __name__ == "__main__":
    root = tk.Tk()
    editor = ImageEditor(root)
    root.mainloop()