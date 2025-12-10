from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# --- AUTHENTICATION VIEWS ---
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
        })
import logging

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Detection
from rest_framework import viewsets
from .models import Detection
from .serializers import DetectionSerializer
from .services import predict_brain_tumor, predict_stroke, predict_alzheimer
from rag.chat import answer_question

logger = logging.getLogger(__name__)

class DetectionViewSet(viewsets.ModelViewSet):
    queryset = Detection.objects.all()
    serializer_class = DetectionSerializer

    def create(self, request, *args, **kwargs):
        # Log incoming request data for debugging
        logger.info(f"Detection create request: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # All of this logic must be indented inside the 'perform_create' method.
        # This method is called by DRF only when a new object is being created (e.g., via a POST request).
        
        # --- AI Analysis ---
        # 1. Save the file and initial data
        instance = serializer.save()
        
        # 2. Check the model type and call appropriate prediction service
        if instance.model_type == Detection.ModelTypes.BRAIN_TUMOR:
            # 3. Get the full path to the uploaded file
            image_path = instance.input_file.path
            
            # 4. Call the brain tumor prediction service
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
                
        elif instance.model_type == Detection.ModelTypes.STROKE:
            # Handle stroke detection
            image_path = instance.input_file.path
            
            # Call the stroke prediction service
            prediction_result = predict_stroke(image_path)
            
            # Handle the prediction result
            if 'error' not in prediction_result:
                # Store the predictions
                instance.result = prediction_result
                
                # Store the visualization path as annotated_image for consistency
                if prediction_result.get('visualization'):
                    instance.annotated_image = prediction_result['visualization']
                
                instance.save()
            else:
                # Handle prediction error
                instance.result = prediction_result
                instance.save()
        
        elif instance.model_type == Detection.ModelTypes.ALZHEIMER:
            # Handle Alzheimer detection
            image_path = instance.input_file.path
            
            # Call the Alzheimer prediction service
            prediction_result = predict_alzheimer(image_path)
            
            # Handle the prediction result
            if 'error' not in prediction_result:
                # Store the predictions
                instance.result = prediction_result
                
                # Store the visualization path as annotated_image for consistency
                if prediction_result.get('visualization'):
                    instance.annotated_image = prediction_result['visualization']
                
                instance.save()
            else:
                # Handle prediction error
                instance.result = prediction_result
                instance.save()
        
        else:
            # Handle unknown model types
            instance.result = {"message": f"Model type {instance.model_type} not yet implemented."}
            instance.save()


class ChatView(APIView):
    """Simple RAG chat endpoint backed by Pinecone and Hugging Face."""

    def post(self, request):
        question = request.data.get("question", "").strip()
        if not question:
            return Response({"error": "question is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = answer_question(question)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as exc:
            logger.exception("ChatView failed")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)