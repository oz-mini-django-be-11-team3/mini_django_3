from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    객체(여기서는 User 인스턴스)의 소유자에게만 권한을 부여합니다.
    """

    message = "자신의 프로필에만 접근/수정/삭제할 수 있습니다."

    # has_permission: 뷰 레벨 권한 (요청 자체가 허용되는지)
    # has_object_permission: 객체 레벨 권한 (특정 객체에 대한 접근이 허용되는지)
    # APIView에서는 get_object()가 없으므로, has_object_permission을 직접 호출해야 합니다.

    def has_permission(self, request, view):
        # GET, PUT, PATCH, DELETE 요청 시에는 인증된 사용자만 view에 접근 허용
        # 이 부분은 IsAuthenticated와 유사
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 관리자는 모든 객체에 접근 가능해야 합니다.
        if request.user.is_superuser:
            return True
        # 요청하는 사용자가 해당 객체의 소유자인지 확인
        # obj는 User 모델 인스턴스이므로, obj.pk와 request.user.pk를 비교합니다.
        return obj == request.user
