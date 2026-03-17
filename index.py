from flask import Flask, request, render_template, redirect, url_for
import oracledb
import os

app = Flask(__name__)

def get_connection():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    dsn_string = os.getenv("DB_DSN")

    if user and password and dsn_string:
        return oracledb.connect(user=user, password=password, dsn=dsn_string)

    return oracledb.connect(
        user=user,
        password=passord,
        dsn=dsn_string,
    )


@app.route("/")
def home():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_ativo, nome, setor, preco_base, estoque FROM tb_ativos_galacticos")
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", produtos=produtos)


@app.route("/processar", methods=["POST"])
def processar():
    evento = request.form["evento"]
    setor = request.form["setor"]

    conn = get_connection()
    cursor = conn.cursor()

    if evento == "RADIACAO":
        valor_str = request.form["valor"].strip().replace(",", ".")
        valor = float(valor_str)
        plsql = """
        DECLARE
            v_setor VARCHAR2(50) := :setor;
            v_valor NUMBER := :valor;
            v_novo_preco NUMBER;
            CURSOR c_produtos IS
                SELECT id_ativo, preco_base FROM tb_ativos_galacticos WHERE setor = v_setor;
        BEGIN
            FOR r IN c_produtos LOOP
                v_novo_preco := r.preco_base * (1 + v_valor / 100);
                UPDATE tb_ativos_galacticos SET preco_base = v_novo_preco WHERE id_ativo = r.id_ativo;
            END LOOP;
            COMMIT;
        END;
        """
        cursor.execute(plsql, {"setor": setor, "valor": valor})

    elif evento == "DESCOBERTA_MINA":
        estoque_adicionar = int(request.form["estoque_adicionar"].strip())
        if estoque_adicionar <= 200:
            reducao = 10
        elif estoque_adicionar <= 500:
            reducao = 20
        else:
            reducao = 30
        plsql = """
        DECLARE
            v_setor VARCHAR2(50) := :setor;
            v_estoque NUMBER := :estoque;
            v_reducao NUMBER := :reducao;
            v_novo_preco NUMBER;
            CURSOR c_produtos IS
                SELECT id_ativo, preco_base, estoque FROM tb_ativos_galacticos WHERE setor = v_setor;
        BEGIN
            FOR r IN c_produtos LOOP
                v_novo_preco := r.preco_base * (1 - v_reducao / 100);
                UPDATE tb_ativos_galacticos SET preco_base = v_novo_preco, estoque = r.estoque + v_estoque WHERE id_ativo = r.id_ativo;
            END LOOP;
            COMMIT;
        END;
        """
        cursor.execute(plsql, {"setor": setor, "estoque": estoque_adicionar, "reducao": reducao})

    cursor.close()
    conn.close()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
