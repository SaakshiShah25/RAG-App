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
        inputs= chunks, # input text 
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

def insert_embeddings_to_db(doc_id, chunks,embeddings,index):
    records = []
    id_list = []
    # zip() : creates an iterator of tuples -> (chunks[0], embeddings[0])
    # enumerate() : adds counter to on iterable
    # here it will be (1, (chunks[0], embeddings[0]) )
    # eg: doc1#chunk1, doc1#chunk2 ..
    for (chunk, embedding) in zip(chunks, embeddings):
        record_id = str(uuid.uuid4())
        id_list.append(record_id)
        records.append({
            "id": record_id, #doc id : must be string
            "values": embedding['values'], # chunk's embedding/vector
            "metadata": {'text': chunk, 'file_name' : doc_id} # chunk text
        })
    # Store to json file 
    # read data from json file
    with open(json_file, "r") as f:
        data = json.load(f)
    # add new data
    data[doc_id] = id_list
    # write the new data to the json file
    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)

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

# List of files uploaded

# Query optimisation

def delete_file_db_local(SAVE_DIR,file_name,index): 
    print("FileName:", file_name)
    # Delete from the DB
    # retrieve the list of ids of embeddings corresponding to the give file_name
    with open(json_file,"r") as f:
        data = json.load(f)

    # list of ids (of embeddings) of the given file
    id_list = data[file_name]
    if id_list: # delete the embeddings based on ids
        index.delete(ids = id_list, namespace="pdf-rag")
    else:
        print("This file does not exist in DB")

    # Delete locally 
    # 1. (from uploads folder)
    file_path = f"{SAVE_DIR}/{file_name}"
    os.remove(file_path)

    # 2. from json file
    # delete (modify the json file)
    with open(json_file,"r") as f:
        data = json.load(f) #read 
        del data[file_name] #delete 
    # write the updated data to the file
    with open(json_file,"w") as f:
        json.dump(data, f, indent=4) #write 

# Helper function

def create_local_storage():
    # create a directory to store files locally
    os.makedirs(SAVE_DIR, exist_ok=True)

    # create an empty data.json file if data.json doesn't exist
    if not os.path.exists(json_file):
        with open(json_file,"w") as f:
            json.dump({},f)




