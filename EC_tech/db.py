import os
import psycopg2
import string
import random
import hashlib

def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

def get_salt():
    charset = string.ascii_letters + string.digits
    salt = ''.join(random.choices(charset, k=30))
    return salt

def get_hash(password, salt):
    b_pw = bytes(password, 'utf-8')
    b_salt = bytes(salt, 'utf-8')
    hashed_password = hashlib.pbkdf2_hmac('sha256', b_pw, b_salt, 1246).hex()
    return hashed_password

def is_username_taken(user_name):
    sql = 'SELECT COUNT(*) FROM shop_user WHERE name = %s'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (user_name,))
        count = cursor.fetchone()[0]
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
        
    return count > 0

def insert_user(user_name, password):
    sql = 'INSERT INTO shop_user (name, hashed_password, salt) VALUES (%s, %s, %s)'
    
    salt = get_salt()
    hashed_password = get_hash(password, salt)
    count = 0
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        if is_username_taken(user_name):
            count = -1
        else:
            cursor.execute(sql, (user_name, hashed_password, salt))
            count = cursor.rowcount
            connection.commit()
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
        
    return count

def login(user_name, password):
    sql = 'SELECT hashed_password, salt FROM shop_user WHERE name = %s'
    flg = False
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (user_name,))
        user = cursor.fetchone()
        
        if user is not None:
            salt = user[1]
            hashed_password = get_hash(password, salt)
            
            if hashed_password == user[0]:
                flg = True
    except psycopg2.DatabaseError:
        flg = False
    finally:
        cursor.close()
        connection.close()
        
    return flg

def get_products():
    sql = 'SELECT * FROM products'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        products = cursor.fetchall()
    except psycopg2.DatabaseError:
        products = []
    finally:
        cursor.close()
        connection.close()
        
    return products

def admin_login(user_name, password):
    sql = 'SELECT hashed_password, salt FROM admist WHERE name = %s'
    flg = False

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (user_name,))
        admin = cursor.fetchone()

        if admin is not None:
            hashed_password = get_hash(password, admin[1])  # saltを使用してパスワードをハッシュ化

            if hashed_password == admin[0]:
                flg = True
    except psycopg2.DatabaseError as e:
        error = str(e)
        print(error)  # エラーメッセージをコンソールに表示
        flg = False
    finally:
        cursor.close()
        connection.close()

    return flg



def is_admin_username_taken(user_name):
    sql = 'SELECT COUNT(*) FROM admist WHERE name = %s'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (user_name,))
        count = cursor.fetchone()[0]
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
        
    return count > 0

def insert_admin(user_name, password):
    sql = 'INSERT INTO admist (name, hashed_password, salt) VALUES (%s, %s, %s)'

    salt = get_salt()
    hashed_password = get_hash(password, salt)
    count = 0

    try:
        connection = get_connection()
        cursor = connection.cursor()

        if is_admin_username_taken(user_name):
            count = -1
        else:
            cursor.execute(sql, (user_name, hashed_password, salt))
            count = cursor.rowcount
            connection.commit()
    except psycopg2.DatabaseError as e:
        error = str(e)
        print(error)  # エラーメッセージをコンソールに表示
        count = 0
    finally:
        cursor.close()
        connection.close()

    return count

def get_users():
    sql = 'SELECT * FROM shop_user'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        users = cursor.fetchall()
    except psycopg2.DatabaseError:
        users = []
    finally:
        cursor.close()
        connection.close()

    return users

def insert_product(name, price, description):
    sql = 'INSERT INTO products (name, price, description) VALUES (%s, %s, %s)'

    count = 0

    try:
        connection = get_connection()
        cursor = connection.cursor()

        if is_product_name_taken(name):
            count = -1
        else:
            cursor.execute(sql, (name, price, description))
            count = cursor.rowcount
            connection.commit()
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()

    return count

def is_product_name_taken(name):
    sql = 'SELECT COUNT(*) FROM products WHERE name = %s'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (name,))
        count = cursor.fetchone()[0]
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()

    return count > 0

def get_user_by_username(username):
    sql = 'SELECT * FROM shop_user WHERE name = %s'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
    except psycopg2.DatabaseError:
        user = None
    finally:
        cursor.close()
        connection.close()

    return user

def delete_user(user_id):
    sql = 'DELETE FROM shop_user WHERE id = %s'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (user_id,))
        connection.commit()
        count = cursor.rowcount
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
        
    return count

# 他の関数はここに記述

def get_users():
    sql = 'SELECT * FROM shop_user'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        users = cursor.fetchall()
    except psycopg2.DatabaseError:
        users = []
    finally:
        cursor.close()
        connection.close()

    return users

def delete_product_by_name(name):
    sql = 'DELETE FROM products WHERE name = %s'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (name,))
        connection.commit()
        count = cursor.rowcount
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()

    return count

def get_product_by_id(product_id):
    sql = 'SELECT * FROM products WHERE id = %s'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (product_id,))
        product = cursor.fetchone()
    except psycopg2.DatabaseError:
        product = None
    finally:
        cursor.close()
        connection.close()

    return product

# 商品情報を更新する関数
def update_product(product_id, name, price, description):
    sql = 'UPDATE products SET name = %s, price = %s, description = %s WHERE id = %s'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (name, price, description, product_id))
        connection.commit()
        count = cursor.rowcount
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()

    return count

def get_all_products():
    sql = 'SELECT * FROM products'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        products = cursor.fetchall()
    except psycopg2.DatabaseError:
        products = []
    finally:
        cursor.close()
        connection.close()
        
    return products

def search_products_by_name(name):
    sql = 'SELECT * FROM products WHERE name ILIKE %s'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, ('%' + name + '%',))
        products = cursor.fetchall()
    except psycopg2.DatabaseError:
        products = []
    finally:
        cursor.close()
        connection.close()

    return products
