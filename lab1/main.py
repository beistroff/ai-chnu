""""This code implements all requirements of Lab 1"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import numpy as np

"""Class for processing images. Note: Some functions may need to be moved out of this class."""
class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")

        # Add variables to track cropping coordinates
        self.cropping = False
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None
        self.cropped_image = None
        self.image_for_vector_calculation = None

        # Left frame for pictures
        self.left_frame = tk.Frame(root)
        self.left_frame.grid(column=0, row=0, rowspan=10, padx=10, pady=10)

        # Right frame for rest of components
        self.right_frame = tk.Frame(root)
        self.right_frame.grid(column=1, row=0, padx=10, pady=10)

        # Set initial size for the picture
        self.image_label = tk.Canvas(self.left_frame, width=300, height=300) # Set initial size for picture
        self.image_label.pack()

        self.upload_button = tk.Button(self.right_frame, text="Upload Image", command=self.upload_image)
        self.upload_button.grid(column=0, row=0)

        self.threshold_label = tk.Label(self.right_frame, text="Black Threshold:")
        self.threshold_label.grid(column=0, row=1)

        self.threshold_entry = tk.Entry(self.right_frame)
        self.threshold_entry.grid(column=0, row=2)

        self.sector_label = tk.Label(self.right_frame, text="Number of Sectors:")
        self.sector_label.grid(column=0, row=3)

        self.sector_selector = ttk.Spinbox(self.right_frame, from_=2, to=10)
        self.sector_selector.grid(column=0, row=4)

        self.process_button = tk.Button(self.right_frame, text="Process Image", command=self.process_image)
        self.process_button.grid(column=0, row=5)

        self.feature_vector_label = tk.Label(self.right_frame, text="Feature Vector:")
        self.feature_vector_label.grid(column=0, row=6)

        self.feature_vector_text = tk.Text(self.right_frame, height=10, width=50)
        self.feature_vector_text.grid(column=0, row=7)

        self.normalized_vector_label = tk.Label(self.right_frame, text="Normalized Vector (S1):")
        self.normalized_vector_label.grid(column=0, row=8)

        # For normalization by module
        self.normalized_vector_text_s1 = tk.Text(self.right_frame, height=2, width=50)
        self.normalized_vector_text_s1.grid(column=0, row=9)

        self.normalized_vector_label = tk.Label(self.right_frame, text="Normalized Vector For Module:")
        self.normalized_vector_label.grid(column=0, row=10)

        # For normalization by modulus
        self.normalized_vector_text_s2 = tk.Text(self.right_frame, height=2, width=50)
        self.normalized_vector_text_s2.grid(column=0, row=11)

        # Bind mouse events to image_label for cropping
        self.image_label.bind("<ButtonPress-1>", self.on_crop_start)
        self.image_label.bind("<B1-Motion>", self.on_crop_drag)
        self.image_label.bind("<ButtonRelease-1>", self.on_crop_end)

        self.image = None
        self.processed_image = None


    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.display_image(self.image)



    def display_image(self, image):
        max_width, max_height = 1360, 1080

        original_width, original_height = image.size
        scaling_factor = min(max_width / original_width, max_height / original_height, 1)

        new_width = int(original_width * scaling_factor)
        new_height = int(original_height * scaling_factor)

        # Resize the image and display it
        img = image.resize((new_width, new_height), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)

        # Update size of the canvas based on picture
        self.image_label.config(width=new_width, height=new_height)
        self.image_label.create_image(0, 0, anchor=tk.NW, image=img)
        self.image_label.image = img  # Save reference of pic in order to avoid memory cleaning


    def process_image(self):
        if self.image is None and self.cropped_image is None:
            messagebox.showerror("Error", "No image uploaded")
            return

        threshold = self.threshold_entry.get()
        if not threshold.isdigit():
            messagebox.showerror("Error", "Invalid threshold value")
            return

        threshold = int(threshold)

        # Use the cropped image if it exists, otherwise fall back to the original image
        if self.cropped_image:
            image_to_process = self.cropped_image.convert("L")
        else:
            image_to_process = self.image.convert("L")

        # Apply black/white threshold to the image
        self.processed_image = image_to_process.point(lambda p: 255 if p > threshold else 0, '1')

        # Make a copy for feature vector calculation
        self.image_for_vector_calculation = self.processed_image.copy()

        # Perform sector segmentation and display the image
        self.segment_and_draw_sectors()
        self.display_image(self.processed_image)
        self.calculate_feature_vector()


    def segment_and_draw_sectors(self):
        draw = ImageDraw.Draw(self.processed_image)
        width, height = self.processed_image.size
        center_x, center_y = width - 1, height - 1

        sectors = int(self.sector_selector.get())
        sector_angles = 90 / sectors

        for i in range(sectors + 1):
            angle = np.radians(i * sector_angles)

            line_end_x = center_x - int(np.cos(angle) * max(width, height) * 2)
            line_end_y = center_y - int(np.sin(angle) * max(width, height) * 2)

            draw.line((center_x, center_y, line_end_x, line_end_y), fill="red", width=2)


    def calculate_feature_vector(self):
        # img_array = np.array(self.processed_image)
        img_array = np.array(self.image_for_vector_calculation)
        height, width = img_array.shape
        total_black_pixels = np.sum(img_array == 0)
        center_x, center_y = width - 1, 0

        sectors = int(self.sector_selector.get())
        sector_angles = 90 / sectors

        feature_vector = []

        for i in range(sectors):
            start_angle = i * sector_angles
            end_angle = (i + 1) * sector_angles

            sector_mask = np.zeros_like(img_array, dtype=bool)

            for y in range(height):
                for x in range(width):
                    dx = x - center_x
                    dy = center_y - y
                    angle = (np.degrees(np.arctan2(dy, dx)) + 90) % 90

                    if start_angle <= angle < end_angle:
                        sector_mask[y, x] = True

            sector_black_pixels = np.sum(np.logical_and(img_array == 0, sector_mask))
            feature_vector.append(sector_black_pixels)

        # Clean up and print output about vectors
        self.feature_vector_text.delete(1.0, tk.END)
        self.normalized_vector_text_s1.delete(1.0, tk.END)
        self.normalized_vector_text_s2.delete(1.0, tk.END)

        # Format text
        feature_vector_str = ', '.join([f's{i+1}: {count}' for i, count in enumerate(feature_vector)])
        self.feature_vector_text.insert(tk.END, f"[{feature_vector_str}]")

        # Normalization for sum
        normalized_vector = [x / total_black_pixels if total_black_pixels > 0 else 0 for x in feature_vector]
        normalized_vector_str = ', '.join([f'(s{i+1}, {val:.4f})' for i, val in enumerate(normalized_vector)])
        self.normalized_vector_text_s1.insert(tk.END, f"[{normalized_vector_str}]")

        # Normalization for module
        max_value = max(feature_vector) if feature_vector else 1  # Avoid division by 0
        normalized_vector_s2 = [x / max_value if max_value > 0 else 0 for x in feature_vector]
        normalized_vector_str_s2 = ', '.join([f'(M{i + 1}, {val:.4f})' for i, val in enumerate(normalized_vector_s2)])
        self.normalized_vector_text_s2.insert(tk.END, f"[{normalized_vector_str_s2}]")


    def on_crop_start(self, event):
        """Start cropping when the user clicks on the image."""
        self.cropping = True
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.image_label.delete(self.rect)  # Remove any previous selection

        self.rect = self.image_label.create_rectangle(
            self.start_x, 
            self.start_y, 
            self.start_x, 
            self.start_y, 
            outline='red'
        )


    def on_crop_drag(self, event):
        """Draw the cropping rectangle as the user drags the mouse."""
        if self.cropping:
            end_x, end_y = event.x, event.y
            if self.rect:
                self.image_label.delete(self.rect)  # Remove the old rectangle
            self.rect = self.image_label.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="blue")


    def on_crop_end(self, event):
        if self.cropping:
            self.end_x = self.image_label.coords(self.rect)[2]
            self.end_y = self.image_label.coords(self.rect)[3]
            self.crop_image(self.start_x, self.start_y, self.end_x, self.end_y)
            self.cropping = False


    def crop_image(self, x1, y1, x2, y2):
        """"Function for croping image"""
        if self.image is None:
            messagebox.showerror("Error", "No image uploaded")
            return
        
        # Get size of image
        img_width, img_height = self.image.size

        x1 = max(0, min(x1, img_width))
        y1 = max(0, min(y1, img_height))
        x2 = max(0, min(x2, img_width))
        y2 = max(0, min(y2, img_height))

        if self.image is not None:
            self.cropped_image = self.image.crop((x1, y1, x2, y2))
            self.display_image(self.cropped_image)  # Display the cropped image


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
