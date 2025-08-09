from langchain.tools import BaseTool
import ast


import requests


class FerramentaCNPJ(BaseTool):
    name: str = "Ferramenta Capturadora de Informações do CNPJ"
    description: str = """
    Utilize essa ferramenta sempre que for solicitado que você ache informações referente a algum CNPJ em específico.
    
    
    Ao explicar a ferramenta para alguém, sempre procure textos curtos para descrever.
    
    # Entradas Requiridas:
    - 'cnpj' (str): CNPJ a verificar (se estiver formatado, retire a formatação).
    
    # EXEMPLO FORMATADO:
    12.345.789/0001-23
    
    # EXEMPLO CORRETO PARA VOCÊ AJUSTAR:
    12345789000123

    Exemplo: cnpj: 15435766000176 
    """
    return_direct: bool = True

    def _run(self, acao):
        acao = ast.literal_eval(acao)
        cnpj = acao.get("cnpj", "")

        url = f"https://receitaws.com.br/v1/cnpj/{cnpj}"
        print(url)

        requisicao = requests.get(url)

        resposta = requisicao.json()

        print(requisicao)

        regime_federal = "Normal"
        if resposta.get('simei').get('optante'):
            regime_federal = "MEI"
        elif resposta.get('simples').get('optante'):
            regime_federal = "Simples Nacional"

        atividades_principais = resposta.get('atividade_principal')
        atividade_principal = atividades_principais[0].get(
            'text', "Não informado")

        qsa = resposta.get('qsa')
        socios = []
        for socio in qsa:
            socios.append(socio.get('nome'))

        socios_texto = ", ".join(socios)

        texto_resposta = f"""
        <p>Claro, aqui estão as informações sobre o CNPJ: <b>{cnpj}</b></p><br/>
            <ul>
            <li><b>Nome:</b> {resposta.get('nome', 'Não informado')}</li>
            <li><b>Fantasia:</b> {resposta.get('fantasia', 'Não informado')}</li>
            <li><b>Porte:</b> {resposta.get('porte', 'Não informado')}</li>
            <li><b>Atividade Principal:</b> {atividade_principal}</li>
            <li><b>Telefone:</b> {resposta.get('telefone', 'Não informado')}</li>
            <li><b>CEP:</b> {resposta.get('cep', 'Não informado')}</li>
            <li><b>Endereço:</b> {resposta.get('logradouro', '')}, {resposta.get('numero', '')} - {resposta.get('bairro', '')} - {resposta.get('municipio', '')}, {resposta.get('uf', '')}</li>
            <li><b>Regime:</b> {regime_federal}</li>
            <li><b>Sócios:</b> {socios_texto}</li>
            </ul>
        
        """

        return texto_resposta
