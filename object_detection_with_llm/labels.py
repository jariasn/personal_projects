import os
import json
from pycocotools.coco import COCO

# Initialize COCO API for instance annotations
coco = COCO('annotations/instances_train2017.json')

# Get the category ID for the person class
person_category_id = coco.getCatIds(catNms=['person'])[0]

# Path to the directory where your downloaded images are
image_folder = 'one_person_images'

# Get the image file names in the folder
image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]

# Initialize a list to store the bounding boxes
bounding_boxes = []

# Loop through the image files and get the corresponding bounding boxes
for image_file in image_files:
    # Extract image ID from file name (remove '000000' and '.jpg')
    image_id = int(image_file.split('_')[-1].split('.')[0])

    # Get image information using the image ID
    img_info = coco.loadImgs([image_id])[0]

    # Get the annotations (person) for that image
    ann_ids = coco.getAnnIds(imgIds=img_info['id'], catIds=[person_category_id])
    anns = coco.loadAnns(ann_ids)

    # Since we filtered for images with only one person, we expect only one annotation
    for ann in anns:
        if ann['category_id'] == person_category_id:
            bbox = ann['bbox']
            bounding_boxes.append({
                'file_name': image_file,
                'bbox': bbox
            })
            print(f"Image: {image_file}, Bounding box: {bbox}")

# Save bounding boxes to a file (optional)
with open('bounding_boxes.json', 'w') as f:
    json.dump(bounding_boxes, f, indent=4)
