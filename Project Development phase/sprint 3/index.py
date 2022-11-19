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



@app.route('/agentregister', methods =['GET', 'POST'])
def agentregister():
   if not session.get("adminusername"):
      return redirect("/adminlogin")
   else:
      msgdecline = ''
      if request.method == 'POST' and 'aname' in request.form and 'aemail' in request.form and 'ausername' in request.form and 'apassword' in request.form and 'aconfirmpassword' in request.form :
         aname = request.form['aname']
         aemail = request.form['aemail']
         ausername = request.form['ausername']
         apassword = request.form['apassword']
         aconfirmpassword = request.form['aconfirmpassword']
         stmt=ibm_db.prepare(conn,'SELECT * FROM agent_information WHERE agent_email = ?')
         ibm_db.bind_param(stmt,1,aemail)
         ibm_db.execute(stmt)
         agent_information = ibm_db.fetch_assoc(stmt)
         if agent_information:
            msgdecline = 'Account already exists ! Try Login'
         else:
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            stmt=ibm_db.prepare(conn,'INSERT INTO agent_information VALUES (?, ?, ?, ?, ?, ?)')
            ibm_db.bind_param(stmt,1,'null')
            ibm_db.bind_param(stmt,2,aname)
            ibm_db.bind_param(stmt,3,aemail)
            ibm_db.bind_param(stmt,4,ausername)
            ibm_db.bind_param(stmt,5,apassword)
            ibm_db.bind_param(stmt,6,timestamp)
            ibm_db.execute(stmt)
            flash('Agent Has been successfully registered !')
            try:
               mailmsg = Message('Customer Care Registry', sender = 'Registration Successful', recipients = ['{}', aemail])
               mailmsg.body = "Hello, You have been Successfully Registered as Agent"
               mail.send(mailmsg)
            except:
               pass
            return redirect(url_for('agentlogin'))
      elif request.method == 'POST':
         msg = 'Please fill out the form !'
   return render_template('agentregister.html', msgdecline = msgdecline)



@app.route('/welcome', methods =['GET', 'POST'])
def welcome():
   if not session.get("cemail"):
      return redirect("/customerlogin")
   else:
      msgsuccess = ''
      msgdecline = ''
      cmail = session['cemail']
      stmt= ibm_db.prepare(conn,'SELECT * FROM complaint_details WHERE customer_email = ? ORDER BY timestamp DESC')
      ibm_db.bind_param(stmt,1,cmail)
      ibm_db.execute(stmt)
      data = ibm_db.fetch_assoc(stmt)
      t_data = []
      while data!=False:
         app.logger.info('LN:::12345')
         t_data.append(data)
         data = ibm_db.fetch_assoc(stmt)
      app.logger.info(t_data)
      stmt= ibm_db.prepare(conn,'SELECT customer_name FROM customers_details WHERE customer_email = ?')
      ibm_db.bind_param(stmt,1,cmail)
      ibm_db.execute(stmt)
      cname = ibm_db.fetch_assoc(stmt)
      if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'category' in request.form and 'subject' in request.form and 'description' in request.form :
         name = request.form['name']
         email = request.form['email']
         category = request.form['category']
         subject = request.form['subject']
         description = request.form['description']
         ticketno = random.randint(100000, 999999)
         ts = time.time()
         timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
         app.logger.info('LN ::::: 123')
         stmt= ibm_db.prepare(conn,'INSERT INTO complaint_details VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? )')
         ibm_db.bind_param(stmt,1,ticketno)
         ibm_db.bind_param(stmt,2,name)
         ibm_db.bind_param(stmt,3,email)
         ibm_db.bind_param(stmt,4,category)
         ibm_db.bind_param(stmt,5,subject)
         ibm_db.bind_param(stmt,6,description)
         ibm_db.bind_param(stmt,7,timestamp)
         ibm_db.bind_param(stmt,8,"pending")
         ibm_db.bind_param(stmt,9,"pending")
         ibm_db.execute(stmt)
         try:
            mailmsg = Message('Customer Care Registry', sender = 'Request Received', recipients = ['{}', email])
            mailmsg.body = "Hello {},\n\nThanks for contacting Customer Care Registry\nWe have received your complain\nYour Ticket Number: {}\nCategory: {}\nSubject: {}\nDescription: {}\n\nWe strive to provide excellent service, and will respond to your request as soon as possible.".format(name, ticketno, category, subject, description)
            mail.send(mailmsg)
         except: 
            app.logger.info('LN3:::: Something happened')
            pass
         flash ('Your complaint is successfully submitted !')
         return redirect(url_for('welcome'))
      elif request.method == 'POST':
         msgdecline = 'Please fill out the form !'
   return render_template('welcome.html', msgsuccess = msgsuccess, data=t_data, cname=cname['CUSTOMER_NAME'])
   


@app.route('/agentdashboard', methods =['GET', 'POST'])
def agentdashboard():
   if not session.get("aemail"):
      return redirect("/agentlogin")
   else:
      msg = ''
      aemail = session['aemail']
      stmt= ibm_db.prepare(conn,'SELECT agent_name FROM agent_information WHERE agent_email = ?')
      ibm_db.bind_param(stmt,1,aemail)
      ibm_db.execute(stmt)
      agent=ibm_db.fetch_assoc(stmt)
      agent_name = agent['AGENT_NAME']
      app.logger.info(agent_name)
         
      stmt= ibm_db.prepare(conn,'SELECT * FROM complaint_details WHERE agent_name = ? ORDER BY timestamp DESC')
      ibm_db.bind_param(stmt,1,agent_name)
      ibm_db.execute(stmt)
      data=[]
      data_res = ibm_db.fetch_assoc(stmt)
      while data_res!=False:
         data.append(data_res)
         data_res=ibm_db.fetch_assoc(stmt)
      if request.method == 'POST' and 'status' in request.form :
         status = request.form['status']
         ticketno = request.form['ticketno']
         stmt= ibm_db.prepare(conn,'UPDATE complaint_details SET status_a = ? WHERE ticketno = ?' )
         ibm_db.bind_param(stmt,1,status)
         ibm_db.bind_param(stmt,2,ticketno)
         ibm_db.execute(stmt)
         msg = 'Your complaint is successfully solved !'
         
         stmt= ibm_db.prepare(conn,'SELECT customer_email FROM complaint_details WHERE ticketno = ?' )
         ibm_db.bind_param(stmt,1,ticketno)
         ibm_db.execute(stmt)
         customer_mail = ibm_db.fetch_assoc(stmt)
         cemail = customer_mail['CUSTOMER_EMAIL']
            
         try:
            mailmsg = Message('Customer Care Registry', sender = 'Your Ticket Status', recipients = ['{}', cemail])
            mailmsg.body = "Hello, \nYour complaint has been successfully solved\nYour Ticket Number: {}".format(ticketno)
            mail.send(mailmsg)
         except:
            pass
         return redirect(url_for('agentdashboard'))
      elif request.method == 'POST':
         msg = 'Please fill out the form !'
   return render_template('agentdashboard.html', msg = msg, data=data, agent_name=agent_name)



@app.route('/admindashboard', methods =['GET', 'POST'])
def admindashboard():
   if not session.get("adminusername"):
      return redirect("/adminlogin")
   else:
      msg = ''
      stmt= ibm_db.prepare(conn,'SELECT * FROM complaint_details ORDER BY timestamp DESC')
      ibm_db.execute(stmt)
      data_res = ibm_db.fetch_assoc(stmt)
      data=[]
      while data_res!=False:
         data.append(data_res)
         data_res=ibm_db.fetch_assoc(stmt)
      stmt= ibm_db.prepare(conn,'SELECT * FROM agent_information')
      ibm_db.execute(stmt)
      agent_res = ibm_db.fetch_assoc(stmt)
      agent=[]
      while agent_res!=False:
         agent.append(agent_res)
         agent_res=ibm_db.fetch_assoc(stmt)
      stmt= ibm_db.prepare(conn,'SELECT COUNT(status_a) AS pending FROM complaint_details WHERE status_a = ?')
      ibm_db.bind_param(stmt,1,'pending')
      ibm_db.execute(stmt)
      pending = ibm_db.fetch_assoc(stmt)
      app.logger.info('LN::::@#$')
      app.logger.info(pending)
      pending=pending['PENDING']
      stmt= ibm_db.prepare(conn,'SELECT COUNT(status_a) AS assigned FROM complaint_details WHERE status_a = ?')
      ibm_db.bind_param(stmt,1,'Agent Assigned')
      ibm_db.execute(stmt)
      assigned = ibm_db.fetch_assoc(stmt)
      assigned=assigned['ASSIGNED']
      stmt= ibm_db.prepare(conn,'SELECT COUNT(status_a) AS completed FROM complaint_details WHERE status_a = ?')
      ibm_db.bind_param(stmt,1,'Closed')
      ibm_db.execute(stmt)
      completed = ibm_db.fetch_assoc(stmt)
      completed=completed['COMPLETED']

      if request.method == 'POST' and 'agentassign' in request.form :
         agentassign = request.form['agentassign']
         adminusername = request.form['adminusername']
         ticketno = request.form['ticketno']
         stmt= ibm_db.prepare(conn,'UPDATE complaint_details SET agent_name = ? WHERE ticketno = ?')
         ibm_db.bind_param(stmt,1,agentassign)
         ibm_db.bind_param(stmt,2,ticketno)
         ibm_db.execute(stmt)
         stmt= ibm_db.prepare(conn,'UPDATE complaint_details SET status_a = ? WHERE ticketno = ?')
         ibm_db.bind_param(stmt,1,"Agent Assigned")
         ibm_db.bind_param(stmt,2,ticketno)
         ibm_db.execute(stmt)
         msg = 'Your complaint is Assigned to Agent !'
         
         stmt= ibm_db.prepare(conn,'SELECT customer_email FROM complaint_details WHERE ticketno = ?')
         ibm_db.bind_param(stmt,1,ticketno)
         ibm_db.execute(stmt)
         customer_mail = ibm_db.fetch_assoc(stmt)
         
         cemail = customer_mail['CUSTOMER_EMAIL']
         
         try:
            mailmsg = Message('Customer Care Registry', sender = 'Agent Assigned', recipients = ['{}', cemail])
            mailmsg.body = "Hello,\nWe have received your complaint and agent {} has been Successfully Assigned\nYour Ticket Number: {}\n\nYou will be notified when your complain will be solved.".format(agentassign, ticketno)
            mail.send(mailmsg)
         except:
            pass
         return redirect(url_for('admindashboard'))
      elif request.method == 'POST':
         msg = 'Please fill out the form !'
   return render_template('admindashboard.html', msg = msg, data=data, agent=agent, pending=pending, assigned=assigned, completed=completed)



@app.route('/adminanalytics')
def adminanalytics():
   mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   mycursor.execute('SELECT COUNT(agent_name) AS JenTile FROM complaint_details WHERE agent_name = %s', ("Jen Tile",))
   JenTile = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(agent_name) AS AllieGrater FROM complaint_details WHERE agent_name = %s', ("Allie Grater",))
   AllieGrater = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(agent_name) AS RaySin FROM complaint_details WHERE agent_name = %s', ("Ray Sin",))
   RaySin = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(category) AS Category1 FROM complaint_details WHERE category = %s', ("Product Exchange or Return",))
   category1 = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(category) AS Category2 FROM complaint_details WHERE category = %s', ("Product Out of Stock",))
   category2 = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(category) AS Category3 FROM complaint_details WHERE category = %s', ("Payments & Transactions",))
   category3 = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(category) AS Category4 FROM complaint_details WHERE category = %s', ("Product Delivery",))
   category4 = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(category) AS Category5 FROM complaint_details WHERE category = %s', ("Other",))
   category5 = mycursor.fetchall()
   print(category1)
   return render_template('adminanalytics.html', JenTile=JenTile, AllieGrater=AllieGrater, RaySin=RaySin, category1=category1, category2=category2, category3=category3, category4=category4, category5=category5)



@app.route('/customerforgotpassword', methods =['GET', 'POST'])
def customerforgotpassword():
      msgdecline = ''
      if request.method == 'POST' and 'customerforgotemail' in request.form :
         forgotemail = request.form['customerforgotemail']
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM customers_details WHERE customer_email = % s', (forgotemail, ))
         customers_details = cursor.fetchone()
         if customers_details:
            session['customerforgotemail'] = forgotemail
            otp = random.randint(1000, 9999)
            session['otp'] = otp
            try:
               mailmsg = Message('Customer Care Registry', sender = 'Forgot Password', recipients = ['{}', forgotemail])
               mailmsg.body = "Hello, \nYour OTP is: {}\nDo not share this OTP to anyone \nUse this OTP to reset your password.".format(otp)
               mailmsg.subject = 'Forgot Passowrd'
               mail.send(mailmsg)
               flash('OTP has been sent to your email')
               return redirect(url_for('enterotp'))
            except:
               msgdecline = 'Oops! Something went wrong! Email not sent'
         else:
            msgdecline = 'This email is not registered!'
      return render_template('customerforgotpassword.html', msgdecline = msgdecline)
   
   
   
@app.route('/agentforgotpassword', methods =['GET', 'POST'])
def agentforgotpassword():
      msgdecline = ''
      if request.method == 'POST' and 'agentforgotemail' in request.form :
         forgotemail = request.form['agentforgotemail']
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM agent_information WHERE agent_email = % s', (forgotemail, ))
         agent_information = cursor.fetchone()
         if agent_information:
            session['agentforgotemail'] = forgotemail
            otp = random.randint(1000, 9999)
            session['otp'] = otp
            try:
               mailmsg = Message('Customer Care Registry', sender = 'Forgot Password', recipients = ['{}', forgotemail])
               mailmsg.body = "Hello, \nYour OTP is: {}\nDo not share this OTP to anyone \nUse this OTP to reset your password.".format(otp)
               mail.send(mailmsg)
               flash('OTP has been sent to your email')
               return redirect(url_for('enterotp'))
            except:
               msgdecline = 'Oops! Something went wrong! Email not sent'
         else:
            msgdecline = 'This email is not registered!'
      return render_template('agentforgotpassword.html', msgdecline = msgdecline)



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True,port = 8080)
