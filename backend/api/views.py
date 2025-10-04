from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Detection
from rest_framework import viewsets
from .models import Detection
from .serializers import DetectionSerializer
from .services import predict_brain_tumor # <-- Import our new function

class DetectionViewSet(viewsets.ModelViewSet):
    queryset = Detection.objects.all()
    serializer_class = DetectionSerializer

    def perform_create(self, serializer):
        # All of this logic must be indented inside the 'perform_create' method.
        # This method is called by DRF only when a new object is being created (e.g., via a POST request).
        
        # --- AI Analysis ---
        # 1. Save the file and initial data
        instance = serializer.save()
        
        # 2. Check if the model type is for brain tumor
        if instance.model_type == Detection.ModelTypes.BRAIN_TUMOR:
            # 3. Get the full path to the uploaded file
            image_path = instance.input_file.path
            
            # 4. Call the prediction service
            prediction_result = predict_brain_tumor(image_path)
            
            # 5. Handle the prediction result
            if 'error' not in prediction_result:
                # Store the predictions
                instance.result = prediction_result
                
                # Store the annotated image path
                if prediction_result.get('annotated_image'):
                    instance.annotated_image = prediction_result['annotated_image']
                
                instance.save()
            else:
                # Handle prediction error
                instance.result = prediction_result
                instance.save()