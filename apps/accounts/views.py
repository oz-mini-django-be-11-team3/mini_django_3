from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account
from .serializers import AccountSerializer


class AccountListApiView(APIView):  # 계좌 목록 조회 , 생성을 처리함
    @extend_schema(
        summary="현재 로그인된 사용자의 계좌 목록 조회",
        description="인증된 사용자가 소유한 모든 계좌의 목록을 조회합니다.",
        responses={
            200: AccountSerializer(many=True),  # 성공 시 계좌 목록 반환
            201: {"description": "성공적으로 생성"},
            400: {"description": "잘못된 요청 데이터 (Bad Request)"},
            401: {"description": "인증 정보 없음 (Unauthorized)"},
        },
        tags=["accounts"],  # Swagger UI에서 뷰를 그룹화하는 태그
    )
    def get(self, request):  # 계좌 목록 조회
        accounts = Account.objects.filter(user=request.user)  # 로그인한 사용자와 관련된 계좌만 필터링
        serializer = AccountSerializer(
            accounts, many=True
        )  # accounts 데이터를 AccountSeriailzer를 사용하여 변환(JSON형식)
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )  # 요청이 성공적으로 처리, 상태코드 200

    @extend_schema(
        summary="새로운 계좌 생성",
        description="현재 로그인된 사용자를 위한 새로운 계좌를 생성합니다.",
        request=AccountSerializer,  # 요청 본문의 스키마를 AccountSeriailzer로 지정
        responses={
            201: AccountSerializer,  # 성공 시 생성된 계좌 정보 반환
            400: {"description": "잘못된 요청 데이터 (Bad Request)"},
            401: {"description": "인증 정보 없음 (Unauthorized)"},
        },
    )
    def post(self, request):  # 새 계좌 생성
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class AccountAPIView(APIView):  # 계좌 삭제 처리
    @extend_schema(
        summary="계좌 삭제",
        description="현재 로그인된 사용자의 계좌를 삭제합니다.",
        request=AccountSerializer,  # 요청 본문의 스키마를 AccountSeriailzer로 지정
        responses={
            201: AccountSerializer,  # 성공 시 생성된 계좌 정보 반환
            400: {"description": "잘못된 요청 데이터 (Bad Request)"},
            401: {"description": "인증 정보 없음 (Unauthorized)"},
            404: {"description": "거래 내역을 찾을 수 없음"},
        },
        tags=["accounts"],
    )
    def delete(self, request, pk):
        # 계좌를 찾거나, 없으면 404 에러를 반환합니다.
        account = get_object_or_404(Account, pk=pk, user=request.user)
        account.delete()
        return Response(
            {"detail": "Account deleted successfully."}, status=status.HTTP_200_OK
        )
