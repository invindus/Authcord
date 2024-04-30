from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from web_dev_noobs_be.settings import SRV_URL
from .serializers import CreateAuthorUserSerializer, LoginSerializer


@extend_schema(
    request=CreateAuthorUserSerializer,
    responses={
        201: inline_serializer(
            name='SignUpResponse',
            fields={
                'status': serializers.CharField(),
                'message': serializers.CharField(),
                'data': CreateAuthorUserSerializer(),
            }
        ),
        400: OpenApiResponse(response="Error")
    },
    description="This endpoint is used to signs up a new user and creates an author profile.",
    summary="User sign up")
class SignUpView(APIView):
    http_method_names = ['post']

    def post(self, request):
        serializer = CreateAuthorUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "status": "success",
                "message": "User signed up",
                "data": serializer.data

            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=LoginSerializer,
    responses={
        200: inline_serializer(
            name='LoginResponse',
            fields={
                'token': serializers.CharField(),
                'author_id': serializers.CharField(),
            }
        ),
        400: 'Your error response structure here',
    },
    description="This endpoint is used to authenticates a user and returns a token along with the author ID.",
    summary="User login"
)

@extend_schema(
    request=LoginSerializer,
    responses={
        200: inline_serializer(
            name='LoginResponse',
            fields={
                'token': serializers.CharField(),
                'author_id': serializers.CharField(),
            }
        ),
        400: 'Your error response structure here',
    },
    description="This endpoint is used to authenticate a user and returns a token along with the author ID.",
    summary="User login"
)
class LoginView(APIView):
    http_method_names = ['post']

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            author_id = user.author.id
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'author_id': author_id, 'serverName': f"{SRV_URL}",
                             "profileImage": user.author.profile_image},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
