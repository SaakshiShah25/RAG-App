import React, { useState } from "react";
import axios from "axios";

const UploadFile = () => {
    const [files, setFiles] = useState([]); // files is initialised to empty array
    const [response,setResponse] = useState([]); // list 
    const [upload,setUpload] = useState("");

    const handleFileChange = (event) => {
        console.log(event.target.files)
        const selectedFiles =  Array.from(event.target.files)  // FileList is converted to array
        setFiles(selectedFiles) // modify 'files' state
    }

    const handleFileSubmit = async () => {
        setUpload("Uploading files..."); // set this once we click "Upload" button 
        const formData = new FormData(); // generally used for file uploads, form submissions
        // uses key-value pair, key: files, value: array of files

        // FormData.append() -> does not accept an array, so you must append each file separately.
        for(let i=0; i<files.length; i++){
            formData.append("files", files[i]) // key,value
        }

        const res = await axios.post("http://127.0.0.1:5000/api/upload_file", formData)
        console.log(res.data)
        setResponse(res.data)
    }
    return(
        <div>
            <h2>Upload Files</h2>
            <input type = "file" multiple onChange={handleFileChange} />
            <button className = "secondary-btn" onClick = {handleFileSubmit}>Upload</button>
            {response.length>0 ? 
                response.map((res,index)=> (
                    <p key={index}>{res}</p>
                )) : (
                    <p>{upload}</p>
                )    
            }

        </div>
    )
}
export default UploadFile;