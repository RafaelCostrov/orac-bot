from langchain.agents import AgentExecutor
from orquestrador.orquestrador import AgenteOrquestrador
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

app = Flask(__name__)
# CORS(app, resources={r"/orac-ia": {"origins": "http://10.10.10.47:5173"}})
CORS(app)

load_dotenv()
SENHA_API = os.getenv('SENHA_API')


@app.route("/orac-ia", methods=['POST'])
def main():
    try:
        pergunta = request.form.get("mensagem")
        nome_usuario = request.form.get("nome_usuario")
        email = request.form.get("email")
        senha = request.form.get("senha")
        arquivo = request.files.get("arquivo")

        if senha != SENHA_API:
            return jsonify({
                "erro": "Senha incorreta."
            }), 403

        if arquivo:
            nome_arquivo = arquivo.filename
            arquivo.save(nome_arquivo)
            pergunta += f"""
            Obs: O documento '{nome_arquivo}' foi anexado.

            # USE SE PRECISAR:
            resp: {nome_usuario}
            email: {email}
            """

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
    app.run(host="0.0.0.0", port=5000, debug=True)
