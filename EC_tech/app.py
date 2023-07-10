from datetime import timedelta
from flask import Flask, render_template, redirect, request, url_for, session
import db
import string
import random

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))


@app.route('/', methods=['GET'])
def index():
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



if __name__ == "__main__":
    app.run(debug=True)
