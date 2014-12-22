from rest_framework import views, status, response

from ncauth import serializers


class SignupView(views.APIView):

    def post(self, request, format=None):
        serializer = serializers.SignupSerializer(data=request.DATA)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        user = serializer.object
        return response.Response({'id': user.id}, status.HTTP_201_CREATED)


class SigninView(views.APIView):

    def post(self, request, format=None):
        serializer = serializers.SigninSerializer(data=request.DATA)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        user = serializer.object
        return response.Response({'id': user.id}, status.HTTP_200_OK)
