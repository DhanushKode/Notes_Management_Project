from flask import Flask,flash,request,url_for,redirect,render_template,flash,session,send_file,jsonify
from flask_session import Session
from otp import generate_otp
from cmail import send_mail
from datetime import datetime,timedelta
import flask_excel as excel
import re
from stoken import entoken, dntoken
from io import BytesIO
from mysql.connector import (connection)
mydb = connection.MySQLConnection(user='root', host='localhost',password='admin123',db='smp')
app = Flask(__name__)
excel.init_excel(app)
app.secret_key=b'\xd9\xad\x1b\xf3-'
app.config['SESSION_TYPE']='filesystem'
Session(app)


@app.route('/',methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/userregister',methods=['GET','POST'])
def userregister():
    try:
        if request.method == 'POST':
            username=request.form['username'].strip()
            useremail=request.form['email'].strip()
            userpassword=request.form['password']
            cursor=mydb.cursor()
            cursor.execute('select count(*) from users where useremail=%s',[useremail])
            email_count=cursor.fetchone()
            if email_count[0]==1:
                flash('Email already exists')
                return redirect(url_for('userregister'))
            elif email_count[0]==0:

                serverotp=generate_otp()
                otp_expiry=datetime.now()+timedelta(minutes=5)
                cursor.execute('insert into users(username,useremail,userpassword,otp,otp_active_time,account_status) values(%s,%s,%s,%s,%s,%s)',
                [username,useremail,userpassword,serverotp,otp_expiry,'pending'])
                mydb.commit()
                cursor.close()
                subject ='OTP Verification For SNM APP '
                body = f"Hello {username} use the following OTP: {serverotp} to verify your account"
                send_mail(to=useremail,subject=subject,body=body)
                flash('OTP has been to given mail')
                return redirect(url_for('verifyotp',email=useremail))
            else:
                flash("something went wrong")
                return redirect(url_for('userregister'))


        return render_template('register.html')
    except Exception as e:
        mydb.rollback()
        print("Here is the Error",e)
        flash("Could not verify user details")
    return render_template('userregister')

@app.route('/verifyotp/<email>',methods=['GET','POST'])
def verifyotp(email):
    if request.method == 'POST':
        user_otp=request.form['otp']
        user_otp_time=datetime.now()
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select otp,otp_active_time ,account_status from users where useremail=%s',[email])
            users=cursor.fetchone()#('opt')
            if not users:
                flash('Email not Found')
                return redirect(url_for('userregister'))
            if users[0]!=user_otp:
                flash('Invalid OTP try again')
                return redirect(url_for('userregister'))

            if users[2]=='active':
                flash('User already active')
                return redirect(url_for('userregister'))
            
            if users[1] < user_otp_time:
                flash('OTP Expired')
                return redirect(url_for('userregister'))
            if users and users[2]=='pending' and users[1]< user_otp_time:
                cursor.execute('delete from users where useremail=%s',[email])
                mydb.commit()
                
            cursor.execute('update users set account_status="active",otp=null,otp_active_time=null where useremail=%s',[email])
            mydb.commit()
        except Exception as e :
            print(e)
            flash('could not verify otp')
            return redirect(url_for('verifyotp',email=email))
        else:
            flash('verification sucessfull')
            return redirect(url_for('userlogin'))
    return render_template('otp.html')
    
@app.route('/userlogin',methods=['GET','POST'])
def userlogin():
    if request.method=='POST':
        login_useremail=request.form['email']
        login_userpassword=request.form['password']
        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('select username,useremail,userpassword from users where useremail=%s',[login_useremail])
            users_details=cursor.fetchone()
            if not users_details:
                flash('user not found')
                return redirect(url_for('home'))
            if users_details[2]!=login_userpassword:
                flash('invalid password')
                return redirect(url_for('userlogin'))
            cursor.close()
        except Exception as e:
            print(e)
            flash('login verification fail')
            return redirect(url_for('userlogin'))
        else:
            session['user']=login_useremail
            flash('login sucessfull')
            return redirect(url_for('dashboard'))                         
    return render_template('login.html')
@app.route('/dashboard',methods=['GET'])
def dashboard():
    if not session.get('user'):
        flash('please login first')
        return redirect(url_for('userlogin'))
    return render_template('dashboard.html')
@app.route('/addnotes',methods=['GET','POST'])
def addnotes():
    if not session.get('user'):
        flash('please login first')
        return redirect(url_for('userlogin'))
    try:
               if request.method=='POST':
                    title=request.form['title']
                    description=request.form['description']
                    cursor=mydb.cursor(buffered=True)
                    cursor.execute('select userid from users where useremail=%s',[session.get('user')])
                    userid=cursor.fetchone()
                    cursor.execute('insert into notesdata(title,content,userid) values(%s,%s,%s)',[title,description,userid[0]])
                    mydb.commit()
                    cursor.close()
                    flash('note added sucessfully')
                    return redirect(url_for('dashboard'))
               return render_template('addnotes.html')
    except Exception as e:
        print(e)
        mydb.rollback()
        flash('could  add notes')
        return redirect(url_for('dashboard'))
@app.route('/viewallnotes',methods=['GET'])
def viewallnotes():
    if not session.get('user'):
        flash('pls login')
        return redirect(url_for('userlogin'))
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select userid from users where useremail=%s',[session.get('user')])
        userid=cursor.fetchone() #(3,)
        cursor.execute('select notesid,title,created_at from notesdata where userid=%s',[userid[0]])
        all_notesdata=cursor.fetchall() #[(),()]
        cursor.close()
        flash('successfully fetched all notes')
        return render_template('viewallnotes.html',all_notesdata=all_notesdata)
    except Exception as e:
        print(e)
        flash('Could fetch notes')
        return redirect(url_for('dashboard'))
@app.route('/viewnotes/<notesid>',methods=['GET'])
def viewnotes(notesid):
    if not session.get('user'):
         flash('please login first')
         return redirect(url_for('userlogin'))
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select userid from users where useremail=%s',[session.get('user')])
        userid=cursor.fetchone() #(3,)
        cursor.execute('select notesid,title,content,created_at from notesdata where userid=%s and notesid=%s',[userid[0],notesid])
        notes_data=cursor.fetchone() #(1,'title','content','2024-06-10 12:00:00')
        return render_template('viewnotes.html',notes_data=notes_data)
    except Exception as e:
        print(e)
        flash('could not fetch notes details')
        return redirect(url_for('viewallnotes'))
    finally:
        if cursor:
         cursor.close()
@app.route('/delete/<notesid>',methods=['GET'])
def delete(notesid):
    if not session.get('user'):
            flash('please login first')
            return redirect(url_for('userlogin'))

    try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select userid from users where useremail=%s',[session.get('user')])
            userid=cursor.fetchone() #(3,)
            cursor.execute('delete from notesdata where userid=%s and notesid=%s',[userid[0],notesid])
            mydb.commit()
            flash('note deleted sucessfully')
            return redirect(url_for('viewallnotes'))
    except Exception as e:
            print(e)
            flash('could not delete note')
            return redirect(url_for('viewallnotes'))
    finally:
            if cursor:
                cursor.close()
@app.route('/updatenotes/<notesid>',methods=['GET','POST'])
def updatenotes(notesid):
    if not session.get('user'):
         flash('please login first')
         return redirect(url_for('userlogin'))
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select userid from users where useremail=%s',[session.get('user')])
        userid=cursor.fetchone() #(3,)
        cursor.execute('select notesid,title,content,created_at from notesdata where userid=%s and notesid=%s',[userid[0],notesid])
        notes_data=cursor.fetchone() #(1,'title','content','2024-06-10 12:00:00')
        if request.method=='POST':
            updated_title=request.form['title']
            updated_content=request.form['content']
            cursor.execute('update notesdata set title=%s,content=%s where userid=%s and notesid=%s',[updated_title,updated_content,userid[0],notesid])
            mydb.commit()
            flash('note updated sucessfully')
            return redirect(url_for('viewallnotes'))
        return render_template('updatenotes.html',notes_data=notes_data)
    except Exception as e:
        print(e)
        flash('could not fetch notes details')
        return redirect(url_for('viewallnotes'))
    finally:
        if cursor:
         cursor.close()
@app.route('/getexceldata',methods=['GET'])
def getexceldata():
    if not session.get('user'):
        flash('pls login')
        return redirect(url_for('userlogin'))
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select userid from users where useremail=%s',[session.get('user')])
        userid=cursor.fetchone() #(3,)
        cursor.execute('select notesid,title,content,created_at from notesdata where userid=%s',[userid[0]])
        all_notesdata=cursor.fetchall() #[(),()]
        cursor.close()
        array_data=[list(i) for i in all_notesdata]
        columns=["Notesid","title","content","time"]
        array_data.insert(0,columns)
        print(array_data)
        return excel.make_response_from_array(array_data, 'xlsx',filename='Notesexcel')
    except Exception as e:
        print(e)
        flash('Could fetch notes')
        return redirect(url_for('dashboard'))
@app.route('/uploadfile',methods=['GET','POST'])
def uploadfile():
    if not session.get('user'):
        flash('pls login')
        return redirect(url_for('userlogin'))
    try:
        if request.method=='POST':
            user_file=request.files['file']
            fdata=user_file.read()
            fname=user_file.filename
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select userid from users where useremail=%s',[session.get('user')])
            userid=cursor.fetchone() [0]#(3,)
            cursor.execute('insert into filesdata(filename,filedata,userid) values(%s,%s,%s)',[fname,fdata,userid])
            mydb.commit()
            cursor.close()
            flash('file uploaded sucessfully')
            return redirect(url_for('uploadfile'))
        return render_template('uploadfile.html')
    except Exception as e:
        print(e)
        flash('Could not upload file')
        return redirect(url_for('dashboard'))
@app.route('/viewallfiles',methods=['GET'])
def viewallfiles():
    if not session.get('user'):
            flash('pls login')
            return redirect(url_for('userlogin'))
    try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select userid from users where useremail=%s',[session.get('user')])
            userid=cursor.fetchone() #(3,)
            cursor.execute('select fileid,filename,created_at from filesdata where userid=%s',[userid[0]])
            all_filesdata=cursor.fetchall() #[(),()]
            cursor.close()
            flash('successfully fetched all files')
            return render_template('viewallfiles.html',all_filesdata=all_filesdata)
    except Exception as e:
            print(e)
            flash('Could not fetch files')
            return redirect(url_for('dashboard'))
@app.route('/viewfile/<fileid>',methods=['GET'])
def viewfile(fileid):
    if not session.get('user'):
         flash('please login first')
         return redirect(url_for('userlogin'))
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select userid from users where useremail=%s',[session.get('user')])
        userid=cursor.fetchone() #(3,)
        cursor.execute('select fileid,filename,filedata,created_at from filesdata where userid=%s and fileid=%s',[userid[0],fileid])
        file_data=cursor.fetchone() #(1,'title','content','2024-06-10 12:00:00')
        file_array=BytesIO(file_data[2])
        cursor.close()
        flash('successfully fetched file details')
        return send_file(file_array,as_attachment=False,download_name=f'{file_data[1]}')
    except Exception as e:
        print(e)
        flash('could not fetch file details')
        return redirect(url_for('viewallfiles'))
    finally:
        if cursor:
         cursor.close()
@app.route('/downloadfile/<fileid>',methods=['GET'])
def downloadfile(fileid):
    if not session.get('user'):
             flash('please login first')
             return redirect(url_for('userlogin'))
    
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select userid from users where useremail=%s',[session.get('user')])
        userid=cursor.fetchone() #(3,)
        cursor.execute('select fileid,filename,filedata,created_at from filesdata where userid=%s and fileid=%s',[userid[0],fileid])
        file_data=cursor.fetchone() #(1,'title','content','2024-06-10 12:00:00')
        file_array=BytesIO(file_data[2])
        cursor.close()
        flash('successfully download file')
        return send_file(file_array,as_attachment=True,download_name=f'{file_data[1]}')
    except Exception as e:
        print(e)
        flash('could not download file')
        return redirect(url_for('viewallfiles'))
    finally:
            if cursor:
             cursor.close()
@app.route('/deletefile/<fileid>',methods=['GET'])
def deletefile(fileid):
    if not session.get('user'):
                 flash('please login first')
                 return redirect(url_for('userlogin'))
    
    
    try:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select userid from users where useremail=%s',[session.get('user')])
        userid=cursor.fetchone() #(3,)
        cursor.execute('delete  from filesdata where userid=%s and fileid=%s',[userid[0],fileid])
        mydb.commit()
        flash('successfully Deleted file')
        return redirect(url_for('viewallfiles'))
    except Exception as e:
        print(e)
        flash('could not delete file')
        return redirect(url_for('viewallfiles'))
    finally:
            if cursor:
                cursor.close()
@app.route('/userlogout')
def userlogout():
     if not session.get('user'):
          flash('pls login')
          return redirect(url_for('userlogin'))
     session.pop('user')
     flash('logout successfull')
     return redirect(url_for('userlogin'))
@app.route('/search',methods=['GET','POST'])
def search():
    if not session.get('user'):
        flash('Please login first')
        return redirect(url_for('userlogin'))
    try:
        search_data=request.form['sdata']
        strg=['A-Za-z0-9']
        pattern=re.compile(f'^{strg}',re.IGNORECASE)
        if pattern.match(search_data):
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select userid from users where useremail=%s',[session.get('user')])
            userid=cursor.fetchone()
            cursor.execute('select notesid, title,created_at from notesdata where userid=%s and (notesid like %s or title like %s or content like %s or created_at like %s)',[userid[0],search_data+'%',search_data+'%',search_data+'%',search_data+'%'])
            search_notesdata=cursor.fetchall()
            cursor.execute('select fileid,filename,created_at from filesdata where userid=%s and (fileid like %s or filename like %s or created_at like %s)',[userid[0],search_data+'%',search_data+'%',search_data+'%'])
            search_filesdata=cursor.fetchall()
            cursor.close()
            flash('successfully fetched all searched notes data')
            return render_template('searchdata.html',all_notesdata=search_notesdata,search_filesdata=search_filesdata)
        else:
            flash('invalid data')
            return redirect(url_for('dashboard'))
      
    except Exception as e:
        print(e)
        flash('Error in search data')
        return redirect(url_for('dashboard'))
@app.route('/forgot',methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        forgot_email=request.form['forgot password']
        
        cursor = mydb.cursor()
        cursor.execute('select count(*) from users where useremail=%s',[forgot_email])#will get number of same usermail of data in userdata
        
        email_count = cursor.fetchone()#(1,)
        print(email_count)
        if email_count[0] == 1:
            subject=f'forgot password reset link for snm appy'
            body=f'use the given link {url_for('newpassword',data=entoken(forgot_email),_external=True)}'
            send_mail(to=forgot_email,subject=subject,body=body)
            flash('sent to mail')
            return redirect(url_for('userlogin'))
        elif email_count[0]==0:
            flash('user not found')
            return redirect(url_for('userlogin'))
        else:
            flash('something went wrong')
            return redirect(url_for('userlogin'))      
    return render_template('forgot.html')
@app.route('/newpassword/<data>', methods=['GET','PUT'])
def newpassword(data):
     if request.method=='PUT':
          try:
            dserialised_email=dntoken(data)
          except Exception as e:
               print(e)
               flash('time out error')
               return redirect(url_for('userlogin'))
          print(request.get_json())
          npassword=request.get_json()['password']
          try:
               cursor=mydb.cursor(buffered=True)
               cursor.execute('select count(*) from users where useremail=%s', [dserialised_email])
               email_count=cursor.fetchone()
               print(email_count)
               if email_count[0]==1:
                    cursor.execute('update users set userpassword=%s where useremail=%s',[npassword,dserialised_email])
                    mydb.commit()
                    return jsonify({"status":"Success","message":"ok"})
               else:
                    return jsonify({"status":"failed","message":"email not found"})
          except Exception as e:
               print(e)
               return jsonify({"status":"failed","message":f"{str(e)}"})
          return render_template('reset.html,userdata=data')

     return render_template('reset.html')
app.run()