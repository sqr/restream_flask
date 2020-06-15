from flask import render_template, flash, redirect, url_for, request
from app import app, db, tasks, scraper
from app.forms import LoginForm, RegistrationForm, StreamingForm, StopForm, MarianizerForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Streaming
from werkzeug.urls import url_parse
from datetime import datetime
from app.forms import EditProfileForm, PostForm
import rq
from redis import Redis
from app.exception_handlers import my_handler
import os, signal
import time
import psutil
import subprocess

@app.route('/oldindex', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db. session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))

    return render_template('index.html', title='Home', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('streamings')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('streamings'))


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself duh')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself duh')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/streamings', methods=['GET', 'POST'])
@login_required
def streamings():

    url_presidente = scraper.get_origin(scraper.URL_PRESIDENTE)
    url_ministros = scraper.get_origin(scraper.URL_MINISTROS)
    form = StreamingForm()
    form2 = StopForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    streamings = Streaming.query.order_by(Streaming.timestamp.desc()).paginate(
        page, app.config['STREAMINGS_PER_PAGE'], False)
    next_url = url_for('streamings', page=streamings.next_num) \
        if streamings.has_next else None
    prev_url = url_for('streamings', page=streamings.prev_num) \
        if streamings.has_prev else None
    
    if form.submit_start.data and form.validate():
        queue = rq.Queue('microblog-tasks', connection=Redis.from_url(app.config['REDIS_URL']))
        job = queue.enqueue('app.tasks.restream', job_timeout=36000, origin=form.origin.data, server=form.server.data, stream_key=form.stream_key.data)
        stream = Streaming(job_id=job.get_id(), title=form.title.data, origin=form.origin.data, server=form.server.data, stream_key=form.stream_key.data, author=current_user)
        db.session.add(stream)
        db.session.commit()
        flash('Your streaming is now live!')
        return redirect(url_for('streamings'))

    if form2.submit_stop.data and form2.validate():
        queue = rq.Queue('microblog-tasks', connection=Redis.from_url(app.config['REDIS_URL']))
        workers = rq.Worker.all(queue=queue)

        for worker in workers:
            peine = worker.get_current_job_id()
            if peine == form2.fld1.data:
                pid = worker.pid
                '''os.kill(worker.pid, signal.SIGINT)'''
                try:
                    parent = psutil.Process(pid)
                except psutil.NoSuchProcess:
                    flash('No worker')
                    return redirect(url_for('streamings'))
                children = parent.children(recursive=True)
                for p in children:
                    os.kill(p.pid, signal.SIGTERM)  

        to_stop = Streaming.query.filter_by(job_id=form2.fld1.data).first()
        to_stop.complete = True
        db.session.commit()
        return redirect(url_for('streamings'))

    return render_template('streamings.html', title='Streamings', streamings=streamings.items, form2=form2, form=form, posts=posts.items, next_url=next_url, prev_url=prev_url, url_presidente=url_presidente, url_ministros=url_ministros,)

@app.route('/marianizer', methods=['GET', 'POST'])
@login_required
def marianizer():
    form = MarianizerForm()

    if form.submit.data and form.validate():
        videotitle = form.title.data
        tweeturl = form.tweet.data
        videoname = "video/" + "-".join([tweeturl.split("/")[-1], "1"]) + ".mp4"
        subprocess.run(['download-twitter-resources', '-c', 'twitter_secrets.json', '--video', '--tweet', tweeturl, ' video'], shell=False)
        subprocess.run(['python', 'mp42youtube.py', '--file', videoname, '--title', videotitle], shell=False)
        file1 = open('id.txt', 'r')
        video = ('https://www.youtube.com/watch?v=' + file1.read())
        return render_template('pass.html', video=video)

    return render_template('marianizer.html', title='Marianizer', form=form)

# @app.route('/marianizer', methods=['POST'])
# @login_required
# def getvalue():
#     tweeturl = request.form['tweeturl']
#     videotitle = request.form['title']
#     videoname = "-".join([tweeturl.split("/")[-1], "1"]) + ".mp4"
#     subprocess.run(['download-twitter-resources', '-c', 'twitter_secrets.json', '--video', '--tweet', tweeturl, ''], shell=True)
#     subprocess.call(['python', 'mp42youtube.py', '--file', videoname, '--title', videotitle], shell=True)
#     file1 = open('id.txt', 'r')
#     video = ('https://www.youtube.com/watch?v=' + file1.read())
#     return render_template('pass.html', video=video)