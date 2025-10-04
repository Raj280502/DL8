# api/services.py

# CORRECTED: Import the modern YOLO class from ultralytics
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import os
import json
import numpy as np
from django.conf import settings
from django.core.files.base import ContentFile
import io

# --- Load The YOLOv11 Model Once ---
try:
    # CORRECTED: Properly join the project's base directory with the relative path to the model
    model_path = os.path.join(settings.BASE_DIR, 'api', 'ml_models', 'Yolov11m_BrainTumor.pt')
    
    # CORRECTED: Load the YOLOv11 model using the ultralytics library
    model = YOLO(model_path)
    print("✅ YOLOv11 model loaded successfully.")

except Exception as e:
    print(f"❌ Error loading YOLOv11 model: {e}")
    model = None

def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.
    Each box is in format [xmin, ymin, xmax, ymax]
    """
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    
    # Calculate intersection area
    intersection_xmin = max(x1_min, x2_min)
    intersection_ymin = max(y1_min, y2_min)
    intersection_xmax = min(x1_max, x2_max)
    intersection_ymax = min(y1_max, y2_max)
    
    # If no intersection
    if intersection_xmin >= intersection_xmax or intersection_ymin >= intersection_ymax:
        return 0.0
    
    intersection_area = (intersection_xmax - intersection_xmin) * (intersection_ymax - intersection_ymin)
    
    # Calculate union area
    box1_area = (x1_max - x1_min) * (y1_max - y1_min)
    box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = box1_area + box2_area - intersection_area
    
    return intersection_area / union_area if union_area > 0 else 0.0

def apply_nms(predictions, iou_threshold=0.5):
    """
    Apply Non-Maximum Suppression to remove overlapping detections.
    Keep only the detection with highest confidence for overlapping boxes.
    """
    if not predictions:
        return predictions
    
    # Sort predictions by confidence in descending order
    sorted_predictions = sorted(predictions, key=lambda x: x['confidence'], reverse=True)
    
    # List to store final predictions after NMS
    final_predictions = []
    
    while sorted_predictions:
        # Take the prediction with highest confidence
        best_prediction = sorted_predictions.pop(0)
        final_predictions.append(best_prediction)
        
        # Remove all other predictions that have high IoU with the best one
        best_box = [best_prediction['xmin'], best_prediction['ymin'], 
                   best_prediction['xmax'], best_prediction['ymax']]
        
        # Filter out overlapping boxes
        remaining_predictions = []
        for pred in sorted_predictions:
            pred_box = [pred['xmin'], pred['ymin'], pred['xmax'], pred['ymax']]
            iou = calculate_iou(best_box, pred_box)
            
            # Keep the prediction only if IoU is below threshold
            if iou < iou_threshold:
                remaining_predictions.append(pred)
        
        sorted_predictions = remaining_predictions
    
    return final_predictions

# --- Prediction Function for YOLOv11 ---
def predict_brain_tumor(image_path, confidence_threshold=0.4, nms_threshold=0.5):
    """
    Runs prediction on a single image using a YOLOv11 model and returns
    the results in a JSON-friendly format compatible with the frontend.
    Also creates an annotated image with bounding boxes.
    
    Args:
        image_path: Path to the image file
        confidence_threshold: Minimum confidence for detections (default: 0.4)
        nms_threshold: IoU threshold for Non-Maximum Suppression (default: 0.5)
    """
    if model is None:
        return {"error": "Model not loaded."}

    try:
        # Run inference with configurable confidence threshold
        results = model.predict(source=image_path, conf=confidence_threshold, iou=0.5)
        
        # CORRECTED: Process results using the modern YOLOv11 result object structure
        predictions = []
        result = results[0] # Get the first result object
        
        # Check if any detections were found
        if result.boxes is None or len(result.boxes) == 0:
            return {
                "predictions": [],
                "message": "No brain tumors detected in this image.",
                "annotated_image": None
            }
        
        # Get the bounding box coordinates, class IDs, and confidence scores
        bboxes = result.boxes.xyxy.tolist()
        class_ids = result.boxes.cls.tolist()
        confidences = result.boxes.conf.tolist()
        
        # Combine the results into the format our frontend expects
        for bbox, class_id, conf in zip(bboxes, class_ids, confidences):
            predictions.append({
                "xmin": bbox[0],
                "ymin": bbox[1],
                "xmax": bbox[2],
                "ymax": bbox[3],
                "confidence": conf,
                "name": result.names[int(class_id)] # Get class name from its ID
            })
        
        # Apply Non-Maximum Suppression to remove duplicate detections
        print(f"🔍 Before NMS: {len(predictions)} detections")
        filtered_predictions = apply_nms(predictions, iou_threshold=nms_threshold)
        print(f"✅ After NMS: {len(filtered_predictions)} detections")
        
        # Log details of filtered predictions
        for i, pred in enumerate(filtered_predictions):
            print(f"   Final Detection {i+1}: {pred['name']} (confidence: {pred['confidence']:.3f})")
        
        # Create annotated image with filtered bounding boxes
        annotated_image_path = create_annotated_image(image_path, filtered_predictions)
        
        return {
            "predictions": filtered_predictions,
            "message": f"Detected {len(filtered_predictions)} brain tumor(s)",
            "annotated_image": annotated_image_path
        }

    except Exception as e:
        return {"error": str(e)}


def create_annotated_image(original_image_path, predictions):
    """
    Creates an annotated image with bounding boxes drawn on detected tumors.
    Returns the path to the annotated image.
    """
    try:
        # Open the original image
        image = Image.open(original_image_path)
        draw = ImageDraw.Draw(image)
        
        # Try to load a font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Define colors for different classes
        colors = {
            'brain_tumor': '#FF0000',  # Red
            'tumor': '#FF0000',        # Red
            'glioma': '#FF6600',       # Orange
            'meningioma': '#FF9900',   # Yellow-Orange
            'pituitary': '#0066FF'     # Blue
        }
        
        # Draw bounding boxes and labels
        for pred in predictions:
            # Get coordinates
            x1, y1, x2, y2 = pred['xmin'], pred['ymin'], pred['xmax'], pred['ymax']
            
            # Get color for this class
            class_name = pred['name'].lower()
            color = colors.get(class_name, '#FF0000')  # Default to red
            
            # Draw bounding box
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            
            # Create label text
            confidence = pred['confidence']
            label = f"{pred['name']}: {confidence:.2f}"
            
            # Draw label background
            text_bbox = draw.textbbox((x1, y1-25), label, font=font)
            draw.rectangle(text_bbox, fill=color)
            
            # Draw label text
            draw.text((x1, y1-25), label, fill='white', font=font)
        
        # Save the annotated image
        base_name = os.path.splitext(os.path.basename(original_image_path))[0]
        annotated_filename = f"{base_name}_annotated.jpg"
        
        # Create annotated images directory if it doesn't exist
        annotated_dir = os.path.join(settings.MEDIA_ROOT, 'annotated_images')
        os.makedirs(annotated_dir, exist_ok=True)
        
        annotated_path = os.path.join(annotated_dir, annotated_filename)
        image.save(annotated_path, 'JPEG', quality=95)
        
        # Return relative path for URL construction
        return f"annotated_images/{annotated_filename}"
        
    except Exception as e:
        print(f"Error creating annotated image: {e}")
        return None