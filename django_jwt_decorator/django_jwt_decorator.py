import jwt

from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth import login


class TokenError(Exception):
    msg = ''

    def __str__(self):
        return '%s' % self.msg


class TokenDecodeError(TokenError):
    msg = 'token decode error'


class TokenExpiredError(TokenError):
    msg = 'token has expired'


class TokenUserNotFound(TokenError):
    msg = 'user not Found'


class TokenAuthModelNotFound(TokenError):
    msg = 'auth model not found'


class TokenBackend:

    _settings = {
        "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),  # 认证TOKEN有效时间
        # "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # 刷新TOKEN有效时间
        "UPDATE_USER_LAST_LOGIN_TIME": True,  # 是否更新USER最后登录时间

        # 签名所使用的算法
        # 包含以下选项
        # [
        #  'HS256', 'HS384', 'HS512', 'ES256', 'ES384', 'ES512',
        #  'RS256', 'RS384', 'RS512', 'PS256', 'PS384', 'PS512',
        #  'EdDSA'
        # ]
        # 除HS系列外，需要额外安装 cryptography 依赖(可选：使用pyjwt[crypto]替代cryptography)
        "ALGORITHM": "HS256",
        "SIGING_KEY": settings.SECRET_KEY,  # 加密私钥 默认使用django的SECRET_KEY
        "VERIFYING_KEY": None,  # 验证密钥 HS算法下，将不会使用该值。 其余算法模式下，此处应填写公钥
        "AUDIENCE": None,
        "ISSUER": None,

        "AUTH_HEADER_TYPES": ['Bearer', ],
        "AUTH_HEADER_NAME": "AUTHORIZATION",
        "USER_PRIMARY_KEY_FIELD_NAME": "id",
        "USER_PRIMARY_KEY_FIELD_CLAIM": "id",
    }

    def __init__(self, *args, **kwargs):
        if hasattr(settings, 'DJANGO_JWT_SETTINGS'):
            self._settings = dict(
                self._settings, **settigns.DJANGO_JWT_SETTINGS)
        super().__init__(*args, **kwargs)

    def __getattr__(self, key):
        return self._settings.get(key)

    def __setattr__(self, key, value):
        self._settings[key] = value

    def get_payload(self, user):
        payload = {
            "expired": int((timezone.now() + self.ACCESS_TOKEN_LIFETIME).timestamp() * 1000),
            "token_type": "access",
        }
        payload[self.USER_PRIMARY_KEY_FIELD_CLAIM] = getattr(
            user, self.USER_PRIMARY_KEY_FIELD_NAME)
        return payload

    def encode(self, payload):
        if not payload.get('aud') and self.AUDIENCE:
            payload['aud'] = self.AUDIENCE
        if not payload.get('iss') and self.ISSUER:
            payload['iss'] = self.ISSUER
        return jwt.encode(payload=payload, key=self.SIGING_KEY, algorithm=self.ALGORITHM)

    def decode(self, raw_token):
        params = {
            "jwt": raw_token,
            "key": self.SIGING_KEY if 'HS' in self.ALGORITHM else self.VERIFYING_KEY,
            "algorithms": [self.ALGORITHM],
        }

        return jwt.decode(**params)

    def access_token(self, user):
        return self.encode(self.get_payload(user))

    def verify(self, raw_token):
        try:
            payload = self.decode(raw_token)
        except:
            raise TokenDecodeError()
        if timezone.now().timestamp() > payload['expired']:
            raise TokenExpiredError()
        User = get_user_model()
        query_params = {}
        query_params[self.USER_PRIMARY_KEY_FIELD_NAME] = payload[self.USER_PRIMARY_KEY_FIELD_CLAIM]
        try:
            user = User.objects.get(**query_params)
        except:
            raise TokenUserNotFound()
        return payload, user


Token = TokenBackend()


def JsonWebTokenAuthentication():

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            authentication = request.headers.get(Token.AUTH_HEADER_NAME, '')
            if not any(map(lambda item: item in authentication, Token.AUTH_HEADER_TYPES)):
                return HttpResponseForbidden()
            try:
                token = authentication.split(' ')[1]
            except IndexError:
                return HttpResponseForbidden()
            try:
                payload, user = Token.verify(token)
            except TokenError:
                return HttpResponseForbidden()
            request.user = user
            request.jwt_payload = payload
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
