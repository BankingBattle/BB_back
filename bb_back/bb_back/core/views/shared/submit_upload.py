from rest_framework import serializers, status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.response import Response
from bb_back.core.utils.view_utils import failed_validation_response

from bb_back.core.models import Submit
from bb_back.settings import SUBMIT_MAX_SIZE
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer


class SubmitRequestSerializer(serializers.Serializer):
    file = serializers.FileField()
    id_command = serializers.IntegerField()
    round_num = serializers.IntegerField()


class SubmitResponseSerializer(BaseResponseSerializer):
    response_data = SubmitRequestSerializer()


class SubmitView(APIView):
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

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
        request_body=SubmitRequestSerializer,
        responses={status.HTTP_200_OK: SubmitResponseSerializer},
    )
    def post(self, request):
        request_data = SubmitRequestSerializer(data=request.data)
        if not request_data.is_valid() or request.FILES.get("file") is None:
            return failed_validation_response(serializer=request_data)
        submit_file = request.FILES.get("file")
        if submit_file.size > SUBMIT_MAX_SIZE:
            return failed_validation_response(serializer=request_data)
        submit_schema = request_data.data
        Submit.objects.create(
            file=submit_file,
            id_command=submit_schema.get("id_command"),
            round_num=submit_schema.get("round_num"),
        )

        response_data = SubmitResponseSerializer(data={"response_data": submit_schema})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)
