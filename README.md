# django-jwt-decorator

基于 json web token 的 django view 认证装饰器

## 生成 Token

```python
from django_jwt_decorator import Token
from django.contrib.auth.models import User

user = User.objects.get(id=1)
token = Token.access_token(user)
# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHBpcmVkIjoxNjEwMzQ1MTk4MzI2LCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiaWQiOjF9.fP-fxNAJ5f-77Ojk_YJwgTSzZ2bN6MgKZCpFWSUn2LI
```

## 认证访问

```python
# views.py
from django_jwt_decorator import JsonWebTokenAuthentication
from django.http import HttpResponse

# url: /test
@JsonWebTokenAuthentication()
def test(request, *args, **kwargs):
    user = request.user
    return HttpResponse()
```

```python
import requests

rsp = requests.get('http://127.0.0.1:8000/test', headers={'AUTHORIZATION': 'Bearer eyJleHBpcmVkIjoxNjEwMzQ1MTk4MzI2LCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiaWQiOjF9.fP-fxNAJ5f-77Ojk_YJwgTSzZ2bN6MgKZCpFWSUn2LI'})

# <Response 200>
```

## 配置

```python
# settings.py

DJANGO_JWT_SETTINGS = {
    # ...
}
```

- ACCESS_TOKEN_LIFETIME 认证 Token 有效时间，默认值`timedelta(minutes=5)`
- UPDATE_USER_LAST_LOGIN_TIME 是否更新 USER 最后登录时间，默认值`True`
- ALGORITHM 签名所使用的的算法，包含以下算法。除 HS 系列外，需要额外安装 cryptography 依赖(可选：使用 pyjwt[crypto]替代 cryptography)，默认值`HS256`
  - HS256
  - HS384
  - HS512
  - ES256
  - ES384
  - ES512
  - RS256
  - RS384
  - RS512
  - PS256
  - PS384
  - PS512
  - EdDSA
- SIGING_KEY 加密密钥 签名所使用的私钥，默认使用 django 项目中 settings 文件的 SECRET_KEY
- VERIFYING_KEY 验证密钥 签名所使用的公钥，HS 算法下，改属性会被忽略
- AUDIENCE
- ISSUER
- AUTH_HEADER_TYPES 认证类型，即 header 传递的 token 的前缀`AUTH_HEADER_TYPE TOKEN`(注意 认证类型字符串与 token 之间使用空格隔开)，默认值`['Bearer', ]`
- AUTH_HEADER_NAME 认证字段名，即 headers 中存储 token 的字段名,默认值``AUTHORIZATION`
- USER_PRIMARY_KEY_FIELD_NAME 用户表的主键
- USER_PRIMARY_KEY_FIELD_CLAIM 用户表主键在 JWT payload 中键名
- LAST_LOGIN_TIME_NAME 用户最后登录时间字段 Name,当`UPDATE_USER_LAST_LOGIN_TIME=True`时有效，默认值`last_login`
