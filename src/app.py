import os
from flask import Flask, session, g
from src.models.model import User, db_session
from src.helper.common import cognito
from src.web_service.leave.views import leave
from src.web_service.login.views import login
from src.web_service.logout.views import logout
from src.web_service.main.views import main
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s :: %(levelname)s :: %(message)s'
)
logger = logging.getLogger()
logger.setLevel('INFO')

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    app.register_blueprint(leave)
    app.register_blueprint(login)
    app.register_blueprint(logout)
    app.register_blueprint(main)

    @app.before_request
    def before_request():
        g.user = None
        if 'sub' in session:
            g.user = db_session.query(User).filter_by(sub=session['sub']).first()

    @app.after_request
    def after_request(response):
        db_session.close()
        # response.headers["Pragma"] = "no-cache"
        # response.headers["Expires"] = "0"
        # response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
        # response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        print(f'response status_code: {response.status_code}')

        return response

    @cognito.tokengetter
    def get_cognito_token():
        user = g.user
        if user is not None:
            logger.info(f'session: {session}')
            return session['id_token']

    logger.info(f'app.url_map: {app.url_map}')
    return app

app = create_app()

try:
    os.environ['AWS_EXECUTION_ENV']  # 해당 키가 존재한다면 lambda환경
except KeyError:
    app.run(port=5001)  # mac os monterey에서 발생하는 이슈, 포트 번호 변경 (로컬 테스트시에만 사용)
else:
    pass
