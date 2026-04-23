from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)
user = None

@app.route('/', methods=['get', 'post'])
def index():
    if not user:
        return redirect(url_for('cadastro'))
    return render_template("index.html")

@app.route('/cadastro', methods=['get', 'post'])
def cadastro():
    if user:
        return redirect(url_for('dash'))
    return render_template('cadastro.html')

@app.route('/login', methods=['get', 'post'])
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

@app.route('/logout', methods=['get', 'post'])
def logout():
    global user
    user = None
    return redirect(url_for('index'))