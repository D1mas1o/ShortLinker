from flask import Flask, render_template, request, views, redirect,Response,json,jsonify,url_for
from services import *
from flask_jwt_extended import (JWTManager,unset_jwt_cookies,jwt_refresh_token_required,jwt_required,create_access_token,create_refresh_token,set_access_cookies,set_refresh_cookies,get_jwt_identity)
import requests
app = Flask(__name__)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_SECRET_KEY'] = 'super-ultra-mega-secret'
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
jwt = JWTManager(app)


@app.route('/token/auth', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'test' or password != 'test':
        return jsonify({'login': False}), 401

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200

@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200

@app.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200

class UserLogin(views.MethodView):
    def get(self):
        return render_template('login.html')
    def post(self):
        content = request.data

        if content is None:
            return render_template('login.html')
        my_json = content.decode('utf8').replace("'", '"')
        data = json.loads(my_json)
        if data["Login"] is None or data["Password"] is None:
            return render_template('login.html')
        info = check_login(data)
        if info:
            js = {
                "UserId":info[0],
                "FirstName": info[1],
                "LastName": info[2],
                "Email": info[3],
                "Login": info[4],
                "Password":info[5],
            }
            access_token = create_access_token(identity=js)
            refresh_token = create_refresh_token(identity=js)
            # Set the JWT access cookie in the response
            resp = jsonify({'login': True})
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            return resp, 200
        return redirect(url_for('userlogin'))

class UserRegister(views.MethodView):
    def get(self):
        return render_template('register.html')
    def post(self):
        content = request.data
        my_json = content.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        if chek_auth_login(data["Login"]):
            return render_template('register.html')
        data = past_info_bd(data)
        if data is False:
            return render_template('register.html')
        access_token = create_access_token(identity=data)
        refresh_token = create_refresh_token(identity=data)
        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)


        return resp, 200

@app.route('/get/token', methods=['GET'])
@jwt_required
def protected():
    username = get_jwt_identity()
    return jsonify(username), 200


class UserIndex(views.MethodView):
    def get(self):
        cookies = {}
        cookies['access_token_cookie'] = request.cookies.get('access_token_cookie')
        cookies['refresh_token_cookie'] = request.cookies.get('refresh_token_cookie')
        cookies['csrf_access_token'] = request.cookies.get('csrf_access_token')
        cookies['csrf_refresh_token'] = request.cookies.get('csrf_refresh_token')
        req = requests.get("http://127.0.0.1:5000/get/token", cookies=cookies)
        data = json.loads(req.text)
        try:
            return render_template('index.html', user_id=data['UserId'], user_firstname=data['FirstName'],
                                   user_lastname=data['LastName'])
        except KeyError:
            return render_template('index.html')
    def post(self):
        cookies = {}
        cookies['access_token_cookie'] = request.cookies.get('access_token_cookie')
        cookies['refresh_token_cookie'] = request.cookies.get('refresh_token_cookie')
        cookies['csrf_access_token'] = request.cookies.get('csrf_access_token')
        cookies['csrf_refresh_token'] = request.cookies.get('csrf_refresh_token')
        req = requests.get("http://127.0.0.1:5000/get/token", cookies=cookies)
        data = json.loads(req.text)
        req = request
        try:
            short_url = get_short_url_authorizade(data,req)
            return render_template('index.html', user_id=data['UserId'], user_firstname=data['FirstName'],
                                   user_lastname=data['LastName'],short_url=short_url)
        except KeyError:
            short_url = get_short_url(req)
            return render_template('index.html', short_url=short_url)
class UserLinks(views.MethodView):
    def get(self):
        cookies = {}
        cookies['access_token_cookie'] = request.cookies.get('access_token_cookie')
        cookies['refresh_token_cookie'] = request.cookies.get('refresh_token_cookie')
        cookies['csrf_access_token'] = request.cookies.get('csrf_access_token')
        cookies['csrf_refresh_token'] = request.cookies.get('csrf_refresh_token')
        req = requests.get("http://127.0.0.1:5000/get/token", cookies=cookies)
        data = json.loads(req.text)

        mas = bd_search_links(data)
        try:
            return render_template('index.html', user_id=data['UserId'], user_firstname=data['FirstName'],
                                   user_lastname=data['LastName'],links=mas)
        except KeyError:
            return render_template('index.html')



@app.route("/sh.ly/<short_url>",methods=['GET'])

def ShortUrl(short_url):


    info = short_answer(short_url)
    if info[1] == 1:
        return redirect(info[0], code=302)
    if info[1] == 2:
        auth = request.authorization
        if not auth or not check_base_auth(auth.username, auth.password):
            return authenticate()
        return redirect(info[0], code=302)
    if info[1] == 3:
        auth = request.authorization
        if not auth or not check_base_auth_private(auth.username, auth.password,info[2]):
            return authenticate()
        return redirect(info[0], code=302)

'''
1 - публичная ссылка
2 - ссылка общего доступа
3 - приватная ссылка
'''
#################################
def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})
################################


app.add_url_rule('/register',view_func=UserRegister.as_view('regiser'))
app.add_url_rule('/login',view_func=UserLogin.as_view('user_login'))
app.add_url_rule('/links',view_func=UserLinks.as_view('index'))
app.add_url_rule('/',view_func=UserIndex.as_view('user_links'))
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

