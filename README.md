# social-login-flask-lambda-cognito
AWS Lambda, Cognito를 활용한 flask social login 프로젝트

## Table of Contents
- [Introduction](#Introduction)
- [Technologies Used](#Technologies-Used)
- [Setup](#Setup)
- [Usage](#Usage)
- [Acknowledgements](#Acknowledgements)

## Introduction
- Flask blueprint를 활용하여 기능별(login, logout, main)로 함수분리
- static디렉토리의 올바른 경로지정을 위해서 `static_url_path` param 필수
- Python package는 lambda layer에서 호출
- AWS Lambda로의 배포는 Serverless framework사용
- Private subnet내에 위치한 DB를 사용하는 경우, NAT gateway 혹은 NAT instance(ec2)를 반드시 설정
- 프로젝트 배포 이후, 로그인 플랫폼별로 callback uri 추가 필요
- AWS Cognito
    - Cognito로 유저 관리
    - resource는 cloudformation으로 생성
    - 유저 생성, 업데이트, 삭제를 위한 소스코드는 builder pattern을 활용

## Technologies Used
- Python: 3.9
- npm: 8.6.0
- Serverless: 3.12.0
- Serverless-wsgi: 3.0.0
- Serverless-export-env: 2.2.0

## Setup
- 기본 환경 설정
    ```shell
    $ pipenv shell --python 3.9
    $ python -V
    $ pipenv install
    $ pip install -t vendor -r requirements.txt
    $ npm i
    $ npm install -g npx
    ```
- `config.py.default`
    - config값들 수정 후, config.py로 파일명 수정
- `serverless.yml.default`
    - insert-your-value값들을 사용자의 환경에 맞게 수정한 후, serverless.yml로 파일명 수정

## Usage
- Local Test
    ```shell
    $ npx invoke local -f app
    ```
    - 웹브라우저로 http://localhost:5001/ 접속
- Project Deploy
    ```shell
    $ npx sls deploy
    ```
- Service Check
    - shell에 출력된 api gateway url(AWS api gateway console 에서도 확인가능)을 웹브라우저에 입력하여 서비스에 접속

## Acknowledgements
- https://medium.com/thedevproject/flask-blueprints-complete-tutorial-to-fully-understand-how-to-use-it-767f7433a02e
- https://refactoring.guru/design-patterns/builder
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/userinfo-endpoint.html
- https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html
- https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpooldomain.html
- https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpoolclient.html

