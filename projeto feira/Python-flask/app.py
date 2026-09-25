# ============================================================
# IMPORTS
# ============================================================

# Flask cria a aplicação.
# render_template carrega os arquivos HTML.
# request recebe dados enviados pelo usuário.
# redirect redireciona para outra rota.
# url_for gera a URL de uma rota.
from flask import Flask, render_template, request, redirect, url_for

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


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == "__main__":

    app.run(debug=True)
# ============================================================
# GUIA PARA CONTINUARMOS O BACK-END DO PROJETO
# ============================================================

# Pessoal, até aqui nós já fizemos a estrutura inicial do nosso
# back-end utilizando Flask e já conseguimos conectar o Python
# com as páginas HTML do nosso projeto.
#
# Os dados dos sebos que estão neste arquivo são apenas dados
# temporários e fictícios que usamos para testar o funcionamento.
# Eles serão substituídos pelos dados reais do banco de dados.
#
# A partir daqui, precisamos continuar o desenvolvimento juntos
# e dividir as próximas etapas entre a equipe.
#
#
# PRÓXIMOS PASSOS DO BACK-END:
#
# 1 - CONECTAR O PYTHON AO MYSQL               (__________________________FEITO_________________________)
#
# Primeiro precisamos fazer a conexão entre o Flask e o banco
# de dados MySQL que a equipe está desenvolvendo.
#
# Depois da conexão, não vamos mais precisar deixar todos os
# dados dos sebos escritos diretamente nesta lista do Python.
#
#
# 2 - CRIAR E ORGANIZAR AS TABELAS DO BANCO (__________________________FEITO_________________________)
#
# Precisamos definir junto com a equipe quais informações serão
# armazenadas no banco de dados.
#
# Por exemplo:
# - Sebos
# - Usuários
# - Avaliações
# - Livros
# - Categorias
#
# A estrutura final deve ser decidida junto com a modelagem
# do banco de dados que a equipe está fazendo.
#
#
# 3 - BUSCAR OS SEBOS NO BANCO DE DADOS  (__________________________incompleto_________________________)
#
# Depois de conectar o MySQL, precisamos substituir os dados
# fictícios da variável "sebos" por dados vindos do banco.
#
# Assim, quando o usuário pesquisar, o Python poderá consultar
# o banco e mostrar os sebos cadastrados de verdade.
#
#
# 4 - MELHORAR A PESQUISA
#
# Atualmente a rota "/pesquisar" recebe o termo pesquisado,
# mas ainda estamos mostrando nossa lista temporária.
#
# Precisamos fazer a pesquisa realmente verificar os dados
# cadastrados no banco.
#
# Também podemos pensar em filtros, como localização, avaliação,
# tipo de livro ou outras informações que decidirmos colocar
# no projeto.
#
#
# 5 - CADASTRO E LOGIN  (__________________________FEITO_________________________)
#
# Precisamos desenvolver a parte lógica do cadastro e do login.
#
# O usuário deverá poder criar uma conta e depois entrar no
# sistema utilizando seus dados.
#
# Essas informações deverão ser armazenadas no banco de dados.
#
#
# 6 - ÁREA DO USUÁRIO
#
# Depois do login, precisamos criar a lógica da área do usuário.
#
# Nela poderemos mostrar informações do usuário e, dependendo
# do que decidirmos para o projeto, permitir que ele veja ou
# altere seus dados e suas avaliações.
#
#
# 7 - AVALIAÇÕES DOS SEBOS
#
# Uma das principais funcionalidades do nosso projeto será
# permitir que os usuários avaliem os sebos.
#
# Precisamos criar a lógica para:
# - receber a avaliação;
# - identificar o usuário;
# - identificar o sebo;
# - salvar a avaliação no banco;
# - mostrar as avaliações na página do sebo.
#
#
# 8 - DETALHES DOS SEBOS
#
# A rota "/sebo/<int:id>" já foi criada e atualmente funciona
# utilizando nossos dados temporários.
#
# Depois da integração com o banco, essa rota deverá buscar
# o sebo pelo ID diretamente no MySQL.
#
#
# 9 - VALIDAR OS DADOS
#
# Precisamos verificar os dados enviados pelos usuários antes
# de salvar qualquer informação no banco.
#
# Por exemplo, verificar se os campos obrigatórios foram
# preenchidos corretamente.
#
#
# 10 - TESTAR TODAS AS FUNCIONALIDADES   (__________________________incompleto_________________________)
#
# Depois que as funcionalidades forem desenvolvidas, precisamos
# testar cada uma delas individualmente.
#
# Vamos verificar principalmente:
# - cadastro;
# - login;
# - pesquisa;
# - detalhes do sebo;
# - avaliações;
# - navegação entre as páginas;
# - possíveis erros.
#
#
# 11 - ORGANIZAR E CORRIGIR O CÓDIGO
#
# Depois que tudo estiver funcionando, precisamos revisar o
# código, organizar os arquivos e corrigir possíveis problemas.
#
# Também devemos manter os comentários importantes para que
# todos da equipe consigam entender o que foi feito.
#
#
# 12 - INTEGRAR TUDO
#
# No final, precisamos garantir que:
#
# HTML/CSS
#     ↓
# Flask / Python
#     ↓
# MySQL
#
# estejam funcionando juntos.
#
# O usuário deverá conseguir utilizar o site normalmente,
# enquanto o Python ficará responsável pela lógica e o MySQL
# pelo armazenamento dos dados.
#
#
# OBJETIVO FINAL
#
# Nosso objetivo é entregar um site funcional sobre os sebos
# de Londrina, permitindo que o usuário encontre sebos e veja
# qual deles atende melhor às suas necessidades.
#
# O front-end já está estruturado.
# O Flask já está funcionando.
# Agora precisamos construir o restante do back-end juntos,
# integrar o banco de dados e testar o produto final.
#
# Vamos fazendo cada etapa juntos para que todo mundo da equipe
# entenda uma parte do projeto e consiga ajudar no desenvolvimento.
# ============================================================
