from flask import Flask, render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_mail import Mail
import json
import os
import math
from datetime import datetime


local_server=True
with open('config.json','r') as c:
    params = json.load(c)["params"]



app = Flask(__name__)
app.secret_key="ramabajrangi"
app.config['UPLOAD_FOLDER']=params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)
if (local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['production_uri']

db = SQLAlchemy(app)

class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=True)
    email = db.Column(db.String(100), unique=False, nullable=True)
    phone = db.Column(db.String(15), unique=False, nullable=True)
    msg = db.Column(db.String(500), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False,nullable=False)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=False, nullable=True)
    tagline = db.Column(db.String(50), unique=False, nullable=True)
    slug = db.Column(db.String(30), unique=False, nullable=True)
    content = db.Column(db.String(255), unique=False, nullable=False)
    img = db.Column(db.String(12), unique=False,nullable=True)
    date = db.Column(db.String(12), unique=False,nullable=False)


@app.route("/")
def home():
    #Pagination
    post = Post.query.filter_by().all()
    last = int(math.ceil(len(post) / params['no_post']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page=int(page)
    post = post[(page - 1) * int(params['no_post']):(page - 1) * int(params['no_post']) + int(params['no_post'])]
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)



    # postprv=Post.query.filter_by().all()[0:params['no_post']]
    return render_template('index.html',params=params,postprv=post,prev=prev,next=next)

@app.route("/about")
def about():
    return render_template('about.html',params=params)



@app.route("/dashboard",methods=['GET','POST'])
def dashboard():

    if 'user' in session and session['user']==params['adm_user']:
        post=Post.query.all()
        return render_template('dashboard.html',params=params,post=post)


    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('pass')
        if username==params['adm_user'] and password==params['adm_pass']:
            session['user']=username
            post=Post.query.all()
            return render_template('dashboard.html',params=params,post=post)



    return render_template('sign.html',params=params)


@app.route("/edit/<string:id>", methods = ['GET','POST'])
def edit(id):
    if 'user' in session and session['user'] == params['adm_user']:
        if request.method=='POST':
            box_title=request.form.get('title')
            tag=request.form.get('tag')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img=request.form.get('img')

            if id=='0':
                post=Post(title=box_title,tagline=tag,slug=slug,content=content,img=img)
                db.session.add(post)
                db.session.commit()
            else:
                post=Post.query.filter_by(id=id).first()
                post.title=box_title
                post.tagline=tag
                post.slug=slug
                post.content=content
                post.img=img
                db.session.commit()
                return redirect('/edit/'+id)
        post=Post.query.filter_by(id=id).first()
        # return render_template('edit.html',params=params,post=post)
        return render_template('edit.html',params=params,id=id)


@app.route("/delete/<string:id>", methods = ['GET','POST'])
def delete(id):
    if 'user' in session and session['user'] == params['adm_user']:
        post=Post.query.filter_by(id=id).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')



@app.route("/upload", methods = ['GET','POST'])
def uploader():
    if 'user' in session and session['user'] == params['adm_user']:
        if (request.method=='POST'):
            f=request.files['file']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "Uploaded Successfully"

@app.route("/c", methods = ['GET','POST'])
def contact():
    if(request.method=='POST'):
        """adding data to database"""
        name = request.form.get('name')
        email = request.form.get('email')
        ph = request.form.get('phone')
        msg = request.form.get('msg')

        entry=Contact(name=name,email=email,phone=ph,date=datetime.now(),msg=msg)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('Portfolio- New Message from' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=msg + "\n" + "Ph - " + ph
                          )

    return render_template('contact.html',params=params)

@app.route("/p/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params,post=post)

@app.route("/logout")
def logout():
    if 'user' in session and session['user'] == params['adm_user']:
        session.pop('user')
        return redirect('/dashboard')
    return redirect('/dashboard')
app.run(debug=True)