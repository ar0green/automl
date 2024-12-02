// src/App.js

import React, { useState } from 'react';
import UploadData from './components/UploadData';
import PipelineForm from './components/PipelineForm';
import TaskStatus from './components/TaskStatus';
import DownloadReport from './components/DownloadReport';
import { Container, Typography } from '@material-ui/core';

function App() {
  const [fileId, setFileId] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [datasetName, setDatasetName] = useState('');
  const [reportId, setReportId] = useState(null);
  const [modelName, setModelName] = useState('');

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        AutoML Service
      </Typography>
      {!fileId && <UploadData setFileId={setFileId} />}
      {fileId && !taskId && (
        <PipelineForm
          fileId={fileId}
          setTaskId={setTaskId}
          setReportId={setReportId} // Добавлено
        />

      )}
      {taskId && <TaskStatus taskId={taskId} />}
      {taskId && (
        <DownloadReport reportId={reportId} />
      )}
    </Container>
  );
}

export default App;
