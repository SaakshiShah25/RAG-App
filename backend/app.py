from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from rag_pdf import *
import io


app = Flask(__name__) # Flask instance
CORS(app)  # Allows cross-origin requests

index_name = os.getenv("INDEX_NAME")
index =  None

# need to call here and not in main function since gunicorn skips if __name__ == "__main__": block
create_local_storage()

@app.route("/api/upload_file", methods=["POST"])
def upload_file():
    uploaded_files = request.files.getlist("files") # array containing files (file objects)
    responses = []

    for uploaded_file in uploaded_files:
        # Save locally (need to handle this)
        file_path = os.path.join(SAVE_DIR, uploaded_file.filename)
        with open(file_path, "wb") as f: # open the file in write and binary mode (file is saved in raw bytes)
            f.write(uploaded_file.read()) # write the raw byte content
  
        #1. Extract text from pdf
        pdf_text = extract_text_from_pdf(uploaded_file)
        #2. Convert text to chunks
        chunks = create_chunks(pdf_text)
        #3. Create embeddings for chunks
        embeddings = create_embeddings_from_chunks(chunks)
        #4. Create index in PineCone DB
        create_index(index_name)
        #5. Initialise connection to an index
        global index 
        index = pc.Index(index_name) #used to initialize a connection to an existing index
        #6. Insert embeddings to the DB (upsert)
        doc_id = uploaded_file.filename # name of file
        insert_embeddings_to_db(doc_id,chunks,embeddings,index)

        responses.append(f"{uploaded_file.filename} uploaded successfully!")

    return jsonify(responses)

@app.route("/api/generate_response", methods=["POST"])
def generate():
    data = request.json
    #print(data)
    query = data.get("query")

    # Create query embedding
    query_embedding =  query_to_embedding(query)
    # Search DB and retrieve relevant documents
    context = retrieve_docs(index, query_embedding)
    # Pass the retrived docs to the LLM
    response = response_generator(context,query)
    print(response)
    return jsonify(response)

@app.route("/api/display_files", methods=["GET"])
def display_files():
    file_path = SAVE_DIR # "uploads"
    files = os.listdir(file_path) # list of files present locally
    return files

@app.route("/api/download_file", methods=["GET"])
def download_file():
    file_name = request.args.get("filename")
    file_path = os.path.join(SAVE_DIR,file_name)
    return send_file(file_path, mimetype="application/pdf") # send_file : sends the file as it is 

   
@app.route("/api/delete_file", methods=["POST"])
def delete_file():
    data = request.json
    file_name = data.get("filename")
    delete_file_db_local(SAVE_DIR,file_name,index)
    response = f"{file_name} deleted successfully!"
    return jsonify(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Dynamically assigned port
    app.run(host="0.0.0.0", port=port, debug=True)
    
