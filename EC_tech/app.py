from datetime import timedelta
from flask import Flask, render_template, redirect, request, url_for, session
import db
import string
import random
import re

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))


@app.route('/', methods=['GET'])
def index():
    if 'user' in session:
        return redirect(url_for('top'))

    msg = request.args.get('msg')

    if msg is None or request.referrer == url_for('login'):
        return render_template('top.html')
    else:
        return render_template('index.html', msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('username')
        password = request.form.get('password')

        if not user_name or not password:
            error = 'ユーザー名とパスワードを入力してください。'
            return render_template('index.html', error=error)

        if db.login(user_name, password):
            session['user'] = user_name  # ユーザー名をセッションに格納
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=1)
            return redirect(url_for('top'))
        else:
            error = 'ユーザ名またはパスワードが違います。'
            input_data = {'user_name': user_name, 'password': password}
            return render_template('index.html', error=error, data=input_data)
    else:
        return render_template('index.html')


@app.route('/top', methods=['GET'])
def top():
    if 'user' in session:
        return render_template('top.html', username=session['user'])
    else:
        return render_template('index.html', msg='ログインが必要です')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/register')
def register_form():
    return render_template('register.html')


@app.route('/register_exe', methods=['POST'])
def register_exe():
    user_name = request.form.get('username')
    password = request.form.get('password')

    if user_name.strip() == '' or password.strip() == '':
        error = 'ユーザー名とパスワードは必須です。'
        return render_template('register.html', error=error)

    if not re.match("^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z0-9]+$", user_name):
        error = 'ユーザー名は英数字を組み合わせて設定してください。'
        return render_template('register.html', error=error)

    if db.is_username_taken(user_name):
        error = 'そのユーザー名は既に使用されています。別のユーザー名を選択してください。'
        return render_template('register.html', error=error)

    count = db.insert_user(user_name, password)

    if count == 1:
        msg = '登録が完了しました。'
        return render_template('index.html', msg=msg)
    else:
        error = '登録に失敗しました。'
        return render_template('register.html', error=error)


@app.route('/admin', methods=['GET'])
def admin():
    if 'user' in session:
        return redirect(url_for('admin_login'))

    msg = request.args.get('msg')

    if msg is None or request.referrer == url_for('admin_login'):
        return render_template('edit.html')
    else:
        return render_template('admist.html', msg=msg)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    
    
    if request.method == 'POST':
        user_name = request.form.get('username')
        password = request.form.get('password')

        if not user_name or not password:
            error = '管理者名とパスワードを入力してください。'
            return render_template('admist.html', error=error)

        if db.admin_login(user_name, password):
            session['admin'] = user_name  # 管理者名をセッションに格納
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=1)
            return redirect(url_for('admin'))
        else:
            error = '管理者名またはパスワードが違います。'
            input_data = {'user_name': user_name, 'password': password}
            return render_template('admist.html', error=error, data=input_data)
        
    else:
        return render_template('admist.html')



@app.route('/edit', methods=['GET'])
def edit():
    if 'admin' in session:
        return render_template('edit.html', username=session['admin'])
    else:
        return redirect(url_for('admin'), msg='ログインが必要です')



@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))


@app.route('/admin/register')
def admin_register_form():
    return render_template('admist_register.html')


@app.route('/admin/register_exe', methods=['POST'])
def admin_register_exe():
    user_name = request.form.get('username')
    password = request.form.get('password')

    if user_name.strip() == '' or password.strip() == '':
        error = 'ユーザー名とパスワードは必須です。'
        return render_template('admist_register.html', error=error)

    if not re.match("^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z0-9]+$", user_name):
        error = 'ユーザー名は英数字を組み合わせて設定してください。'
        return render_template('admist_register.html', error=error)

    if db.is_admin_username_taken(user_name):
        error = 'そのユーザー名は既に使用されています。別のユーザー名を選択してください。'
        return render_template('admist_register.html', error=error)

    count = db.insert_admin(user_name, password)

    if count == 1:
        msg = '登録が完了しました。'
        return render_template('admist.html', msg=msg)
    else:
        error = '登録に失敗しました。'
        return render_template('admist_register.html', error=error)

@app.route('/return_top', methods=['GET'])
def return_top():
        return render_template('top.html')


if __name__ == "__main__":
    app.run(debug=True)
