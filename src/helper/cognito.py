import base64
import hmac
import hashlib
import os
import boto3
from config import DevelopmentConfig


class Cognito:
    def __init__(self):
        try:
            os.environ['AWS_EXECUTION_ENV']
        except KeyError:
            boto3.setup_default_session(profile_name=os.environ['ACCOUNT_ID'])
            self.cognito_idp_client = boto3.client('cognito-idp', region_name=os.environ['REGION'])
        else:
            self.cognito_idp_client = boto3.client('cognito-idp')
        self.cognito_user_pool_id = DevelopmentConfig.COGNITO_USER_POOL_ID
        self.cognito_app_client_id = DevelopmentConfig.COGNITO_APP_CLIENT_ID
        self.cognito_app_client_secret = DevelopmentConfig.COGNITO_APP_CLIENT_SECRET

    def _retrieve_secret_hash(self, username):
        dig = hmac.new(
            key=bytes(self.cognito_app_client_secret, 'utf-8'),
            msg=bytes(f'{username}{self.cognito_app_client_id}', 'utf-8'),
            digestmod=hashlib.sha256
        )
        secret_hash = base64.b64encode(s=dig.digest()).decode()
        return secret_hash

    def is_registered_user(self, platform, platform_id):
        """사용자가 cognito에 등록되었는지 확인
        - Filter에는 standard attribute뿐만 아니라, cognito 'User name'도 필터 가능
        - response
            {
                'Users': [],
                'ResponseMetadata':
                {
                    'RequestId': '1baaab0b-fdf6-479d-b597-755e3cefb5fd',
                    'HTTPStatusCode': 200,
                    'HTTPHeaders':
                    {
                        'date': 'Tue, 02 Aug 2022 16:34:56 GMT',
                        'content-type': 'application/x-amz-json-1.1',
                        'content-length': '12',
                        'connection': 'keep-alive',
                        'x-amzn-requestid': '1baaab0b-fdf6-479d-b597-755e3cefb5fd'
                    },
                    'RetryAttempts': 0
                }
            }

            {
                'Users': [
                {
                    'Username': 'Twitter_342144389',
                    'Attributes': [
                    {
                        'Name': 'sub',
                        'Value': '597f1fae-8f0b-4736-ae1e-XXXXXXXXX'
                    },
                    {
                        'Name': 'website',
                        'Value': 'sdadasd'
                    },
                    {
                        'Name': 'email_verified',
                        'Value': 'false'
                    },
                    {
                        'Name': 'name',
                        'Value': 'hahahahahah'
                    },
                    {
                        'Name': 'picture',
                        'Value': 'http://pbs.twimg.com/profile_images/92394752/XpwOa5VI_normal.jpg'
                    }],
                    'UserCreateDate': datetime.datetime(2022, 8, 2, 1, 23, 33, 836000, tzinfo = tzlocal()),
                    'UserLastModifiedDate': datetime.datetime(2022, 8, 2, 1, 43, 23, 985000, tzinfo = tzlocal()),
                    'Enabled': True,
                    'UserStatus': 'CONFIRMED'
                }],
                'ResponseMetadata':
                {
                    'RequestId': '99a4e8e6-94a8-473e-916c-482837f277f8',
                    'HTTPStatusCode': 200,
                    'HTTPHeaders':
                    {
                        'date': 'Tue, 02 Aug 2022 14:53:30 GMT',
                        'content-type': 'application/x-amz-json-1.1',
                        'content-length': '456',
                        'connection': 'keep-alive',
                        'x-amzn-requestid': '99a4e8e6-94a8-473e-916c-482837f277f8'
                    },
                    'RetryAttempts': 0
                }
            }
        """
        response = self.cognito_idp_client.list_users(
            UserPoolId=self.cognito_user_pool_id,
            Limit=1,
            # Filter='given_name^=\"jw\"'
            # Filter=f'sub=\"{sub}\"'
            Filter=f'username=\"{platform}_{platform_id}\"'
        )

        try:
            sub = response.get('Users')[0].get('Attributes')[0].get('Value')
        except IndexError:
            sub = None  # 신규 유저
        return sub

    def invoke_sign_up(self, platform, platform_id, email, name, picture):
        """사용자 등록
        - Username
            - email이 아닌 사용자명을 사용하고 싶다면 Username은 임의로 정하고, UserAttributes에만 email을 입력하면 된다
            - 현재 설정된 cognito에 추가 설정할 필요는 없었음
        - 기본 비번 설정 규칙: 대문자1개 / 숫자1개 / 특문1개 이상 포함
        - UserAttributes
            - pool생성 당시에만 설정이 가능 <- 수정은 cognito 삭제 후 재생성 해야함
            - standard attributes 목록
                - https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-attributes.html
            - username, photo라는 attribute는 없다 (name, picture가 올바른 attribute key)
            - 빈 str이 attributes value로 입력되는 경우 cognito에는 key 자체가 안들어감
        - response
            {
                'UserConfirmed': False,
                'UserSub': '14330090-bab2-4c57-b949-b720b541e640',
                'ResponseMetadata':
                {
                    'RequestId': '08205bf7-3484-46ca-93e8-0ee3db72c3c3',
                    'HTTPStatusCode': 200,
                    'HTTPHeaders':
                    {
                        'date': 'Tue, 02 Aug 2022 15:10:26 GMT',
                        'content-type': 'application/x-amz-json-1.1',
                        'content-length': '72',
                        'connection': 'keep-alive',
                        'x-amzn-requestid': '08205bf7-3484-46ca-93e8-0ee3db72c3c3'
                    },
                    'RetryAttempts': 0
                }
            }
        """
        username = f'{platform}_{platform_id}'

        response = self.cognito_idp_client.sign_up(
            ClientId=self.cognito_app_client_id,
            SecretHash=self._retrieve_secret_hash(username),
            Username=username,
            Password=f'{platform}_{platform_id}123!',
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'name',
                    'Value': name
                },
                {
                    'Name': 'picture',
                    'Value': picture
                }
            ]
        )
        return response.get('UserSub')

    def invoke_admin_confirm_sign_up(self, platform, platform_id):
        response = self.cognito_idp_client.admin_confirm_sign_up(
            UserPoolId=self.cognito_user_pool_id,
            Username=f'{platform}_{platform_id}'
        )
        return response

    def invoke_admin_update_user_attributes(self, platform, platform_id, email, name, picture):
        """기존 attribute value가 변경이 될 때에만 cognito console에 update time이 변경된다"""
        response = self.cognito_idp_client.admin_update_user_attributes(
            UserPoolId=self.cognito_user_pool_id,
            Username=f'{platform}_{platform_id}',
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'name',
                    'Value': name
                },
                {
                    'Name': 'picture',
                    'Value': picture
                }
            ]
        )
        return response

    def invoke_admin_initiate_auth(self, platform, platform_id):
        """AccessToken, IdToken return
        - AWS::Cognito::UserPoolClient Resource에 사용할 AuthFlow값 추가 필요
        - response
            {
                'ChallengeParameters':
                {},
                'AuthenticationResult':
                {
                    'AccessToken': <your-access-token>,
                    'ExpiresIn': 3600,
                    'TokenType': 'Bearer',
                    'RefreshToken': <your-refresh-token>,
                    'IdToken': <your-id-token>
                },
                'ResponseMetadata':
                {
                    'RequestId': '50f2fa04-213e-49ef-a988-3a5db80a394e',
                    'HTTPStatusCode': 200,
                    'HTTPHeaders':
                    {
                        'date': 'Tue, 02 Aug 2022 15:10:26 GMT',
                        'content-type': 'application/x-amz-json-1.1',
                        'content-length': '4144',
                        'connection': 'keep-alive',
                        'x-amzn-requestid': '50f2fa04-213e-49ef-a988-3a5db80a394e'
                    },
                    'RetryAttempts': 0
                }
            }
        """
        username = f'{platform}_{platform_id}'

        response = self.cognito_idp_client.admin_initiate_auth(
            UserPoolId=self.cognito_user_pool_id,
            ClientId=self.cognito_app_client_id,
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': f'{platform}_{platform_id}123!',
                'SECRET_HASH': self._retrieve_secret_hash(username)
            }
        )

        return response.get('AuthenticationResult')

    def invoke_list_groups(self):
        """
            {
                'Groups': [
                    {
                        'GroupName': 'string',
                        'UserPoolId': 'string',
                        'Description': 'string',
                        'RoleArn': 'string',
                        'Precedence': 123,
                        'LastModifiedDate': datetime(2015, 1, 1),
                        'CreationDate': datetime(2015, 1, 1)
                    },
                ],
                'NextToken': 'string'
            }        
        """
        response = self.cognito_idp_client.list_groups(
            UserPoolId=self.cognito_user_pool_id
        )
        return [row.get('GroupName') for row in response.get('Groups')]

    def invoke_create_group(self, groupname):
        self.cognito_idp_client.create_group(
            GroupName=groupname,
            UserPoolId=self.cognito_user_pool_id
        )

    def invoke_admin_add_user_to_group(self, platform, platform_id, groupname):
        self.cognito_idp_client.admin_add_user_to_group(
            UserPoolId=self.cognito_user_pool_id,
            Username=f'{platform}_{platform_id}',
            GroupName=groupname
        )

    def invoke_admin_delete_user(self, platform, platform_id):
        self.cognito_idp_client.admin_delete_user(
            UserPoolId=self.cognito_user_pool_id,
            Username=f'{platform}_{platform_id}'
        )
