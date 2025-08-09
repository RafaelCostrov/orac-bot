from tools.ferramenta_analisadora import FerramentaAnalisadora
from tools.ferramenta_informacoes_cnpj import FerramentaCNPJ
from tools.ferramenta_auxiliadora_dominio import FerramentaAuxiliadoraDominio
from langchain.tools import Tool
from langchain.agents import Tool
from langchain.agents import create_react_agent
from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from auxiliares.my_models import GEMINI_FLASH
from auxiliares.my_keys import GEMINI_API_KEY
from langchain.globals import set_debug
set_debug(False)


class AgenteOrquestrador:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            api_key=GEMINI_API_KEY,
            model=GEMINI_FLASH
        )
        ferramenta_analisadora = FerramentaAnalisadora()
        ferramenta_cnpj = FerramentaCNPJ()
        ferramente_auxiliadora_dominio = FerramentaAuxiliadoraDominio()

        self.tools = [
            Tool(
                name=ferramenta_analisadora.name,
                func=ferramenta_analisadora.run,
                description=ferramenta_analisadora.description,
                return_direct=ferramenta_analisadora.return_direct
            ),
            Tool(
                name=ferramenta_cnpj.name,
                func=ferramenta_cnpj.run,
                description=ferramenta_cnpj.description,
                return_direct=ferramenta_cnpj.return_direct
            ),
            Tool(
                name=ferramente_auxiliadora_dominio.name,
                func=ferramente_auxiliadora_dominio.run,
                description=ferramente_auxiliadora_dominio.description,
                return_direct=ferramente_auxiliadora_dominio.return_direct
            )
        ]

        prompt = hub.pull("hwchase17/react")
        prompt = prompt.partial(
            instructions=(
                "Se o usuário perguntar sobre suas habilidades, funções, "
                "ou sobre o que você pode fazer, responda diretamente sem usar nenhuma ferramenta.\n"
                "Somente use ferramentas quando precisar buscar ou processar informações externas."
            )
        )

        self.agente = create_react_agent(self.llm, self.tools, prompt)
