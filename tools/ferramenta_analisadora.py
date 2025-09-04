from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from retuns_models.detalhes_extrato import Tabela
from auxiliares.my_models import GEMINI_FLASH, GEMINI_PRO
from auxiliares.my_keys import GEMINI_API_KEY
from auxiliares.my_helper import pdf_to_base64_images
from time import sleep
from google_services.envio_drive import salvar_drive
from google_services.envio_email import enviar
import ast
import json
import os
import time


class FerramentaAnalisadora(BaseTool):
    name: str = "Ferramenta Analisadora de Extratos"
    description: str = """
    Utilize essa ferramenta sempre que for solicitado que você extraia informações de um extrato.
    Você deve verificar o .pdf que for mandado para você, extraindo todas as informações que tiver presente no extrato.
    
    # Entradas Requiridas:
    - 'nome_pdf' (str): Nome do extrato que foi anexado, com extensão PDF.
    - 'email' (str): Email para o qual o resultado será enviado.
    - 'resp' (str): Nome da pessoa responsável que solicitou a análise
    
    **Não** solicitar ao usuário email e resp, o próprio frontend vai mandar essas duas informações.
    
    Ao explicar a ferramenta para alguém, peça apenas o arquivo anexado, o nome virá para você na requisição. E sempre procure textos curtos para descrever.
    
    Exemplo: {
        "nome_pdf": "CAIXA THT 02.24.pdf",
        "email": "usuario@dominio.com",
        "resp": "João da Silva"
        }
    """
    return_direct: bool = True

    def _run(self, acao):
        acao = ast.literal_eval(acao)
        caminho_pdf = acao.get("nome_pdf", "")
        email_destino = acao.get("email", "")
        responsavel = acao.get("resp", "")

        llm = ChatGoogleGenerativeAI(
            api_key=GEMINI_API_KEY,
            model=GEMINI_FLASH
        )

        imagem_extrato = pdf_to_base64_images(f"{caminho_pdf}")

        template_analisador = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    Assuma que você é um extrato de informações de extratos.
                    A sua tarefa principal consiste em analisar o extrato, extrair todas as informações que estão nele e organizar **todas as transações** em formato de tabela, como se fosse para importar
                    para excel.
                    
                    # REGRAS OBRIGATORIAS
                    - Se encontrar uma tabela, não retorne os dados como descritivo, mas sim como se fosse uma tabela, 
                    onde as colunas são separadas por "|", inclusive com os cabeçalhos.
                    - Se o cabecalho/linha de valores possuir (x) campos, você deve colocar apenas (x-1) "|" para dividir, assim como as células, não 
                    colocando na extremidade direita. 
                    -  Procure por um título que descreva a tabela que encontrou. Algo como "Conta Corrente" ou "Poupança", indicando 
                    a tabela que encontrou. Caso não encontre isso, mas tenha um "Movimentação" ou algo assim
                    pode retornar. Se não possuir nada acima, **não** retorne nada como título.
                    - Se encontrar alguma página que não possui tabelas, **retorne "Não há tabelas"** 
                    - Qualquer célula vazia encontrada, deve continuar vazia, não coloque "-" para mostrar que estar vazio.
                    - Lembrar-se que alguns bancos abreviam a palavra "SALDO" para "SDO", então se começar tanto com "SDO" quanto "SALDO"
                    considerar para o campo de saldo.
                    - Sempre que um valor vier com um sinal negativo "-" tanto do lado direito do número, quanto no esquerdo 
                    (MESMO SE TIVER R$ ENTRE O SINAL E O VALOR), **considerar** como crédito.
                    - Células conjuntas as vezes vem separadas em duas linhas, porém sem uma divisão de linhas entre elas. Sempre que isso acontecer,
                    considerar como se fosse na mesma célula. **Não deixe expressões vazias como:**
                    | CONSIGAZ CILINDROS LTDA | | | | |
                    - Critério para considerar nova transação: uma nova linha só deve iniciar um novo registro se contiver um novo valor, de qualquer
                    outro campo. Caso contrário, assume-se que é uma continuação do descritivo anterior.
                    
                    # EXEMPLO
                    Data | Descrição | Nº Documento | Movimentos (R$) Créditos | Movimentos (R$) Débitos | Saldo (R$)
                    --- | --- | --- | --- | --- | ---
                    | PIX ENVIADO FRANCISCO B DE SOUZA S FE | | | 650,71- | |
                    
                    # COMO NÃO DEVE SER
                    **Cabeçalho das Colunas:** Data, Descrição, Nº Documento, Movimentos (R$) Créditos, Movimentos (R$) Débitos, Saldo (R$)

                    **Transações:**

                    *   **Data não especificada (saldo anterior):**
                        *   Descrição: PIX ENVIADO R T H SERVICOS E USINAGEN, Nº Documento: 163611, Débito: R$ 80.000,00
                        *   Descrição: DEBITO PAGAMENTO DE SALARIO PAGSAL: 1 PAGTOS, Nº Documento: 010109, Débito: R$ 1.908,04
                        *   Descrição: APLICACAO CONTAMAX, Débito: R$ 220.573,35, **Saldo: R$ 1.534,77**

                    
                    # FORMATO DE SAIDA
                    Data | Descrição | Nº Documento | Movimentos (R$) Créditos | Movimentos (R$) Débitos | Saldo (R$)
                    10/01 | PIX ENVIADO FRANCISCO B DE SOUZA |  |  | 650,71 | 
                    10/01 | PARC 001/001 290000002430 | 002430 |  | 205.466,64 | 
                    10/01 | CHEQUE EMITIDO/DEBITADO | 002606 |  | 618,40 | 
                    11/01 | JUROS SALDO UTILIZ ATE LIMITE |  |  | 1.996,59 | 
                    """
                ),
                (
                    "user",
                    [
                        {
                            "type": "text",
                            "text": "Extraia as informações do extrato e retorne **apenas as tabelas**"
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": "data:image/jpeg;base64,{imagem_extrato}"}
                        }
                    ]
                )
            ]
        )

        cadeia_analise = template_analisador | llm | StrOutputParser()

        respostas = []
        for i, imagem_extrato_unica in enumerate(imagem_extrato, start=1):
            print(f"\nAnalisando página {i}...")

            try:
                resposta = cadeia_analise.invoke(
                    {"imagem_extrato": imagem_extrato_unica})
            except OutputParserException as e:
                resposta = str(e)

            respostas.append(f"\n{resposta.strip()}")
            sleep(1)

        resposta_cadeia_extrator = "".join(respostas)

        parser = PydanticOutputParser(pydantic_object=Tabela)

        template_resposta = PromptTemplate(
            template="""
            Você é um organizador de tabelas de extratos bancários. Sua tarefa é pegar um texto com transações financeiras em forma de tabela e formatá-lo seguindo estas regras:

            1. Preencha os campos de datas vazias com a data mais recente anterior.
            2. Remova repetições de cabeçalhos que estejam no meio da tabela.
            3. Ignore cabeçalhos e rodapés de página como "Extrato Consolidado", "Página 1/13" e similares.

            A resposta deve ser apenas a tabela formatada, como no exemplo abaixo:

            ---
            Exemplo de entrada:
            05/01 | WALK CHEOQ QUINTINO PARDI | - | - | - | -
            Extrato Consolidado
            Data | Descrição | Nº Documento | Movimentos (R$) Créditos | Movimentos (R$) Débitos | Saldo (R$)
            --- | --- | --- | --- | --- | ---
            | PIX ENVIADO | - | | 60,00 |

            Exemplo de saída correta:
            Data | Descrição | Nº Documento | (R$) Créditos | (R$) Débitos | Saldo (R$)
            05/01 | WALK CHEOQ QUINTINO PARDI | - | - | - | -
            05/01 | PIX ENVIADO | - | | 60,00 |
            ---

            Texto de entrada:
            <<<br
            {resposta_cadeia}
            >>>

            Lembre-se: **não gere explicações, nem código, nem texto extra**. Apenas a tabela formatada.
            """,
            input_variables=["resposta_cadeia"]
        )

        cadeia_final = template_resposta | llm | StrOutputParser()

        resposta_final = cadeia_final.invoke(
            {"resposta_cadeia": resposta_cadeia_extrator})

        with open(f"{caminho_pdf.replace(".pdf", "")}.txt", "w", encoding="utf-8") as file:
            file.write(resposta_final)

        time.sleep(2)

        link = salvar_drive(caminho_arquivo=f"{caminho_pdf.replace(".pdf", "")}.txt",
                            resp=responsavel, nome_arquivo=f"{caminho_pdf.replace(".pdf", "")}.txt")

        time.sleep(1)

        email = enviar(destinatario=email_destino,
                       assunto=f"Extrato Solicitado 📄 - {caminho_pdf.replace(".pdf", "")}", link=link)

        os.remove(f"{caminho_pdf.replace(".pdf", "")}.txt")

        return f"Resumo gerado com sucesso. 😁</br> Foi enviado no email 📧: </br> <b>{email}</b>"
