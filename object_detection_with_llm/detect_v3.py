# %%
from openai import OpenAI
import base64
from io import BytesIO
from IPython.display import HTML, display
from PIL import Image, ImageDraw, ImageFont
import io
import cv2
import numpy as np
from pydantic import BaseModel
from typing import Tuple, List
import os
import json

# %%
def convert_to_base64(img):
    """
    Convert PIL images to Base64 encoded strings

    :param pil_image: PIL image
    :return: Re-sized Base64 string
    """

    buffered = BytesIO()
    img.save(buffered, format="PNG")  # You can change the format if needed
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def draw_axes_opencv(img, font_scale, grid_size=(4, 4)):
    """
    Draw axes and row/column labels with contours on an image using OpenCV.

    :param img: PIL Image
    :param font_scale: Scale factor for the font size
    :param grid_size: Tuple indicating (rows, cols) of the grid
    :return: PIL Image with axes and row/column labels
    """
    
    # Convert PIL image to NumPy array (for OpenCV)
    img_cv = np.array(img)
    
    # If image has alpha channel, convert it to BGR
    if img_cv.shape[2] == 4:
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGBA2RGB)
    
    height, width, _ = img_cv.shape
    
    # Calculate cell size based on the grid size
    rows, cols = grid_size
    cell_width = width // cols
    cell_height = height // rows
    
    # Define grid line color and thickness
    grid_color = (255, 0, 0)  # Blue in BGR
    if width > 400:
        grid_thickness = 2
    else:
        grid_thickness = 1
    
    # Draw the vertical grid lines
    for i in range(1, cols):
        x = i * cell_width
        cv2.line(img_cv, (x, 0), (x, height), grid_color, grid_thickness)
    
    # Draw the horizontal grid lines
    for i in range(1, rows):
        y = i * cell_height
        cv2.line(img_cv, (0, y), (width, y), grid_color, grid_thickness)
    
    # Define text properties
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_color = (255, 255, 255)  # White text
    contour_color = (0, 0, 0)      # Black contour for better visibility
    font_scale_adjusted = min(cell_width, cell_height) / 100
    if width > 400:
        font_thickness = 2          # Thickness for the fill text
        contour_thickness = 6       # Thickness for the contour
    else:
        font_thickness = 1
        contour_thickness = 4      # Thickness for the contour

    
    # -----------------------
    # Add Column Labels (Top)
    # -----------------------
    for col in range(cols):
        # Define column label as a number (1, 2, 3, ...)
        col_label = str(col + 1)
        text = col_label
        
        # Get the text size to center it properly within the cell
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale_adjusted, font_thickness)
        
        # Calculate the position: center of the top cell
        center_x = col * cell_width + (cell_width - text_width) // 2
        center_y = (cell_height + text_height) // 2  # Slight padding from the top
        
        # Draw contour (outline) by drawing the text in contour color with higher thickness
        cv2.putText(img_cv, text, (center_x, center_y), font, font_scale_adjusted, contour_color, contour_thickness, cv2.LINE_AA)
        
        # Draw the text in the fill color with lower thickness
        cv2.putText(img_cv, text, (center_x, center_y), font, font_scale_adjusted, font_color, font_thickness, cv2.LINE_AA)
    
    # -----------------------
    # Add Row Labels (Left)
    # -----------------------
    for row in range(rows):
        # Define row label as a number (1, 2, 3, ...)
        row_label = str(row + 1)
        text = row_label
        
        # Get the text size to center it properly within the cell
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale_adjusted, font_thickness)
        
        # Calculate the position: center of the left cell
        center_x = (cell_width - text_width) // 2
        center_y = row * cell_height + (cell_height + text_height) // 2
        
        # Draw contour (outline) by drawing the text in contour color with higher thickness
        cv2.putText(img_cv, text, (center_x, center_y), font, font_scale_adjusted, contour_color, contour_thickness, cv2.LINE_AA)
        
        # Draw the text in the fill color with lower thickness
        cv2.putText(img_cv, text, (center_x, center_y), font, font_scale_adjusted, font_color, font_thickness, cv2.LINE_AA)
    
    # -----------------------
    # Optional: Highlight Top-Left Cell
    # -----------------------
    # If you want to leave the top-left cell blank or add a special label (like a corner indicator), uncomment the following lines:
    # top_left_cell = (0, 0)
    # cv2.rectangle(img_cv, (0, 0), (cell_width, cell_height), grid_color, grid_thickness)
    # Alternatively, add a special label:
    # corner_label = "X"  # Or any other symbol
    # (text_width, text_height), baseline = cv2.getTextSize(corner_label, font, font_scale_adjusted, font_thickness)
    # text_x = (cell_width - text_width) // 2
    # text_y = (cell_height + text_height) // 2
    # cv2.putText(img_cv, corner_label, (text_x, text_y), font, font_scale_adjusted, contour_color, contour_thickness, cv2.LINE_AA)
    # cv2.putText(img_cv, corner_label, (text_x, text_y), font, font_scale_adjusted, font_color, font_thickness, cv2.LINE_AA)
    
    # Convert back to PIL Image
    return Image.fromarray(img_cv)

def add_white_contour_opencv(img, font_scale=2):
    """
    Add a white background and labels to an image using OpenCV
    """
    # Convert PIL image to NumPy array (for OpenCV)
    img_cv = np.array(img)
    height, width, _ = img_cv.shape
    # Add padding for the white contour
    size = int(width * 0.11)
    new_img = np.full((height + size, width + size, 3), (255, 255, 255), dtype=np.uint8)
    new_img[size:, size:] = img_cv
    
    # Add the label using OpenCV
    cv2.putText(new_img, "(0, 0)", (int(size*0.2), int(size*0.6)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), 2)
    cv2.putText(new_img, f"{height//4}", (int(size*0.4), height//4+size), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), 2)
    cv2.putText(new_img, f"{height}", (int(size*0.4), height+int(size*0.9)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), 2)
    cv2.putText(new_img, f"{height//2}", (int(size*0.4), height//2+size), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), 2)
    cv2.putText(new_img, f"{(height//2)+(height//4)}", (int(size*0.4), (height//2)+(height//4)+size), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), 2)

    cv2.putText(new_img, f"{width}", (width+int(size*0.4), int(size*0.6)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), 2)
    cv2.putText(new_img, f"{width//4}", (width//4+int(size*0.8), int(size*0.6)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), 2)
    cv2.putText(new_img, f"{width//2}", (width//2+int(size*0.8), int(size*0.6)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), 2)
    cv2.putText(new_img, f"{(width//4)+(width//2)}", ((width//4)+(width//2)+int(size*0.8), int(size*0.6)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), 2)
    # Convert back to PIL image
    return Image.fromarray(new_img)

def pre_process_image_opencv(img, boxes, font_scale=0.0007):
    """
    Pre-process an image before displaying it with OpenCV

    :param img: PIL image
    :return: PIL image with axes, quadrants, and white contour
    """
    font_scale = img.size[0] * font_scale
    img = draw_axes_opencv(img, font_scale)
    if boxes:
        img = draw_bounding_boxes(img, boxes)
    #img = add_white_contour_opencv(img, font_scale)
    return img

def reduce_image_size(image, max_size=500):
    """
    Reduce the size of an image while maintaining the aspect ratio

    :param image: PIL image
    :param max_size: Maximum size for the image
    :return: Resized PIL image
    """
    width, height = image.size
    if width > height:
        new_width = max_size
        new_height = int(max_size * height / width)
    else:
        new_height = max_size
        new_width = int(max_size * width / height)
    return image.resize((new_width, new_height))

def reduce_resolution(image, resample_filter=Image.NEAREST):
    """
    Lower the resolution of the image by applying a resample filter.
    :param image: PIL image
    :param resample_filter: Resampling filter to use (default: Image.NEAREST for lower quality)
    :return: Lower resolution PIL image
    """
    # Applying the selected filter for downsampling
    width, height = image.size
    return image.resize((width, height), resample=resample_filter)

def process(image, reduce_resolution=False, reduce_size=True, boxes=None):
    
    image = pre_process_image_opencv(image, boxes)

    if reduce_size:
        image = reduce_image_size(image)
    if reduce_resolution:
        image = reduce_resolution(image)
        
    image_base64 = convert_to_base64(image)
    return image_base64

def save_img(image, path):
    image.save(path)

def draw_bounding_boxes(image, boxes):
    """
    Draws bounding boxes on an image.

    :param image: PIL image object
    :param boxes: List of tuples, each tuple containing (x1, y1, x2, y2) 
                  which represent the top-left and bottom-right corners of a box
    :return: Image with bounding boxes drawn
    """
    
    # Create a drawing context
    image_copy = image.copy()
    draw = ImageDraw.Draw(image_copy)
    
    # Loop through each box in the list
    for box in boxes:
        x1, y1, x2, y2 = box
        
        # Draw rectangle with a red outline (you can adjust color and width)
        draw.rectangle([x1, y1, x2, y2], outline="green", width=4)
    
    return image_copy

def plt_image(image):
    display(HTML(f'<img src="data:image/png;base64,{image}">'))

def get_cells(response):
    return [response.cell_numbers[0].top, response.cell_numbers[0].bottom, response.cell_numbers[0].left, response.cell_numbers[0].right]

def calculate_box_from_crops(image, cells):
    """
    Calculate the bounding boxes based on the cell coordinates provided.

    :param image: The image object.
    :param cells: List of lists, where each sublist contains tuples of (col, row) coordinates.
                  Example: [[(1,1), (2,1)], [(3,2), (4,2)]]
    :return: List of tuples, each tuple containing (x1, y1, x2, y2) 
             which represent the top-left and bottom-right corners of a box.
    """
    # Define the cell size based on the grid size
    rows, cols = 4, 4  # Assuming the grid is 4x4
    width, height = image.size
    left_pixels, top_pixels, right_pixels, bottom_pixels = 0, 0, width, height
    boxes = []

    for i in range(len(cells)):
        cell_width = width // cols
        cell_height = height // rows

        cell_top = min(cells[i][0][1])  #  min of rows
        cell_bottom = max(cells[i][0][1])  # max of rows
        cell_left = min(cells[i][0][0])  # min of cols
        cell_right = max(cells[i][0][0])  # max of cols

        # Calculate pixel positions
        left = (cell_left - 1) * cell_width
        right = cell_right * cell_width
        top = (cell_top - 1) * cell_height
        bottom = cell_bottom * cell_height

        left_pixels += left
        top_pixels += top
        right_pixels -= (width - right)
        bottom_pixels -= (height - bottom)

        width = right - left
        height = bottom - top


    boxes.append((left_pixels, top_pixels, right_pixels, bottom_pixels))

    return boxes

def crop_image(image, cells, grid_size=(4, 4)):
    """
    Crop an image by including only specified rows and columns.

    :param image: PIL Image
    :param included_rows: List of row indices to include (1-based)
    :param included_columns: List of column indices to include (1-based)
    :param grid_size: Tuple indicating (rows, cols) of the grid (default is 4x4)
    :return: Cropped PIL Image
    """
    included_columns, included_rows = cells[0]
    rows, cols = grid_size
    cell_width = image.size[0] // cols
    cell_height = image.size[1] // rows

    # Calculate new image dimensions
    new_width = cell_width * len(included_columns)
    new_height = cell_height * len(included_rows)

    # Create a new blank image with the same mode as the original
    new_image = Image.new(image.mode, (new_width, new_height))

    # Iterate over included rows and columns to paste cells into the new image
    for i, row in enumerate(included_rows):
        for j, col in enumerate(included_columns):
            left = (col - 1) * cell_width
            upper = (row - 1) * cell_height
            right = left + cell_width
            lower = upper + cell_height

            # Crop the specific cell
            cell = image.crop((left, upper, right, lower))
            
            # Paste the cell into the new image
            new_image.paste(cell, (j * cell_width, i * cell_height))

    return new_image

# %%
#image_path = 'test.png'
example_path = 'Zidane from Ultralytics.jpg'
example = Image.open(example_path)

# %%
image_path = 'person_7.jpg'
image = Image.open(image_path)


# %%
image_processed = process(image)
example_processed = process(example)

# %%
class BoundingBox(BaseModel):
    label: str
    top_left: list[int]  
    bottom_right: list[int]

class Detection(BaseModel):
    bounding_boxes: list[BoundingBox]

class ColRows(BaseModel):
    label: str
    columns: list[int]
    rows: list[int]
    done: bool


class Response(BaseModel):
    contains_object: list[ColRows]

# Function to ask LLM to detect UI elements and return bounding boxes
def ask_llm_to_detect_ui(client, example, image, overlayed_image, image_size, max_tokens=500):
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": [
                                    {
                                    "type": "text",
                                    "text": """
                                            You are a computer vision model that detects objects in images. 
                                            The image has a 4x4 grid overlay with the columns and rows numbered. Note that the numbers are inside the cells. 
                                            For each object, you have to follow these steps:
                                            1. Detect which columns contain the detected object.
                                            2. Detect which rows contain the detected object.
                                            3. Return the columns and rows.
                                            4. Set the variable 'done' to True if ALL rows and columns contain at least one part of the object.

                                            Ensure you reference the columns and rows numbers as they appear on the grid overlay 
                                            in the image. If there are ANY rows or columns that don't contain any part of the object,
                                            return False for the variable 'done.' But if ALL rows and columns contain at least one part of the object,
                                            return True for the variable 'done.'
                                            IMPORTANT: Make sure to compare the original image with the image with the grid overlay to know what exactly constitutes the object to detect.
                                            A cell is considered to contain a part of the object if there is at least a small part of the object in the cell.

                    
                                            """,
                                    },

                ]},
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": f"Detect the people in this image, no matter how small they are or if they are not complete. Here you have the original image for your reference and the image with the grid cells. Make sure to compare both images so that you know what exactly constitutes the object to detect:",
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}",
                },
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{overlayed_image}",
                },
                },
                                {
                "type": "text",
                "text": """
                        Here you have an example of how to do this: you are asked to detect the people in the image below:  
                        """,
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{example}",
                },
                },
                {
                "type": "text",
                "text": """
                        Then your response would be:
                        For the person on the left: columns (1, 2, 3, 4), rows (2, 3, 4), and done = False because row 1 doesn't contain any part of the person. 
                        For the person on the right: columns (3, 4), rows (1, 2, 3, 4), and done = False because columns 1 and 2 don't contain any part of the person.
                        """,
                },
            ],
            }
        ],
        max_tokens=max_tokens,
        response_format=Response,
        )
    #print(response)
    return response.choices[0].message.parsed


# %%
# Main process
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])



def load_existing_json(json_file_path):
    """
    Load existing JSON file if it exists, otherwise return an empty list.
    
    :param json_file_path: Path to the JSON file
    :return: List of existing bounding box data or an empty list if the file does not exist
    """
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            return json.load(f)
    return []

def append_to_json(file_name, bbox, json_file_path):
    """
    Append a single image's bounding box data to the JSON file.
    
    :param file_name: Name of the image file
    :param bbox: Bounding box as [x_center, y_center, width, height]
    :param json_file_path: Path to the JSON file
    """
    new_entry = {
        "file_name": file_name,
        "bbox": bbox
    }
    
    # Load existing data
    data = load_existing_json(json_file_path)
    
    # Append the new entry
    data.append(new_entry)
    
    # Write back to the JSON file
    with open(json_file_path, 'w') as f:
        json.dump(data, f, indent=4)

def process_directory(directory, client, example, json_file_path):
    """
    Process all images in the directory and dynamically append bounding boxes to a JSON file.
    
    :param directory: Path to the directory containing images
    :param client: OpenAI client for LLM detection
    :param example: Pre-processed example image for comparison
    :param json_file_path: Path to the JSON file to save bounding boxes dynamically
    :return: None
    """
    # Iterate over each file in the directory
    i = 0
    for file_name in os.listdir(directory):
        # Only process image files (you can add more extensions if needed)
        if file_name.endswith(".jpg") or file_name.endswith(".png"):
            file_path = os.path.join(directory, file_name)
            
            try:
                # Open the image
                image = Image.open(file_path)
                
                # Pre-process the image and generate the overlayed grid image
                image_processed = process(image)
                
                # Initialize variables for storing bounding boxes
                image_ = image
                cells = []
                done = False
                
                # Detect objects and crop iteratively
                for i in range(3):
                    response = ask_llm_to_detect_ui(client, example, convert_to_base64(reduce_image_size(image_)), image_processed, image_.size)
                    if response.contains_object[0].done:
                        break
                    col = response.contains_object[0].columns
                    row = response.contains_object[0].rows
                    cells.append([(col, row)])
                    image_ = crop_image(image_, cells[i])
                    image_processed = process(image_)
                
                # Calculate bounding box based on the crops
                boxes = calculate_box_from_crops(image, cells)
                if boxes:
                    left, top, right, bottom = boxes[0]
                    width = right - left
                    height = bottom - top
                    x_center = left + width / 2
                    y_center = top + height / 2
                    
                    # Append the result to the JSON file dynamically
                    append_to_json(file_name, [x_center, y_center, width, height], json_file_path)
                    print(f"Processed {file_name} and appended to JSON.")
                
            except Exception as e:
                print(f"Error processing {file_name}: {e}")
        i += 1
        print(f"Processed {i} images.")

# Usage
directory_path = 'one_person_images'  # Directory containing images
json_file_path = 'bounding_boxes_llm.json'  # JSON file to save results
process_directory(directory_path, client, example_processed, json_file_path)
