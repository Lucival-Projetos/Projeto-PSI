from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)
user = None

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/cadastro')
def cadastrar():
    if user:
        return redirect(url_for('dash'))
    return render_template('cadastro.html')

@app.route('/login', methods=['post'])
def login():
    global user
    if user:
        return redirect(url_for('dash'))
    user = request.form.get('nome')
    senha = request.form.get('senha')
    return redirect(url_for('dash'))

@app.route('/dash')
def dash():
    if not user:
        return redirect(url_for('cadastro'))
    return render_template('dash.html', user = user)

@app.route('/logout', methods=['post'])
def logout():
    global user
    user = None
    return redirect(url_for('index'))