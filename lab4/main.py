import tkinter as tk
import math

# Initialize constants
SECTOR_ANGLE = 45  # Each sector is 45 degrees (360/8)
NUM_SECTORS = 8
TEXT_PADDING_X = 12
TEXT_PADDING_Y = 12

# Function to calculate angle between two points
def calculate_angle(p1, p2):
    delta_y = p2[1] - p1[1]
    delta_x = p2[0] - p1[0]
    angle = math.degrees(math.atan2(delta_y, delta_x))
    if angle < 0:
        angle += 360
    return angle

# Determine sector from angle
def get_sector(angle):
    return int(angle // SECTOR_ANGLE) + 1

# Calculate similarity between two lists
def calculate_similarity(list1, list2):
    matches = sum(1 for a, b in zip(list1, list2) if a == b)
    similarity = (matches / max(len(list1), len(list2))) * 100
    return similarity

class DirectionDrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lab 4")

        # Create two canvases for drawing
        self.canvas1 = tk.Canvas(root, bg="white", width=300, height=300)
        self.canvas2 = tk.Canvas(root, bg="white", width=300, height=300)
        self.canvas1.grid(row=0, column=0, padx=10, pady=10)
        self.canvas2.grid(row=0, column=1, padx=10, pady=10)

        # Initialize variables to store drawing points and directions
        self.points1, self.directions1 = [], []
        self.points2, self.directions2 = [], []
        self.class_vectors = {1: [], 2: [], 3: []}  # Store vectors for each class

        # Bind mouse events for drawing
        self.canvas1.bind("<Button-1>", self.start_draw1)
        self.canvas1.bind("<B1-Motion>", self.draw1)
        self.canvas2.bind("<Button-1>", self.start_draw2)
        self.canvas2.bind("<B1-Motion>", self.draw2)

        # Text widgets to display vectors
        self.vector1_text = tk.Text(root, height=8, width=40, font=("Arial", 10), wrap="none")
        self.vector1_text.grid(row=2, column=0, padx=10, pady=5)

        self.vector2_text = tk.Text(root, height=8, width=40, font=("Arial", 10), wrap="none")
        self.vector2_text.grid(row=2, column=1, padx=10, pady=5)

        self.class_buttons = []
        colors = ["lightgreen", "lightblue", "orange"]

        for i in range(1, 4):
            button = tk.Button(root, text=f"Save Class {i}", command=lambda i=i: self.save_class_vector(i), bg=colors[i-1])
            button.grid(row=2 + i, column=0)
            self.class_buttons.append(button)

        self.pixels_label = tk.Label(root, text="Threshold in px:")
        self.pixels_label.grid(column=0, row=7)

        self.pixels_selector = tk.Spinbox(root, from_=10, to=80)
        self.pixels_selector.grid(column=0, row=8)

        # Button to calculate similarity
        self.compare_button = tk.Button(root, text="Compare with Classes", command=self.compare_with_classes)
        self.compare_button.grid(row=9, column=0, columnspan=3, pady=10)

        # Label for similarity result
        self.similarity_label = tk.Label(root, text="Схожість: N/A", font=("Arial", 14))
        self.similarity_label.grid(row=6, column=1, columnspan=2)

    # Start drawing on canvas 1
    def start_draw1(self, event):
        self.canvas1.delete("all")
        self.points1, self.directions1 = [(event.x, event.y)], []
        self.canvas1.delete("text")

    # Draw on canvas 1
    def draw1(self, event):
        last_point = self.points1[-1]
        new_point = (event.x, event.y)

        # Only draw and record if the distance exceeds STEP_SIZE
        if math.hypot(new_point[0] - last_point[0], new_point[1] - last_point[1]) >= int(self.pixels_selector.get()):
            self.canvas1.create_line(last_point[0], last_point[1], new_point[0], new_point[1], fill="green", width=2)
            angle = calculate_angle(last_point, new_point)
            sector = get_sector(angle)
            self.directions1.append(sector)
            self.points1.append(new_point)

            # Display sector number on the canvas
            mid_point = ((last_point[0] + new_point[0]) / 2, (last_point[1] + new_point[1]) / 2)
            self.canvas1.create_text(mid_point[0] + TEXT_PADDING_X, mid_point[1] + TEXT_PADDING_Y,
                                     text=str(sector), fill="gray", font=("Arial", 8), tags="text")

    # Start drawing on canvas 2
    def start_draw2(self, event):
        self.canvas2.delete("all")
        self.points2, self.directions2 = [(event.x, event.y)], []
        self.canvas2.delete("text")

    # Draw on canvas 2 with direction tracking
    def draw2(self, event):
        last_point = self.points2[-1]
        new_point = (event.x, event.y)

        if math.hypot(new_point[0] - last_point[0], new_point[1] - last_point[1]) >= int(self.pixels_selector.get()):
            self.canvas2.create_line(last_point[0], last_point[1], new_point[0], new_point[1], fill="blue", width=2)
            angle = calculate_angle(last_point, new_point)
            sector = get_sector(angle)
            self.directions2.append(sector)
            self.points2.append(new_point)

            # Display sector number on the canvas with padding
            mid_point = ((last_point[0] + new_point[0]) / 2, (last_point[1] + new_point[1]) / 2)
            self.canvas2.create_text(mid_point[0] + TEXT_PADDING_X, mid_point[1] + TEXT_PADDING_Y,
                                     text=str(sector), fill="gray", font=("Arial", 8), tags="text")

    # Save current canvas1 drawing as a class vector
    def save_class_vector(self, class_num):
        if self.directions1:
            self.class_vectors[class_num] = self.directions1.copy()
            self.similarity_label.config(text=f"Class {class_num} vector saved!")
        else:
            self.similarity_label.config(text="Draw a picture on Canvas 1 to save!")

    # Compare the drawing on canvas2 with each saved class vector
    def compare_with_classes(self):
        if not all(self.class_vectors.values()):
            self.similarity_label.config(text="Please save a drawing for all classes!")
            return

        self.pad_vectors()  # Ensure both vectors have the same length
        similarities = {class_num: calculate_similarity(self.directions2, class_vector)
                        for class_num, class_vector in self.class_vectors.items()}

        # Display similarity for each class
        similarity_text = "\n".join(f"Class {class_num} Similarity: {similarity:.2f}%"
                                    for class_num, similarity in similarities.items())
        self.similarity_label.config(text=similarity_text)

    # Pad vectors to be the same length
    def pad_vectors(self):
        max_length = max(len(self.directions2), max(len(v) for v in self.class_vectors.values()))
        self.directions2.extend([0] * (max_length - len(self.directions2)))
        for class_num in self.class_vectors:
            self.class_vectors[class_num].extend([0] * (max_length - len(self.class_vectors[class_num])))

# Run the application
root = tk.Tk()
app = DirectionDrawingApp(root)
root.mainloop()
