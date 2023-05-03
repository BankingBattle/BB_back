import codecs
import csv
from math import exp

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from bb_back.core.models import Submit, Round
from bb_back.core.utils.view_utils import failed_validation_response, response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer
from bb_back.settings import SUBMIT_MAX_SIZE


class SubmitRequestSerializer(serializers.Serializer):
    file = serializers.FileField()
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
        team = request.user.team
        request_data = SubmitRequestSerializer(data=request.data)
        if not request_data.is_valid() or request.FILES.get("file") is None:
            return failed_validation_response(serializer=request_data)
        submit_file = request.FILES.get("file")
        if submit_file.size > SUBMIT_MAX_SIZE:
            return failed_validation_response(serializer=request_data)
        submit_schema = request_data.data
        round = Round.objects.filter(id=submit_schema.get("round_num")).first()
        if not round:
            return response(
                status_code=status.HTTP_400_BAD_REQUEST,
                data={},
                message=
                f"Round with id={submit_schema.get('round_num')} not found")
        try:
            csv_file = csv.DictReader(codecs.iterdecode(submit_file, 'utf-8'))
            for line in csv_file:
                line: dict
                if list(line.keys()) != ['id', 'rate']:
                    raise ValueError(
                        'CSV file columns must be: "id", "fact", "amount"')
                if not all([value.isnumeric() for value in line.values()]):
                    raise ValueError(
                        'All provided values must be valid integers')
        except ValueError as ex:
            return response(status_code=status.HTTP_400_BAD_REQUEST,
                            data={},
                            message=f"{str(ex)}")
        score = score_submit(submit_file=submit_file, round_id=round.id)

        Submit.objects.create(file=submit_file,
                              id_command=team.id,
                              round_num=submit_schema.get("round_num"),
                              score=score)

        response_data = SubmitResponseSerializer(
            data={"response_data": submit_schema})
        response_data.is_valid()
        return Response(data=response_data.data, status=status.HTTP_200_OK)


def score_submit(submit_file, round_id: int):
    submit = list(csv.DictReader(codecs.iterdecode(submit_file, 'utf-8')))
    total_score = 0.0
    round = Round.objects.get(id=round_id)
    target = list(
        csv.DictReader(codecs.iterdecode(round.round_target, 'utf-8')))
    for result in submit:
        target_line = [
            line for line in target if line.get('id') == result.get("id")
        ][0]
        rate: float = float(result.get("rate"))  # type: ignore
        fact = int(target_line.get("fact"))  # type: ignore
        amount = float(target_line.get("amount"))  # type: ignore
        p_tup = 1 / (1 + exp(-(0.1 - rate / 100) * 20))
        result_score = p_tup * ((1 - fact) * amount * rate - fact * amount)
        total_score += result_score

    return total_score
