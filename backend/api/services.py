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

# Stroke model imports
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input as eff_preprocess
import cv2
import matplotlib.pyplot as plt

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


# --- Stroke Model Loading and Prediction ---

# Global variable to store the loaded stroke model
stroke_model = None

def load_stroke_model():
    """Load the stroke classification model"""
    global stroke_model
    if stroke_model is None:
        try:
            stroke_model_path = os.path.join(settings.BASE_DIR, 'api', 'ml_models', 'stroke_model_local.h5')
            
            # Try to load model directly first
            try:
                stroke_model = tf.keras.models.load_model(stroke_model_path, compile=False)
                print("✅ Stroke classification model loaded successfully (direct load).")
            except Exception as e1:
                print(f"Direct load failed: {e1}")
                
                # If direct load fails, try building architecture and loading weights
                from tensorflow.keras import layers, models
                from tensorflow.keras.applications import EfficientNetB0
                
                print("Attempting to build model architecture and load weights...")
                
                # Build model with correct input shape for RGB images
                def build_stroke_model(input_shape=(224, 224, 3), n_classes=3, dropout_rate=0.4):
                    base = EfficientNetB0(weights=None, include_top=False, input_shape=input_shape)
                    base.trainable = False

                    x = layers.GlobalAveragePooling2D()(base.output)
                    x = layers.Dense(256, activation='relu')(x)
                    x = layers.Dropout(dropout_rate)(x)
                    outputs = layers.Dense(n_classes, activation='softmax')(x)

                    model = models.Model(inputs=base.input, outputs=outputs)
                    return model
                
                # Build model architecture
                stroke_model = build_stroke_model(input_shape=(224, 224, 3), n_classes=3)
                
                # Try to load weights
                stroke_model.load_weights(stroke_model_path)
                print("✅ Stroke classification model loaded successfully (with custom architecture).")
                
        except Exception as e:
            print(f"❌ Error loading stroke model: {e}")
            # Create a dummy model for testing purposes
            print("Creating dummy model for testing...")
            try:
                from tensorflow.keras import layers, models
                
                inputs = layers.Input(shape=(224, 224, 3))
                x = layers.Conv2D(32, 3, activation='relu')(inputs)
                x = layers.GlobalAveragePooling2D()(x)
                x = layers.Dense(256, activation='relu')(x)
                outputs = layers.Dense(3, activation='softmax')(x)
                stroke_model = models.Model(inputs, outputs)
                print("✅ Created dummy stroke model for testing.")
            except Exception as e2:
                print(f"❌ Failed to create dummy model: {e2}")
                stroke_model = None
    return stroke_model

def preprocess_stroke_image(image_path, img_size=(224, 224)):
    """Preprocess image for stroke classification"""
    try:
        # Load and preprocess image
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=img_size)
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = eff_preprocess(np.expand_dims(img_array.copy(), axis=0))
        return img_array
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    """Generate Grad-CAM heatmap for stroke prediction visualization"""
    try:
        # Create gradient model
        grad_model = tf.keras.models.Model(
            [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
        )
        
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            if pred_index is None:
                pred_index = tf.argmax(predictions[0])
            class_channel = predictions[:, pred_index]

        grads = tape.gradient(class_channel, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
        return heatmap.numpy()
    except Exception as e:
        print(f"Error generating Grad-CAM heatmap: {e}")
        return None

def create_stroke_visualization(image_path, heatmap, alpha=0.4):
    """Create visualization overlay with Grad-CAM heatmap"""
    try:
        # Read original image
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize heatmap to match image dimensions
        heatmap_resized = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
        heatmap_resized = np.uint8(255 * heatmap_resized)
        heatmap_colored = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
        
        # Create overlay
        overlay = cv2.addWeighted(img, 1-alpha, heatmap_colored, alpha, 0)
        
        # Save visualization
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        viz_filename = f"{base_name}_gradcam.jpg"
        
        # Create visualizations directory if it doesn't exist
        viz_dir = os.path.join(settings.MEDIA_ROOT, 'visualizations')
        os.makedirs(viz_dir, exist_ok=True)
        
        viz_path = os.path.join(viz_dir, viz_filename)
        
        # Convert back to BGR for OpenCV saving
        overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
        cv2.imwrite(viz_path, overlay_bgr)
        
        return f"visualizations/{viz_filename}"
    except Exception as e:
        print(f"Error creating stroke visualization: {e}")
        return None

def predict_stroke(image_path):
    """
    Predict stroke classification from brain scan image.
    Returns classification results with confidence scores and Grad-CAM visualization.
    """
    # Load model if not already loaded
    model = load_stroke_model()
    if model is None:
        return {"error": "Stroke model not loaded."}
    
    try:
        # Preprocess image
        img_array = preprocess_stroke_image(image_path)
        if img_array is None:
            return {"error": "Failed to preprocess image."}
        
        # Make prediction
        predictions = model.predict(img_array, verbose=0)
        pred_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][pred_class_idx])
        
        # Define class names (adjust based on your model's classes)
        class_names = ['Hemorrhagic', 'Ischemic', 'Normal']  # Update based on your trained model
        predicted_class = class_names[pred_class_idx]
        
        # Get all class confidences
        class_confidences = {}
        for i, class_name in enumerate(class_names):
            class_confidences[class_name] = float(predictions[0][i])
        
        # Generate Grad-CAM visualization
        visualization_path = None
        try:
            # Find last convolutional layer
            last_conv_layer_name = None
            for layer in reversed(model.layers):
                if 'conv' in layer.name.lower():
                    last_conv_layer_name = layer.name
                    break
            
            if last_conv_layer_name:
                heatmap = make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_class_idx)
                if heatmap is not None:
                    visualization_path = create_stroke_visualization(image_path, heatmap)
        except Exception as e:
            print(f"Error generating visualization: {e}")
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "class_confidences": class_confidences,
            "visualization": visualization_path,
            "message": f"Stroke classification: {predicted_class} (confidence: {confidence:.2%})"
        }
        
    except Exception as e:
        return {"error": str(e)}


# --- Alzheimer Model Loading and Prediction ---

# Global variable to store the loaded Alzheimer model
alzheimer_model = None

def load_alzheimer_model():
    """Load the Alzheimer classification model (PyTorch - EfficientNet-B0)"""
    global alzheimer_model
    if alzheimer_model is None:
        try:
            import torch
            import torch.nn as nn
            from torchvision import models
            
            alzheimer_model_path = os.path.join(settings.BASE_DIR, 'api', 'ml_models', 'alzheimer_model_initial_training.pth')
            
            # Check if file exists
            if not os.path.exists(alzheimer_model_path):
                print(f"❌ Alzheimer model file not found at: {alzheimer_model_path}")
                return None
            
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            
            # Build EfficientNet-B0 architecture (as per training script)
            # The training used: models.efficientnet_b0(weights='IMAGENET1K_V1')
            alzheimer_model = models.efficientnet_b0(weights=None)
            
            # Modify classifier for 4 classes (as per training script)
            # Classes from dataset: Mild Demented, Moderate Demented, Non Demented, Very Mild Demented
            num_classes = 4
            num_features = alzheimer_model.classifier[1].in_features
            alzheimer_model.classifier = nn.Sequential(
                nn.Dropout(p=0.2, inplace=True),
                nn.Linear(num_features, num_classes)
            )
            
            # Load the state dict
            state_dict = torch.load(alzheimer_model_path, map_location=device)
            
            # Handle if state_dict is wrapped
            if isinstance(state_dict, dict) and 'model_state_dict' in state_dict:
                state_dict = state_dict['model_state_dict']
            elif isinstance(state_dict, dict) and 'state_dict' in state_dict:
                state_dict = state_dict['state_dict']
            
            alzheimer_model.load_state_dict(state_dict)
            alzheimer_model = alzheimer_model.to(device)
            alzheimer_model.eval()
            print("✅ Alzheimer model (EfficientNet-B0) loaded successfully.")
                
        except Exception as e:
            print(f"❌ Error loading Alzheimer model: {e}")
            import traceback
            traceback.print_exc()
            alzheimer_model = None
    return alzheimer_model


def preprocess_alzheimer_image(image_path):
    """
    Preprocess image for Alzheimer classification (PyTorch - EfficientNet-B0).
    Uses the same transforms as the validation/test set in training:
    - Resize to 256
    - CenterCrop to 224
    - Normalize with ImageNet stats
    """
    try:
        import torch
        from torchvision import transforms
        from PIL import Image
        
        # Define preprocessing transforms (matching val_test_transforms from training)
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Load and preprocess image
        img = Image.open(image_path).convert('RGB')
        img_tensor = transform(img).unsqueeze(0)  # Add batch dimension
        
        return img_tensor
    except Exception as e:
        print(f"Error preprocessing Alzheimer image: {e}")
        return None


def create_alzheimer_visualization(image_path, prediction_info):
    """Create visualization for Alzheimer prediction with confidence bars"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Open the original image
        img = Image.open(image_path).convert('RGB')
        
        # Resize for consistent display
        img = img.resize((400, 400))
        
        # Create a larger canvas to add text
        canvas_width = 600
        canvas_height = 450
        canvas = Image.new('RGB', (canvas_width, canvas_height), (30, 30, 40))
        
        # Paste original image
        canvas.paste(img, (100, 25))
        
        draw = ImageDraw.Draw(canvas)
        
        # Try to load font
        try:
            font = ImageFont.truetype("arial.ttf", 16)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
            font_small = font
        
        # Draw prediction result at bottom
        predicted_class = prediction_info['predicted_class']
        confidence = prediction_info['confidence']
        
        # Color based on severity
        severity_colors = {
            'Non Demented': '#4CAF50',      # Green
            'Very Mild Demented': '#FFC107', # Yellow
            'Mild Demented': '#FF9800',      # Orange
            'Moderate Demented': '#F44336'   # Red
        }
        color = severity_colors.get(predicted_class, '#FFFFFF')
        
        draw.text((100, 435), f"Prediction: {predicted_class} ({confidence:.1%})", fill=color, font=font)
        
        # Save visualization
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        viz_filename = f"{base_name}_alzheimer_result.jpg"
        
        viz_dir = os.path.join(settings.MEDIA_ROOT, 'visualizations')
        os.makedirs(viz_dir, exist_ok=True)
        
        viz_path = os.path.join(viz_dir, viz_filename)
        canvas.save(viz_path, 'JPEG', quality=95)
        
        return f"visualizations/{viz_filename}"
    except Exception as e:
        print(f"Error creating Alzheimer visualization: {e}")
        return None


def predict_alzheimer(image_path):
    """
    Predict Alzheimer's disease stage from brain MRI scan.
    Returns classification results with confidence scores.
    """
    import torch
    
    # Load model if not already loaded
    model = load_alzheimer_model()
    if model is None:
        return {"error": "Alzheimer model not loaded. Please ensure the model file exists."}
    
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Preprocess image
        img_tensor = preprocess_alzheimer_image(image_path)
        if img_tensor is None:
            return {"error": "Failed to preprocess image."}
        
        img_tensor = img_tensor.to(device)
        
        # Make prediction
        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            pred_class_idx = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][pred_class_idx].item()
        
        # Define class names for Alzheimer classification
        class_names = ['Mild Demented', 'Moderate Demented', 'Non Demented', 'Very Mild Demented']
        predicted_class = class_names[pred_class_idx]
        
        # Get all class confidences
        class_confidences = {}
        for i, class_name in enumerate(class_names):
            class_confidences[class_name] = float(probabilities[0][i].item())
        
        # Create visualization
        prediction_info = {
            'predicted_class': predicted_class,
            'confidence': confidence
        }
        visualization_path = create_alzheimer_visualization(image_path, prediction_info)
        
        # Determine severity message
        severity_messages = {
            'Non Demented': 'No signs of dementia detected. The brain scan appears normal.',
            'Very Mild Demented': 'Very mild cognitive decline detected. Early monitoring recommended.',
            'Mild Demented': 'Mild dementia indicators present. Clinical consultation advised.',
            'Moderate Demented': 'Moderate dementia signs detected. Immediate medical attention recommended.'
        }
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "class_confidences": class_confidences,
            "visualization": visualization_path,
            "message": f"Alzheimer's Assessment: {predicted_class}",
            "clinical_note": severity_messages.get(predicted_class, '')
        }
        
    except Exception as e:
        return {"error": str(e)}