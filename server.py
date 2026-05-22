import sqlite3
import json
import os
import hashlib
import secrets
from datetime import datetime, date
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS

app = Flask(__name__, static_folder='public')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app, supports_credentials=True)

DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'atlas_toldos.db'))

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            perfil TEXT DEFAULT 'vendedor',
            ativo INTEGER DEFAULT 1,
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            email TEXT,
            cpf TEXT,
            endereco TEXT,
            bairro TEXT,
            cidade TEXT,
            cep TEXT,
            data_cadastro TEXT NOT NULL,
            data_instalacao TEXT,
            data_proxima_ligacao TEXT,
            status TEXT DEFAULT 'ativo',
            observacoes TEXT,
            sincronizado INTEGER DEFAULT 0,
            criado_por INTEGER,
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            numero TEXT NOT NULL,
            descricao TEXT NOT NULL,
            largura REAL,
            altura REAL,
            tipo_toldo TEXT,
            cor_tecido TEXT,
            cor_estrutura TEXT,
            mecanismo TEXT,
            valor_total REAL,
            status TEXT DEFAULT 'pendente',
            data_visita TEXT,
            vendedor TEXT,
            observacoes TEXT,
            criado_por INTEGER,
            criado_em TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        CREATE TABLE IF NOT EXISTS config (
            chave TEXT PRIMARY KEY,
            valor TEXT
        );

        INSERT OR IGNORE INTO config VALUES ('supabase_url', '');
        INSERT OR IGNORE INTO config VALUES ('supabase_key', '');
        INSERT OR IGNORE INTO config VALUES ('anos_recompra', '3');
    ''')

    # Criar admin padrão se não existir
    adm = conn.execute("SELECT id FROM usuarios WHERE email='admin@atlastoldos.com'").fetchone()
    if not adm:
        conn.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?)",
            ('Administrador', 'admin@atlastoldos.com', hash_senha('atlas2024'), 'admin')
        )
    conn.commit()
    conn.close()

init_db()

# ── MIDDLEWARE AUTH ────────────────────────────────────────────────────
def requer_login(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'erro': 'Não autenticado'}), 401
        return f(*args, **kwargs)
    return decorated

def requer_admin(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'erro': 'Não autenticado'}), 401
        if session.get('perfil') != 'admin':
            return jsonify({'erro': 'Acesso negado — requer perfil admin'}), 403
        return f(*args, **kwargs)
    return decorated

# ── AUTH ──────────────────────────────────────────────────────────────
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip().lower()
    senha = data.get('senha', '')
    conn = get_db()
    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE email=? AND ativo=1",
        (email,)
    ).fetchone()
    conn.close()
    if not usuario or usuario['senha_hash'] != hash_senha(senha):
        return jsonify({'erro': 'E-mail ou senha incorretos'}), 401
    session['usuario_id'] = usuario['id']
    session['nome'] = usuario['nome']
    session['perfil'] = usuario['perfil']
    return jsonify({
        'id': usuario['id'],
        'nome': usuario['nome'],
        'email': usuario['email'],
        'perfil': usuario['perfil']
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})

@app.route('/api/auth/me', methods=['GET'])
def me():
    if 'usuario_id' not in session:
        return jsonify({'autenticado': False}), 401
    return jsonify({
        'autenticado': True,
        'id': session['usuario_id'],
        'nome': session['nome'],
        'perfil': session['perfil']
    })

# ── USUÁRIOS (admin only) ─────────────────────────────────────────────
@app.route('/api/usuarios', methods=['GET'])
@requer_admin
def listar_usuarios():
    conn = get_db()
    usuarios = conn.execute("SELECT id, nome, email, perfil, ativo, criado_em FROM usuarios ORDER BY criado_em DESC").fetchall()
    conn.close()
    return jsonify([dict(u) for u in usuarios])

@app.route('/api/usuarios', methods=['POST'])
@requer_admin
def criar_usuario():
    data = request.json
    nome = data.get('nome', '').strip()
    email = data.get('email', '').strip().lower()
    senha = data.get('senha', '')
    perfil = data.get('perfil', 'vendedor')
    if not nome or not email or not senha:
        return jsonify({'erro': 'Nome, e-mail e senha são obrigatórios'}), 400
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?)",
            (nome, email, hash_senha(senha), perfil)
        )
        conn.commit()
        u = dict(conn.execute("SELECT id, nome, email, perfil, ativo, criado_em FROM usuarios WHERE id=?", (cursor.lastrowid,)).fetchone())
        conn.close()
        return jsonify(u), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'erro': 'Este e-mail já está cadastrado'}), 409

@app.route('/api/usuarios/<int:id>', methods=['PUT'])
@requer_admin
def atualizar_usuario(id):
    data = request.json
    conn = get_db()
    if data.get('senha'):
        conn.execute(
            "UPDATE usuarios SET nome=?, email=?, perfil=?, ativo=?, senha_hash=? WHERE id=?",
            (data['nome'], data['email'].lower(), data['perfil'], data.get('ativo', 1), hash_senha(data['senha']), id)
        )
    else:
        conn.execute(
            "UPDATE usuarios SET nome=?, email=?, perfil=?, ativo=? WHERE id=?",
            (data['nome'], data['email'].lower(), data['perfil'], data.get('ativo', 1), id)
        )
    conn.commit()
    u = dict(conn.execute("SELECT id, nome, email, perfil, ativo, criado_em FROM usuarios WHERE id=?", (id,)).fetchone())
    conn.close()
    return jsonify(u)

@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
@requer_admin
def deletar_usuario(id):
    if id == session.get('usuario_id'):
        return jsonify({'erro': 'Não é possível excluir o próprio usuário'}), 400
    conn = get_db()
    conn.execute("DELETE FROM usuarios WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── CLIENTES ──────────────────────────────────────────────────────────
@app.route('/api/clientes', methods=['GET'])
@requer_login
def listar_clientes():
    conn = get_db()
    busca = request.args.get('busca', '')
    status = request.args.get('status', '')
    query = "SELECT * FROM clientes WHERE 1=1"
    params = []
    if busca:
        query += " AND (nome LIKE ? OR telefone LIKE ? OR cpf LIKE ?)"
        params += [f'%{busca}%', f'%{busca}%', f'%{busca}%']
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY criado_em DESC"
    clientes = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(c) for c in clientes])

@app.route('/api/clientes', methods=['POST'])
@requer_login
def criar_cliente():
    data = request.json
    conn = get_db()
    data_cadastro = data.get('data_cadastro') or date.today().isoformat()
    data_base = data.get('data_instalacao') or data_cadastro
    try:
        dt = datetime.strptime(data_base, '%Y-%m-%d')
        anos = int(conn.execute("SELECT valor FROM config WHERE chave='anos_recompra'").fetchone()['valor'])
        proxima = dt.replace(year=dt.year + anos).isoformat()[:10]
    except:
        proxima = None
    cursor = conn.execute('''
        INSERT INTO clientes (nome, telefone, email, cpf, endereco, bairro, cidade, cep,
            data_cadastro, data_instalacao, data_proxima_ligacao, status, observacoes, criado_por)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['nome'], data['telefone'], data.get('email'), data.get('cpf'),
        data.get('endereco'), data.get('bairro'), data.get('cidade'), data.get('cep'),
        data_cadastro, data.get('data_instalacao'), proxima,
        data.get('status', 'ativo'), data.get('observacoes'), session.get('usuario_id')
    ))
    conn.commit()
    cliente_id = cursor.lastrowid
    cliente = dict(conn.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,)).fetchone())
    conn.close()
    return jsonify(cliente), 201

@app.route('/api/clientes/<int:id>', methods=['GET'])
@requer_login
def get_cliente(id):
    conn = get_db()
    cliente = conn.execute("SELECT * FROM clientes WHERE id=?", (id,)).fetchone()
    orcamentos = conn.execute("SELECT * FROM orcamentos WHERE cliente_id=? ORDER BY criado_em DESC", (id,)).fetchall()
    conn.close()
    if not cliente:
        return jsonify({'erro': 'Cliente não encontrado'}), 404
    result = dict(cliente)
    result['orcamentos'] = [dict(o) for o in orcamentos]
    return jsonify(result)

@app.route('/api/clientes/<int:id>', methods=['PUT'])
@requer_login
def atualizar_cliente(id):
    data = request.json
    conn = get_db()
    data_base = data.get('data_instalacao') or data.get('data_cadastro')
    try:
        dt = datetime.strptime(data_base, '%Y-%m-%d')
        anos = int(conn.execute("SELECT valor FROM config WHERE chave='anos_recompra'").fetchone()['valor'])
        proxima = dt.replace(year=dt.year + anos).isoformat()[:10]
    except:
        proxima = data.get('data_proxima_ligacao')
    conn.execute('''
        UPDATE clientes SET nome=?, telefone=?, email=?, cpf=?, endereco=?, bairro=?, cidade=?, cep=?,
            data_cadastro=?, data_instalacao=?, data_proxima_ligacao=?, status=?, observacoes=?, sincronizado=0
        WHERE id=?
    ''', (
        data['nome'], data['telefone'], data.get('email'), data.get('cpf'),
        data.get('endereco'), data.get('bairro'), data.get('cidade'), data.get('cep'),
        data.get('data_cadastro'), data.get('data_instalacao'), proxima,
        data.get('status', 'ativo'), data.get('observacoes'), id
    ))
    conn.commit()
    cliente = dict(conn.execute("SELECT * FROM clientes WHERE id=?", (id,)).fetchone())
    conn.close()
    return jsonify(cliente)

@app.route('/api/clientes/<int:id>', methods=['DELETE'])
@requer_login
def deletar_cliente(id):
    conn = get_db()
    conn.execute("DELETE FROM orcamentos WHERE cliente_id=?", (id,))
    conn.execute("DELETE FROM clientes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── ORÇAMENTOS ────────────────────────────────────────────────────────
@app.route('/api/orcamentos', methods=['POST'])
@requer_login
def criar_orcamento():
    data = request.json
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) as c FROM orcamentos").fetchone()['c']
    numero = f"ORC-{date.today().year}-{count+1:04d}"
    cursor = conn.execute('''
        INSERT INTO orcamentos (cliente_id, numero, descricao, largura, altura, tipo_toldo,
            cor_tecido, cor_estrutura, mecanismo, valor_total, status, data_visita, vendedor, observacoes, criado_por)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['cliente_id'], numero, data['descricao'],
        data.get('largura'), data.get('altura'), data.get('tipo_toldo'),
        data.get('cor_tecido'), data.get('cor_estrutura'), data.get('mecanismo'),
        data.get('valor_total'), data.get('status', 'pendente'),
        data.get('data_visita'), data.get('vendedor'), data.get('observacoes'),
        session.get('usuario_id')
    ))
    conn.commit()
    orc = dict(conn.execute("SELECT * FROM orcamentos WHERE id=?", (cursor.lastrowid,)).fetchone())
    conn.close()
    return jsonify(orc), 201

@app.route('/api/orcamentos/<int:id>', methods=['PUT'])
@requer_login
def atualizar_orcamento(id):
    data = request.json
    conn = get_db()
    conn.execute('''
        UPDATE orcamentos SET descricao=?, largura=?, altura=?, tipo_toldo=?,
            cor_tecido=?, cor_estrutura=?, mecanismo=?, valor_total=?, status=?,
            data_visita=?, vendedor=?, observacoes=?
        WHERE id=?
    ''', (
        data['descricao'], data.get('largura'), data.get('altura'), data.get('tipo_toldo'),
        data.get('cor_tecido'), data.get('cor_estrutura'), data.get('mecanismo'),
        data.get('valor_total'), data.get('status', 'pendente'),
        data.get('data_visita'), data.get('vendedor'), data.get('observacoes'), id
    ))
    conn.commit()
    orc = dict(conn.execute("SELECT * FROM orcamentos WHERE id=?", (id,)).fetchone())
    conn.close()
    return jsonify(orc)

@app.route('/api/orcamentos/<int:id>', methods=['DELETE'])
@requer_login
def deletar_orcamento(id):
    conn = get_db()
    conn.execute("DELETE FROM orcamentos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── DASHBOARD ─────────────────────────────────────────────────────────
@app.route('/api/dashboard', methods=['GET'])
@requer_login
def dashboard():
    conn = get_db()
    hoje = date.today().isoformat()
    mes_atual = hoje[:7]
    total_clientes = conn.execute("SELECT COUNT(*) as c FROM clientes WHERE status='ativo'").fetchone()['c']
    ligacoes_mes = conn.execute(
        "SELECT COUNT(*) as c FROM clientes WHERE data_proxima_ligacao LIKE ?", (f'{mes_atual}%',)
    ).fetchone()['c']
    orcamentos_pendentes = conn.execute(
        "SELECT COUNT(*) as c FROM orcamentos WHERE status='pendente'"
    ).fetchone()['c']
    valor_orcamentos = conn.execute(
        "SELECT COALESCE(SUM(valor_total),0) as v FROM orcamentos WHERE status='aprovado'"
    ).fetchone()['v']
    proximas_ligacoes = conn.execute('''
        SELECT id, nome, telefone, data_proxima_ligacao
        FROM clientes
        WHERE data_proxima_ligacao >= ? AND status='ativo'
        ORDER BY data_proxima_ligacao ASC
        LIMIT 10
    ''', (hoje,)).fetchall()
    conn.close()
    return jsonify({
        'total_clientes': total_clientes,
        'ligacoes_mes': ligacoes_mes,
        'orcamentos_pendentes': orcamentos_pendentes,
        'valor_orcamentos': valor_orcamentos,
        'proximas_ligacoes': [dict(r) for r in proximas_ligacoes]
    })

# ── CONFIG ────────────────────────────────────────────────────────────
@app.route('/api/config', methods=['GET'])
@requer_login
def get_config():
    conn = get_db()
    rows = conn.execute("SELECT * FROM config").fetchall()
    conn.close()
    cfg = {r['chave']: r['valor'] for r in rows}
    cfg.pop('supabase_key', None)
    return jsonify(cfg)

@app.route('/api/config', methods=['PUT'])
@requer_admin
def salvar_config():
    data = request.json
    conn = get_db()
    for k, v in data.items():
        conn.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", (k, v))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── STATIC / FRONTEND ─────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  ATLAS TOLDOS - Sistema de Gestão")
    print("  Acesse: http://localhost:5000")
    print("  Admin padrão: admin@atlastoldos.com / atlas2024")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
