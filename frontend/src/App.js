// App.js
import React, { useState } from 'react';
import { AppBar, Toolbar, Typography, Button, Menu, MenuItem, Box } from '@material-ui/core';

import UploadData from './components/UploadData';
import PipelineForm from './components/PipelineForm';
import TaskStatus from './components/TaskStatus';
import DownloadReport from './components/DownloadReport';
import ApplyModel from './components/ApplyModel'; // Допустим, мы создали этот компонент

function App() {
  const [anchorEl, setAnchorEl] = useState(null);
  const [view, setView] = useState('upload'); 
  const [fileId, setFileId] = useState(null);    // Добавляем состояние fileId
  const [taskId, setTaskId] = useState(null);
  const [reportId, setReportId] = useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const navigateTo = (section) => {
    setView(section);
    handleClose();
  };

  return (
    <Box style={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" style={{ flexGrow: 1 }}>
            AutoML Service
          </Typography>
          <Button color="inherit" onClick={() => navigateTo('upload')}>
            Upload Data
          </Button>
          <Button color="inherit" onClick={() => navigateTo('pipeline')}>
            Configure Pipeline
          </Button>
          <Button color="inherit" onClick={() => navigateTo('report')}>
            View Reports
          </Button>
          <Button color="inherit" onClick={handleMenu}>
            Models
          </Button>
          <Menu
            id="model-menu"
            anchorEl={anchorEl}
            keepMounted
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem onClick={() => navigateTo('applyModel')}>Apply Model</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      
      <Box style={{ margin: '20px' }}>
        {view === 'upload' && (
          <UploadData setFileId={setFileId} />
        )}
        {view === 'pipeline' && (
          <PipelineForm
            fileId={fileId}
            setTaskId={setTaskId}
            setReportId={setReportId}
          />
        )}
        {view === 'report' && (
          <DownloadReport reportId={reportId} />
        )}
        {view === 'applyModel' && (
          <ApplyModel />
        )}
        {view === 'status' && (
          <TaskStatus taskId={taskId} />
        )}
      </Box>
    </Box>
  );
}

export default App;
