import React, { useState } from "react";
import Home from "./components/Home.js"
import UploadFile from "./components/UploadFile.js";
import QueryGenerator from "./components/QueryGenerator.js";
import ViewFile from "./components/ViewFile.js";

function App() {
  const [activeTab, setActiveTab] = useState("home");  // by default home is the main tab
  
  return (
      <div>
        {/* Navigation Buttons */}
        <div>
          <button className = "primary-btn" onClick={() => setActiveTab("home")}>Home</button>
          <button className = "primary-btn" onClick={() => setActiveTab("upload")}>Upload File</button>
          <button className = "primary-btn" onClick={() => setActiveTab("query")}>Generate Query</button>
          <button className = "primary-btn" onClick={() => setActiveTab("view")}>View Files</button>
        </div>
        
        {/* Display selected tab */}
        <div className="box">
          {/* renders the corresponding component based on the activeTab value */}
          {activeTab === "home" && <Home />} 
          {activeTab === "upload" && <UploadFile />}
          {activeTab === "query" && <QueryGenerator />}
          {activeTab === "view" && <ViewFile/>}
        </div>
      </div>

  );
}

export default App;
