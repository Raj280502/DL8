# Files NOT included in Git Repository

## Large Files Excluded:
- `api/ml_models/Yolov11m_BrainTumor.pt` - YOLO model file (~40MB+)
- `media/scans/` - Uploaded MRI scan images
- `media/annotated_images/` - Generated images with bounding boxes
- `db.sqlite3` - Development database

## To Setup Project:
1. Download the YOLO model file separately
2. Place it in `backend/api/ml_models/`
3. Create media directories:
   ```bash
   mkdir -p backend/media/scans
   mkdir -p backend/media/annotated_images
   ```

## Model File:
- Original model should be trained YOLOv11m for brain tumor detection
- Place as: `backend/api/ml_models/Yolov11m_BrainTumor.pt`
- Alternative: Use Git LFS for large files