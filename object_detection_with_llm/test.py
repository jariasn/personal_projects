import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# Image dimensions
image_path = 'test.png'  # Update with the correct path to the image
image_width = 3024
image_height = 1964

# Creating a figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Load the image to display as background
img = Image.open(image_path)
ax.imshow(img)

updated_bounding_boxes = [
    {"label": "Explorer Panel", "x": 0, "y": 0, "w": 450, "h": 1964},
    {"label": "Main Code Editor", "x": 450, "y": 0, "w": 1800, "h": 1100},
    {"label": "Terminal Panel", "x": 450, "y": 1100, "w": 1800, "h": 864},
    {"label": "Outline Section", "x": 2250, "y": 0, "w": 624, "h": 1964},
]

# Adding rectangles for each bounding box
for box in updated_bounding_boxes:
    rect = patches.Rectangle((box["x"], box["y"]), box["w"], box["h"], linewidth=2, edgecolor='g', facecolor='none')
    ax.add_patch(rect)
    # Adding labels
    ax.text(box["x"] + 10, box["y"] + 20, box["label"], color='white', fontsize=12, bbox=dict(facecolor='black', alpha=0.5))

# Display the plot
plt.axis('off')  # Hide axes
plt.show()

