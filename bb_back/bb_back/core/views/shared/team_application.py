from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from bb_back.core.models import TeamApplication, Team
from ..utils.base_serializers import BaseResponseSerializer
from ...utils.view_utils import failed_validation_response, response


class CreateTeamAppRequestSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()


class CreateTeamAppInnerResponse(serializers.Serializer):
    id = serializers.IntegerField()
    team_id = serializers.IntegerField()
    user = serializers.CharField


class CreateTeamAppResponseSerializer(BaseResponseSerializer):
    response_data = CreateTeamAppInnerResponse()


class ApplicationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    applicant_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=['Pending', 'Accepted', 'Declined'])


class GetTeamAppInnerResponse(serializers.Serializer):
    team_id = serializers.IntegerField()
    applications = ApplicationSerializer(many=True)


class GetTeamAppResponseSerializer(BaseResponseSerializer):
    response_data = GetTeamAppInnerResponse()


class TeamAppView(APIView):

    @swagger_auto_schema(
        responses={status.HTTP_201_CREATED: CreateTeamAppResponseSerializer})
    def post(self, request, team_id):
        request_data = CreateTeamAppRequestSerializer(data=request.data)
        if not request_data.is_valid():
            return failed_validation_response(serializer=request_data)
        team = Team.objects.filter(id=team_id).first()
        if not team:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Team with id = {team_id} does not exist.",
            )
        application = TeamApplication.objects.create(team=team,
                                                     applicant=request.user,
                                                     status='Pending')
        application.save()
        response_data = CreateTeamAppResponseSerializer(
            data={
                "response_data":
                CreateTeamAppInnerResponse(id=application.id,
                                           team_id=request_data.team_id)
            })
        response_data.is_valid()
        return Response(response_data.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: GetTeamAppResponseSerializer})
    def get(self, request, team_id):
        team = Team.objects.filter(id=team_id).first()
        if not team:
            return response(
                status_code=status.HTTP_404_NOT_FOUND,
                data={},
                message=f"Team with id = {team_id} does not exist.",
            )
        raw_applications = TeamApplication.objects.filter(team=team)

        applications = []
        for i, app in enumerate(raw_applications):
            applications.append({
                "id": app.id,
                "applicant_id": app.applicant.id,
                "status": app.status
            })

        applications_data = ApplicationSerializer(applications, many=True)
        inner_response = {
            "team_id": team_id,
            "applications": applications_data.data
        }
        inner_response = GetTeamAppInnerResponse(data=inner_response)
        response_data = GetTeamAppResponseSerializer(
            response_data=inner_response)
        response_data.is_valid()
        return Response(response_data.data, status=status.HTTP_200_OK)
