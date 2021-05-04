from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.shortcuts import get_object_or_404

from club_project import serializers
from club_project.permissions import IsOwnerOrReadOnly
from club_project.models import TblProjectIntroduction, TblClub

from submit_pow import settings

import jwt


class ProjectAPIView(APIView):
    serializer_class = serializers.ProjectSerializer
    authentication_classes = [JSONWebTokenAuthentication]
    permission_classes = (IsOwnerOrReadOnly,)

    def verify_authentication_token(self, request, club_id):
        token = jwt.decode(request.auth, settings.SECRET_KEY, algorithms=["HS256"])
        # {'user_id': 1, 'username': 'kwak', 'exp': 1619447947, 'email': 'kwak@kwak.com', 'orig_iat': 1618843147}
        return token['club_id'] != club_id

    def get(self, request, club_id):
        queryset = TblProjectIntroduction.objects.filter(club_id=club_id)
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)

    def post(self, request, club_id):
        """Create a project object"""
        if self.verify_authentication_token(request, club_id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class ProjectDetailAPIView(APIView):
    serializer_class = serializers.ProjectSerializer

    def verify_authentication_token(self, request, club_id):
        # {'user_id': 1, 'username': 'kwak', 'exp': 1619447947, 'email': 'kwak@kwak.com', 'orig_iat': 1618843147}
        token = jwt.decode(request.auth, settings.SECRET_KEY, algorithms=["HS256"])
        return token['club_id'] != club_id

    def get_object(self, project_id):
        return get_object_or_404(TblProjectIntroduction, pk=project_id)

    def get(self, request, club_id, project_id, format=None):
        """Project detail"""
        project = self.get_object(project_id)
        serializer = self.serializer_class(project)
        return Response(serializer.data)


    def put(self, request, club_id, project_id):
        """Update a project object"""
        if self.verify_authentication_token(request, club_id):
            return Response(
                {"error_message": "You don't have permission to update"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        project = self.get_object(project_id)
        serializer = self.serializer_class(project, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, club_id, project_id):
        """Delete a project object"""
        if self.verify_authentication_token(request, club_id):
            return Response(
                {"error_message": "You don't have permission to delete"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        project = self.get_object(project_id)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClubIntroUpdateAPIView(APIView):

    serializer_class = serializers.ClubSerializer

    def verify_authentication_token(self, request, club_id):
        # {'user_id': 1, 'username': 'kwak', 'exp': 1619447947, 'email': 'kwak@kwak.com', 'orig_iat': 1618843147}
        token = jwt.decode(request.auth, settings.SECRET_KEY, algorithms=["HS256"])
        return token['club_id'] != club_id

    def get(self, request, club_id):
        club = get_object_or_404(TblClub, pk=club_id)
        serializer = self.serializer_class(club)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, club_id):
        if self.verify_authentication_token(request, club_id):
            return Response(
                {"error_message": "You don't have permission to create"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = serializers.ClubSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, club_id):
        """Update a club introduction(contents)"""
        if self.verify_authentication_token(request, club_id):
            return Response(
                {"error_message": "You don't have permission to update"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        club = get_object_or_404(TblClub.objects.filter(id=club_id))
        serializer = serializers.ClubSerializer(club, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)