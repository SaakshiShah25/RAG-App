import React, { useEffect, useState } from "react";
import axios from "axios";


const ViewFile = () => {

    const [files,setFiles] = useState([]);  

    const displayFiles = async () => {
        const res = await axios.get("https://rag-app-awh9.onrender.com/api/display_files");
        // console.log("Files list: ", res.data)
        setFiles(res.data) // set the "files" that we get by GET request 
    }
    
    useEffect(()=>{
        displayFiles();
    },[]) // Empty array => displayFiles is called only once, when the component is first rendered


    
    const downloadFile = (filename) => {
        window.open(`https://rag-app-awh9.onrender.com/api/download_file?filename=${filename}`, "_blank");
    };
    
        

    const deleteFile = async (filename,index) => {
        const res = await axios.post("https://rag-app-awh9.onrender.com/api/delete_file",{filename});
        console.log(res.data);
        //Modify the files variable after deletion 
        setFiles(prevFiles => {
            const updatedFiles = [...prevFiles]
            updatedFiles.splice(index,1)
            return updatedFiles
        });
    }

    return(
        <div>
            {/* as soon as the files variable is set/updated we can see the filename along with 2 buttons */}
            <ul>
                {files.length>0 ?  files.map((filename,index) => (
                    <li key={index}>
                        <p>{filename}</p>
                        <button className = "secondary-btn" onClick = {() => downloadFile(filename)}>Download File</button>
                        <button className = "secondary-btn" onClick={() => deleteFile(filename,index)}>Delete file</button>
                    </li>
                )) : (
                    <p>No files present in the DB!</p>
                )}
            </ul>
            
        </div>
    )
}
export default ViewFile;