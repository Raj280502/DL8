# Stroke Model Integration Guide

## Overview
This document explains how to use the integrated stroke classification model in the Brain Disease Detection system.

## Setup Instructions

### 1. Dependencies
Ensure all required packages are installed:
```bash
cd backend
pip install -r requirements.txt
```

### 2. Model File
The stroke model (`stroke_model_local.h5`) should be located in:
```
backend/api/ml_models/stroke_model_local.h5
```

### 3. Media Directories
The following directories are created automatically:
- `backend/media/scans/` - For uploaded brain scans
- `backend/media/visualizations/` - For Grad-CAM heatmap overlays
- `backend/media/annotated_images/` - For brain tumor detection annotations

## How to Use

### 1. Start the Backend Server
```bash
cd backend
python manage.py runserver
```

### 2. Start the Frontend
```bash
cd frontend
npm start
```

### 3. Using the Stroke Detection
1. Open the dashboard
2. Select "Stroke Detection" from the available models
3. Upload a brain scan image (JPEG, PNG supported)
4. View the results including:
   - Classification result (Hemorrhagic, Ischemic, or Normal)
   - Confidence scores for all classes
   - Grad-CAM visualization showing areas the AI focused on

## API Endpoints

### POST /api/detections/
Upload an image for stroke classification:
```bash
curl -X POST http://localhost:8000/api/detections/ \
  -F "model_type=STROKE" \
  -F "input_file=@brain_scan.jpg"
```

### Response Format for Stroke Classification
```json
{
  "id": 1,
  "model_type": "STROKE",
  "input_file": "http://localhost:8000/media/scans/brain_scan.jpg",
  "annotated_image": "visualizations/brain_scan_gradcam.jpg",
  "result": {
    "predicted_class": "Ischemic",
    "confidence": 0.89,
    "class_confidences": {
      "Hemorrhagic": 0.05,
      "Ischemic": 0.89,
      "Normal": 0.06
    },
    "visualization": "visualizations/brain_scan_gradcam.jpg",
    "message": "Stroke classification: Ischemic (confidence: 89%)"
  },
  "created_at": "2025-10-11T12:56:48.123456Z"
}
```

## Model Classes
The stroke model classifies images into three categories:
- **Hemorrhagic**: Bleeding in the brain
- **Ischemic**: Blood clot blocking blood flow
- **Normal**: No stroke detected

## Grad-CAM Visualization
The system automatically generates Grad-CAM (Gradient-weighted Class Activation Mapping) visualizations that show:
- Areas of the brain image the AI model focused on for making its decision
- Heat map overlay with warmer colors indicating higher importance
- Helps with interpretability and clinical understanding

## Frontend Features
- **Classification Display**: Shows the predicted class with confidence percentage
- **Confidence Breakdown**: Visual progress bars for all class probabilities
- **Grad-CAM Overlay**: Interactive visualization of model attention
- **Clinical Warning**: Disclaimer about AI usage in medical contexts

## Technical Details

### Model Architecture
- Base: EfficientNetB0 pre-trained on ImageNet
- Input size: 224x224 pixels
- Classes: 3 (Hemorrhagic, Ischemic, Normal)
- Output: Softmax probabilities

### Preprocessing
- Images are resized to 224x224
- EfficientNet preprocessing applied
- Normalization for optimal model performance

### Grad-CAM Implementation
- Uses the last convolutional layer for gradient computation
- Generates class-specific attention maps
- Overlays heatmap on original image with 40% alpha blending

## Error Handling
The system includes comprehensive error handling for:
- Invalid image formats
- Model loading failures
- Preprocessing errors
- Visualization generation issues

## Limitations and Disclaimers
⚠️ **Important Medical Disclaimer**
- This system is for research and educational purposes only
- Not intended for clinical diagnosis
- Always consult qualified medical professionals
- AI predictions should not replace professional medical judgment

## Troubleshooting

### Common Issues
1. **Model Not Loading**: Ensure `stroke_model_local.h5` is in the correct directory
2. **TensorFlow Errors**: Verify TensorFlow installation: `pip install tensorflow>=2.13.0`
3. **OpenCV Issues**: Install OpenCV: `pip install opencv-python>=4.8.0`
4. **Memory Issues**: Reduce batch size or image resolution if needed

### Logging
Check Django logs for detailed error messages:
```bash
python manage.py runserver --verbosity=2
```