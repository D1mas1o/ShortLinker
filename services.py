import sqlite3
import requests
import random
import string
import hashlib
import pickle
from flask_jwt_extended import (JWTManager,jwt_required,create_access_token,get_jwt_identity)
def get_short_url(data):
    if data.form['user_url'] is not None and data.form['LinkMode'] is not None:
        try:
            requests.get(data.form['user_url'])
            short_link = get_hash()
            long_link =data.form['user_url']
            link_mode = data.form['LinkMode']
            with sqlite3.connect('ShortLinkBd.db') as conn:
                c = conn.cursor()
                c.execute('INSERT INTO Links (LongLink,ShortLink,LinkMode) VALUES (?,?,?)',(long_link,short_link,link_mode))
            return "http://127.0.0.1:5000/sh.ly/" + short_link
        except requests.exceptions.MissingSchema:
            return "Введите корретную ссылку"

def get_short_url_authorizade(user_info,data):
    if data.form['user_url'] is not None and data.form['LinkMode'] is not None and user_info['UserId'] is not None:
        try:
            requests.get(data.form['user_url'])

            short_link = get_hash()
            long_link =data.form['user_url']
            link_mode = data.form['LinkMode']
            with sqlite3.connect('ShortLinkBd.db') as conn:
                c = conn.cursor()
                c.execute('INSERT INTO Links (LongLink,ShortLink,LinkMode,UserId) VALUES (?,?,?,?)',(long_link,short_link,link_mode,user_info['UserId']))
            return "http://127.0.0.1:5000/sh.ly/" + short_link
        except requests.exceptions.MissingSchema:
            return "Введите корретную ссылку"

def get_hash():
    while True:
        hash = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=random.randint(8,12)))
        with sqlite3.connect('ShortLinkBd.db') as conn:
            c = conn.cursor()
            c.execute('SELECT ShortLink From Links Where ShortLink = (?) ',(hash,))
            list = c.fetchall()
        if len(list) == 0:
            return hash

def short_answer(short_url):
    with sqlite3.connect('ShortLinkBd.db') as conn:
        c = conn.cursor()
        c.execute('SELECT LongLink,LinkMode,UserId FROM Links WHERE ShortLink=(?)',(short_url,))

        mas = c.fetchone()
        long_link = mas[0]
        link_mode = mas[1]
        author = mas[2]
    return long_link,link_mode,author

def check_base_auth(username, password):
    try:
        with sqlite3.connect('ShortLinkBd.db') as conn:
            c = conn.cursor()
            c.execute('SELECT Password FROM Users WHERE Login=(?)', (username,))
            qwer = c.fetchone()[0]

            m = hashlib.sha1(pickle.dumps(password))

            return username == username and m.hexdigest() == qwer
    except TypeError:
        return False
def check_base_auth_private(username, password,author):
    try:
        with sqlite3.connect('ShortLinkBd.db') as conn:
            c = conn.cursor()
            c.execute('SELECT Password FROM Users WHERE Login=(?)', (author,))
            qwer_auth = c.fetchone()[0]
            c.execute('SELECT Password FROM Users WHERE Login=(?)', (username,))
            qwer_user = c.fetchone()[0]
            if qwer_user == qwer_auth:
                m = hashlib.sha1(pickle.dumps(password))
                return username == username and m.hexdigest() == qwer_auth
    except TypeError:
        return False
    finally:return False
def chek_auth_login(login):
    try:
        with sqlite3.connect('ShortLinkBd.db') as conn:
            c = conn.cursor()
            c.execute('SELECT Password FROM Users WHERE Login=(?)', (login,))
            qwer = c.fetchone()[0]
            return True
    except TypeError:
        return False
def past_info_bd(data):
    first_name = data["FirstName"]
    last_name = data["LastName"]
    email = data["Email"]
    login = data["Login"]
    password = data["Password"]
    m = hashlib.sha1(pickle.dumps(password))
    try:
        with sqlite3.connect('ShortLinkBd.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO Users(FirstName,LastName,Email,Login,Password) VALUES(?,?,?,?,?)', (first_name,last_name,email,login,m.hexdigest()))
            c.execute('SELECT UserId FROM Users WHERE Login=(?)',(login,))
            Id = c.fetchone()[0]
        data["UserId"] = Id
    except sqlite3.IntegrityError:
        return False
    return data

def check_login(data):
    try:
        with sqlite3.connect('ShortLinkBd.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM Users WHERE Login=(?)', (data["Login"],))
            qwer = c.fetchall()[0]
            m = hashlib.sha1(pickle.dumps(data["Password"]))
        if m.hexdigest() == qwer[5]:
            return qwer
        else: return None
    except TypeError:
        return None
def bd_search_links(data):
    with sqlite3.connect('ShortLinkBd.db') as conn:
        c = conn.cursor()
        c.execute('SELECT LongLink,ShortLink,LinkMode FROM Links WHERE UserId=(?)',(data['UserId'],))
        mas = c.fetchall()
    return mas