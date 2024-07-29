# 웹 요청을 처리하는 라우트
from flask import render_template, redirect, url_for, request
from .database import db

def init_routes(app):

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            # 인증 로직
            return redirect(url_for('dashboard'))
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        users = db.get_collection('users').find()
        return render_template('dashboard.html', users=users)
