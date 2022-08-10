from flask import Blueprint, session, request, redirect, url_for

logout = Blueprint(
    name='logout',
    import_name=__name__
)

@logout.route('/logout')
def user_logout():
    session.clear()
    print(f'session cleared: {session}')
    return redirect(request.referrer or url_for('main.index'))
