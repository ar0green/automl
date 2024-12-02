// src/components/UploadData.js

import React, { useState } from 'react';
import { Button, Typography } from '@material-ui/core';
import axios from 'axios';

function UploadData({ setFileId }) {
  const [selectedFile, setSelectedFile] = useState(null);

  const uploadFile = () => {
    const data = new FormData();
    data.append('file', selectedFile);

    axios.post('/upload_data', data)
      .then(response => {
        setFileId(response.data.file_id);
        alert('File uploaded successfully!');
      })
      .catch(error => {
        console.error(error);
        alert('Failed to upload file.');
      });
  };

  return (
    <div>
      <Typography variant="h6">Upload your dataset</Typography>
      <input
        type="file"
        onChange={e => setSelectedFile(e.target.files[0])}
      />
      <Button variant="contained" color="primary" onClick={uploadFile}>
        Upload
      </Button>
    </div>
  );
}

export default UploadData;
