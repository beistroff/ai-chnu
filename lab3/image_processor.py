from PIL import Image, ImageDraw, ImageTk
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import image_processor_crop


class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Classifier")
        self.root.geometry("300x300")
        self.root.configure(bg="#2C3E50")

        self.frame = tk.Frame(root, bg="#34495E")
        self.frame.pack(padx=20, pady=20)

        # Title label
        self.title_label = tk.Label(self.frame, text="Image Classifier", font=("Helvetica", 16, "bold"), bg="#34495E", fg="#ECF0F1")
        self.title_label.pack(pady=10)

        # Class buttons
        self.class_buttons = []
        for i in range(1, 4):
            button = tk.Button(self.frame, text=f"Upload Class {i} Images", command=lambda cls=i: self.set_class(cls), 
                               bg="#1ABC9C", fg="#FFFFFF", font=("Helvetica", 12), relief="flat", width=20)
            button.pack(pady=5)
            self.class_buttons.append(button)

        # Open image processor button
        self.upload_button = tk.Button(self.frame, text="Image Processor", command=self.open_image_processor,
                                       bg="#3498DB", fg="#FFFFFF", font=("Helvetica", 12), relief="flat", width=20)
        self.upload_button.pack(pady=10)

        self.image_paths = []
        self.image_labels = []

        # Default directories for class images
        self.class1_default_dir = "D:\\university\\4d_course\\1st_term\\ai-labs\\ai-chnu\\lab2\\pictures\\class_1"
        self.class2_default_dir = "D:\\university\\4d_course\\1st_term\\ai-labs\\ai-chnu\\lab2\\pictures\\class_2"
        self.class3_default_dir = "D:\\university\\4d_course\\1st_term\\ai-labs\\ai-chnu\\lab2\\pictures\\class_3"

        # Vectors for each class (2 vectors per class: sum and max normalization)
        self.vectors_s1_class1 = []
        self.vectors_m1_class1 = []
        self.vectors_s1_class2 = []
        self.vectors_m1_class2 = []
        self.vectors_s1_class3 = []
        self.vectors_m1_class3 = []

        # Vectors for avg values
        self.vectors_s1_class1_avg = []
        self.vectors_s1_class2_avg = []
        self.vectors_s1_class3_avg = []

        self.vectors_m1_class1_avg = []
        self.vectors_m1_class2_avg = []
        self.vectors_m1_class3_avg = []

    def set_class(self, class_num):
        self.selected_class = class_num
        self.upload_images()

    def open_image_processor(self):
        new_window = tk.Toplevel(self.frame)
        new_window.title("Image Processor")

        image_processor = image_processor_crop.ImageProcessor(new_window,
                                              self.vectors_s1_class1_avg,
                                              self.vectors_s1_class2_avg,
                                              self.vectors_s1_class3_avg,
                                              self.vectors_m1_class1_avg,
                                              self.vectors_m1_class2_avg,
                                              self.vectors_m1_class3_avg)

    def open_image_window(self, image_path):
        self.image_paths = image_path
        images_window = tk.Toplevel(self.root)
        images_window.title("Selected Images")

        canvas = tk.Canvas(images_window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(images_window, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        images_frame = tk.Frame(canvas)
        images_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=images_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.image_labels = []
        row, col = 0, 0
        for index, file_path in enumerate(image_path):
            img = Image.open(file_path)
            img.thumbnail((200, 200))
            img_tk = ImageTk.PhotoImage(img)

            label = tk.Label(images_frame, image=img_tk)
            label.image = img_tk
            label.grid(row=row, column=col, padx=5, pady=5)

            self.image_labels.append(label)

            col += 1
            if col == 3:
                col = 0
                row += 1    

        self.process_button = tk.Button(images_window, text="Process Image", command=self.process_all_images)
        self.process_button.pack(side=tk.BOTTOM, pady=20)

    def upload_images(self):
        # Set default directory based on selected class
        if self.selected_class == 1:
            default_dir = self.class1_default_dir
        elif self.selected_class == 2:
            default_dir = self.class2_default_dir
        elif self.selected_class == 3:
            default_dir = self.class3_default_dir
        else:
            messagebox.showerror("Error", "No class selected.")
            return

        file_paths = filedialog.askopenfilenames(title='Select Images',
                                                 initialdir=default_dir,
                                                 filetypes=[('Image Files', '*.bmp *.jpeg *.png')])

        if len(file_paths) < 4:
            messagebox.showwarning("Insufficient Images", "Please upload at least 5 images.")
        else:
            self.open_image_window(file_paths)

    def print_matrix(self, matrix, label):
        print(f"\n{label}:")
        for row in matrix:
            rounded_row = [round(float(value), 4) for value in row]
            print(rounded_row)

    # Function to calculate avg value
    def find_average(self, matrix):
        averages = []

        for i in range(len(matrix[0])):
            column = [matrix[j][i] for j in range(len(matrix))]
            average_value = sum(column) / len(column)
            averages.append(average_value)

        return averages

    def process_all_images(self):
        # Lists to hold normalization vectors
        if self.selected_class == 1:
            vectors_s1 = self.vectors_s1_class1
            vectors_m1 = self.vectors_m1_class1
            vectors_s1_avg = self.vectors_s1_class1_avg
            vectors_m1_avg = self.vectors_m1_class1_avg
        elif self.selected_class == 2:
            vectors_s1 = self.vectors_s1_class2
            vectors_m1 = self.vectors_m1_class2
            vectors_s1_avg = self.vectors_s1_class2_avg
            vectors_m1_avg = self.vectors_s1_class2_avg
        elif self.selected_class == 3:
            vectors_s1 = self.vectors_s1_class3
            vectors_m1 = self.vectors_m1_class3
            vectors_s1_avg = self.vectors_s1_class3_avg
            vectors_m1_avg = self.vectors_s1_class3_avg
        else:
            messagebox.showerror("Error", "No class selected for processing.")
            return

        for file_path in self.image_paths:
            img = Image.open(file_path)
            processed_image = img.convert("L").point(lambda p: 0 if p < 250 else 255, "1")

            # Create a copy for calculations
            image_for_vector_calculation = processed_image.copy()

            # Draw sectors on the processed image
            self.segment_and_draw_sectors(processed_image)

            img_tk = ImageTk.PhotoImage(processed_image)
            index = self.image_paths.index(file_path)
            self.image_labels[index].config(image=img_tk)
            self.image_labels[index].image = img_tk

            # Calculate the feature vector for each sector
            feature_vector = self.calculate_feature_vector(image_for_vector_calculation)
            total_black_pixels = np.sum(feature_vector)

            # Normalize the feature vectors
            normalized_vector_s1 = [x / total_black_pixels if total_black_pixels > 0 else 0 for x in feature_vector]
            vectors_s1.append(normalized_vector_s1)

            max_value = max(feature_vector) if feature_vector else 1
            normalized_vector_m1 = [x / max_value if max_value > 0 else 0 for x in feature_vector]
            vectors_m1.append(normalized_vector_m1)

            # Print results for each image
            print(f"\nProcessed {file_path[35:]}:")
            print("Total black pixels:", total_black_pixels)
            print("Feature vector:", feature_vector)

        self.print_matrix(vectors_s1, "Class - Normalized vectors by sum")
        self.print_matrix(vectors_m1, "Class - Normalized vectors by max")

        vectors_s1_avg = self.find_average(vectors_s1)
        vectors_m1_avg = self.find_average(vectors_m1)

        print("\nClass - SAvg\n", [round(float(value), 4) for value in vectors_s1_avg])
        print("Class - MAvg\n", [round(float(value), 4) for value in vectors_m1_avg])

        if self.selected_class == 1:
            self.vectors_s1_class1_avg = vectors_s1_avg
            self.vectors_m1_class1_avg = vectors_m1_avg
        elif self.selected_class == 2:
            self.vectors_s1_class2_avg = vectors_s1_avg
            self.vectors_m1_class2_avg = vectors_m1_avg
        elif self.selected_class == 3:
            self.vectors_s1_class3_avg = vectors_s1_avg
            self.vectors_m1_class3_avg = vectors_m1_avg

    def segment_and_draw_sectors(self, image):
        draw = ImageDraw.Draw(image)
        width, height = image.size
        center_x, center_y = width - 1, height - 1  # Right bottom corner

        sectors = 4
        sector_angles = 90 / sectors

        for i in range(sectors + 1):
            angle = np.radians(i * sector_angles)

            line_end_x = center_x - int(np.cos(angle) * max(width, height) * 2) # Right bottom corner
            line_end_y = center_y - int(np.sin(angle) * max(width, height) * 2) # Right bottom corner

            draw.line((center_x, center_y, line_end_x, line_end_y), fill="red", width=2)

    def calculate_feature_vector(self, img):
        img_array = np.array(img)
        height, width = img_array.shape
        feature_vector = [0] * 4
        center_x, center_y = width - 1, height - 1  # Right bottom corner
        sectors = 4
        sector_angles = 90 / sectors

        for y in range(height):
            for x in range(width):
                if img_array[y, x] == 0:  # Ensure the correct indexing for height and width
                    dx = x - center_x
                    dy = center_y - y
                    angle = (np.degrees(np.arctan2(dy, dx)) + 90) % 90

                    for i in range(sectors):
                        if (i * sector_angles) <= angle < ((i + 1) * sector_angles):
                            feature_vector[i] += 1

        return feature_vector


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()