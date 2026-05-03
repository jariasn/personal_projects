import os
import requests
from pycocotools.coco import COCO

# Initialize COCO API for instance annotations
coco = COCO('annotations/instances_train2017.json')

# Get all person category images
person_category_id = coco.getCatIds(catNms=['person'])[0]
img_ids = coco.getImgIds(catIds=[person_category_id])

# Filter images to those with only one person
one_person_images = []
for img_id in img_ids:
    ann_ids = coco.getAnnIds(imgIds=img_id, catIds=[person_category_id])
    anns = coco.loadAnns(ann_ids)
    if len(anns) == 1:  # Only one person in the image
        one_person_images.append(coco.loadImgs(img_id)[0])

# Download the first 100 images
output_dir = 'one_person_images'
os.makedirs(output_dir, exist_ok=True)

for i, img_info in enumerate(one_person_images[:100]):
    img_url = img_info['coco_url']
    img_data = requests.get(img_url).content
    with open(os.path.join(output_dir, f"{img_info['file_name']}"), 'wb') as f:
        f.write(img_data)
    print(f"Downloaded {i+1}/100: {img_info['file_name']}")
