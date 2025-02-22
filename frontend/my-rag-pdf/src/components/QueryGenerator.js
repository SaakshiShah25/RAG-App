import React, { useState } from "react";
import axios from "axios";


const QueryGenerator = () => {
    // initialised to empty string, setQuery changes the state of query variable
    const [query, setQuery] = useState(""); 
    const [response, setResponse] = useState("");

    const handleQuery = (event) => {
        setQuery(event.target.value)
    }
    const handleSubmit = async () => {
        const res = await axios.post("https://rag-app-awh9.onrender.com/api/generate_response", { query } , { headers: { "Content-Type": "application/json" }}); // query is passed as json data 
        // console.log(query)
        // console.log(res)
        setResponse(res.data); // updates response variable and displays the latest value
    };
    return(
        <div>
            <h2>RAG System</h2>
                <input type="text" placeholder="Enter query" value={query} className = "text-input" onChange={handleQuery} />
                {/* updates 'query' when the user types, and re-renders the component showing the updated query value */}
                <button className = "secondary-btn" onClick={handleSubmit}>Generate</button>
                <p>Response: {response}</p>
        </div>
    )
}
export default QueryGenerator;