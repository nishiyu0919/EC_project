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
