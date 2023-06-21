import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
#from transformers import pipeline
import pinecone
import os


OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
#Api-Key = os.environ.get('PINECONE_API_KEY')
model_name = "gpt2-medium"
model_revision = "2.0"
#nlp = pipeline("text-generation", "gpt2")

# Create a summarization pipeline using Hugging Face's Transformers library
#summarizer = pipeline("summarization")

pinecone.init(api_key="1a2e1f95-ccf3-4bc6-9d92-025490ff2874",environment="us-west1-gcp-free")

index_name ="adaza-chatbot"

index = pinecone.Index(index_name)
index_stats = index.describe_index_stats()
print(index_stats)

if index_name not in pinecone.list_indexes():
        # we create a new index
    pinecone.create_index(
            name=index_name,
            metric='cosine',
            dimension=1536  # 1536 dim of text-embedding-ada-002
        )


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    #vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    vectorstore = Pinecone.from_texts(texts=text_chunks,embedding=embeddings,index_name=index_name)
    
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def is_summary_request(user_question):
    # Check if the user input contains keywords indicating a summary request
    summary_keywords = ['summary', 'summarize', 'tl;dr']
    for keyword in summary_keywords:
        if keyword in user_question.lower():
            return True
    return False

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']
   
   
    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
            
#def generate_summary(text):
    # Use the summarization pipeline to generate a summary
   # result = summarizer(text, max_length=100, min_length=30, do_sample=False)
    #summary = result[0]["summary_text"]
    #return summary
 


def main():
    load_dotenv()
    st.set_page_config(layout="wide", initial_sidebar_state="auto",menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About':None

    })  # Set sidebar to "auto" or False to hide it

    st.sidebar.title("Search History")

    st.write(css, unsafe_allow_html=True)

    # Initialize search history list
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    
    user_question = st.text_input("Hello, I am Adaza, how can I help you today?")
    if user_question:
        handle_userinput(user_question)
        # Save user's search to history
        #if st.button("Search"):
         #   st.session_state.search_history.append(user_question)
         # Display search history in the sidebar
        #for question in st.session_state.search_history:
         #   st.sidebar.write(question)
# Summarize the user input
   # if user_question:
     #   summary = generate_summary(user_question)
      #  st.session_state.search_history.append(summary)


    st.session_state.search_history.append(user_question)
    
         # Display search history in the sidebar
    for question in st.session_state.search_history:
       st.sidebar.write(question)

    # Display search history in the sidebar
    #for summary in st.session_state.search_history:
       # st.sidebar.write(summary)
    
    #vectorstore = None  # Initialize vectorstore variable

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)
                print(vectorstore)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)
    

if __name__ == '__main__':
    main()

