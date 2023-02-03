from rest_framework import serializers, status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.response import Response
from django.http import HttpResponse
from bb_back.core.utils.view_utils import failed_validation_response
import os

from bb_back.core.models import Round
from bb_back.settings import SUBMIT_MAX_SIZE
from bb_back.settings import MEDIA_ROOT
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer


class RoundRequestSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    name = serializers.CharField(max_length=63)
    description = serializers.CharField()

    datetime_start = serializers.DateTimeField()
    datetime_end = serializers.DateTimeField()
    
    is_active = serializers.BooleanField(default=True)

    data = serializers.FileField()


class RoundResponseSerializer(BaseResponseSerializer):
    response_data = RoundRequestSerializer()


class RoundView(APIView):
     def get(self, request):
        file_path = os.path.join(MEDIA_ROOT, "submits/pom.xml")
        if os.path.exists(file_path):
            fh = open(file_path, 'rb')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
        return failed_validation_response(serializer=request_data)


class GetRoundDataView(APIView):
    def get(self, request, round_id):
        round = Round.objects.filter(id=round_id).first()
        file_path = os.path.join(MEDIA_ROOT, f"round_data/{1}/{round_id}.txt")
        if os.path.exists(file_path):
            fh = open(file_path, 'rb')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
        return failed_validation_response(serializer=request_data)