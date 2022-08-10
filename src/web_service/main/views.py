import logging
from flask import Blueprint, flash, render_template, session, g
import jwt
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s :: %(levelname)s :: %(message)s'
)
logger = logging.getLogger()
logger.setLevel('INFO')


main = Blueprint(
    name='main',
    import_name=__name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/main/static'
)

@main.route('/')
def index():
    user_info = None

    if g.user is not None:
        user_info = jwt.decode(session['id_token'], options={"verify_signature": False})

        if user_info:
            logger.info(user_info)
        else:
            flash('소셜 플랫폼에서 데이터 로드가 불가능합니다.')

    return render_template('index.html', user_info=user_info)
