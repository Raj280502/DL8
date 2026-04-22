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

# Stroke model imports - loaded lazily to avoid startup crashes
# import tensorflow as tf
# from tensorflow.keras.applications.efficientnet import preprocess_input as eff_preprocess
import cv2
import matplotlib.pyplot as plt

# Report generation
from .report_generator import (
    generate_brain_tumor_report,
    generate_stroke_report,
    generate_alzheimer_report
)

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

        # Generate medical report
        prediction_result = {
            "predictions": filtered_predictions,
            "message": f"Detected {len(filtered_predictions)} brain tumor(s)",
            "annotated_image": annotated_image_path
        }
        try:
            report = generate_brain_tumor_report(prediction_result)
            prediction_result["report"] = report
        except Exception as e:
            print(f"Error generating brain tumor report: {e}")

        return prediction_result

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
    import tensorflow as tf
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
    import tensorflow as tf
    from tensorflow.keras.applications.efficientnet import preprocess_input as eff_preprocess
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
    import tensorflow as tf
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

def apply_stroke_fusion(image_probs: dict, clinical_data: dict) -> dict:
    """
    Rule-based late fusion for stroke classification: adjust image probabilities
    using clinical signals (age, risk_factors) without retraining the image model.

    Age interpretation:
        <50     → Lower stroke risk
        50-65   → Moderate stroke risk
        65-75   → Higher stroke risk
        >75     → Highest stroke risk
    """
    import copy
    probs = copy.deepcopy(image_probs)  # {'Hemorrhagic': 0.x, 'Ischemic': 0.x, 'Normal': 0.x}

    try:
        age = float(clinical_data.get('age', 60))
        age = max(0.0, min(120.0, age))
    except (TypeError, ValueError):
        return probs

    # Age-based adjustments
    if age >= 75:
        probs['Hemorrhagic'] *= 1.25
        probs['Ischemic'] *= 1.30
        probs['Normal'] *= 0.70
    elif age >= 65:
        probs['Hemorrhagic'] *= 1.15
        probs['Ischemic'] *= 1.20
        probs['Normal'] *= 0.85
    elif age >= 50:
        probs['Hemorrhagic'] *= 1.05
        probs['Ischemic'] *= 1.10
        probs['Normal'] *= 0.95
    else:  # age < 50
        probs['Normal'] *= 1.20
        probs['Ischemic'] *= 0.90
        probs['Hemorrhagic'] *= 0.85

    # Re-normalise so values sum to 1
    total = sum(probs.values())
    if total > 0:
        probs = {k: v / total for k, v in probs.items()}
    return probs


def predict_stroke(image_path, clinical_data=None):
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

        # Apply late fusion if clinical data provided
        image_only_probs = class_confidences.copy()
        fusion_applied = False
        if clinical_data and any(clinical_data.get(k) not in (None, '', 0) for k in ('age',)):
            fused_probs = apply_stroke_fusion(class_confidences, clinical_data)
            class_confidences = fused_probs
            fusion_applied = True

        # Get final predicted class after potential fusion
        predicted_class = max(class_confidences, key=class_confidences.get)
        confidence = class_confidences[predicted_class]

        # Generate medical report
        prediction_result = {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "class_confidences": class_confidences,
            "image_only_probs": image_only_probs,
            "visualization": visualization_path,
            "message": f"Stroke classification: {predicted_class} (confidence: {confidence:.2%})",
            "fusion_applied": fusion_applied,
            "clinical_inputs": clinical_data or {},
        }
        try:
            report = generate_stroke_report(prediction_result)
            prediction_result["report"] = report
        except Exception as e:
            print(f"Error generating stroke report: {e}")

        return prediction_result
        
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


# --- PyTorch Grad-CAM helpers for EfficientNet-B0 ---

_gradcam_gradients = {}
_gradcam_activations = {}

def _save_gradient(name):
    def hook(grad):
        _gradcam_gradients[name] = grad
    return hook

def _save_activation(name):
    def hook(module, input, output):
        _gradcam_activations[name] = output
    return hook


def make_alzheimer_gradcam(model, img_tensor, pred_class_idx, device):
    """
    Generate a Grad-CAM heatmap for a PyTorch EfficientNet-B0 model.
    Hooks into the last convolutional block (features[-1]).
    Returns a numpy heatmap array (H x W) normalised to [0, 1].
    """
    import torch
    _gradcam_gradients.clear()
    _gradcam_activations.clear()

    # Register hooks on the last feature block
    target_layer = model.features[-1]
    fwd_handle = target_layer.register_forward_hook(_save_activation('target'))
    img_tensor = img_tensor.to(device)

    # Forward pass
    model.eval()
    output = model(img_tensor)           # (1, num_classes)

    # Register backward hook after forward so we capture grads
    act = _gradcam_activations.get('target')  # (1, C, H, W)
    if act is None:
        fwd_handle.remove()
        return None

    act.retain_grad()
    bwd_handle = act.register_hook(_save_gradient('target'))

    # Backward on the predicted class
    model.zero_grad()
    score = output[0, pred_class_idx]
    score.backward()

    fwd_handle.remove()
    bwd_handle.remove()

    grads = _gradcam_gradients.get('target')   # (1, C, H, W)
    if grads is None:
        return None

    # Global average pooling over spatial dims
    weights = grads.squeeze(0).mean(dim=(1, 2))  # (C,)
    activation = act.squeeze(0)                   # (C, H, W)

    # Weighted combination
    cam = torch.zeros(activation.shape[1:], device=device)
    for i, w in enumerate(weights):
        cam += w * activation[i]

    cam = torch.relu(cam)
    cam = cam.detach().cpu().numpy()

    # Normalise
    if cam.max() > 0:
        cam = cam / cam.max()
    return cam


def create_alzheimer_visualization(image_path, prediction_info, heatmap=None):
    """Create Grad-CAM heatmap overlay for Alzheimer prediction."""
    try:
        # Read original image via OpenCV for easy overlay
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            raise ValueError("cv2 could not read image")
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        h, w = img_rgb.shape[:2]

        if heatmap is not None:
            # Resize heatmap to image size
            hm_resized = cv2.resize(heatmap, (w, h))
            hm_uint8  = np.uint8(255 * hm_resized)
            hm_color  = cv2.applyColorMap(hm_uint8, cv2.COLORMAP_JET)
            hm_rgb    = cv2.cvtColor(hm_color, cv2.COLOR_BGR2RGB)
            overlay   = cv2.addWeighted(img_rgb, 0.55, hm_rgb, 0.45, 0)
        else:
            overlay = img_rgb  # fallback: plain image

        # Save
        base_name    = os.path.splitext(os.path.basename(image_path))[0]
        viz_filename = f"{base_name}_alzheimer_gradcam.jpg"
        viz_dir      = os.path.join(settings.MEDIA_ROOT, 'visualizations')
        os.makedirs(viz_dir, exist_ok=True)
        viz_path     = os.path.join(viz_dir, viz_filename)
        cv2.imwrite(viz_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        return f"visualizations/{viz_filename}"
    except Exception as e:
        print(f"Error creating Alzheimer Grad-CAM visualization: {e}")
        return None


# --- Rule-Based Late Fusion ---

CLASS_NAMES_ALZ = ['Mild Demented', 'Moderate Demented', 'Non Demented', 'Very Mild Demented']

def apply_late_fusion(image_probs: dict, clinical_data: dict) -> dict:
    """
    Rule-based late fusion: adjust EfficientNet-B0 image probabilities using
    clinical signals (age, mmse_score) without retraining the image model.

    MMSE interpretation:
        27-30 → Normal
        21-26 → Mild impairment
        10-20 → Moderate impairment
         0-9  → Severe impairment

    Age weight: probability of more-severe classes increases for patients >75.
    """
    import copy
    probs = copy.deepcopy(image_probs)   # {'Non Demented': 0.x, ...}

    try:
        age        = float(clinical_data.get('age', 65))
        mmse       = float(clinical_data.get('mmse_score', 27))
        mmse       = max(0.0, min(30.0, mmse))
        age        = max(0.0, min(120.0, age))
    except (TypeError, ValueError):
        # Bad input — return image probs unchanged
        return probs

    # --- MMSE adjustments ---
    if mmse >= 27:          # Normal range
        probs['Non Demented']       *= 1.30
        probs['Very Mild Demented'] *= 0.85
    elif mmse >= 21:        # Mild impairment
        probs['Non Demented']       *= 0.75
        probs['Very Mild Demented'] *= 1.25
        probs['Mild Demented']      *= 1.20
    elif mmse >= 10:        # Moderate impairment
        probs['Non Demented']       *= 0.40
        probs['Very Mild Demented'] *= 0.70
        probs['Mild Demented']      *= 1.35
        probs['Moderate Demented']  *= 1.50
    else:                   # Severe impairment
        probs['Non Demented']       *= 0.20
        probs['Very Mild Demented'] *= 0.40
        probs['Mild Demented']      *= 0.80
        probs['Moderate Demented']  *= 2.00

    # --- Age adjustments ---
    if age >= 80:
        probs['Moderate Demented']  *= 1.20
        probs['Mild Demented']      *= 1.10
        probs['Non Demented']       *= 0.85
    elif age >= 70:
        probs['Mild Demented']      *= 1.08
        probs['Non Demented']       *= 0.95
    elif age < 55:          # Younger patients: lower prior for severe classes
        probs['Non Demented']       *= 1.15
        probs['Moderate Demented']  *= 0.70

    # Re-normalise so values sum to 1
    total = sum(probs.values())
    if total > 0:
        probs = {k: v / total for k, v in probs.items()}
    return probs


def predict_alzheimer(image_path, clinical_data=None):
    """
    Predict Alzheimer's disease stage from brain MRI scan.
    Optionally accepts clinical_data dict with 'age' and 'mmse_score'
    for multimodal late-fusion adjustment.
    """
    import torch

    model = load_alzheimer_model()
    if model is None:
        return {"error": "Alzheimer model not loaded. Please ensure the model file exists."}

    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        img_tensor = preprocess_alzheimer_image(image_path)
        if img_tensor is None:
            return {"error": "Failed to preprocess image."}

        img_tensor = img_tensor.to(device)

        # ── Step 1: Forward pass to get image-only probabilities ──
        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)

        class_names_alz = CLASS_NAMES_ALZ
        image_probs = {name: float(probabilities[0][i].item()) for i, name in enumerate(class_names_alz)}

        # ── Step 2: Grad-CAM (hook-based, no input gradients needed) ──
        pred_class_idx  = int(torch.argmax(probabilities, dim=1).item())
        heatmap = None
        try:
            heatmap = make_alzheimer_gradcam(model, img_tensor, pred_class_idx, device)
        except Exception as gc_err:
            print(f"Grad-CAM skipped: {gc_err}")

        # ── Step 3: Late Fusion (if clinical data provided) ──
        fusion_applied = False
        if clinical_data and any(clinical_data.get(k) not in (None, '', 0) for k in ('age', 'mmse_score')):
            fused_probs   = apply_late_fusion(image_probs, clinical_data)
            fusion_applied = True
        else:
            fused_probs = image_probs

        # Final prediction from fused probabilities
        predicted_class = max(fused_probs, key=fused_probs.get)
        confidence      = fused_probs[predicted_class]

        # ── Step 4: Visualization ──
        prediction_info   = {'predicted_class': predicted_class, 'confidence': confidence}
        visualization_path = create_alzheimer_visualization(image_path, prediction_info, heatmap=heatmap)

        severity_messages = {
            'Non Demented':       'No signs of dementia detected. The brain scan appears normal.',
            'Very Mild Demented': 'Very mild cognitive decline detected. Early monitoring recommended.',
            'Mild Demented':      'Mild dementia indicators present. Clinical consultation advised.',
            'Moderate Demented':  'Moderate dementia signs detected. Immediate medical attention recommended.',
        }

        result = {
            "predicted_class":  predicted_class,
            "confidence":       confidence,
            "class_confidences": fused_probs,
            "image_only_probs": image_probs,
            "visualization":    visualization_path,
            "message":          f"Alzheimer's Assessment: {predicted_class}",
            "clinical_note":    severity_messages.get(predicted_class, ''),
            "fusion_applied":   fusion_applied,
            "clinical_inputs":  clinical_data or {},
        }

        # Generate medical report
        try:
            report = generate_alzheimer_report(result)
            result["report"] = report
        except Exception as e:
            print(f"Error generating Alzheimer report: {e}")

        return result

    except Exception as e:
        import traceback; traceback.print_exc()
        return {"error": str(e)}