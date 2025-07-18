from django.db import models


class CommonModel(models.Model):
    # 생성된 시간 (고정)
    created_at = models.DateTimeField(auto_now_add=True)

    # 데이터가 업데이트된 시간 (업데이트 할 때 마다 계속 시간이 변경)
    updated_at = models.DateTimeField(auto_now=True)

    """
    # DB에 테이블을 추가하지 마시오.
    # 다른 모델들이 상속할 수 있게
    """

    class Meta:
        abstract = True
