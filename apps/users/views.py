from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView, Response
from .permissions import IsOwner
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, UserRegistrationSerializer, UserSerializer

User = get_user_model()

class UserRegistrationView(APIView):
    """
    새로운 사용자 계정을 생성하는 API 뷰입니다.
    """

    authentication_classes = ()
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
        if serializer.is_valid():
            serializer.save()  # 시리얼라이저의 create 메서드 호출
            return Response(
                {"message": "회원가입이 성공적으로 완료되었습니다."},
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
        serializer.is_valid(
            raise_exception=True
        )  # 유효성 검사 실패 시 자동으로 400 응답

        user = serializer.validated_data[
            "user"
        ]  # validate 메서드에서 설정한 user 가져오기

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # user 객체를 시리얼라이저에 바로 전달
        user_serializer = UserSerializer(user)

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
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token이 제공되지 않았습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)  # RefreshToken 객체로 만들어줌
            token.blacklist()  # refresh token을 블랙리스트에 추가

            response = Response(
                {"message": "성공적으로 로그아웃되었습니다."},
                status=status.HTTP_205_RESET_CONTENT,  # HTTP 204 No Content도 흔히 사용됨
            )

            #    로그인 시 설정했던 쿠키 옵션과 동일하게 설정하는 것이 중요함!
            response.set_cookie(
                "refresh_token",
                value="",  # 값을 비워줌
                httponly=True,
                secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
                samesite="Lax",
                max_age=0,  # 만료 시간을 0으로 설정하여 즉시 삭제
                expires="Thu, 01 Jan 1970 00:00:00 GMT",
            )
            return response

        except TokenError:
            # simplejwt의 TokenError (예: 토큰이 유효하지 않거나 만료됨)
            return Response(
                {"error": "유효하지 않거나 만료된 토큰입니다."},
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

    @extend_schema(
        responses={
            200: {"message": "프로필이 성공적으로 조회되었습니다."},
            500: {"message": "서버에 문제가 있습니다."},
        }
    )
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

    @extend_schema(
        request=UserSerializer,
        responses={
            200: {"message": "프로필이 성공적으로 수정되었습니다."},
            400: UserSerializer,
        },
    )
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

    @extend_schema(responses={204: None, 500: {"message": "서버에 문제가 있습니다."}})
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