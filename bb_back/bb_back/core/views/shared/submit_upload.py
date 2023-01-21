from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers, status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Создайте здесь представления.
from bb_back.core.utils.view_utils import response, failed_validation_response
from bb_back.core.models import Submit
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser


class SubmitRequestSerializer(serializers.Serializer):
    file = serializers.FileField()


class SubmitView(APIView):
    # parser_classes = (FileUploadParser,)
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    @csrf_exempt
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "file",
                in_=openapi.IN_FORM,
                description="file",
                type=openapi.TYPE_FILE,
                required=True,
            )
        ],
    )
    def post(self, request):
        request_data = SubmitRequestSerializer(data=request.data)
        if not request_data.is_valid() or request.FILES.get("file") == None:
            return failed_validation_response(serializer=request_data)
        # if request.FILES.get("file").size >
        submit_file = request.FILES.get("file")
        Submit.objects.create(file=submit_file)
        return response({"success": "True"})


class ResView(APIView):
    @csrf_exempt
    def get(self, request):
        return response(data=Submit.objects.count(), status_code=status.HTTP_200_OK)
