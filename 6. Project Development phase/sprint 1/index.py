from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re, random, smtplib, os, time, datetime
from flask_mail import Mail, Message
import ibm_db
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

app.secret_key = '12345'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'care2'

mysql = MySQL(app)

mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'customercareregistry22@gmail.com'
app.config['MAIL_PASSWORD'] = 'vxzttcjvdvrqeeve'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=xgl47707;PWD=gzw6dwHPkRJMqGrS", '', '')



@app.route('/', methods =['GET', 'POST'])
def index():
   if request.method == 'POST' and 'email' in request.form:
      email = request.form['email']
      stmt = ibm_db.prepare(conn,'SELECT * FROM subscriptions WHERE email = ?')
      ibm_db.bind_param(stmt, 1, email)
      ibm_db.execute(stmt)
      subscriptions = ibm_db.fetch_assoc(stmt)
      if subscriptions:
         flash('This Email Is Already Subscribed')
      else:
         ts = time.time()
         timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
         stmt=ibm_db.prepare(conn,'INSERT INTO subscriptions VALUES (?, ?, ?)')
         ibm_db.bind_param(stmt, 1, 'NULL')
         ibm_db.bind_param(stmt, 2, email)
         ibm_db.bind_param(stmt, 3, timestamp)
         ibm_db.execute(stmt)
         flash('You have successfully Subscribed')
   return render_template('index.html')



@app.route('/customerlogin', methods =['GET', 'POST'])
def customerlogin():
   msgdecline = ''
   if request.method == 'POST' and 'cemail' in request.form and 'cpassword' in request.form:
      cemail = request.form['cemail']
      cpassword = request.form['cpassword']
      stmt=ibm_db.prepare(conn,'SELECT * FROM customers_details WHERE customer_email = ? AND customer_password = ?')
      ibm_db.bind_param(stmt,1,cemail)
      ibm_db.bind_param(stmt,2,cpassword)
      ibm_db.execute(stmt)
      customers_details = ibm_db.fetch_assoc(stmt)
      if customers_details:
         session['loggedin'] = True
         session['cemail'] = customers_details['CUSTOMER_EMAIL']
         msgsuccess = 'Logged in successfully !'
         return redirect(url_for('welcome'))
      else:
         msgdecline = 'Incorrect Email / Password !'
   return render_template('customerlogin.html', msgdecline = msgdecline)



@app.route('/agentlogin', methods =['GET', 'POST'])
def agentlogin():
   msgdecline = ''
   if request.method == 'POST' and 'aemail' in request.form and 'apassword' in request.form:
      aemail = request.form['aemail']
      apassword = request.form['apassword']
      stmt =ibm_db.prepare(conn,'SELECT * FROM agent_information WHERE agent_email = ? AND agent_password = ?')
      ibm_db.bind_param(stmt,1,aemail)
      ibm_db.bind_param(stmt,2,apassword)
      ibm_db.execute(stmt)
      agent_information = ibm_db.fetch_both(stmt)
      if agent_information:
         session['loggedin'] = True
         session['aemail'] = agent_information['AGENT_EMAIL']
         msgsuccess = 'Logged in successfully !'
         return redirect(url_for('agentdashboard'))
      else:
         msgdecline = 'Incorrect Email / Password !'
   return render_template('agentlogin.html', msgdecline = msgdecline)



@app.route('/adminlogin', methods =['GET', 'POST'])
def adminlogin():
   msgdecline = ''
   if request.method == 'POST' and 'adminusername' in request.form and 'adminpassword' in request.form:
      adminusername = request.form['adminusername']
      adminpassword = request.form['adminpassword']
      stmt=ibm_db.prepare(conn,'SELECT * FROM admin_details WHERE admin_username = ? AND admin_password = ?')
      ibm_db.bind_param(stmt,1,adminusername)
      ibm_db.bind_param(stmt,2,adminpassword)
      ibm_db.execute(stmt)
      admin = ibm_db.fetch_both(stmt)
      if admin:
         session['loggedin'] = True
         session['adminusername'] = admin['ADMIN_USERNAME']
         msgsuccess = 'Logged in successfully !'
         return redirect(url_for('admindashboard'))
      else:
         msgdecline = 'Incorrect Username / Password !'
   return render_template('adminlogin.html', msgdecline = msgdecline)
  
  
  
@app.route('/customerregister', methods =['GET', 'POST'])
def customerregister():
   msgdecline = ''
   if request.method == 'POST' and 'cname' in request.form and 'cemail' in request.form and 'cpassword' in request.form and 'cconfirmpassword' in request.form :
      cname = request.form['cname']
      cemail = request.form['cemail']
      cpassword = request.form['cpassword']
      cconfirmpassword = request.form['cconfirmpassword']
      stmt=ibm_db.prepare(conn,'SELECT * FROM customers_details WHERE customer_email = ?')
      ibm_db.bind_param(stmt,1,cemail)
      ibm_db.execute(stmt)
      user_registration = ibm_db.fetch_both(stmt)
      if user_registration:
         msgdecline = 'Account already exists ! Try Login'
      elif cpassword != cconfirmpassword:
         msgdecline = 'Password did not match !'
      else:
         ts = time.time()
         timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
         stmt=ibm_db.prepare(conn,'INSERT INTO customers_details VALUES (?, ?, ?, ?, ?)')
         ibm_db.bind_param(stmt,1,'null')
         ibm_db.bind_param(stmt,2,cname)
         ibm_db.bind_param(stmt,3,cemail)
         ibm_db.bind_param(stmt,4,cpassword)
         ibm_db.bind_param(stmt,5,timestamp)
         ibm_db.execute(stmt)
         flash('You have successfully registered ! Try Login')
         try:
            mailmsg = Message('Customer Care Registry', sender = 'Registration Successful', recipients = ['{}', cemail])
            mailmsg.body = "Hello {},\nYou have successfully registered on Customer Care Registry".format(cname)
            mail.send(mailmsg)
         except:
            pass
         return redirect(url_for('customerlogin'))
   elif request.method == 'POST':
      msgdecline = 'Please fill out the form !'
   return render_template('customerregister.html', msgdecline = msgdecline)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True,port = 8080)
