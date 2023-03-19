from django.db import transaction
from rest_framework import serializers, permissions, status as django_status
from rest_framework.views import APIView

from bb_back.core.constants import TeamApplicationStatusesEnum, TEAM_APPLICATION_STATUSES_NAMES
from bb_back.core.models import Team
from bb_back.core.models import TeamApplication
from bb_back.core.utils.view_utils import response, failed_validation_response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer, BadRequestResponseSerializer, \
    UserRolePermissionDeniedSerializer
from bb_back.core.views.utils.decorators import is_staff_user
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema


# region post review serializers
class CreateReviewApplicationRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    status = serializers.ChoiceField(
        required=True, choices=list(TEAM_APPLICATION_STATUSES_NAMES.values()))


class CreateReviewApplicationResponsePrivateSerializer(
        CreateReviewApplicationRequestSerializer):
    ...


class CreateReviewApplicationResponseSerializer(BaseResponseSerializer):
    response_data = CreateReviewApplicationResponsePrivateSerializer()


# endregion


class ReviewTeamApplicationView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(request_body=CreateReviewApplicationRequestSerializer,
                         responses={
                             django_status.HTTP_200_OK:
                             CreateReviewApplicationResponseSerializer,
                             django_status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer,
                             django_status.HTTP_403_FORBIDDEN:
                             UserRolePermissionDeniedSerializer
                         })
    @is_staff_user
    def post(self, request):
        request_data = CreateReviewApplicationRequestSerializer(
            data=request.data)
        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        data = request_data.data
        team_application = TeamApplication.objects.filter(
            id=data.get("id")).first()
        if not team_application:
            return response(
                status_code=django_status.HTTP_404_NOT_FOUND,
                data={},
                message=
                f"Team Application with id = {data.get('id')} does not exist.")
        with transaction.atomic():
            status = {i.name: i.value
                      for i in TeamApplicationStatusesEnum
                      }.get(data.get("status"))
            team_application.status = status
            team_application.save()
            if status == TeamApplicationStatusesEnum.STATUS_ACCEPTED.value:
                team = Team.objects.create(game=team_application.game,
                                           name=team_application.team_name,
                                           application=team_application)
                team_application.applicant.team = team
                team_application.applicant.save()
        response_data = CreateReviewApplicationResponseSerializer(
            data={
                "response_data": {
                    "id": team_application.id,
                    "status": data.get("status")
                }
            })
        response_data.is_valid()
        return Response(data=response_data.data,
                        status=django_status.HTTP_200_OK)
