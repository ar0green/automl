// src/components/DownloadReport.js

import React, { useState } from 'react';
import { Button, TextField } from '@material-ui/core';

function DownloadReport({ reportId }) {
  const [reportFilename, setReportFilename] = useState('');

  const downloadReport = () => {
    window.location.href = `/api/download_report/${reportId}/${reportFilename}`;
  };

  return (
    <div>
      <TextField
        label="Report Filename"
        value={reportFilename}
        onChange={e => setReportFilename(e.target.value)}
        fullWidth
        margin="normal"
      />
      <Button variant="contained" color="primary" onClick={downloadReport}>
        Download Report
      </Button>
    </div>
  );
}

export default DownloadReport;
