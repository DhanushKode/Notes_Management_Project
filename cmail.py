import smtplib
from email.message import  EmailMessage
def send_mail(to,subject,body):
    try:
        server= smtplib.SMTP_SSL('smtp.gmail.com',465)
        server.login('kodedhanush9@gmail.com','evjk dsao xopw rnba')
        msg=EmailMessage()
        msg['FROM']='kodedhanush9@gmail.com'
        msg['TO']=to
        msg['SUBJECT']=subject
        msg.set_content(body)
        server.send_message(msg)

    except Exception as e:
        print(e)
        print('Email error')
    finally:
        server.quit()