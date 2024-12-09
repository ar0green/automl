// PipelineForm.js
import React, { useState, useEffect } from 'react';
import { Button, TextField, Typography, FormControl, InputLabel, Select, MenuItem, Grid, Box } from '@material-ui/core';
import axios from 'axios';

function PipelineForm({ setTaskId, setReportId }) {
  const [params, setParams] = useState({
    target_column: '',
    task_type: 'classification',
    sep: ',',
    dataset_name: 'dataset',
    model_name: ''
  });

  const [fileId, setFileId] = useState(''); // Теперь мы будем выбирать fileId на этой странице
  const [columns, setColumns] = useState([]);
  const [models, setModels] = useState(['Random Forest', 'Logistic Regression', 'XGBoost', 'LightGBM']);
  const [datasets, setDatasets] = useState([]);

  useEffect(() => {
    // Загружаем список датасетов
    axios.get('/api/list_datasets')
      .then(response => {
        setDatasets(response.data.datasets || []);
      })
      .catch(error => console.error(error));
  }, []);

  useEffect(() => {
    if (fileId) {
      axios.get(`/api/get_dataset_info?file_id=${fileId}`)
        .then(response => {
          setColumns(response.data.columns || []);
        })
        .catch(error => console.error(error));
    }
  }, [fileId]);

  const runPipeline = () => {
    // При запуске пайплайна нам нужен fileId
    if (!fileId) {
      alert('Please select a dataset first.');
      return;
    }

    // Отправляем запрос на запуск пайплайна, передаём fileId
    axios.post(`/api/run_pipeline/${fileId}`, params)
      .then(response => {
        setTaskId(response.data.task_id);
        setReportId(response.data.report_id);
        alert('Pipeline started!');
      })
      .catch(error => {
        console.error(error);
        alert('Failed to start pipeline.');
      });
  };

  const handleChange = (e) => {
    setParams({ ...params, [e.target.name]: e.target.value });
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Configure Pipeline</Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel id="dataset_select_label">Select Dataset</InputLabel>
            <Select
              labelId="dataset_select_label"
              value={fileId}
              onChange={(e) => setFileId(e.target.value)}
            >
              {datasets.map(ds => (
                <MenuItem key={ds.file_id} value={ds.file_id}>
                  {ds.filename}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            label="Dataset Name"
            name="dataset_name"
            value={params.dataset_name}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            label="Separator"
            name="sep"
            value={params.sep}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel id="task_type_label">Task Type</InputLabel>
            <Select
              labelId="task_type_label"
              name="task_type"
              value={params.task_type}
              onChange={handleChange}
            >
              <MenuItem value="classification">Classification</MenuItem>
              <MenuItem value="regression">Regression</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth margin="normal" disabled={!fileId || columns.length === 0}>
            <InputLabel id="target_column_label">Target Column</InputLabel>
            <Select
              labelId="target_column_label"
              name="target_column"
              value={params.target_column}
              onChange={handleChange}
            >
              {columns.map((col) => (
                <MenuItem key={col} value={col}>{col}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel id="model_name_label">Model</InputLabel>
            <Select
              labelId="model_name_label"
              name="model_name"
              value={params.model_name}
              onChange={handleChange}
            >
              {models.map((model) => (
                <MenuItem key={model} value={model}>{model}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12}>
          <Button variant="contained" color="primary" onClick={runPipeline} disabled={!fileId}>
            Run Pipeline
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
}

export default PipelineForm;
