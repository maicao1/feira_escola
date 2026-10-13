
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
# Biblioteca para conexão com MySQL.
import mysql.connector


# ============================================================
# CRIAÇÃO DA APLICAÇÃO
# ============================================================

app = Flask(__name__)


# ============================================================
# CONFIGURAÇÃO DO MYSQL
# ============================================================

bd_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'escola',
    'database': 'feiraCiencias',
    'ssl_disabled': True
}


# ============================================================
# FUNÇÃO DE ACESSO AOS DADOS
# ============================================================

def buscar_sebos():

    try:
        conexao = mysql.connector.connect(**bd_config)

        curso = conexao.cursor(dictionary=True)

        curso.execute("SELECT * FROM dadosSebos")

        sebos = curso.fetchall()

        curso.close()
        conexao.close()

        return sebos

    except mysql.connector.Error as err:
        print(f"Erro ao buscar sebos: {err}")
        return []


# ============================================================
# PÁGINA INICIAL
# ============================================================

@app.route("/")
def inicio():

    try:

        conexao = mysql.connector.connect(**bd_config)

        curso = conexao.cursor(dictionary=True)

        # Busca todos os sebos cadastrados
        curso.execute("SELECT * FROM dadosSebos")

        lista_sebos = curso.fetchall()

        curso.close()
        conexao.close()

        return render_template(
            "index.html",
            sebos=lista_sebos
        )

    except mysql.connector.Error as err:

        return f"Erro ao carregar a tabela: {err}"


# ============================================================
# SOBRE O PROJETO
# ============================================================

@app.route("/sobre")
def sobre():

    return render_template("sobre.html")


# ============================================================
# CADASTRAR SEBO
# ============================================================

@app.route("/cadastrar", methods=["POST"])
def criar_cadastro():

    try:

        # ----------------------------------------------------
        # RECEBE OS DADOS DO FORMULÁRIO
        # ----------------------------------------------------

        identificacao = request.form["id"]
        nome = request.form["nome"]
        localizacao = request.form["localizacao"]
        avaliacao = request.form["avaliacao"]
        descricao = request.form["descricao"]
        telefone = request.form["telefone"]
        horario = request.form["horario"]
        endereco = request.form["endereco"]


        # ----------------------------------------------------
        # CONEXÃO COM O BANCO
        # ----------------------------------------------------

        conexao = mysql.connector.connect(**bd_config)

        curso = conexao.cursor()


        # ----------------------------------------------------
        # INSERE O SEBO
        # ----------------------------------------------------

        query = """
            INSERT INTO dadosSebos
            (
                id,
                nome,
                localizacao,
                avaliacao,
                descricao,
                telefone,
                horario,
                endereco
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        curso.execute(
            query,
            (
                identificacao,
                nome,
                localizacao,
                avaliacao,
                descricao,
                telefone,
                horario,
                endereco
            )
        )


        # Salva a alteração no banco
        conexao.commit()


        # Fecha conexão
        curso.close()
        conexao.close()


        # Volta para a página inicial
        return redirect(url_for("inicio"))


    except mysql.connector.Error as err:

        return f"Erro ao gravar no banco: {err}"


# ============================================================
# EXCLUIR SEBO
# ============================================================

@app.route("/excluir/<int:id>")
def excluir(id):

    try:

        conexao = mysql.connector.connect(**bd_config)

        curso = conexao.cursor()


        # ----------------------------------------------------
        # EXCLUI O SEBO PELO ID
        # ----------------------------------------------------

        curso.execute(
            "DELETE FROM dadosSebos WHERE id = %s",
            (id,)
        )


        # Salva a alteração
        conexao.commit()


        curso.close()
        conexao.close()


        # Volta para a página inicial
        return redirect(url_for("inicio"))


    except mysql.connector.Error as err:

        return f"Erro ao deletar: {err}"


# ============================================================
# PESQUISA
# ============================================================

@app.route("/pesquisar")
def pesquisar():

    # --------------------------------------------------------
    # RECEBE O TERMO PESQUISADO
    # --------------------------------------------------------

    termo = request.args.get(
        "busca",
        ""
    )


    # --------------------------------------------------------
    # VALIDAÇÃO BÁSICA
    # --------------------------------------------------------

    LIMITE_CARACTERES_BUSCA = 100

    termo = termo.strip()[:LIMITE_CARACTERES_BUSCA]


    # --------------------------------------------------------
    # PESQUISA NO MYSQL
    # --------------------------------------------------------

    try:

        conexao = mysql.connector.connect(**bd_config)

        curso = conexao.cursor(dictionary=True)


        # O MySQL fará a pesquisa.
        #
        # Procuramos o termo em:
        # - nome
        # - localização
        # - descrição

        query = """
            SELECT *
            FROM dadosSebos
            WHERE nome LIKE %s
            OR localizacao LIKE %s
            OR descricao LIKE %s
        """


        busca = "%" + termo + "%"


        curso.execute(
            query,
            (
                busca,
                busca,
                busca
            )
        )


        resultados = curso.fetchall()


        curso.close()
        conexao.close()


        # ----------------------------------------------------
        # TRATAMENTO DA PESQUISA
        # ----------------------------------------------------

        mensagem = None


        # Pesquisa vazia
        if termo == "":

            resultados = []

            mensagem = "Digite um termo para pesquisar."


        # Nenhum resultado
        elif len(resultados) == 0:

            mensagem = f'Nenhum sebo encontrado para "{termo}".'


        # ----------------------------------------------------
        # ENVIA PARA O HTML
        # ----------------------------------------------------

        return render_template(
            "resultado.html",
            termo=termo,
            sebos=resultados,
            mensagem=mensagem
        )


    except mysql.connector.Error as err:

        return f"Erro ao pesquisar: {err}"


# ============================================================
# PÁGINA INDIVIDUAL DO SEBO
# ============================================================

@app.route("/sebo/<int:id>")
def detalhes_sebo(id):

    # --------------------------------------------------------
    # VALIDAÇÃO DO ID
    # --------------------------------------------------------

    if id <= 0:

        return "ID inválido", 404


    try:

        conexao = mysql.connector.connect(**bd_config)

        curso = conexao.cursor(dictionary=True)


        # ----------------------------------------------------
        # PROCURA O SEBO PELO ID
        # ----------------------------------------------------

        curso.execute(
            """
            SELECT *
            FROM dadosSebos
            WHERE id = %s
            """,
            (id,)
        )


        sebo_encontrado = curso.fetchone()


        curso.close()
        conexao.close()


        # ----------------------------------------------------
        # SE NÃO EXISTIR
        # ----------------------------------------------------

        if sebo_encontrado is None:

            return "Sebo não encontrado", 404


        # ----------------------------------------------------
        # ENVIA PARA O HTML
        # ----------------------------------------------------

        return render_template(
            "sebo.html",
            sebo=sebo_encontrado
        )


    except mysql.connector.Error as err:

        return f"Erro ao carregar sebo: {err}"

//


# ============================================================
# CADASTRO DE USUÁRIOS
# ============================================================

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro_usuario():

    if request.method == "GET":
        return render_template("cadastro.html")

    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip().lower()
    senha = request.form.get("senha", "")
    confirmar_senha = request.form.get("confirmar_senha", "")

    if not nome or not email or not senha or not confirmar_senha:
        return "Preencha todos os campos!", 400

    if senha != confirmar_senha:
        return "As senhas não coincidem!", 400

    senha_hash = generate_password_hash(senha)

    conexao = None
    curso = None

    try:
        conexao = mysql.connector.connect(**bd_config)
        curso = conexao.cursor()

        query = """
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (%s, %s, %s)
        """

        curso.execute(query, (nome, email, senha_hash))
        conexao.commit()

        return redirect(url_for("pagina_login"))

    except mysql.connector.IntegrityError:
        return "Este e-mail já está cadastrado.", 409

    except mysql.connector.Error as err:
        app.logger.error("Erro ao cadastrar usuário: %s", err)
        return "Não foi possível concluir o cadastro.", 500

    finally:
        if curso is not None:
            curso.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()


# ============================================================
# PÁGINA DE LOGIN
# ============================================================

@app.route("/login")
def pagina_login():
    return render_template("login.html")


# ============================================================
# INICIAR SERVIDOR
# ============================================================
//


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro_usuario():

    if request.method == "GET":
        return render_template("cadastro.html")

    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip().lower()
    senha = request.form.get("senha", "")
    confirmar_senha = request.form.get("confirmar_senha", "")

    if not nome or not email or not senha or not confirmar_senha:
        return "Preencha todos os campos!", 400

    if senha != confirmar_senha:
        return "As senhas não coincidem!", 400

    if len(senha) < 8:
        return "A senha deve ter pelo menos 8 caracteres.", 400

    senha_hash = generate_password_hash(senha)

    conexao = None
    curso = None

    try:
        conexao = mysql.connector.connect(**bd_config)
        curso = conexao.cursor()

        curso.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (%s, %s, %s)
            """,
            (nome, email, senha_hash)
        )

        conexao.commit()

        return redirect(url_for("pagina_login"))

    except mysql.connector.IntegrityError:
        return "Este e-mail já está cadastrado.", 409

    except mysql.connector.Error:
        app.logger.exception("Erro ao cadastrar usuário")
        return "Não foi possível concluir o cadastro.", 500

    finally:
        if curso is not None:
            curso.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()


@app.route("/login")
def pagina_login():
    return render_template("login.html")


//
if __name__ == "__main__":

    app.run(debug=True)
