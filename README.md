# Orac-IA: Automação Contábil Inteligente

#### Descrição Geral 📌

O Orac-IA é uma solução de automação para rotinas contábeis, integrando análise de extratos bancários, pesquisa inteligente em documentos, consulta de informações de CNPJ e envio automatizado de resultados via Google Drive e Gmail. Utiliza IA generativa (Google Gemini), Pinecone para busca vetorial, e APIs oficiais do Google para armazenamento e comunicação.

Principais funcionalidades:
- **Análise automática de extratos bancários em PDF** com extração de tabelas e envio dos resultados por e-mail.
- **Pesquisa inteligente** em manuais do ERP contábil usando embeddings e busca vetorial.
- **Consulta de informações de CNPJ** diretamente da ReceitaWS.
- **Organização e compartilhamento de arquivos** no Google Drive.
- **Envio automático de e-mails** com resultados e links para download.

---

## Ferramentas utilizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-000000?style=for-the-badge&logo=langchain&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Pinecone](https://img.shields.io/badge/Pinecone-6C47FF?style=for-the-badge)
![Google Drive](https://img.shields.io/badge/Google%20Drive-4285F4?style=for-the-badge&logo=google-drive&logoColor=white)
![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

---

## Passo a passo da automação

O arquivo main.py é o ponto de entrada da aplicação, expondo uma API Flask que recebe requisições para análise de extratos, pesquisas e consultas.

### 🤖 O que o sistema faz?

1. **Recebe requisições via API**:
   - Permite anexar arquivos PDF de extratos bancários.
   - Recebe perguntas e dados do usuário (nome, e-mail, senha).

2. **Orquestra o fluxo de análise**:
   - Utiliza o agente inteligente (`AgenteOrquestrador`) para decidir qual ferramenta usar (análise de extrato, pesquisa, consulta CNPJ).
   - Executa a ferramenta adequada conforme o contexto da requisição.

3. **Análise de extratos bancários**:
   - Extrai imagens das páginas do PDF.
   - Usa IA generativa para identificar e extrair tabelas de transações.
   - Formata e organiza os dados conforme regras contábeis.
   - Salva o resultado em arquivo `.txt`.

4. **Armazenamento e compartilhamento**:
   - Salva o arquivo gerado no Google Drive, organizado por mês e responsável.
   - Compartilha a pasta automaticamente com o responsável.

5. **Envio de e-mail automático**:
   - Envia o link para download do arquivo ao responsável, usando um template HTML personalizado.

6. **Pesquisa inteligente em documentos**:
   - Utiliza embeddings e Pinecone para buscar respostas em documentos contábeis.
   - Formata a resposta em HTML para o usuário.

7. **Consulta de informações de CNPJ**:
   - Busca dados diretamente da ReceitaWS e retorna informações detalhadas em HTML.

---

## Funções Auxiliares

### 📁 servico_google.py

#### 🔧 `acessando_drive()`
Estabelece conexão autenticada com a API do Google Drive usando credenciais de conta de serviço.

---

### 📁 envio_drive.py

#### 📂 `compartilhar_pasta(drive_service, pasta_id, seu_email)`
Compartilha uma pasta do Google Drive com um usuário específico, concedendo permissão de escrita.

#### 💾 `salvar_drive(caminho_arquivo, resp, nome_arquivo)`
Salva um arquivo no Google Drive, organizando em estrutura de pastas por mês e responsável. Retorna o link para download.

---

### 📁 envio_email.py

#### 📄 `carregar_template(link)`
Carrega e formata o template HTML do e-mail, inserindo o link para download do extrato.

#### ✉️ `criar_email(destinatario, assunto, link)`
Cria o e-mail em formato raw (base64), preenchendo o conteúdo HTML.

#### 📬 `enviar(destinatario, assunto, link)`
Envia o e-mail ao destinatário com o link do arquivo gerado.

---

### 📁 embeddings.py & pesquisar.py

#### 🧠 Embeddings e Pesquisa Vetorial
- Carregam documentos, dividem em chunks, geram embeddings com Gemini e indexam no Pinecone.
- Permitem busca inteligente por contexto, retornando respostas formatadas em HTML.

---

### 📁 ferramenta_analisadora.py

#### 🏦 Análise de Extratos Bancários
- Recebe PDF, extrai imagens, utiliza IA para identificar e extrair tabelas de transações.
- Organiza e formata os dados, salva no Drive e envia por e-mail.

---

### 📁 ferramenta_informacoes_cnpj.py

#### 🏢 Consulta de CNPJ
- Busca informações detalhadas do CNPJ na ReceitaWS.
- Retorna dados formatados em HTML.

---

### 📁 ferramenta_auxiliadora_dominio.py

#### 🔍 Pesquisa Inteligente no Dominio Sistemas
- Seleciona o namespace correto para busca vetorial conforme o módulo do Dominio.
- Retorna respostas detalhadas em HTML.

---

## Autor

- [@RafaelCostrov](https://github.com/RafaelCostrov)
