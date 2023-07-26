from datetime import timedelta
from flask import Flask, render_template, redirect, request, url_for, session, jsonify
import db
import string
import random
import re

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))

# Flask-Sessionの設定
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)  # セッションの有効期限を10分に設定



@app.route('/', methods=['GET'])
def index():
    products = session.get('products') or db.get_products()  # セッションに商品リストがあればそれを取得、なければDBから取得
    session['products'] = products  # 商品リストをセッションに保持
   
   
    if 'user' in session:
        return render_template('top.html', products=products, username=session['user'])
    else:
        msg = request.args.get('msg')
        if msg is None or request.referrer == url_for('login'):
            return render_template('top.html', products=products)
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
    search_keyword = request.args.get('search')

    if search_keyword:
        session['search_keyword'] = search_keyword
        products = db.search_products_by_name(search_keyword)
    else:
        session.pop('search_keyword', None)
        products = db.get_products()

        return render_template('top.html', products=products, search_keyword=search_keyword)




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
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    msg = request.args.get('msg')

    if msg is None or request.referrer == url_for('admin_login'):
        return render_template('edit.html')
    else:
        users = db.get_users()  # ユーザ一覧を取得
        return render_template('admist.html', msg=msg, users=users)



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
        msg = 'ログインが必要です'
        return redirect(url_for('admin'), msg=msg)



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
    
@app.route('/user_list')
def user_list():
    users = db.get_users()  # ユーザ一覧を取得
    return render_template('user_list.html', users=users)

    
@app.route('/return_edit')
def return_edit():
    if 'admin' in session:
        return redirect(url_for('edit'))
    else:
        return redirect(url_for('admin_login'))

@app.route('/product/add', methods=['GET', 'POST'])
def product_add():
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        description = request.form.get('description')

        if db.is_product_name_taken(name):
            error = '同じ名前の商品が既に登録されています。別の名前を選択してください。'
            return render_template('products.html', error=error)

        count = db.insert_product(name, price, description)

        if count == 1:
            msg='商品が登録されました'
            return render_template('products.html', msg=msg)
        else:
            error = '商品の登録に失敗しました。'
            return render_template('products.html', error=error)

    return render_template('products.html')
    
        
@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # 削除対象のユーザー名を取得
    username = request.form.get('username')
    # ユーザー名からデータベースで該当するユーザーを検索
    user = db.get_user_by_username(username)

    if not user:
        error = 'ユーザーが見つかりません。'
        # ユーザーが見つからない場合はエラーメッセージを表示してユーザーリスト画面に戻る
        users = db.get_users()  # ユーザーリストを取得
        return render_template('user_list.html', error=error, users=users)

    # ユーザーをデータベースから削除
    count = db.delete_user(user[0])

    updated_users = db.get_users()
    
    if count == 1:
        msg = 'ユーザーを削除しました。'
        # 削除成功した場合に成功メッセージと更新後のユーザーデータをテンプレートに渡す
        return render_template('user_list.html', msg=msg, users=updated_users)
    else:
        error = 'ユーザーの削除に失敗しました。'
        # 削除失敗した場合にエラーメッセージと更新後のユーザーデータをテンプレートに渡す
        return render_template('user_list.html', error=error, users=updated_users)

@app.route('/product/list')
def product_list():
    search_keyword = request.args.get('search')

    if search_keyword:
        products = db.search_products_by_name(search_keyword)
    else:
        products = db.get_products()

    return render_template('products_list.html', products=products)

@app.route('/product/delete', methods=['POST'])
def delete_product():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    product_name = request.form.get('product_name')
    
    
    if product_name is None:
        msg='商品が見つかりませんでした。'
        return render_template('products_list.html', msg=msg, products=products)

    count = db.delete_product_by_name(product_name)
    products = db.get_products()

    if count == 1:
        msg = '商品を削除しました。'
        return render_template('products_list.html', msg=msg , products=products)
    else:
        error = '商品が見つかりませんでした。'
        return render_template('products_list.html', error=error , products=products)

@app.route('/edit_list')
def edit_list():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    products = db.get_all_products()
    return render_template('edit_list.html', products=products)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = db.get_product_by_id(product_id)  # 修正：関数名を修正
    if product:
        return render_template('product_edit.html', product=product)
    else:
        return "商品が見つかりません", 404

@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if request.method == 'POST':
        product_name = request.form.get('edit_product_name')
        product_price = float(request.form.get('edit_product_price'))
        product_description = request.form.get('edit_product_description')

        # データベースで商品情報を更新する
        count = db.update_product(product_id, product_name, product_price, product_description)
        products = db.get_products()

        if count == 1:
            msg = '商品情報が更新されました。'
        else:
            msg = '商品情報の更新に失敗しました。'

        # 更新された商品リストを表示するために、edit_list ルートにリダイレクトする
        return render_template('edit_list.html', msg=msg, products=products)  # 修正：url_forを使用してリダイレクト



# 他のルートの定義など（省略）

@app.route('/search', methods=['POST'])
def search():
    search_keyword = request.form.get('search')
    products = db.search_products_by_name(search_keyword)

    if products:
        # 検索結果がある場合は、その商品リストをtop.htmlに表示
        return render_template('top.html', products=products, search_keyword=search_keyword)
    else:
        # 商品が見つからなかった場合はエラーメッセージを表示してtop.htmlにリダイレクト
        error = '商品が見つかりませんでした。'
        return render_template('top.html', error=error , products=products)


@app.route('/product/detail/<int:product_id>')
def product_detail(product_id):
    product = db.get_product_by_id(product_id)
    if product:
        return render_template('product_detail.html', product=product)
    else:
        return "商品が見つかりません", 404

def create_user_session(user_name):
    session['user'] = user_name  # ユーザー名をセッションに格納
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)


def add_to_cart(product_id, quantity):
    cart_data = session.get('cart', {})
    cart_item = cart_data.get(product_id)

    if cart_item:
        # すでにカートに同じ商品が存在する場合は数量を加算
        cart_item['quantity'] += quantity
    else:
        # カートに新しい商品として追加
        cart_item = {
            'product_id': product_id,
            'quantity': quantity
        }
        cart_data[product_id] = cart_item

    session['cart'] = cart_data  # セッションにカート情報を保存

# cartルートの定義
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'add_to_cart' in request.form:
            product_id = request.form.get('product_id')
            quantity_str = request.form.get('quantity')
            try:
                quantity = int(quantity_str)
                if quantity < 1:
                    quantity = 1
                add_to_cart(product_id, quantity)
            except ValueError:
                pass

    cart_data = session.get('cart', {})
    products_data = []
    total_price = 0

    for product_id, item in cart_data.items():
        product = db.get_product_by_id(product_id)
        if product:
            product_info = {
                'id': product[0],
                'name': product[1],
                'price': product[2],
                'quantity': item['quantity'],
                'subtotal': product[2] * item['quantity']
            }
            total_price += product_info['subtotal']
            products_data.append(product_info)

    return render_template('cart.html', products_data=products_data, total_price=total_price)


@app.route('/update_cart', methods=['POST'])
def update_cart():
    if 'user' not in session:
        return redirect(url_for('login'))

    cart_data = session.get('cart', {})
    cart_json = request.get_json()

    for product_id, quantity in cart_json.items():
        if quantity < 1:
            quantity = 1
        cart_data[product_id]['quantity'] = quantity

    session['cart'] = cart_data

    return jsonify(success=True)



if __name__ == "__main__":
    app.run(debug=True)

