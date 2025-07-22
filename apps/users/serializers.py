from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers, status
from rest_framework.views import Response

User = get_user_model()


# HTTP 응답시, 필요한 정보만 선별해서 전달
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "name",
            "nickname",
            "phone_number",
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,  # 비밀번호는 response하지 않음
        required=True,  # 필수임
        style={
            "input_type": "password"
        },  # 비밀번호 입력 필드로 표시(DRF HTML에서 ****처럼 값이 안보이게 랜더링)
        min_length=8,  # 최소 비밀번호 길이 설정
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        min_length=8,
    )

    class Meta:
        model = User
        fields = ("email", "nickname", "name", "phone_number", "password", "password2")
        # extra_kwargs = {
        #     "email": {"required": True},
        #     "nickname": {"required": True},
        #     "name": {"required": True},
        # }

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "두 비밀번호가 일치하지 않습니다."}
            )

        # Class field로 알아서 검증
        # email = data["email"]
        # if User.objects.filter(email=email).exists():
        #     raise serializers.ValidationError("이미 가입된 이메일입니다.")

        return data

    def create(self, validated_data):
        # 비밀번호2는 모델에 저장할 필요 없으므로 제거
        validated_data.pop("password2")

        # CustomUserManager.create_user()
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            nickname=validated_data.get("nickname"),
            name=validated_data.get("name"),
            phone_number=validated_data.get("phone_number"),
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "name",
            "nickname",
            "password",
            "phone_number",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "created_at",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        # user = User.objects.filter(pk=instance.pk)
        instance.set_password(validated_data["password"])  # 비밀번호 해싱
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # django.auth.authenticate(): db에서 가입자 여부, 비번 일치 여부 확인
        user = authenticate(self.context.get("request"), email=email, password=password)

        data["user"] = user
        return data
