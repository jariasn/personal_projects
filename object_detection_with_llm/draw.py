import os
import json
from PIL import Image, ImageDraw

def draw_bounding_boxes(image, bbox):
    """
    Draw bounding box on an image.
    
    :param image: PIL Image object
    :param bbox: Bounding box as [x_center, y_center, width, height]
    :return: Image with bounding box drawn
    """
    draw = ImageDraw.Draw(image)
    x_center, y_center, width, height = bbox
    
    # Calculate the top-left and bottom-right corners from the center, width, and height
    left = x_center - width / 2
    right = x_center + width / 2
    top = y_center - height / 2
    bottom = y_center + height / 2
    
    # Draw the bounding box (green rectangle)
    draw.rectangle([left, top, right, bottom], outline="green", width=3)
    
    return image

def visualize_bounding_boxes(directory, json_file, output_directory=None):
    """
    Visualize the bounding boxes on the labeled images.
    
    :param directory: Path to the directory containing the images
    :param json_file: Path to the JSON file containing bounding box data
    :param output_directory: Path to save the images with bounding boxes (if None, display instead)
    :return: None
    """
    # Load the bounding box data from the JSON file
    with open(json_file, 'r') as f:
        bbox_data = json.load(f)
    
    # Create the output directory if it doesn't exist
    if output_directory:
        os.makedirs(output_directory, exist_ok=True)
    
    # Iterate through the bounding box data
    for entry in bbox_data:
        file_name = entry["file_name"]
        bbox = entry["bbox"]
        
        # Open the corresponding image
        image_path = os.path.join(directory, file_name)
        if not os.path.exists(image_path):
            print(f"Image {file_name} not found in directory {directory}. Skipping.")
            continue
        
        image = Image.open(image_path)
        
        # Draw the bounding box on the image
        image_with_box = draw_bounding_boxes(image, bbox)
        
        # Save or display the image
        if output_directory:
            output_path = os.path.join(output_directory, file_name)
            image_with_box.save(output_path)
            print(f"Saved image with bounding box: {output_path}")
        else:
            image_with_box.show()

# Usage
directory_path = 'true_boxes'  # Directory containing original images
json_file_path = 'bounding_boxes_llm.json'  # Path to the JSON file with bounding boxes
output_dir = 'labeled_images_and_true_boxes'  # Directory to save images with bounding boxes (set to None to display instead)

visualize_bounding_boxes(directory_path, json_file_path, output_dir)
