from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)
IMAGES_FOLDER = "static/images"
CONTROLE_CSV = "controle_crachas.csv"

def carregar_controle():
    if os.path.exists(CONTROLE_CSV):
        df = pd.read_csv(CONTROLE_CSV)
    else:
        df = pd.DataFrame(columns=["Arquivo", "Data_criacao", "Refeitos"])
    return df

@app.route("/", methods=["GET", "POST"])
def index():
    df = carregar_controle()
    search_query = request.args.get("q", "").lower()  # captura pesquisa

    # Adiciona nova data de refazer (manual)
    if request.method == "POST":
        arquivo = request.form["arquivo"]
        nova_data = request.form["nova_data"]
        if arquivo in df["Arquivo"].values:
            idx = df[df["Arquivo"] == arquivo].index[0]
            refeitos = df.at[idx, "Refeitos"]
            lista_refeitos = [] if pd.isna(refeitos) else refeitos.split(";")
            if nova_data not in lista_refeitos:
                lista_refeitos.append(nova_data)
            df.at[idx, "Refeitos"] = ";".join(lista_refeitos)
            df.to_csv(CONTROLE_CSV, index=False)
        return redirect(url_for("index", q=search_query))

    imagens = []
    for f in os.listdir(IMAGES_FOLDER):
        if f.lower().endswith((".jpg", ".png", ".jpeg")):
            if search_query and search_query not in f.lower():
                continue  # ignora se não bate com pesquisa

            caminho = os.path.join(IMAGES_FOLDER, f)
            if f in df["Arquivo"].values:
                idx = df[df["Arquivo"] == f].index[0]
                # Preenche Data_criacao se estiver vazia
                if pd.isna(df.at[idx, "Data_criacao"]) or df.at[idx, "Data_criacao"] == "":
                    data_criacao = datetime.fromtimestamp(os.path.getmtime(caminho)).strftime("%d/%m/%Y")
                    df.at[idx, "Data_criacao"] = data_criacao
                    df.to_csv(CONTROLE_CSV, index=False)
                else:
                    data_criacao = df.at[idx, "Data_criacao"]
                refeitos = df.at[idx, "Refeitos"]
            else:
                data_criacao = datetime.fromtimestamp(os.path.getmtime(caminho)).strftime("%d/%m/%Y")
                refeitos = ""
                df = pd.concat([df, pd.DataFrame([{
                    "Arquivo": f,
                    "Data_criacao": data_criacao,
                    "Refeitos": ""
                }])], ignore_index=True)
                df.to_csv(CONTROLE_CSV, index=False)

            imagens.append({
                "nome": f,
                "data_criacao": data_criacao,
                "refeitos": refeitos
            })

    return render_template("index.html", imagens=imagens, search_query=search_query)

if __name__ == "__main__":
    app.run(debug=True)
