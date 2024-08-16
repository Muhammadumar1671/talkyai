import os
from django.core.cache import cache
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQAWithSourcesChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.memory import ConversationBufferMemory


def initialize_environment(api_key): 
    os.environ['OPENAI_API_KEY'] = api_key

def LLM():
    return ChatOpenAI(temperature=0.5, max_tokens= 800, model="gpt-4o")

def load_and_split_documents(directory_path):
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        filenames = os.listdir(directory_path)
        docs = []

        for filename in filenames:
            file_path = os.path.join(directory_path, filename)
            print('Processing filename:', filename)

            if filename.endswith('.pdf'):
                print("Loading PDF file...")
                try:
                    loader = PyPDFLoader(file_path=file_path)
                except Exception as e:
                    return f"Error loading PDF file: {e}"
                text = loader.load()
                docs.extend(splitter.split_documents(text))
               

            elif filename.endswith('.csv'):
                loader = CSVLoader(file_path=file_path)
                text = loader.load()
                docs.extend(splitter.split_documents(text))


        print("Document loading and splitting complete.")
        return docs

    except Exception as e:
        return f"Error in load_and_split_documents function: {e}"

def save_vector_index(vector_index, path):
    print("Saving vector index...")
    try:
        vector_index.save_local(path)
        print("Vector index saved successfully.")
        return "Vector index saved successfully."
    except Exception as e:
        return f"Error saving vector index: {e}"

def load_vector_index(path):
    try:
        print("Loading vector index...")
        embeddings = OpenAIEmbeddings()
        index = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        print("Vector index loaded successfully.")
        return index
    except Exception as e:
        return f"Error loading vector index: {e}"

def create_vector_index(docs):
    print("Creating vector index...")
    embeddings = OpenAIEmbeddings()
    print("Embeddings created successfully.")
 
    index = FAISS.from_documents(docs, embeddings)
    print("Vector index created successfully.")
    return index

def start_bot(api_key, pdf_directory, retriever_directory):
    initialize_environment(api_key)
    docs = load_and_split_documents(pdf_directory)
   
    if isinstance(docs, str) and 'Error' in docs:
        return docs
    vector_index = create_vector_index(docs)
    save_vector_index(vector_index, retriever_directory)
    return "Bot initialized successfully."

def retriever(vector_index, prompt, instructions):   
    custom_prompt_template = f"""
    {prompt}
    Context: {{context}}
    Question: {{question}}.
    Do not use any special characters such as * or # or any bold words. 
    """ + instructions

    print("Custom prompt:", custom_prompt_template)

    custom_prompt = PromptTemplate(input_variables=["context", "question"], template=custom_prompt_template)
    return vector_index.as_retriever(), custom_prompt

def create_chain(custom_prompt, retriever_instance):
    qa_chain = load_qa_with_sources_chain(
        llm=LLM(),
        chain_type="stuff",
        prompt=custom_prompt,
        document_variable_name="context"
    )
    return RetrievalQA(retriever=retriever_instance, combine_documents_chain=qa_chain)

def get_bot_responses(api_key, question, prompt, retriever_directory, instructions): 
    initialize_environment(api_key)
    vector_index = load_vector_index(retriever_directory)
    if isinstance(vector_index, str) and 'Error' in vector_index: 
        return vector_index
    retriever_instance, custom_prompt = retriever(vector_index, prompt, instructions)
    chain = create_chain(custom_prompt, retriever_instance)
    response = chain({"query": question, "return_only_outputs": False})
    return response.get('result')


def igcse_retriever(vector_index, prompt):   
    custom_prompt_template = prompt + f"""
    Context: {{context}}
    Only use the information provided in the context and provide simple and short answers.
    """

    custom_prompt = PromptTemplate(input_variables=["context"], template=custom_prompt_template)
    return vector_index.as_retriever(), custom_prompt

def get_igcse_response(api_key, prompt, retriever_directory):
    initialize_environment(api_key)
    vector_index = load_vector_index(retriever_directory)
    if isinstance(vector_index, str) and 'Error' in vector_index: 
        return vector_index
    retriever_instance, custom_prompt = igcse_retriever(vector_index, prompt)
    chain = create_chain(custom_prompt, retriever_instance)
    response = chain({"query": prompt, "return_only_outputs": False})
    message = response.get('result')
    return   cleanmessage(message)

import re
def cleanmessage(response):
    cleaned_message = re.sub(r'[`*#]', '',response)
    cleaned_message += "\n\nIf You need more explanation please press the first button below."

    return cleaned_message