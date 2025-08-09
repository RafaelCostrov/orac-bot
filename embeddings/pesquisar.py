import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from auxiliares.my_models import GEMINI_FLASH
from auxiliares.my_keys import GEMINI_API_KEY, PINECONE_API_KEY
import pinecone


def pesquisar(pergunta, namespace):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    llm = ChatGoogleGenerativeAI(
        api_key=GEMINI_API_KEY,
        model=GEMINI_FLASH
    )

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GEMINI_API_KEY
    )
    pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("orac")

    pergunta_vector = embeddings.embed_query(pergunta)

    resultado = index.query(
        vector=pergunta_vector,
        top_k=10,
        include_metadata=True,
        namespace=namespace
    )

    documentos = []
    for match in resultado.get('matches', []):
        metadata = match.get('metadata', {})
        conteudo = metadata.get('text') or metadata.get('page_content') or ""
        documentos.append(
            Document(page_content=conteudo, metadata=metadata)
        )

    if not documentos:
        return "Não encontrei nada"

    contexto = "\n\n".join([doc.page_content for doc in documentos])

    template_auxiliar = PromptTemplate(
        template="""
            Assuma que você é auxiliar de um sistema contábil chamado Dominio.
            A sua tarefa principal consiste em explicar para o usuário como faz determinada ação,
            baseando-se para isso no contexto fornecido e na pergunta do usuário.
            
            # REGRAS OBRIGATORIAS
            - Não invente algo, se não receber no contexto, **fale que não sabe como fazer**
            - Saída deve ser formatada em **HTML**, não em markdown. E lembre-se, não utilize style.
            - Não coloque elementos como <body> e <html>, apenas use <p>, <li> <b> <ol> <ul> e </br>
            - Seja o mais descritivo possível, passando passo a passo se você tiver condições.
            - Lembre-se, você é o que dá a resposta **final** pro usuário, então não fale que o contexto passado não te passa mais informações e nem coloque observações relacionada ao contexto passado.
            
            pergunta:
            {pergunta}
            
            contexto:
            {contexto}
        """,
        input_variables=["pergunta", "contexto"]
    )

    cadeia_analise = template_auxiliar | llm | StrOutputParser()

    resposta = cadeia_analise.invoke(
        {"pergunta": pergunta, "contexto": contexto}
    )

    return resposta
