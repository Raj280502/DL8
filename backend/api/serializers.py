from rest_framework import serializers
from .models import Detection
class DetectionSerializer(serializers.ModelSerializer):
  class Meta:
      model = Detection
      fields = ['id', 'model_type', 'input_file', 'annotated_image', 'result', 'created_at']
      read_only_fields = ['annotated_image', 'result', 'created_at'] 