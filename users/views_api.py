from .serializers import MyTokenObtainPairSerializer, OtpRequestSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser
from .serializers import RegisterSerializer, AccountSerializer, UpdateAccountSerializer, AccountVerificationSerializer
from rest_framework import generics, mixins
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import random
from drf_yasg.utils import swagger_auto_schema
from kavenegar import *
from rest_framework import status
from django.core.cache import cache


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    parser_classes = (FormParser, MultiPartParser)


class Profile(mixins.RetrieveModelMixin, generics.GenericAPIView, mixins.UpdateModelMixin):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated,)
    parser_classes = (FormParser, MultiPartParser)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AccountSerializer
        if self.request.method == 'PUT':
            return UpdateAccountSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.request.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


def send_otp(phone):
    otp = random.randint(1000, 9999)
    print('otp:', otp)

    user = CustomUser.objects.get(phone_number=phone)
    if user.phone_number_verified:
        message = f'Use {otp} to verify your Online Store account.'
    else:
        message = f'Use {otp} to verify your number on Online Store'
    try:
        api = KavenegarAPI(
            '5947445A44507850306C71474B7158554153357A66626A324B56584753726955485A3662443275354278553D')
        params = {
            'sender': '10008663',
            'receptor': f'0{phone}',
            'message': message
        }
        api.sms_send(params)
    except APIException as e:
        print(e)
        # return Response({'phone': phone}, status=status.HTTP_404_NOT_FOUND)
    except HTTPException as e:
        print(e)
        # return Response({'phone': phone}, status=status.HTTP_404_NOT_FOUND)
    cache.set(f'otp:{phone}', otp, timeout=300)
    return Response({'phone': phone}, status=status.HTTP_200_OK)


class OtpView(generics.GenericAPIView):

    @swagger_auto_schema(request_body=OtpRequestSerializer)
    def post(self, request):
        serializer = OtpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        try:
            user = CustomUser.objects.get(phone_number=phone)
        except:
            return Response({'message': f'{phone} not found!'}, status=status.HTTP_404_NOT_FOUND)
        if not user.phone_number_verified:
            return Response({'message': 'Account not verified!'}, status=status.HTTP_401_UNAUTHORIZED)
        return send_otp(phone)


class SendAccountVerificationCodeView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        phone = request.user.phone_number
        try:
            user = CustomUser.objects.get(phone_number=phone)
        except:
            return Response({'message': f'{phone} not found!'}, status=status.HTTP_404_NOT_FOUND)
        if user.phone_number_verified:
            return Response({'message': 'Account already verified!'}, status=status.HTTP_201_CREATED)
        return send_otp(phone)


class EnterAccountVerificationCodeView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=AccountVerificationSerializer)
    def post(self, request):
        serializer = AccountVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        phone = request.user.phone_number

        try:
            otp = cache.get(f'otp:{phone}')
            if otp is None:
                raise Exception
        except:
            return Response({'message': 'One time password has expired or not sent please try again!'},
                            status=status.HTTP_404_NOT_FOUND)
        if code == str(otp):
            request.user.phone_number_verified = True
            request.user.save()
            cache.delete(f'otp:{phone}')
            return Response({'message': 'Account verified!'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Wrong code!'}, status=status.HTTP_401_UNAUTHORIZED)
