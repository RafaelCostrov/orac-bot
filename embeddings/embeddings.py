from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyMuPDFLoader
from auxiliares.my_keys import GEMINI_API_KEY, PINECONE_API_KEY, GEMINI_API_KEY_PESSOAL, GEMINI_API_KEY_MILLENA, GEMINI_API_KEY_RAFA
import zipfile
import re
import os
import time
import unicodedata


def limpar_pagina(texto):
    texto = re.sub(
        r"Centro de Treinamento Domínio A sua melhor escolha", "", texto)
    texto = re.sub(r"\n\d+\s*$", "", texto.strip())
    return texto.strip()


def normalizar_ascii(texto):
    texto_ascii = unicodedata.normalize('NFKD', texto).encode(
        'ASCII', 'ignore').decode('utf-8')
    texto_ascii = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', texto_ascii)
    return texto_ascii


def processar_em_lotes(iterable, batch_size=100):
    """Divide um iterável em lotes de um tamanho específico."""
    l = len(iterable)
    for ndx in range(0, l, batch_size):
        yield iterable[ndx:min(ndx + batch_size, l)]


def rodar():
    zip_path = 'embeddings/documentos.zip'
    pasta_docs = 'docs'

    # with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    #     zip_ref.extractall(pasta_docs)

    documents = []
    for filename in os.listdir(pasta_docs):
        print(pasta_docs)
        file_path = os.path.join(pasta_docs, filename)
        loader = PyMuPDFLoader(file_path)
        paginas = loader.load()
        for i, pagina in enumerate(paginas):
            pagina.page_content = limpar_pagina(pagina.page_content)
            pagina.metadata["source"] = filename
            pagina.metadata["page_number"] = i + 1
            documents.append(pagina)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len
    )
    print(f"Documentos carregados: {len(documents)}")
    chunks = text_splitter.split_documents(documents)

    print(f"✅ Documentos foram divididos em {len(chunks)} chunks no total.")

    # chunks = chunks[1201:]

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GEMINI_API_KEY
    )

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("orac")

    total_chunks_enviados = 0

    for chunk_batch in processar_em_lotes(chunks, batch_size=100):

        textos_do_lote = [doc.page_content for doc in chunk_batch]

        print(
            f"Gerando embeddings para um lote de {len(textos_do_lote)} chunks...")
        lote_de_vetores = embeddings.embed_documents(textos_do_lote)

        vectors_to_upsert = []
        for i, doc in enumerate(chunk_batch):

            chunk_global_index = total_chunks_enviados + i
            source_normalizado = normalizar_ascii(doc.metadata['source'])
            vector_id = f"{source_normalizado}_{doc.metadata['page_number']}_{chunk_global_index}"

            vectors_to_upsert.append(
                (vector_id, lote_de_vetores[i], {
                 **doc.metadata, "text": doc.page_content})
            )

        if vectors_to_upsert:
            index.upsert(vectors=vectors_to_upsert,
                         namespace="dominio-importacao")
            total_chunks_enviados += len(vectors_to_upsert)
            print(
                f"✅ Lote de {len(vectors_to_upsert)} chunks enviado. Total: {total_chunks_enviados}")
        else:
            print("⚠ Nenhum chunk no lote para envio.")
        print("Dormindo por 60 segundos...")
        time.sleep(61)
