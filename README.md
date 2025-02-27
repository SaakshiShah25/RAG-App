# **RAG-App**

## **Overview**
RAG-App (Retrieval-Augmented Generation Application) is a system that enhances the capabilities of a Large Language Model (LLM) by incorporating external knowledge from a vector database. It enables document-based querying by retrieving relevant information before generating a response.

## **Architecture**

![](https://www.google.com/url?sa=i&url=https%3A%2F%2Fblog.stackademic.com%2Fmastering-retrieval-augmented-generation-rag-architecture-unleash-the-power-of-large-language-a1d2be5f348c&psig=AOvVaw0kNOEGHcE8Rji0tl7DtPbe&ust=1740576834398000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCPjTrZH43osDFQAAAAAdAAAAABAE)![image](https://github.com/user-attachments/assets/56bcfe5c-3526-4ff7-8795-4e3e443cba3c)
The application follows the standard RAG architecture:
1. **Document Processing**: Extracts and preprocesses text from PDFs.
2. **Embedding Generation**: Converts document chunks into vector representations.
3. **Vector Storage**: Stores embeddings in Pinecone DB for efficient retrieval.
4. **Query Processing**: Converts user queries into embeddings and retrieves relevant documents.
5. **LLM Interaction**: Passes retrieved documents and queries to an LLM for response generation.
6. **Output Generation**: Provides an AI-generated response based on relevant retrieved content.

## **Workflow**
### **1. Extract Text from PDFs**
- **Library Used**: `pdfplumber`
- Extracts text content from PDF files for further processing.

### **2. Text Chunking**
- **Purpose**: Splits documents into smaller segments to fit within the token limits of the LLM.
- **Parameters**:
  - `chunk_size = 512`
  - `chunk_overlap = 50`

### **3. Create Embeddings of Chunks**
- **Model Used**: `multilingual-e5-large`
- **Vector Dimension**: `1024`

### **4. Index Creation in Pinecone DB**
- **Metric Used**: `cosine similarity`
- **Purpose**: Enables efficient retrieval of relevant document chunks.

### **5. Upserting Embeddings into Pinecone**
- **Operation**:
  - If an embedding with the given ID exists, it updates the data.
  - If the embedding does not exist, it inserts new data.

### **6. Query Processing & Retrieval**
- **Steps**:
  1. Convert user query into an embedding (`query_embedding`).
  2. Search the Pinecone DB using the `query_embedding`.
  3. Retrieve the top `k` most similar documents (`top_k = 2`).

### **7. LLM Interaction & Response Generation**
- **Model Used**: `llama-3.3-70b-versatile`
- **Process**:
  - The retrieved documents and user query are combined into a structured prompt.
  - The prompt is sent to the LLM for response generation.
  - The model generates a contextually aware response based on the input.

## **Deployment**
### **Frontend**
- **Framework**: ReactJS
- **Hosting**: Render.com

### **Backend**
- **Framework**: Flask
- **Endpoints**:
  - `/extract_text` – Extracts text from uploaded PDFs.
  - `/generate_embedding` – Converts text chunks into vector embeddings.
  - `/query` – Processes user queries, retrieves relevant documents, and generates responses.

### **Vector Database**
- **Database**: Pinecone
- **Storage & Indexing**:
  - Stores embeddings of document chunks.
  - Enables efficient similarity search using cosine similarity.

### **Storage**
- **Database**: S3 Bucket
- **Purpose**:
  - Stores raw document files.
  - Provides long-term storage for user-uploaded content.

### **Live Website**
- [RAG-App Frontend](https://rag-app-frontend-vn1q.onrender.com)

## **Conclusion**
RAG-App effectively integrates document retrieval and LLM capabilities to provide accurate, context-aware responses. By leveraging embeddings, a vector database, and a powerful LLM, it enhances traditional AI-based querying with document-based insights. The system is designed for scalability, efficiency, and high-performance retrieval-augmented generation.

