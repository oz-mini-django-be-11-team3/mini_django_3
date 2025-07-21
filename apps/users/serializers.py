from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


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
        model = User  # 모델에는 password2의 필드가 없는데 어찌 사용이 가능한가
        fields = ("email", "nickname", "name", "phone_number", "password", "password2")
        extra_kwargs = {
            "email": {"required": True},
            "nickname": {"required": True},
            "name": {"required": True},
        }

    def validate(self, data):
        # 비밀번호와 비밀번호 확인이 일치하는지 검증
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "두 비밀번호가 일치하지 않습니다."}
            )
        phone_number = data["phone_number"]
        if not phone_number.isdigit():
            raise serializers.ValidationError("휴대폰 번호는 숫자만 입력해야 합니다.")

        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("이미 등록된 휴대폰 번호입니다.")

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
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email:
            raise serializers.ValidationError("이메일을 입력하세요.")
        if not password:
            raise serializers.ValidationError("비밀번호를 입력하세요.")

        # authenticate는 db에 이메일이 존재하는지 등 사용자 존재 여부 확인을 해줌
        user = authenticate(self.context.get("request"), email=email, password=password)

        if not user:
            raise serializers.ValidationError("잘못된 이메일 또는 비밀번호입니다.")

        data["user"] = user
        return data
