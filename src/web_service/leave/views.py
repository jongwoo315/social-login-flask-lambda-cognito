from flask import Blueprint, session, request, redirect, url_for, flash
from src.helper.user_flow import Director, ExistingUserBuilder

leave = Blueprint(
    name='leave',
    import_name=__name__
)

@leave.route('/leave')
def user_leave():
    builder = ExistingUserBuilder(session)
    director = Director()
    director.builder = builder
    director.load_user_data()
    builder.existing_user.unregister_user()
    session.clear()
    flash('회원탈퇴가 완료되었습니다.')  # session.clear() 이후에 사용해야 main으로 redirect된 이후에도 message가 화면에 출력된다.
    return redirect(request.referrer or url_for('main.index'))
    
