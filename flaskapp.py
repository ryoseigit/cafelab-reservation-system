from flask import Flask
from flask import render_template, request, redirect, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
import datetime
from sendMail import sendMail
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os



app = Flask(__name__)

class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.secret_key = os.getenv("secret_key")
db.init_app(app)






class Reserve(db.Model):
    __tablename__ = 'Reserve'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String)
    date: Mapped[str] = mapped_column(String) 
    time: Mapped[str] = mapped_column(String)
    number: Mapped[int] = mapped_column(Integer)
    chair: Mapped[str] = mapped_column(String)

with app.app_context():
    db.create_all()

class MyModelView(ModelView):
    __tablename__ = 'MyModelView'
    column_filters = ['date']
    column_default_sort = 'time'

class Adminuser(db.Model):
    __tablename__ = 'Adminuser'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(250))
  


admin = Admin(app)
admin.add_view(MyModelView(Reserve, db.session))




@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        reserves = Reserve.query.order_by(Reserve.time)
        newreserves = []
        
        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        today = str(now.month) + '月' + str(now.day) + '日'
        
        
        for reserve in reserves:
            if reserve.date[:6] == today:
                newreserves.append(reserve)
           
                
        return render_template('index.html', newreserves=newreserves, today=today)

    else:
        name = request.form.get("name")
        email = request.form.get("email")
        date = request.form.get("date")
        time = request.form.get("time")
        number = request.form.get("number")
        chair = request.form.get("chair")

            
        reserve = Reserve(name=name, email=email, date=date, time=time, number=number, chair=chair)
        

        db.session.add(reserve)
        db.session.commit()
        
        return redirect("/successReserve" )
    
        


@app.route("/successReserve", methods=["GET"])
def successReserve():
    return render_template('successReserve.html')



    





 
 
def job():
    with app.app_context():
        reserves = Reserve.query.order_by(Reserve.time)
        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        after_15min = now + datetime.timedelta(minutes=15)
        after_15min_date = str(after_15min.strftime("%m")) + "月" + str(after_15min.strftime("%d")) + "日"
        after_15min_time = str(after_15min.strftime("%H:%M"))
        
        for reserve in reserves:
            if reserve.date[:6]  == after_15min_date   and   reserve.time == after_15min_time:
                userEmail = reserve.email
                sendMail(userEmail)
            # else:
            #     print(after_15min_time) 

# apsschedulerの使い方

scheduler = BackgroundScheduler()



scheduler.add_job(job, 'interval', minutes=30,
    start_date="2023-10-28 08:45:00",
    end_date="2023-10-29 15:45:00")

scheduler.start()




if __name__ == "__main__":
    app.run()

