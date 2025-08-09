from langchain.agents import AgentExecutor
from orquestrador.orquestrador import AgenteOrquestrador
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/orac-ia": {"origins": "http://localhost:5173"}})


@app.route("/orac-ia", methods=['POST'])
def main():
    try:
        pergunta = request.form.get("mensagem")
        nome_usuario = request.form.get("nome_usuario")
        email = request.form.get("email")
        arquivo = request.files.get("arquivo")
        print(f"{nome_usuario} - {email}")

        if arquivo:
            nome_arquivo = arquivo.filename
            arquivo.save(nome_arquivo)
            pergunta += f"""
            Obs: O documento '{nome_arquivo}' foi anexado.

            # USE SE PRECISAR:
            resp: {nome_usuario}
            email: {email}
            """
        else:
            print("Nenhum arquivo recebido.")

        pergunta += f"\n\nLembrando que você irá responder em um chat **HTML**, então não use markdown para formatação, se quiser use elementos HTML\n"

        agente = AgenteOrquestrador()
        orquestrador = AgentExecutor(
            agent=agente.agente,
            tools=agente.tools,
            verbose=True,
            handle_parsing_errors=True
        )

        resposta = orquestrador.invoke({"input": pergunta})
        if arquivo:
            os.remove(nome_arquivo)
        return jsonify({
            "resposta": resposta
        })
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({
            "erro": "Ocorreu um erro! Tente novamente"
        }), 400


if __name__ == "__main__":
    app.run()
