import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps, ImageDraw
import numpy as np


class ImageProcessor:
    def __init__(self, root, vectors_s1_class1_avg, vectors_s1_class2_avg, vectors_s1_class3_avg,
                 vectors_m1_class1_avg, vectors_m1_class2_avg, vectors_m1_class3_avg):
        self.root = root
        self.root.title("Image Processor")
        self.root.configure(bg="#F0F0F0")

        # Left frame
        self.left_frame = tk.Frame(root, bg="#FFFFFF", bd=2, relief=tk.RAISED)
        self.left_frame.grid(column=0, row=0, rowspan=10, padx=10, pady=10)

        # Right frame
        self.right_frame = tk.Frame(root, bg="#FFFFFF", bd=2, relief=tk.RAISED)
        self.right_frame.grid(column=1, row=0, padx=10, pady=10)

        # Додаємо елементи в лівий фрейм (картинка)
        self.image_label = tk.Canvas(self.left_frame, width=700, height=550, bg="#D9D9D9")
        self.image_label.pack()

        # Додаємо елементи в правий фрейм
        self.upload_button = tk.Button(self.right_frame, text="Upload Image", command=self.upload_image, bg="#4CAF50", fg="white", bd=0)
        self.upload_button.grid(column=0, row=0, padx=10, pady=5)

        # Black threshold field
        self.threshold_label = tk.Label(self.right_frame, text="Black Threshold:", bg="#FFFFFF")
        self.threshold_label.grid(column=0, row=1)

        self.threshold_entry = tk.Entry(self.right_frame)
        self.threshold_entry.grid(column=0, row=2, padx=10)

        self.process_button = tk.Button(self.right_frame, text="Process Image", command=self.process_image, bg="#2196F3", fg="white", bd=0)
        self.process_button.grid(column=0, row=5, padx=10, pady=5)

        self.feature_vector_label = tk.Label(self.right_frame, text="Feature Vector:", bg="#FFFFFF")
        self.feature_vector_label.grid(column=0, row=6)

        self.feature_vector_text = tk.Text(self.right_frame, height=3, width=50, bg="#F9F9F9", bd=1)
        self.feature_vector_text.grid(column=0, row=7, padx=10)

        self.class_vector_label_result = tk.Label(self.right_frame, text="Classification result:")
        self.class_vector_label_result.grid(column=0, row=8)

        self.class_vector_text_result = tk.Text(self.right_frame, height=3, width=42)
        self.class_vector_text_result.grid(column=0, row=9)

        self.class_vector_label_distance = tk.Label(self.right_frame, text="Calculated lengths:", bg="#FFFFFF")
        self.class_vector_label_distance.grid(column=0, row=10)

        self.class_vector_text_distance = tk.Text(self.right_frame, height=3, width=40, bg="#F9F9F9", bd=1)
        self.class_vector_text_distance.grid(column=0, row=11, padx=10)

        self.normalized_vector_label = tk.Label(self.right_frame, text="Normalized vector (S1):", bg="#FFFFFF")
        self.normalized_vector_label.grid(column=0, row=12)

        self.normalized_vector_text_s1 = tk.Text(self.right_frame, height=2, width=60, bg="#F9F9F9", bd=1)
        self.normalized_vector_text_s1.grid(column=0, row=13, padx=10)
    
        self.normalized_vector_label = tk.Label(self.right_frame, text="Normalized vector (M1):", bg="#FFFFFF")
        self.normalized_vector_label.grid(column=0, row=14)

        self.normalized_vector_text_s2 = tk.Text(self.right_frame, height=2, width=60, bg="#F9F9F9", bd=1)
        self.normalized_vector_text_s2.grid(column=0, row=15, padx=10)

        self.vector_label_s = tk.Label(self.right_frame, text="Class vectors S1 AVG:", bg="#FFFFFF")
        self.vector_label_s.grid(column=0, row=16)

        self.vector_text_s = tk.Text(self.right_frame, height=6, width=55, bg="#F9F9F9", bd=1)
        self.vector_text_s.grid(column=0, row=17, padx=10)

        self.vector_label_m = tk.Label(self.right_frame, text="Classes vectors M1 AVG:", bg="#FFFFFF")
        self.vector_label_m.grid(column=0, row=18)

        self.vector_text_m = tk.Text(self.right_frame, height=6, width=55, bg="#F9F9F9", bd=1)
        self.vector_text_m.grid(column=0, row=19, padx=10)

        # Add variables to track cropping coordinates
        self.cropping = False
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None
        self.cropped_image = None
        self.image_for_vector_calculation = None

        self.image = None
        self.processed_image = None

        # Bind mouse events to image_label for cropping
        self.image_label.bind("<ButtonPress-1>", self.on_crop_start)
        self.image_label.bind("<B1-Motion>", self.on_crop_drag)
        self.image_label.bind("<ButtonRelease-1>", self.on_crop_end)

        # AVG vectors
        self.vectors_s1_class1_avg = vectors_s1_class1_avg
        self.vectors_s1_class2_avg = vectors_s1_class2_avg
        self.vectors_s1_class3_avg = vectors_s1_class3_avg
        self.vectors_m1_class1_avg = vectors_m1_class1_avg
        self.vectors_m1_class2_avg = vectors_m1_class2_avg
        self.vectors_m1_class3_avg = vectors_m1_class3_avg

        self.display_vectors()

    def display_vectors(self):
        all_vectors_s = {
            "Class 1 Vector S1 Avg": self.vectors_s1_class1_avg,
            "Class 2 Vector S1 Avg": self.vectors_s1_class2_avg,
            "Class 3 Vector S1 Avg": self.vectors_s1_class3_avg,
        }

        all_vectors_m = {
            "Class 1 Vector M1 Avg": self.vectors_m1_class1_avg,
            "Class 2 Vector M1 Avg": self.vectors_m1_class2_avg,
            "Class 3 Vector M1 Avg": self.vectors_m1_class3_avg,
        }

        for class_name, vectors in all_vectors_s.items():
            self.vector_text_s.insert(tk.END, f"{class_name}: {[round(float(value), 4) for value in vectors]}\n")

        for class_name, vectors in all_vectors_m.items():
            self.vector_text_m.insert(tk.END, f"{class_name}: {[round(float(value), 4) for value in vectors]}\n")

    def upload_image(self):
        # Set the default directory
        default_dir = "D:\\university\\4d_course\\1st_term\\ai-labs\\ai-chnu\\lab2\\pictures\\check_images"
        
        file_path = filedialog.askopenfilename(initialdir=default_dir)
        
        if file_path:
            self.image = Image.open(file_path)
            self.display_image(self.image)

    def display_image(self, image):
        max_width, max_height = 800, 600

        original_width, original_height = image.size
        scaling_factor = min(max_width / original_width, max_height / original_height, 1)

        new_width = int(original_width * scaling_factor)
        new_height = int(original_height * scaling_factor)

        img = image.resize((new_width, new_height), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img)

        self.image_label.delete("all")
        x_offset = (800 - new_width) // 2
        y_offset = (600 - new_height) // 2

        # Display the image centered in the canvas
        self.image_label.create_image(x_offset, y_offset, anchor=tk.NW, image=self.tk_image)
        self.image_label.image = self.tk_image

        # Store the scaling factor for cropping
        self.scaling_factor = scaling_factor

    def process_image(self):
        if self.cropped_image is not None:
            self.processed_image = self.cropped_image  # Use cropped image if available
        elif self.image is not None:
            self.processed_image = self.image  # Fallback to original image
        else:
            messagebox.showerror("Error", "No image uploaded or cropped")
            return

        threshold = self.threshold_entry.get()
        if not threshold.isdigit():
            messagebox.showerror("Error", "Invalid threshold value")
            return

        threshold = int(threshold)
        self.processed_image = self.processed_image.convert("L")
        
        # Apply black/white threshold to the image
        self.processed_image = self.processed_image.point(lambda p: 255 if p > threshold else 0, '1')

        # Make a copy for feature vector calculation
        self.image_for_vector_calculation = self.processed_image.copy()

        # Perform sector segmentation and display the image
        self.segment_and_draw_sectors()
        self.display_image(self.processed_image)
        self.calculate_feature_vector()
        self.processed_image = None

    def segment_and_draw_sectors(self):
        draw = ImageDraw.Draw(self.processed_image)
        width, height = self.processed_image.size
        center_x, center_y = width - 1, height - 1  # Right bottom corner

        sectors = 4                  # static
        sector_angles = 90 / sectors # static 

        for i in range(sectors + 1):
            angle = np.radians(i * sector_angles)

            line_end_x = center_x - int(np.cos(angle) * max(width, height) * 2)
            line_end_y = center_y - int(np.sin(angle) * max(width, height) * 2)

            draw.line((center_x, center_y, line_end_x, line_end_y), fill="red", width=2)

    def calculate_feature_vector(self):
        img_array = np.array(self.image_for_vector_calculation)
        height, width = img_array.shape
        total_black_pixels = np.sum(img_array == 0)
        center_x, center_y = width - 1, height - 1  # Right bottom corner

        sectors = 4                  # static 
        sector_angles = 90 / sectors # static

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
        feature_vector_str = ', '.join([f'S{i + 1}: {count}' for i, count in enumerate(feature_vector)])
        self.feature_vector_text.insert(tk.END, feature_vector_str)

        # Normalization for sum
        normalized_vector_s1 = [x / total_black_pixels if total_black_pixels > 0 else 0 for x in feature_vector]
        normalized_vector_str_s1 = ', '.join([f'(S{i + 1}, {val:.4f})' for i, val in enumerate(normalized_vector_s1)])
        self.normalized_vector_text_s1.insert(tk.END, f"[{normalized_vector_str_s1}]")

        # Normalization for module
        max_value = max(feature_vector) if feature_vector else 1
        normalized_vector_s2 = [x / max_value if max_value > 0 else 0 for x in feature_vector]
        normalized_vector_str_s2 = ', '.join([f'(M{i + 1}, {val:.4f})' for i, val in enumerate(normalized_vector_s2)])
        self.normalized_vector_text_s2.insert(tk.END, f"[{normalized_vector_str_s2}]")

        class_vectors = {
            'Class 1': (self.vectors_s1_class1_avg),
            'Class 2': (self.vectors_s1_class2_avg),
            'Class 3': (self.vectors_s1_class3_avg),
        }
        
        # Обчислюємо евклідові відстані
        euclidian_distances = []
        for class_name, class_vector in class_vectors.items():
            distance = pow(sum(pow(normalized_vector_s1[i] - class_vector[i], 2) for i in range(len(normalized_vector_s1))), 1/2)
            euclidian_distances.append(distance)

        # Очищуємо і виводимо відстані
        self.class_vector_text_distance.delete(1.0, tk.END)
        euclidian_distances_str = ', '.join([f'd{i+1}: {d:.4f}' for i, d in enumerate(euclidian_distances)])
        self.class_vector_text_distance.insert(tk.END, f"[{euclidian_distances_str}]")

        # Класифікація на основі відстаней (найменша відстань вказує на клас)
        classification_result = self.classify_image(euclidian_distances, class_vectors)

        self.class_vector_text_result.delete(1.0, tk.END)
        self.class_vector_text_result.insert(tk.END, classification_result)

    def classify_image(self, distances, class_vectors):
        min_distance_index = distances.index(min(distances))
        class_name = list(class_vectors.keys())[min_distance_index]
        return f"The image belongs to {class_name}"
    

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


    def crop_image(self, start_x, start_y, end_x, end_y):
        """"Cropping with boundary checks"""
        x_offset = (800 - self.tk_image.width()) // 2
        y_offset = (600 - self.tk_image.height()) // 2

        # Adjust the crop rectangle based on the offsets and scaling factor
        adjusted_start_x = int((start_x - x_offset) / self.scaling_factor)
        adjusted_start_y = int((start_y - y_offset) / self.scaling_factor)
        adjusted_end_x = int((end_x - x_offset) / self.scaling_factor)
        adjusted_end_y = int((end_y - y_offset) / self.scaling_factor)

        # Get the dimensions of the actual image (not the displayed one)
        img_width, img_height = self.image.size

        # Ensure the crop coordinates stay within the bounds of the image
        adjusted_start_x = max(0, min(adjusted_start_x, img_width))
        adjusted_start_y = max(0, min(adjusted_start_y, img_height))
        adjusted_end_x = max(0, min(adjusted_end_x, img_width))
        adjusted_end_y = max(0, min(adjusted_end_y, img_height))

        # Crop the image using the adjusted and bounded coordinates
        self.cropped_image = self.image.crop((adjusted_start_x, adjusted_start_y, adjusted_end_x, adjusted_end_y))
        
        # Display the cropped image
        self.display_image(self.cropped_image)

        # Clear the rectangle selection
        if self.rect:
            self.image_label.delete(self.rect)
            self.rect = None


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
