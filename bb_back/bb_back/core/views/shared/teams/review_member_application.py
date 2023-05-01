from django.db import transaction
from rest_framework import serializers, permissions, status as django_status
from rest_framework.views import APIView

from bb_back.core.constants import TeamApplicationStatusesEnum, TEAM_APPLICATION_STATUSES_NAMES, MEMBER_COUNT_LIMIT
from bb_back.core.models.teams.member_application import MemberApplication
from bb_back.core.utils.view_utils import response, failed_validation_response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer, BadRequestResponseSerializer, \
    UserRolePermissionDeniedSerializer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema


class CreateReviewMemberAppRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    status = serializers.ChoiceField(
        required=True, choices=list(TEAM_APPLICATION_STATUSES_NAMES.values()))


class CreateReviewMemberAppResponsePrivateSerializer(
        CreateReviewMemberAppRequestSerializer):
    ...


class CreateReviewMemberAppResponseSerializer(BaseResponseSerializer):
    response_data = CreateReviewMemberAppResponsePrivateSerializer()


class ReviewMemberApplicationView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(request_body=CreateReviewMemberAppRequestSerializer,
                         responses={
                             django_status.HTTP_200_OK:
                             CreateReviewMemberAppResponseSerializer,
                             django_status.HTTP_400_BAD_REQUEST:
                             BadRequestResponseSerializer,
                             django_status.HTTP_403_FORBIDDEN:
                             UserRolePermissionDeniedSerializer
                         })
    def post(self, request):
        request_data = CreateReviewMemberAppRequestSerializer(
            data=request.data)
        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        data = request_data.data
        member_application = MemberApplication.objects.filter(
            id=data.get("id")).first()
        if not member_application:
            return response(
                status_code=django_status.HTTP_404_NOT_FOUND,
                data={},
                message=
                f"Member Application with id = {data.get('id')} does not exist."
            )
        team = member_application.team
        team_founder = team.application.applicant
        if request.user != team_founder:
            return response(
                status_code=django_status.HTTP_404_NOT_FOUND,
                data={},
                message=
                f"Only team founder with id = {team_founder.id} permitted to review members."
            )
        if not team.game.is_active:
            return response(
                status_code=django_status.HTTP_404_NOT_FOUND,
                data={},
                message="Application no longer active due to game been inactive"
            )

        accepted = TeamApplicationStatusesEnum.STATUS_ACCEPTED
        members = MemberApplication.objects.filter(team=team, status=accepted)
        if members.count() > MEMBER_COUNT_LIMIT and data.get(
                "status") == accepted:
            return response(status_code=django_status.HTTP_400_BAD_REQUEST,
                            data={},
                            message="Member limit exceeded.")

        with transaction.atomic():
            status = {i.name: i.value
                      for i in TeamApplicationStatusesEnum
                      }.get(data.get("status"))
            member_application.status = status
            member_application.save()
            if status == TeamApplicationStatusesEnum.STATUS_ACCEPTED.value:
                member_application.applicant.team = team
                member_application.applicant.save()
        response_data = CreateReviewMemberAppResponseSerializer(
            data={
                "response_data": {
                    "id": member_application.id,
                    "status": data.get("status")
                }
            })
        response_data.is_valid()
        return Response(data=response_data.data,
                        status=django_status.HTTP_200_OK)
