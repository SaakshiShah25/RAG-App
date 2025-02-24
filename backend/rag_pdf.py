import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from groq import Groq
from dotenv import load_dotenv
import time
import warnings
import os
import requests
import json
import uuid
import boto3
import numpy as np
warnings.filterwarnings("ignore")

# Load the necessary keys from the .env file
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
index_name = os.getenv("INDEX_NAME")
SAVE_DIR = os.getenv("SAVE_DIR")
json_file = os.getenv("JSON_FILE")

pc = Pinecone(api_key=PINECONE_API_KEY)

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n" # extract text content from each page of pdf
    return text


def create_chunks(pdf_text):
    # eg: text is of 1000 tokens (words)
    # chunk 1 : 0 - 511
    # chunk 2 : 512-50 = 462 + 511 = 973 (ideally should start from 512 but since overlap=50, it considers last 50 words of chunk1 for starting )
    #         : 462 - 973
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    chunks = text_splitter.split_text(pdf_text)
    return chunks

def create_embeddings_from_chunks(chunks):
    embeddings = pc.inference.embed(
        model="multilingual-e5-large", # creates vector embeddings
        inputs = chunks, # input text 
        parameters={"input_type": "passage", "truncate": "END"}
    )
    return embeddings

def create_index(index_name):
    if not pc.has_index(index_name):
        print("Index does not exist")
        pc.create_index(
            name=index_name,
            dimension=1024, # dimension of vector produced by "multilingual-e5-large"
            metric="cosine", # similarity metric
            spec=ServerlessSpec(
                cloud='aws', 
                region='us-east-1'
            ) 
        ) 

def insert_embeddings_to_db(doc_id,chunks,embeddings,index):
    records = []
    # zip() : creates an iterator of tuples -> (chunks[0], embeddings[0])
    # here it will be (chunks[0], embeddings[0])
    for (chunk, embedding) in zip(chunks, embeddings):
        record_id = str(uuid.uuid4())
        records.append({
            "id": record_id, #doc id : must be string
            "values": embedding['values'], # chunk's embedding/vector
            "metadata": {'text': chunk, 'file_name' : doc_id} # chunk text
        })

    index.upsert( # update or insert
        vectors=records, # "vectors" expects a list of dictionaries
        namespace="pdf-rag"
    )

def query_to_embedding(query):
    query_embedding = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[query],
        parameters={
            "input_type": "query"
        }
    )
    return query_embedding

def retrieve_docs(index,query_embedding):
    results = index.query(
        namespace="pdf-rag",
        vector=query_embedding[0].values, # query_embedding(vector)
        top_k=2, # 2 most similar documents
        include_values=False,
        include_metadata=True
    )

    retrieved_docs = []
    for result in results.matches:
        retrieved_docs.append(result["metadata"]["text"])

    return retrieved_docs

def response_generator(context,query):
    prompt = f"Use the following context to answer the query:\n\n{context}\n\nQuestion: {query}\nAnswer:"

    client = Groq(api_key=GROQ_API_KEY)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content


def delete_embeddings_from_db(file_name,index): 
    print(index.describe_index_stats())  # Check if vectors exist

    response = index.query(
        vector = [0]*1024,
        top_k = 100,
        filter = {"file_name" : {"$eq" : file_name}}, # for exact matches
        namespace="pdf-rag",
        include_metadata = True
    )
    id_list = []
    for match in response['matches']:
        id_list.append(match['id'])

    if id_list: # delete the embeddings based on ids
        index.delete(ids = id_list, namespace="pdf-rag")
    else:
        print("This file does not exist in DB")


def connect_to_s3():
    # boto3 is given the required credentials (of IAM user)
    # checks if the IAM user has access to S3 services
    # Connects to S3 using those credentials and returns an instance

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="ap-south-1"
    ) 
    # buckets = s3.list_buckets()
    return s3

