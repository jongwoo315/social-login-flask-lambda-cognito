from datetime import datetime
from flask import Blueprint, request, session, url_for, redirect, flash
from src.helper.cognito import Cognito
from src.helper.common import twitter, kakao, map_auth_response_key
from src.helper.user_flow import Director, NewUserBuilder, ExistingUserBuilder
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s :: %(levelname)s :: %(message)s'
)
logger = logging.getLogger()
logger.setLevel('INFO')

cognito = Cognito()

login = Blueprint(
    name='login',
    import_name=__name__
)


@login.route('/twitter-login', methods=['POST', 'GET'])
def twitter_login():
    url_for_res = url_for(
        '.oauth_authorized',
        next=request.args.get('next') or request.referrer or None
    )
    session['platform'] = 'Twitter'
    return twitter.authorize(callback=url_for_res)

@login.route('/kakao-login')
def kakao_login():
    url_for_res = url_for(
        '.oauth_authorized',
        _external=True
    )
    session['platform'] = 'Kakao'
    return kakao.authorize(callback=url_for_res)

@login.route('/oauth-authorized', methods=['GET'])
def oauth_authorized():
    if session['platform'] == 'Twitter':
        resp = twitter.authorized_response()
    elif session['platform'] == 'Kakao':
        resp = kakao.authorized_response()

    user_info = map_auth_response_key(resp, session['platform'])
    logger.info(f'user_info: {user_info}')

    next_url = request.args.get('next') or url_for('main.index')
    if user_info is None:
        flash(u'로그인 권한 없음')
        return redirect(next_url)

    director = Director()

    sub = cognito.is_registered_user(user_info['platform'], user_info['user_id'])
    if sub:
        user_info['sub'] = sub
        builder = ExistingUserBuilder(user_info)
        director.builder = builder
        director.load_user_data()
        authentication_result = builder.existing_user.update_user()
    else:
        builder = NewUserBuilder(user_info)
        director.builder = builder
        director.load_user_data()
        authentication_result, sub = builder.new_user.sign_up_user()

    session['sub'] = sub
    session['access_token'] = authentication_result['AccessToken']
    session['id_token'] = authentication_result['IdToken']
    session['platform'] = user_info.get('platform')
    session['user_id'] = user_info.get('user_id')

    logger.info(f'authorized session: {session}')
    flash('로그인되었습니다.')

    return redirect(next_url)
