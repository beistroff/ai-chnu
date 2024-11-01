import tkinter as tk
import math

# Initialize constants
SECTOR_ANGLE = 45  # Each sector is 45 degrees (360/8)
STEP_SIZE = 20     # Calculate direction every 20 pixels
NUM_SECTORS = 8
TEXT_PADDING_X = 12  # Horizontal padding in pixels
TEXT_PADDING_Y = 12  # Vertical padding in pixels

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
        self.root.title("Direction Drawing App")

        # Create two canvases for drawing
        self.canvas1 = tk.Canvas(root, bg="white", width=300, height=300)
        self.canvas2 = tk.Canvas(root, bg="white", width=300, height=300)
        self.canvas1.grid(row=0, column=0, padx=10, pady=10)
        self.canvas2.grid(row=0, column=1, padx=10, pady=10)

        # Initialize variables to store drawing points and directions
        self.points1, self.directions1 = [], []
        self.points2, self.directions2 = [], []

        # Bind mouse events for drawing
        self.canvas1.bind("<Button-1>", self.start_draw1)
        self.canvas1.bind("<B1-Motion>", self.draw1)
        self.canvas2.bind("<Button-1>", self.start_draw2)
        self.canvas2.bind("<B1-Motion>", self.draw2)

        # Label for similarity result
        self.similarity_label = tk.Label(root, text="Similarity: N/A", font=("Arial", 14))
        self.similarity_label.grid(row=1, column=0, columnspan=2, pady=10)

        # Text widgets to display vectors
        self.vector1_text = tk.Text(root, height=8, width=40, font=("Arial", 10), wrap="none")
        self.vector1_text.grid(row=2, column=0, padx=10)
        self.vector2_text = tk.Text(root, height=8, width=40, font=("Arial", 10), wrap="none")
        self.vector2_text.grid(row=2, column=1, padx=10)

        # Button to calculate similarity
        self.compare_button = tk.Button(root, text="Compare", command=self.compare_drawings)
        self.compare_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Start drawing on canvas 1
    def start_draw1(self, event):
        self.canvas1.delete("all")
        self.points1 = [(event.x, event.y)]
        self.directions1 = []
        self.canvas1.delete("text")

    # Also we just repeat same functionality with methods draw1() and draw2() 

    # Draw on canvas 1
    def draw1(self, event):
        last_point = self.points1[-1]
        new_point = (event.x, event.y)
        
        # Draw pencil-like line. It sucks tbh, because of step with 20 pixels, we actually draw polygons
        # because we can't update on each pixels... We need to fix it
        self.canvas1.create_line(last_point[0], last_point[1], new_point[0], new_point[1], fill="red", width=2)
        
        # Only record direction if distance exceeds STEP_SIZE
        if math.hypot(new_point[0] - last_point[0], new_point[1] - last_point[1]) >= STEP_SIZE:
            angle = calculate_angle(last_point, new_point)
            sector = get_sector(angle)
            self.directions1.append(sector)
            self.points1.append(new_point)

            # Display sector number on the canvas
            mid_point = ((last_point[0] + new_point[0]) / 2, (last_point[1] + new_point[1]) / 2)
            padded_x = mid_point[0] + TEXT_PADDING_X
            padded_y = mid_point[1] + TEXT_PADDING_Y
            self.canvas1.create_text(padded_x, padded_y, text=str(sector), fill="blue", font=("Arial", 8), tags="text")

    # Start drawing on canvas 2
    def start_draw2(self, event):
        self.canvas2.delete("all")
        self.points2 = [(event.x, event.y)]
        self.directions2 = []
        self.canvas2.delete("text")

    # Draw on canvas 2
    def draw2(self, event):
        last_point = self.points2[-1]
        new_point = (event.x, event.y)
        
        self.canvas2.create_line(last_point[0], last_point[1], new_point[0], new_point[1], fill="blue", width=2)
        
        # Only record direction if distance exceeds STEP_SIZE
        if math.hypot(new_point[0] - last_point[0], new_point[1] - last_point[1]) >= STEP_SIZE:
            angle = calculate_angle(last_point, new_point)
            sector = get_sector(angle)
            self.directions2.append(sector)
            self.points2.append(new_point)

            # Display sector number on the canvas with padding
            mid_point = ((last_point[0] + new_point[0]) / 2, (last_point[1] + new_point[1]) / 2)
            padded_x = mid_point[0] + TEXT_PADDING_X
            padded_y = mid_point[1] + TEXT_PADDING_Y
            self.canvas2.create_text(padded_x, padded_y, text=str(sector), fill="red", font=("Arial", 8), tags="text")

    # Pad vectors to be the same length
    def pad_vectors(self):
        max_length = max(len(self.directions1), len(self.directions2))
        self.directions1.extend([0] * (max_length - len(self.directions1)))
        self.directions2.extend([0] * (max_length - len(self.directions2)))

    # Display vectors
    def display_vectors(self):
        self.vector1_text.delete("1.0", tk.END)
        self.vector2_text.delete("1.0", tk.END)

        # Format vectors with 18 numbers per line
        vector1_str = "\n".join(", ".join(map(str, self.directions1[i:i + 18])) for i in range(0, len(self.directions1), 20))
        vector2_str = "\n".join(", ".join(map(str, self.directions2[i:i + 18])) for i in range(0, len(self.directions2), 20))

        # Insert into text field
        self.vector1_text.insert(tk.END, f"Vector 1:\n{vector1_str}")
        self.vector2_text.insert(tk.END, f"Vector 2:\n{vector2_str}")

    # Compare drawings from both canvases
    def compare_drawings(self):
        self.pad_vectors()  # Ensure both vectors have the same length
        similarity = calculate_similarity(self.directions1, self.directions2)
        self.similarity_label.config(text=f"Similarity: {similarity:.2f}%")
        
        self.display_vectors()  # Show padded vectors in formatted view

        # Print vectors in console
        print("Canvas 1 Vector:", self.directions1)
        print("Canvas 2 Vector:", self.directions2)
        print(f"Similarity: {similarity:.2f}%")

# Run the application
root = tk.Tk()
app = DirectionDrawingApp(root)
root.mainloop()
