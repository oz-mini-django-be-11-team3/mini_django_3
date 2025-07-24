from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsOwner
from .serializers import (
    LoginSerializer,
    UserInfoSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()


class UsersAPIView(APIView):
    """
    새로운 사용자 계정을 생성하는 API 뷰입니다.
    """

    # .settings.py의 기본 설정인 'simplejwt' 사용 해제
    authentication_classes = ()

    # .settings.py의 기본 설정인 '인증된 사용자만 허용' 사용 해제
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="새로운 사용자 계정 등록",
        description="이메일, 닉네임, 이름, 비밀번호를 사용하여 새로운 사용자 계정을 생성합니다. 전화번호는 선택 사항입니다.",
        request=UserRegistrationSerializer,
        responses={
            201: {
                "description": "회원가입 성공",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "example": "회원가입이 성공적으로 완료되었습니다.",
                                }
                            },
                        }
                    }
                },
            },
            400: UserRegistrationSerializer,  # 유효성 검사 실패 시 시리얼라이저 에러 반환
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():  # UserRegistrationSerializer.validate()
            serializer.save()  # UserRegistrationSerializer.create()
            return Response(
                data={"message": "회원가입이 성공적으로 완료되었습니다."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JWTLoginView(APIView):
    """
    SimpleJWT를 활용한 LoginView
    """

    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: {"message": "로그인이 성공적으로 완료되었습니다."},
            400: LoginSerializer,
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})

        try:
            # ValidationError:HTTP_400_BAD_REQUEST 응답
            serializer.is_valid(raise_exception=True)

            user = serializer.validated_data["user"]

            # Token 발급
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            user_serializer = UserInfoSerializer(user)

            response = Response(
                {"access": access_token, "user": user_serializer.data},
                status=status.HTTP_200_OK,
            )
            response.set_cookie(
                "refresh_token",
                value=str(refresh),
                httponly=True,
                secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
                samesite="Lax",
                max_age=5 * 60 * 60,  # 5시간
            )
            return response
        except AttributeError:
            return Response(
                {"error": f"아이디나 비밀번호를 확인해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class JWTLogoutView(APIView):
    """
    쿠키로 refresh_token을 받아 logout해주는 View
    """

    @extend_schema(
        responses={
            205: {"message": "성공적으로 로그아웃되었습니다."},
            500: {"message": "서버에 문제가 있습니다."},
        }
    )
    def get(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            # SimpleJWT가 앱 수준에서 HTTP_401_UNAUTHORIZED 에러 내줌
            # error: Authentication credentials were not provided
            # error: token_not_valid
            # "code": "user_not_found"
            #
            # 이상한 토큰이나 만료된 토큰이면, HTTP_400_BAD_REQUEST
            # error: Token is blacklisted
            #
            # if not refresh_token:
            #     return Response(
            #         {"error": "Refresh token이 제공되지 않았습니다."},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )

            token = RefreshToken(refresh_token)
            token.blacklist()  # refresh token을 블랙리스트에 추가

            response = Response(
                {"message": "성공적으로 로그아웃되었습니다."},
                status=status.HTTP_205_RESET_CONTENT,  # or HTTP_204_NO_CONTENT
            )
            response.set_cookie(
                "refresh_token",
                value="",
                httponly=True,
                secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
                samesite="Lax",
                max_age=0,  # 만료 시간을 0으로 설정하여 즉시 삭제
            )
            return response
        except TokenError as e:
            return Response(
                data={"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            # 그 외 예상치 못한 에러
            return Response(
                {"error": f"로그아웃 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserProfileAPIView(APIView):
    """
    사용자 프로필 조회, 수정, 삭제를 위한 API 뷰
    """

    # View 수준 권한 검사
    permission_classes = (IsOwner,)

    @extend_schema(
        responses={
            200: {"message": "프로필이 성공적으로 조회되었습니다."},
            500: {"message": "서버에 문제가 있습니다."},
        }
    )
    def get(self, request):
        """
        GET: 특정 사용자의 프로필 정보를 조회합니다.
        """

        # custom_permission_classes 안 쓰고 request.user.pk로 대신 사용 가능
        user_to_retrieve = get_object_or_404(User, pk=request.user.id)

        # 객체 수준 권한 검사: 요청하는 사용자가 이 프로필의 소유자인지 확인
        # APIView는 generics 뷰와 달리 check_object_permissions을 명시적으로 호출해야 합니다.
        self.check_object_permissions(request, user_to_retrieve)

        serializer = UserInfoSerializer(user_to_retrieve)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserProfileSerializer,
        responses={
            200: {"message": "프로필이 성공적으로 수정되었습니다."},
            400: UserProfileSerializer,
        },
    )
    def patch(self, request):
        """
        PATCH: 특정 사용자의 프로필 정보를 부분 업데이트합니다.
        """
        user_to_update = get_object_or_404(User, pk=request.user.id)
        self.check_object_permissions(request, user_to_update)

        # partial=True는 PATCH 요청에 필수적입니다. 일부 필드만 검증합니다.
        serializer = UserProfileSerializer(
            user_to_update, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # 인스턴스 전체 저장

        user.set_password(user.password)  # 비밀번호 해싱
        user.save()

        user_serializer = UserInfoSerializer(user)

        return Response(user_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            204: None,
        }
    )
    def delete(self, request):
        """
        DELETE: 특정 사용자 계정을 삭제합니다.
        """

        user_to_delete = get_object_or_404(User, pk=request.user.id)
        self.check_object_permissions(request, user_to_delete)

        user_to_delete.delete()  # 사용자 삭제
        return Response(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
