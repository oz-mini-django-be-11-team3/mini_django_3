# apps/users/serializers.py
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


# HTTP 응답시, 필요한 정보만 선별해서 전달
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "name", "nickname")


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,  # 비밀번호는 response하지 않음
        required=True,
        style={
            "input_type": "password"
        },  # 비밀번호 입력 필드로 표시(DRF HTML에서 ****처럼 값이 안보이게 랜더링)
        min_length=8,
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        min_length=8,
    )

    class Meta:
        model = User  # CustomUserModel의 필드 특성 다 가져옴.
        fields = ("email", "name", "nickname", "phone_number", "password", "password2")
        # extra_kwargs = {
        #     "email": {"required": True},
        #     "nickname": {"required": True},
        #     "name": {"required": True},
        # }

    def validate(self, data):
        # 비밀번호와 비밀번호 확인이 일치하는지 검증
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "두 비밀번호가 일치하지 않습니다."}
            )

        # email = data["email"]
        # if User.objects.filter(email=email).exists():
        #     raise serializers.ValidationError("이미 등록된 이메일 주소입니다.")

        return data

    def create(self, validated_data):
        # 비밀번호2는 모델에 저장할 필요 없으므로 제거
        validated_data.pop("password2")

        # CustomUserManager의 create_user 메서드를 사용하여 사용자 생성
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            nickname=validated_data.get("nickname"),
            name=validated_data.get("name"),
            phone_number=validated_data.get("phone_number"),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "name",
            "nickname",
            "phone_number",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "created_at",
            "updated_at",
        ]


class LoginSerializer(serializers.Serializer):
    # serializers.ValidationError() 알아서 내줌
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")

        user = User.objects.filter(email=email).first()
        """
        password = data.get("password")

        # django.auth.authenticate(): db에서 가입자 여부 확인
        # 사용자 여부 / 오류 여부 구분 추가 가능?
        user = authenticate(self.context.get("request"), email=email, password=password)

        if not user:
            raise serializers.ValidationError("잘못된 이메일 또는 비밀번호입니다.")    
        """

        data = user  # data["user"] = user 도 가능.
        return data
