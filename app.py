from flask import Flask, render_template, json, request, redirect, session
from flask_mysqldb import MySQL
from werkzeug import generate_password_hash, check_password_hash
from contextlib import closing
import bcrypt

app = Flask(__name__)
mysql = MySQL(app)

app.secret_key = 'why would I tell you my secret key?'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'BucketList'

@app.route("/", methods=['POST'])
def main():
	return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/signUp',methods=['POST','GET'])
def signUp():

    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:

            # All Good, let's call the MySQL

            cur = mysql.connection.cursor()
            # _hashed_password = generate_password_hash(_password)
            #cur.callproc('sp_createUser',(_name,_email,_password))
            cur.execute('''SELECT MAX(user_id) FROM tbl_user ''')
            maxid = cur.fetchone()
            #hash
            handstand = bcrypt.hashpw(_password.encode("utf-8"), bcrypt.gensalt(5))
            cur.execute('''INSERT INTO tbl_user (user_name, user_username, user_userpassword ) VALUES (%s, %s, %s)''', (_name, _email, handstand))
            mysql.connection.commit()
            data = cur.fetchall()

            if len(data) is 0:
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
            cur.commit()
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cur.close()

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

    # connect to mysql
 
        cur = mysql.connection.cursor()
        cur.callproc('sp_validateLogin',(_username,))
        handstand = bcrypt.hashpw(_password.encode("utf-8"), bcrypt.gensalt(5))
        data = cur.fetchall()
 
        if len(data) > 0:
            if bcrypt.checkpw(_password.encode("utf-8"), handstand):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
 
 
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cur.close()

if __name__ == "__main__":
    app.debug = True
    app.run(port=5000)
