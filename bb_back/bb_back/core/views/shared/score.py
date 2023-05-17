import codecs
import csv
from math import exp

from django.db.models import Max
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from bb_back.core.models import Round, Submit
from bb_back.core.utils.view_utils import response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer
from bb_back.core.views.utils.decorators import is_staff_user


class ScoreView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    round_id = openapi.Parameter(
        'round_id',
        openapi.IN_QUERY,
        type=openapi.TYPE_INTEGER,
    )

    @swagger_auto_schema(
        manual_parameters=[round_id],
        responses={status.HTTP_200_OK: BaseResponseSerializer})
    @is_staff_user
    def put(self, request):
        DEFAULT_MAX_RATE = 999999999999999
        round_id = request.query_params.get("round_id")
        round = Round.objects.filter(id=round_id).first()
        if not round:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Round with id = {round_id} does not exist.")

        round_target = round.round_target
        target = [
            line for line in csv.DictReader(
                codecs.iterdecode(round_target, 'utf-8'))
        ]
        submit_dts = Submit.objects.filter(
            round_num=round.id).values('id_command').annotate(
                max_created_at=Max('created_at')).order_by().values(
                    'id_command', 'max_created_at')

        latest_submits = Submit.objects.filter(
            created_at__in=submit_dts.values('max_created_at'))
        submit_file_per_id = {
            submit.id: [
                line for line in csv.DictReader(
                    codecs.iterdecode(submit.file, 'utf-8'))
            ]
            for submit in latest_submits
        }
        for k, v in submit_file_per_id.items():
            transformed_submit = {val.get("id"): val.get("rate") for val in v}
            submit_file_per_id[k] = transformed_submit
        score_per_submit = {submit.id: 0 for submit in latest_submits}

        for line in target:
            company_id = line.get("id")
            fact = int(line.get("fact"))
            amount = float(line.get("amount"))
            min_rate_submit_id = None
            min_rate = DEFAULT_MAX_RATE
            for submit_id, rates_info in submit_file_per_id.items():
                rate = float(rates_info.get(company_id))
                if rate < min_rate:
                    min_rate_submit_id = submit_id
                    min_rate = rate
            if not min_rate_submit_id:
                continue
            p_tup = 1 / (1 + exp(-(0.1 - min_rate / 100) * 20))
            result_score = p_tup * (
                (1 - fact) * amount * min_rate - fact * amount)
            score_per_submit[min_rate_submit_id] += result_score
        for submit_id, score in score_per_submit.items():
            submit = Submit.objects.get(id=submit_id)
            submit.score = score
            submit.save()
        return Response(data={"scored": True}, status=status.HTTP_200_OK)
