// src/components/TaskStatus.js

import React, { useState, useEffect } from 'react';
import { Typography, Button } from '@material-ui/core';
import axios from 'axios';

function TaskStatus({ taskId }) {
  const [status, setStatus] = useState('Unknown');

  useEffect(() => {
    const interval = setInterval(() => {
      axios.get(`/api/task_status/${taskId}`)
        .then(response => {
          setStatus(response.data.status);
        })
        .catch(error => {
          console.error(error);
        });
    }, 5000);

    return () => clearInterval(interval);
  }, [taskId]);

  return (
    <div>
      <Typography variant="h6">Task Status</Typography>
      <Typography>Status: {status}</Typography>
    </div>
  );
}

export default TaskStatus;
