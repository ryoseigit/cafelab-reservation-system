from apps import app
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy import Column,Integer,String
import datetime
from apps.sendMail import sendMail
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
import pytz





# class Base(DeclarativeBase):
#   pass
# db = SQLAlchemy(model_class=Base)



app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.secret_key = os.getenv("secret_key")
db = SQLAlchemy(app)
# db.init_app(app)





# apsschedulerで定期実行
# startdateの9時間後にスタート


def job():
    with app.app_context():
        reserves = Reserve.query.order_by(Reserve.time)
        now = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
        after_15min = now + datetime.timedelta(minutes=15)
        after_15min_date = after_15min.strftime("%Y-%m-%d")
        after_15min_time = after_15min.strftime("%H:%M")
        
        for reserve in reserves:
            if reserve.date  == after_15min_date   and   reserve.time == after_15min_time:
                userEmail = reserve.email
                sendMail(userEmail)



scheduler = BackgroundScheduler()

scheduler.add_job(job, 'interval', minutes=30,
        start_date="2023-11-11 10:45:00",
        end_date="2024-01-01 00:15:00")


@app.before_first_request
def start_scheduler():
    scheduler.start()





class Reserve(db.Model):
    __tablename__ = 'Reserve'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String)
    date= Column(String) 
    time = Column(String)
    number = Column(Integer)
    chair = Column(String)

with app.app_context():
    db.create_all()

class MyModelView(ModelView):
    # column_filters = ['date']
    column_default_sort = 'date'
    column_default_sort = 'time'
    form_excluded_columns = ['email']
    column_exclude_list = ['email']



admin = Admin(app)
admin.add_view(MyModelView(Reserve, db.session))




@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        reserves = Reserve.query.order_by(Reserve.time)
        newreserves = []
        
        now = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
        today = now.strftime("%Y-%m-%d")
        
        
        for reserve in reserves:
            if reserve.date == today:
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
        
        
        
        
        return redirect("/successReserve")
    
        


@app.route("/successReserve", methods=["GET"])
def successReserve():
    return render_template('successReserve.html')


