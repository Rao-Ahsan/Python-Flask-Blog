
from flask import Flask ,render_template, request ,session , redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from flask_mail import Mail
import json
import math

local_server = True

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'super_secret_key'

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]
db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    slug= db.Column(db.String(21), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    
    
    


@app.route("/about")
def about_func():
    return render_template("about.html", params=params)

@app.route("/dashboard")
def dashboard_func():
    if ('user' in session and session['user'] == params['admin_user']):
        posts= Posts.query.all()
        return render_template("dashboard.html", params=params,  posts=posts)

    if request.method == 'POST':
        user_name=request.form.get('uname')
        user_password= request.form.get('pass')
        if (user_name == params['admin_user'] and user_password == params['admin_password']):
            session['user'] = user_name
            posts= Posts.query.all()
            return render_template("dashboard.html", params=params , posts=posts)
    else:
        return render_template("login.html", params=params)

    

@app.route("/contact" , methods=['GET' , 'POST'])
def contact_func():
    if(request.method =='POST'):
        #Add entry to DB
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')

        entry= Contacts(name=name , phone_num=phone, email=email , date=datetime.now(), msg=message)
        
        db.session.add(entry)
        db.session.commit()
             

    return render_template("contact.html", params=params)

@app.route("/post/<string:post_slug>" , methods=["GET"])
def post_func(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()


    return render_template("post.html", params=params, post=post)

@app.route("/")
def home_func():
    posts=Posts.query.filter_by().all()[0:2]
    return render_template("index.html", params=params, posts=posts)




@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit_func(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            box_tagline = request.form.get('tline')
            box_slug = request.form.get('slug')
            box_content = request.form.get('content')
            date = datetime.now()
            if sno =='0':
                post=Posts(title= box_title , slug =box_slug , tagline = box_tagline , content = box_content, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post =Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = box_slug
                post.tagline = box_tagline
                post.content = box_content
                post.date = date
                db.session.commit()
                return redirect('/edit/'+ sno)
        post =Posts.query.filter_by(sno= sno).first()
        return render_template("edit.html", params=params , post=post , sno=sno)


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete_func(sno):
     if ('user' in session and session['user'] == params['admin_user']):
        delete_post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(delete_post)
        db.session.commit()
        return redirect("/dashboard")

@app.route("/logout" , methods=['GET'])
def logout_func():
    session.pop('user')
    return redirect("/dashboard")



app.run(debug=True)