from flask import Flask, render_template, request, url_for, redirect, flash, abort

app = Flask(__name__)
app.secret_key = '00000'
user = None

lista_buracos = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if not user:
        return redirect(url_for('cadastro'))
    return render_template("index.html")

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if user:
        return redirect(url_for('dash'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    if user:
        return redirect(url_for('dash'))
    user = request.form.get('nome')
    senha = request.form.get('senha')
    flash('Bem vindo a RuaHole', 'success')
    return redirect(url_for('dash'))

@app.route('/dash')
def dash():
    if not user:
        abort(401)
    return render_template('dash.html', user = user)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global user
    user = None
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('index'))

@app.errorhandler(404)
def error404(error):
    return render_template('error/error404.html'), 404

@app.errorhandler(401)
def error401(error):
    return render_template('error/error401.html'), 401

@app.route('/cadastrar_buraco', methods=['POST'])
def cadastrar_buraco():
    global lista_buracos

    if not user:
        abort(401)

    nova_rua = request.form.get('rua')
    novo_bairro = request.form.get('bairro')
    nova_referencia = request.form.get('referencia')
    nova_gravidade = request.form.get('gravidade')

    if lista_buracos:
        novo_id = lista_buracos[-1]['id'] + 1
    else:
        novo_id = 1
    
    novo_registro = {
        "id": novo_id,
        "rua": nova_rua,
        "bairro": novo_bairro,
        "referencia": nova_referencia,
        "gravidade": nova_gravidade
    }

    if not nova_rua or not novo_bairro:
        flash("Preencha todos os campos!", "error")
        return redirect(url_for('index'))
    
    lista_buracos.append(novo_registro)
    flash("Buraco relatado com sucesso!", "success")
    return redirect(url_for('exibir_lista'))

@app.route('/lista')
def exibir_lista():
    if not user:
        abort(401)
    return render_template('lista.html', buracos = lista_buracos)

@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    global lista_buracos
    
    if not user:
        abort(401)

    lista_buracos = [buraco for buraco in lista_buracos if buraco['id'] != id]
    
    flash("Relato removido e IDs reordenados.", "warning")
    return redirect(url_for('exibir_lista'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if not user:
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
