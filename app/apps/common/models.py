from django.db import models


class CommonModel(models.Model):
    # 고정
    created_at = models.DateTimeField("생성 일시", auto_now_add=True)

    # 데이터를 업데이트할 때 마다 변경
    updated_at = models.DateTimeField("최근 업데이트 일시", auto_now=True)

    """
    # DB에 테이블을 추가하지 마시오.
    # 다른 모델들이 상속할 수 있게
    """

    class Meta:
        abstract = True
