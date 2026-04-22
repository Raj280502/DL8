from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import HttpResponse
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
        username_or_email = request.data.get('username', '')
        password = request.data.get('password', '')
        
        # Try to authenticate using the provided value as a username
        user = authenticate(request, username=username_or_email, password=password)
        
        # If that fails, try to see if it's an email address
        if user is None:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
                
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user.username
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
        # 1. Save the file and initial data
        instance = serializer.save()

        # 2. Check the model type and call appropriate prediction service
        if instance.model_type == Detection.ModelTypes.BRAIN_TUMOR:
            image_path = instance.input_file.path
            prediction_result = predict_brain_tumor(image_path)

            if 'error' not in prediction_result:
                instance.result = prediction_result
                if prediction_result.get('annotated_image'):
                    instance.annotated_image = prediction_result['annotated_image']
            else:
                instance.result = prediction_result
            instance.save()

        elif instance.model_type == Detection.ModelTypes.STROKE:
            image_path = instance.input_file.path

            # Extract clinical data from request (age) for late fusion
            clinical_data = None
            try:
                import json
                raw = self.request.data.get('clinical_data', None)
                if raw:
                    clinical_data = json.loads(raw) if isinstance(raw, str) else raw
                    instance.clinical_data = clinical_data
            except Exception as e:
                logger.warning(f"Could not parse clinical_data: {e}")

            prediction_result = predict_stroke(image_path, clinical_data=clinical_data)

            if 'error' not in prediction_result:
                instance.result = prediction_result
                if prediction_result.get('visualization'):
                    instance.annotated_image = prediction_result['visualization']
            else:
                instance.result = prediction_result
            instance.save()

        elif instance.model_type == Detection.ModelTypes.ALZHEIMER:
            image_path = instance.input_file.path

            # Extract clinical data from request (age + mmse_score) for late fusion
            clinical_data = None
            try:
                import json
                raw = self.request.data.get('clinical_data', None)
                if raw:
                    clinical_data = json.loads(raw) if isinstance(raw, str) else raw
                    # Persist clinical data on the instance
                    instance.clinical_data = clinical_data
            except Exception as e:
                logger.warning(f"Could not parse clinical_data: {e}")

            prediction_result = predict_alzheimer(image_path, clinical_data=clinical_data)

            if 'error' not in prediction_result:
                instance.result = prediction_result
                if prediction_result.get('visualization'):
                    instance.annotated_image = prediction_result['visualization']
            else:
                instance.result = prediction_result
            instance.save()

        else:
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


class ReportDownloadView(APIView):
    """Download analysis report as text file."""

    def get(self, request, detection_id):
        try:
            detection = Detection.objects.get(id=detection_id)
            result = detection.result or {}
            report = result.get("report", "")

            if not report:
                return Response(
                    {"error": "No report available for this analysis"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Generate filename based on analysis type and timestamp
            model_type = detection.get_model_type_display()
            timestamp = detection.created_at.strftime("%Y%m%d_%H%M%S")
            filename = f"{model_type.replace(' ', '_')}_{timestamp}.txt"

            # Return report as downloadable text file
            response = HttpResponse(report, content_type='text/plain; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Detection.DoesNotExist:
            return Response(
                {"error": "Analysis not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error downloading report: {e}")
            return Response(
                {"error": "Error downloading report"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )