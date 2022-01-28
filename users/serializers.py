from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import CustomUser
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from versatileimagefield.serializers import VersatileImageFieldSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'phone/email'

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        return token


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    image = VersatileImageFieldSerializer(
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__100x100'),
        ],
        required=False
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number', 'password', 'password2', 'first_name', 'last_name', 'gender', 'image')
        extra_kwargs = {
            'phone_number': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'gender': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        try:
            user = CustomUser.objects.create(
                email=validated_data['email'],
                phone_number=validated_data['phone_number'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                gender=validated_data['gender'],
                image=validated_data['image'],
                )
        except KeyError:
            user = CustomUser.objects.create(
                email=validated_data['email'],
                phone_number=validated_data['phone_number'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                gender=validated_data['gender'],
            )

        user.set_password(validated_data['password'])
        user.save()

        return user


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'gender', 'image')


class UpdateAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'gender', 'image')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'gender': {'required': False},
            'image': {'required': False},
        }


class OtpRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=10)


class AccountVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4)
