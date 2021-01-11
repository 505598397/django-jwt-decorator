from setuptools import setup, find_packages

setup(
    name='django-jwt-decorator',
    version='0.0.1',
    author='sunwei',
    author_email='505598397@qq.com',
    url='https://github.com/505598397/django-jwt-decorator',
    description='View authentication decorator based on django json web token',
    packages=find_packages(),
    install_requires=[
        'pyjwt',
    ],
)
