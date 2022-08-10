import json
import os
from flask_oauthlib.client import OAuth
import requests
from config import DevelopmentConfig

def map_auth_response_key(resp, platform):
    """플랫폼별로 다른 유저 정보 key 매핑
    - response
        - twitter
            {
                'oauth_token': <your-oauth-token>,
                'oauth_token_secret': <your-oauth-token-secret>,
                'user_id': <your-user-id>,
                'screen_name': '__kjw_',
                'profile_image_url': 'http://pbs.twimg.com/profile_images/83443/XpwOa5VI_normal.jpg',
                'email': ''
                'platform': 'Twitter'
            }
        - kakao
            {
                'oauth_token': <your-oauth-token>,
                'oauth_token_secret': '',
                'user_id': <your-user-id>,
                'screen_name': '김종우',
                'profile_image_url': 'http://k.kakaocdn.net/dn/bRSQ1V/btrhUYreUXU/ABC/img_640x640.jpg',
                'thumbnail_image_url': 'http://k.kakaocdn.net/dn/bRSQ1V/btrhUYreUXU/ABC/img_110x110.jpg',
                'email': <your-email>,
                'platform': 'Kakao'
            }
    """
    user_info = {}

    if not platform:
        raise ValueError('platform value not given')
    elif platform == 'Twitter':
        user_info = resp
        # https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-show
        with requests.Session() as session:
            session.headers.update({
                'Authorization': f'Bearer {DevelopmentConfig.TWITTER_BEARER_TOKEN}'
            })
            response = session.get(
                url=f'https://api.twitter.com/1.1/users/show.json',
                params={'user_id': user_info.get("user_id")}
            )
        response_data = json.loads(response.content)
        user_info['profile_image_url'] = response_data.get('profile_image_url')
        user_info['email'] = ''
        user_info['platform'] = platform
    elif platform == 'Kakao':
        with requests.Session() as session:
            session.headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Bearer {resp["access_token"]}'
            })
            response = session.post('https://kapi.kakao.com/v2/user/me')

        response_data = json.loads(response.content)
        user_info['oauth_token'] = resp['access_token']
        user_info['oauth_token_secret'] = ''
        user_info['user_id'] = response_data.get('id')
        user_info['screen_name'] = response_data.get('kakao_account').get('profile').get('nickname')
        user_info['profile_image_url'] = response_data.get('kakao_account').get('profile').get('profile_image_url')
        user_info['thumbnail_image_url'] = response_data.get('kakao_account').get('profile').get('thumbnail_image_url')
        user_info['email'] = response_data.get('kakao_account').get('email')
        user_info['platform'] = platform
    else:
        raise ValueError('incorrect platform parameter')

    return user_info

oauth = OAuth()
twitter = oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    access_token_url='https://api.twitter.com/oauth/access_token',
    consumer_key=DevelopmentConfig.TWITTER_CONSUMER_KEY,
    consumer_secret=DevelopmentConfig.TWITTER_CONSUMER_SECRET
)

kakao = oauth.remote_app(
    'kakao',
    base_url='https://kapi.kakao.com/v2/',
    authorize_url='https://kauth.kakao.com/oauth/authorize',
    access_token_url='https://kauth.kakao.com/oauth/token',
    consumer_key=DevelopmentConfig.KAKAO_CONSUMER_KEY,
    consumer_secret=DevelopmentConfig.KAKAO_CONSUMER_SECRET
)

cognito = oauth.remote_app(
    'cognito',
    base_url=os.path.join(DevelopmentConfig.COGNITO_URL, 'oauth2/idpresponse'),
    authorize_url=os.path.join(DevelopmentConfig.COGNITO_URL, 'oauth2/authorize'),
    access_token_url=os.path.join(DevelopmentConfig.COGNITO_URL, 'oauth2/token'),
    consumer_key=DevelopmentConfig.COGNITO_APP_CLIENT_ID,
    consumer_secret=DevelopmentConfig.COGNITO_APP_CLIENT_SECRET
)
