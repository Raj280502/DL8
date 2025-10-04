from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Detection(models.Model):
    class ModelTypes(models.TextChoices):
        BRAIN_TUMOR = 'BRAIN_TUMOR', 'Brain Tumor Detection'
        ALZHEIMER = 'ALZHEIMER', 'Alzheimer Detection'
        STROKE = 'STROKE', 'Stroke Detection'
        
     # user = models.ForeignKey(User, on_delete=models.CASCADE) # We'll add user logic later
    model_type = models.CharField(max_length=50, choices=ModelTypes.choices)
    input_file = models.FileField(upload_to='scans/')
    annotated_image = models.CharField(max_length=500, null=True, blank=True)  # Store path to annotated image
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_model_type_display()} request at {self.created_at.strftime('%Y-%m-%d %H:%M')}"