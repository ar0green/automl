// DownloadReport.js

import React, { useState } from 'react';
import { Button, TextField, Typography } from '@material-ui/core';
import axios from 'axios';

function DownloadReport({ reportId }) {
  const [reportData, setReportData] = useState(null);

  const getReport = () => {
    axios.get(`/api/download_report/${reportId}`)
      .then(response => {
        setReportData(response.data);
      })
      .catch(error => {
        console.error(error);
        alert('Failed to get report.');
      });
  };

  return (
    <div>
      <Typography variant="h6">Report</Typography>
      <Button variant="contained" color="primary" onClick={getReport}>
        Get Report
      </Button>
      {reportData && (
        <pre>{JSON.stringify(reportData, null, 2)}</pre>
      )}
    </div>
  );
}

export default DownloadReport;
