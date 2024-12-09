// StatusPipeline.js
import React, { useEffect, useState } from 'react';
import { Typography, Table, TableBody, TableCell, TableHead, TableRow, Button, Box } from '@material-ui/core';
import axios from 'axios';

function StatusPipeline() {
  const [pipelines, setPipelines] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);

  useEffect(() => {
    axios.get('/api/list_pipelines')
      .then(response => {
        setPipelines(response.data.pipelines || []);
      })
      .catch(error => console.error(error));
  }, []);

  const viewReport = (report_id) => {
    axios.get(`/api/download_report/${report_id}`)
      .then(response => {
        setSelectedReport(response.data);
      })
      .catch(error => {
        console.error(error);
        alert('Failed to get report.');
      });
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Status of Pipelines</Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Task ID</TableCell>
            <TableCell>Report ID</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Dataset Name</TableCell>
            <TableCell>Model Name</TableCell>
            <TableCell>Created At</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {pipelines.map((p) => (
            <TableRow key={p.report_id}>
              <TableCell>{p.task_id}</TableCell>
              <TableCell>{p.report_id}</TableCell>
              <TableCell>{p.status}</TableCell>
              <TableCell>{p.dataset_name}</TableCell>
              <TableCell>{p.model_name}</TableCell>
              <TableCell>{p.created_at}</TableCell>
              <TableCell>
                <Button variant="contained" color="primary" onClick={() => viewReport(p.report_id)}>
                  View Report
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {selectedReport && (
        <Box style={{ marginTop: 20 }}>
          <Typography variant="h6">Report Data</Typography>
          <pre>{JSON.stringify(selectedReport, null, 2)}</pre>
        </Box>
      )}
    </Box>
  );
}

export default StatusPipeline;
