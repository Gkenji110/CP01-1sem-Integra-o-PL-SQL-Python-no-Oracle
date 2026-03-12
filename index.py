from flask import Flask, request, render_template, redirect, url_for
import oracledb
import os

app = Flask(__name__)

def get_connection():
    
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    dsn_string = os.getenv("DB_DSN")

    conn = oracledb.connect(
        user=user,
        password=password,
        dsn=dsn_string
    )

    return conn


@app.route("/")
def home():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_ativo, nome, setor, preco_base, estoque
        FROM tb_ativos_galacticos
    """)

    produtos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", produtos=produtos)


@app.route("/processar", methods=["POST"])
def processar():

    evento = request.form["evento"]
    setor = request.form["setor"]
    valor_str = request.form["valor"].strip().replace(",", ".")
    valor = float(valor_str)

    conn = get_connection()
    cursor = conn.cursor()

    plsql = """
    DECLARE

        v_evento VARCHAR2(50) := :evento;
        v_setor VARCHAR2(50) := :setor;
        v_valor NUMBER := :valor;

        v_novo_preco NUMBER;

        CURSOR c_produtos IS
            SELECT id_ativo, preco_base
            FROM tb_ativos_galacticos
            WHERE setor = v_setor;

    BEGIN

        FOR r IN c_produtos LOOP

            v_novo_preco := r.preco_base;

            IF v_evento = 'RADIACAO' THEN
                v_novo_preco := r.preco_base * (1 + v_valor/100);

            ELSIF v_evento = 'CRISE' THEN
                v_novo_preco := r.preco_base * (1 - v_valor/100);
            END IF;

            UPDATE tb_ativos_galacticos
            SET preco_base = v_novo_preco
            WHERE id_ativo = r.id_ativo;

        END LOOP;

        COMMIT;

    END;
    """

    cursor.execute(plsql, {
        "evento": evento,
        "setor": setor,
        "valor": valor
    })

    cursor.close()
    conn.close()

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)