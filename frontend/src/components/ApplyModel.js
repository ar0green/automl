// ApplyModel.js

import React, { useState } from 'react';
import { Typography, Button, TextField, FormControl, InputLabel, Select, MenuItem, Grid, Box } from '@material-ui/core';
import axios from 'axios';

function ApplyModel() {
  const [modelId, setModelId] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);
  const [availableModels, setAvailableModels] = useState([]); // Предположим, что мы можем получить список моделей с бэкенда

  // При монтировании компонента можно сделать запрос на бэкенд за списком доступных моделей
  // useEffect(() => {
  //   axios.get('/api/get_models')
  //     .then(response => setAvailableModels(response.data.models))
  //     .catch(error => console.error(error));
  // }, []);

  const applyModel = () => {
    const data = new FormData();
    data.append('file', selectedFile);
    data.append('model_id', modelId);

    axios.post('/api/apply_model', data)
      .then(response => {
        setPredictionResult(response.data);
      })
      .catch(error => {
        console.error(error);
        alert('Failed to apply model.');
      });
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Apply a Trained Model</Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel id="model_select_label">Select Model</InputLabel>
            <Select
              labelId="model_select_label"
              value={modelId}
              onChange={(e) => setModelId(e.target.value)}
            >
              {availableModels.map((m) => (
                <MenuItem key={m.id} value={m.id}>{m.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6}>
          <Typography variant="body1">Upload New Data for Prediction</Typography>
          <input type="file" onChange={e => setSelectedFile(e.target.files[0])} />
        </Grid>

        <Grid item xs={12}>
          <Button variant="contained" color="primary" onClick={applyModel}>
            Get Predictions
          </Button>
        </Grid>

        {predictionResult && (
          <Grid item xs={12}>
            <Typography variant="body1">Prediction Result:</Typography>
            <pre>{JSON.stringify(predictionResult, null, 2)}</pre>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default ApplyModel;
