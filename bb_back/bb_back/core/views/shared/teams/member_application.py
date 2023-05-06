from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers, permissions
from bb_back.core.models import Team
from ...utils.base_serializers import BaseResponseSerializer
from ....constants import TEAM_APPLICATION_STATUSES_NAMES, TeamApplicationStatusesEnum
from ....models.teams.member_application import MemberApplication
from ....utils.view_utils import response


class CreateTeamAppRequestSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()


class CreateTeamAppInnerResponse(serializers.Serializer):
    app_id = serializers.IntegerField()
    team_id = serializers.IntegerField()
    team_name = serializers.CharField()


class CreateMemberAppResponseSerializer(BaseResponseSerializer):
    response_data = CreateTeamAppInnerResponse()


class MemberApplicationSerializer(serializers.Serializer):
    app_id = serializers.IntegerField()
    applicant_email = serializers.CharField()
    status = serializers.ChoiceField(
        required=True, choices=list(TEAM_APPLICATION_STATUSES_NAMES.values()))


class GetMemberApplicationInnerResponse(serializers.Serializer):
    team_name = serializers.CharField()
    applications = MemberApplicationSerializer(many=True)


class GetMemberApplicationResponseSerializer(BaseResponseSerializer):
    response_data = GetMemberApplicationInnerResponse()


class MemberApplicationView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        responses={status.HTTP_201_CREATED: CreateMemberAppResponseSerializer})
    def post(self, request, team_id):
        team = Team.objects.filter(id=team_id).first()
        if not team:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Team with id = {team_id} does not exist.",
            )

        if request.user.team and request.user.team.game.id == team.game.id:
            return response(
                status_code=status.HTTP_400_BAD_REQUEST,
                data={},
                message=
                "You can't create member application while being a part of another team."
            )

        if team.application.status != TeamApplicationStatusesEnum.STATUS_ACCEPTED.value:
            return response(
                status_code=status.HTTP_400_BAD_REQUEST,
                data={},
                message=
                f"Team application with id = {team.application.id} has not been accepted.",
            )

        if MemberApplication.objects.filter(
                team=team, applicant=request.user).count() != 0:
            return response(
                status_code=status.HTTP_400_BAD_REQUEST,
                data={},
                message="Application was sent from this user",
            )

        application = MemberApplication.objects.create(
            team=team,
            applicant=request.user,
            status=TeamApplicationStatusesEnum.STATUS_PENDING)
        application.save()
        response_data = CreateMemberAppResponseSerializer(data={
            "response_data": {
                "app_id": application.id,
                "team_id": team_id
            }
        })
        response_data.is_valid()
        return Response(response_data.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: GetMemberApplicationResponseSerializer})
    def get(self, request, team_id):
        team = Team.objects.filter(id=team_id).first()
        if not team:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Team with id = {team_id} does not exist.",
            )
        raw_applications = MemberApplication.objects.filter(team=team)

        applications = []
        for i, app in enumerate(raw_applications):
            applications.append({
                "app_id":
                app.id,
                "applicant_email":
                app.applicant.email,
                "status":
                TEAM_APPLICATION_STATUSES_NAMES[app.status]
            })

        applications_data = MemberApplicationSerializer(applications,
                                                        many=True)
        response_data = GetMemberApplicationResponseSerializer(
            data={
                "response_data": {
                    "team_name": team.name,
                    "applications": applications_data.data
                }
            })
        response_data.is_valid()
        return Response(response_data.data, status=status.HTTP_200_OK)
