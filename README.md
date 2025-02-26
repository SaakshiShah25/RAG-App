## RAG Architecture:
![](https://www.google.com/url?sa=i&url=https%3A%2F%2Fblog.stackademic.com%2Fmastering-retrieval-augmented-generation-rag-architecture-unleash-the-power-of-large-language-a1d2be5f348c&psig=AOvVaw0kNOEGHcE8Rji0tl7DtPbe&ust=1740576834398000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCPjTrZH43osDFQAAAAAdAAAAABAE)![image](https://github.com/user-attachments/assets/56bcfe5c-3526-4ff7-8795-4e3e443cba3c)

### Working of RAG-App:

1. Extract text from pdf 
- Library used : **pdfplumber**

2. Create chunks of the text 
- Chunking the text means splitting the entire document into smaller, more manageable pieces or segments.
- It’s done to fit the text on token limits of models(RAG).
- **chunk_size=512, chunk_overlap=50**

4. Create embeddings of chunks
- Model used : **multilingual-e5-large**
- Dimension of the vector : **1024**

5. Create an index in Pinecone DB
- Metric used : **“cosine”** (i.e. cosine similarity)
6. Initialise connection to the index
7. Insert embeddings to the DB (upsert)
- If you have a vector with the **ID** "vector_1" and you upsert it into the index, it will be added if it doesn't exist. If "vector_1" already exists, the upsert operation will update it with the new vector data you provide.

8. Input the query, convert query to query_embedding
9. Search the DB with query_embedding and retrieve relevant documents based on **similarity**
- Here, top_k = 2 i.e. **2 most similar documents are retrieved**
10. Pass the **retrieved documents + query** to LLM and generate output
- Model used : **"llama-3.3-70b-versatile"**


### Website: https://rag-app-frontend-vn1q.onrender.com

### Tech Stack:
- Backend : Flask
- Frontend : ReactJS
- Vector Database : Pinecone
- Database : S3 Bucket
