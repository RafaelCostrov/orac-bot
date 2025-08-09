from langchain.tools import BaseTool
from embeddings.pesquisar import pesquisar
import ast


class FerramentaAuxiliadoraDominio(BaseTool):
    name: str = "Ferramenta Auxiliadora do Dominio Sistemas"
    description: str = """
    Utilize essa ferramenta sempre que for solicitado para você alguma informação relativa ao **Dominio**.
    
    Para seu contexto, o Dominio é o nosso software contábil, então todos na contabilidade usam ele.
    
    Você deve entender de qual módulo ele está falando, e com isso escolher o **namespace** do pinecone que utilizará para fazer a pesquisa vetorial.
    
    # namespaces disponíveis:
    Dúvida de dominio honorarios (módulo sobre o financeiro da contabilidade): namespace = dominio-honorarios
    Dúvida de dominio auditoria (módulo de auditoria): namespace = dominio-auditoria
    Dúvida de dominio importacao (módulo de importação fiscal): namespace = dominio-importacao
    
    # Entradas Requiridas:
    - 'pergunta' (str): Pergunta do usuário, tirar todo o contexto recebido envolta, como as observações e etc.
    - 'namespace' (str): Namespace do pinecone **gerado por você** baseado na pergunta do usuário.
    
    **Não** solicitar ao usuário o nomespace, você escolherá isso.
    
    Ao explicar a ferramenta para alguém, peça apenas a dúvida do usuário, e sempre procure textos curtos para descrever.
    
    Exemplo: {
        "pergunta": "Como faço para emitir um boleto?",
        "namespace": "dominio-honorarios",
        }
    """
    return_direct: bool = True

    def _run(self, acao):
        acao = ast.literal_eval(acao)
        pergunta = acao.get("pergunta")
        namespace = acao.get("namespace")

        resposta = pesquisar(pergunta, namespace)

        return resposta
