import json
import numpy as np

def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.
    
    :param box1: Bounding box 1 [x_center, y_center, width, height]
    :param box2: Bounding box 2 [x_center, y_center, width, height]
    :return: IoU value
    """
    # Convert from (x_center, y_center, width, height) to (x1, y1, x2, y2)
    def convert_to_corners(bbox):
        x_center, y_center, width, height = bbox
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center + height / 2
        return x1, y1, x2, y2
    
    x1_1, y1_1, x2_1, y2_1 = convert_to_corners(box1)
    x1_2, y1_2, x2_2, y2_2 = convert_to_corners(box2)
    
    # Calculate intersection
    x1_inter = max(x1_1, x1_2)
    y1_inter = max(y1_1, y1_2)
    x2_inter = min(x2_1, x2_2)
    y2_inter = min(y2_1, y2_2)
    
    inter_area = max(0, x2_inter - x1_inter) * max(0, y2_inter - y1_inter)
    
    # Calculate union
    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
    
    union_area = box1_area + box2_area - inter_area
    
    # Calculate IoU
    iou = inter_area / union_area if union_area != 0 else 0
    
    return iou

def calculate_containment(box1, box2):
    """
    Check if the predicted bounding box is fully or partially contained within the ground truth box.
    
    :param box1: Ground truth bounding box [x_center, y_center, width, height]
    :param box2: Predicted bounding box [x_center, y_center, width, height]
    :return: (fully_contained, partially_contained) -> two boolean values
    """
    # Convert both boxes to corner format
    def convert_to_corners(bbox):
        x_center, y_center, width, height = bbox
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center + height / 2
        return x1, y1, x2, y2
    
    x1_1, y1_1, x2_1, y2_1 = convert_to_corners(box1)
    x1_2, y1_2, x2_2, y2_2 = convert_to_corners(box2)
    
    # Check for full containment: all corners of box2 (predicted) inside box1 (ground truth)
    fully_contained = (
        x1_2 >= x1_1 and y1_2 >= y1_1 and 
        x2_2 <= x2_1 and y2_2 <= y2_1
    )
    
    # Calculate IoU
    iou = calculate_iou(box1, box2)
    
    # Partially contained if IoU > 0.1
    partially_contained = iou > 0.5
    
    return fully_contained, partially_contained

def convert_ground_truth_bbox(bbox):
    """
    Convert ground truth bounding box from [x_top_left, y_top_left, width, height] 
    to [x_center, y_center, width, height].
    
    :param bbox: Ground truth bounding box [x_top_left, y_top_left, width, height]
    :return: Bounding box in [x_center, y_center, width, height] format
    """
    x_top_left, y_top_left, width, height = bbox
    x_center = x_top_left + width / 2
    y_center = y_top_left + height / 2
    return [x_center, y_center, width, height]

def evaluate_model_with_containment(true_bboxes_file, predicted_bboxes_file, iou_threshold=0.5):
    """
    Evaluate the performance of the object detection model using IoU, mAP, and containment measures.
    This version evaluates only the images present in the predicted_bboxes_file.
    
    :param true_bboxes_file: Path to JSON file with ground truth bounding boxes
    :param predicted_bboxes_file: Path to JSON file with predicted bounding boxes
    :param iou_threshold: IoU threshold to consider a detection as correct
    :return: Mean Average Precision (mAP) score, and containment statistics
    """
    # Load the predicted bounding boxes
    with open(predicted_bboxes_file, 'r') as f:
        predicted_bboxes = json.load(f)
    
    # Load the ground truth bounding boxes
    with open(true_bboxes_file, 'r') as f:
        true_bboxes = json.load(f)
    
    # Create a dictionary of ground truth bboxes for quick lookup by file_name
    true_bboxes_dict = {entry["file_name"]: entry for entry in true_bboxes}
    
    # Initialize variables for evaluation
    total_iou = 0
    total_detections = 0
    correct_detections = 0
    precisions = []
    iou_list = []
    
    # Variables for containment stats
    fully_contained_count = 0
    partially_contained_count = 0
    
    # Iterate over the predicted bounding boxes
    for pred_box in predicted_bboxes:
        file_name = pred_box["file_name"]
        
        # Only evaluate if the ground truth exists for this file
        if file_name in true_bboxes_dict:
            true_box = true_bboxes_dict[file_name]
            
            # Convert ground truth bbox to [x_center, y_center, width, height]
            true_bbox_converted = convert_ground_truth_bbox(true_box["bbox"])
            
            # Calculate IoU between the predicted and true bounding boxes
            iou = calculate_iou(true_bbox_converted, pred_box["bbox"])
            iou_list.append(iou)
            total_iou += iou
            total_detections += 1
            
            # Check for containment
            fully_contained, partially_contained = calculate_containment(true_bbox_converted, pred_box["bbox"])
            
            # Count full and partial containment
            if fully_contained:
                fully_contained_count += 1
            elif partially_contained:
                partially_contained_count += 1
            
            # If IoU is greater than the threshold, count it as a correct detection
            if iou >= iou_threshold:
                correct_detections += 1
            
            # Calculate precision at this point
            precision = correct_detections / total_detections
            precisions.append(precision)
        else:
            print(f"Warning: No ground truth bounding box found for {file_name}")
    
    # Calculate mean IoU
    mean_iou = total_iou / total_detections if total_detections > 0 else 0

    
    
    # Calculate Average Precision (AP) at the IoU threshold
    average_precision = np.mean(precisions) if precisions else 0
    
    # Print containment results
    print(f"Fully Contained: {fully_contained_count}/{total_detections}")
    print(f"Partially Contained (> 50% IoU): {partially_contained_count}/{total_detections}")
    
    # Print evaluation metrics
    print(f"Mean IoU: {mean_iou:.4f}")
    print(f"Average Precision at IoU {iou_threshold}: {average_precision:.4f}")
    
    return average_precision, fully_contained_count, partially_contained_count, iou_list

# Example Usage
true_bboxes_file = 'bounding_boxes.json'  # Ground truth bounding boxes
predicted_bboxes_file = 'bounding_boxes_llm.json'  # Model predicted bounding boxes

# Evaluate model performance and containment statistics
map_score, fully_contained, partially_contained, iou_list = evaluate_model_with_containment(true_bboxes_file, predicted_bboxes_file, iou_threshold=0.5)

print(f"IoU > 0.95: {sum(np.array(iou_list) > 0.95)}")
print(f"IoU > 0.79: {sum(np.array(iou_list) > 0.79)}")
print(f"IoU > 0.4: {sum(np.array(iou_list) > 0.4)}")

#plot histogram of IoU values
import matplotlib.pyplot as plt
plt.hist(iou_list, bins=20, color='c', edgecolor='k', alpha=0.7)
plt.xlabel('IoU')
plt.ylabel('Frequency')
plt.title('IoU Distribution')
plt.show()