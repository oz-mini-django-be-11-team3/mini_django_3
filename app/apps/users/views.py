from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.exceptions import (AuthenticationFailed,
                                                 InvalidToken, TokenError)
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsOwner
from .serializers import (LoginSerializer, UserInfoSerializer,
                          UserRegistrationSerializer, UserSerializer)

User = get_user_model()


class UserRegistrationView(APIView):
    """
    새로운 사용자 계정을 생성하는 API 뷰입니다.
    """

    # .settings.py의 기본 설정인 'simplejwt' 사용 해제
    authentication_classes = ()

    # .settings.py의 기본 설정인 '인증된 사용자만 허용' 사용 해제
    permission_classes = (AllowAny,)  # = [IsAuthenticated]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():  # UserRegistrationSerializer.validate()
            instance = serializer.save()  # UserRegistrationSerializer.create()
            serializer = UserInfoSerializer(instance)

            return Response(
                data=f"{serializer.data.get("nickname")} 님, 가입을 환영합니다!",
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import rest_framework_simplejwt.settings
import rest_framework_simplejwt.tokens
from rest_framework_simplejwt.serializers import (TokenBlacklistSerializer,
                                                  TokenObtainPairSerializer,
                                                  TokenRefreshSerializer,
                                                  TokenVerifySerializer)
from rest_framework_simplejwt.tokens import (AccessToken, BlacklistMixin,
                                             RefreshToken)
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)


# 로그인
class JWTLoginView(TokenObtainPairView):
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
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)

            # 역직렬화(JSON -> Model)
            serializer = LoginSerializer(
                data=request.data, context={"request": request}
            )

            # LoginSerializer.validate() 실행
            # (raise_exception=True): ValidationError:HTTP_400_BAD_REQUEST 응답
            serializer.is_valid()

            # LoginSerializer.validate()에서 설정한 user 객체
            instance = serializer.validated_data

            # 직렬화 위한 serializer
            return_serial = UserInfoSerializer(instance)

        except AuthenticationFailed as e:
            return Response(
                {f"{str(e)}": "잘못된 이메일 또는 비밀번호입니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Token 발급
        refresh = response.data["refresh"]  # RefreshToken.for_user(user)
        access = response.data["access"]

        # 응답 후, cookie에 token 저장
        response = Response(
            {"access": access, "refresh": refresh, "user": return_serial.data},
            headers={"Authorization": "Bearer " + str(access)},
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


from rest_framework_simplejwt.authentication import JWTAuthentication


# 로그아웃
class JWTLogoutView(TokenVerifyView):  #
    """
    쿠키로 refresh_token을 받아 logout해주는 View
    """

    # authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            # super().post(request, *args, **kwargs)  # 블랙리스트 추가 여부 들어있음.

            token = RefreshToken(refresh_token)
            # print(token)
            # print(token.token_type) # refresh

            # refresh token을 블랙리스트에 추가
            token.blacklist()  # TokenBlacklistSerializer(data=token).is_valid(): 정상 RefreshToken+AccessToken 아님

            response = Response(
                {"message": "성공적으로 로그아웃되었습니다."},
                status=status.HTTP_205_RESET_CONTENT,  # HTTP_204_NO_CONTENT
            )
            response.set_cookie(
                "refresh_token",
                value="",  # 값을 비워줌
                httponly=True,
                secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
                samesite="Lax",
                max_age=0,  # 만료 시간을 0으로 설정하여 즉시 삭제
                # expires="Thu, 01 Jan 1970 00:00:00 GMT",
            )
            return response
        except TokenError as e:
            return Response(
                {"error": f"유효하지 않은 토큰입니다: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except ValidationError as e:
            return Response(
                {"error": f"만료된 토큰입니다: {str(e)}"},
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
    permission_classes = (IsOwner,)  # IsAuthenticated는 has_permission에서 처리

    def get(self, request, pk):
        """
        GET: 특정 사용자의 프로필 정보를 조회합니다.
        """
        user_to_retrieve = get_object_or_404(User, pk=pk)

        # 객체 수준 권한 검사: 요청하는 사용자가 이 프로필의 소유자인지 확인
        # APIView는 generics 뷰와 달리 check_object_permissions을 명시적으로 호출해야 합니다.
        self.check_object_permissions(request, user_to_retrieve)

        serializer = UserSerializer(user_to_retrieve)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """
        PATCH: 특정 사용자의 프로필 정보를 부분 업데이트합니다.
        """
        user_to_update = get_object_or_404(User, pk=pk)

        # 객체 수준 권한 검사
        self.check_object_permissions(request, user_to_update)

        # partial=True는 PATCH 요청에 필수적입니다. 일부 필드만 검증합니다.
        serializer = UserSerializer(user_to_update, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # 업데이트된 인스턴스 저장
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        DELETE: 특정 사용자 계정을 삭제합니다.
        """
        user_to_delete = get_object_or_404(User, pk=pk)

        # 객체 수준 권한 검사
        self.check_object_permissions(request, user_to_delete)

        user_to_delete.delete()  # 사용자 삭제
        return Response(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
