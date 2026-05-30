from flask import Flask, render_template, request, url_for, redirect, flash, abort, session
from .db import criar_conexao, inicializar_banco

app = Flask(__name__)
app.config['SECRET_KEY'] = '00000'

inicializar_banco()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' in session:
        return redirect(url_for('dash'))
    return render_template("cadastro.html")

@app.route('/cadastroBuracos')
def cadastro_buracos():
    if 'user' not in session:
        abort(401)
    return render_template('cadastroBuracos.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'user' in session:
        return redirect(url_for('dash'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not nome or not email or not senha:
            flash("Preencha todos os campos!", "error")
            return redirect(url_for('cadastro'))

        conexao = criar_conexao()
        resultado = conexao.execute("SELECT * FROM usuarios WHERE nome == ?", (nome,))
        user = resultado.fetchone()

        if not user:
            conexao.execute("INSERT INTO usuarios(nome, email,senha) VALUES (?,?,?)", (nome, email, senha))
            conexao.commit()
            conexao.close()
            return redirect(url_for('login'))
        
        else:
            flash('usuário existente')
            return redirect(url_for('cadastro'))

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'post'])
def login():
    if 'user' in session:
        return redirect(url_for('dash'))
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if not nome or not senha:
            flash("Preencha todos os campos!", "error")
            return redirect(url_for('login'))

        conexao = criar_conexao()

        resultado = conexao.execute("SELECT * FROM usuarios WHERE nome == ?", (nome,))
        user = resultado.fetchone()

        if user and user['nome'] == nome and user['senha'] == senha:
            session['user'] = nome
            session['id'] = user['id']
            return redirect(url_for('dash'))
        else:
            flash('usuário ou senha incorreto(s)')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/dash')
def dash():
    if 'user' in session:
        return render_template('dash.html', user = session['user'])
    abort(401)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    session.pop('id', None)
    return redirect(url_for('index'))

@app.errorhandler(404)
def error404(error):
    return render_template('error/error404.html'), 404

@app.errorhandler(401)
def error401(error):
    return render_template('error/error401.html'), 401

# Mecher a partir daqui para adicionar as funcionalidades dos buracos, OBS a tabela de buracos já foi criada no banco de dados

@app.route('/cadastrar_buraco', methods=['POST'])
def cadastrar_buraco():
    if 'user' not in session:
        abort(401)

    if not nova_rua or not novo_bairro:
        flash("Preencha todos os campos!", "error")
        return redirect(url_for('index'))
    

    nova_rua = request.form.get('rua')
    novo_bairro = request.form.get('bairro')
    nova_referencia = request.form.get('referencia')
    nova_gravidade = request.form.get('gravidade')

    
    novo_registro = {
        "rua": nova_rua,
        "bairro": novo_bairro,
        "referencia": nova_referencia,
        "gravidade": nova_gravidade
    }


    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO buracos (nome_rua,nome_bairro,nome_gravidade,referencial,usu_id) VALUES (?,?,?,?,?)", (novo_registro['rua'],novo_registro['bairro'],novo_registro['gravidade'],novo_registro['referencia'],session['id']))
    conexao.commit()
    cursor.execute("SELECT * FROM buracos WHERE usu_id = ?", (session['id'],))
    buracos = cursor.fetchall()
    conexao.close()

    
    return redirect(url_for('exibir_lista'))

@app.route('/lista', methods=['post', 'get'])
def exibir_lista():
    if 'user' not in session:
        abort(401)

    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM buracos WHERE usu_id = ?", (session['id'],))

    buracos = cursor.fetchall()
    conexao.close()

    return render_template('lista.html', buracos=buracos)

@app.route('/deletar/<int:id>')
def deletar(id):
    global lista_buracos
    
    nova_lista_buracos = []
    for buraco in lista_buracos:
        if buraco['id'] != id:
            nova_lista_buracos.append(buraco)
    
    lista_buracos = nova_lista_buracos

    for i, buraco in enumerate(lista_buracos):
        buraco['id'] = i + 1  
    
    flash("Relato removido e IDs reordenados.", "warning")
    return redirect(url_for('exibir_lista'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'user' not in session:
        abort(401)

    buraco_procurado = None

    for buraco in lista_buracos:
        if buraco['id'] == id:
            buraco_procurado = buraco
            break

    if buraco_procurado is None:
        abort(404)

    if request.method == 'POST':
        buraco_procurado['rua'] = request.form.get('rua')
        buraco_procurado['bairro'] = request.form.get('bairro')
        buraco_procurado['referencia'] = request.form.get('referencia')
        buraco_procurado['gravidade'] = request.form.get('gravidade')
        
        flash("Informações atualizadas!", "info")
        return redirect(url_for('exibir_lista'))

    return render_template('editar.html', buraco=buraco_procurado)
