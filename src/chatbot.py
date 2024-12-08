import os
from transformers import pipeline
from langchain.vectorstores import Qdrant
from langchain.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_huggingface.llms import HuggingFacePipeline
import qdrant_client
from langchain.llms.openai import OpenAI
# import langchain_openai import OpenAI

API_KEY = "Z2d647t3DOltO-ITznT0GoGKaEod0jVTAbKbEFpv0d_cfedhbDzWWw"
QDRANT_URL = "https://a1292b51-e420-4fd8-9e53-0f1ad16ce6ca.us-west-2-0.aws.cloud.qdrant.io:6333/"
OPENAI_API_KEY = ""

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=API_KEY
)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

collection_name = "CV_Database"
vector_store = Qdrant(client=qdrant_client, collection_name=collection_name, embeddings=embeddings)

llm = OpenAI(temperature=0.0, openai_api_key=OPENAI_API_KEY)

template = """You will recieve some CVs in the context section. The content of each CV will start with the file name (.pdf or .docx).
In those CVs, there will be some infomations you should focus on. Using those infomations to answer the question.
The informations in those CVs will not be related to each other. Therefore, please do not answer my question about the information in this CV using the information from another CV.
Context: 
{context}
This is the end of the context section. 
Now is your question. If you don't know the answer, just say "I don't know" instead of giving wrong infomations.
Question: {question}
"""
prompt = PromptTemplate(template = template, input_variables=["context", "question"])

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_store.as_retriever(),
    return_source_documents=False,
    chain_type_kwargs= {'prompt': prompt}
)

question = "Infomation of Richard Sanchez's Education."

response = qa_chain.invoke({"query": question})

print("Answer:", response['result'])
