// src/components/PipelineForm.js

import React, { useState } from "react";
import { Button, TextField, Typography } from "@material-ui/core";
import axios from "axios";

function PipelineForm({ fileId, setTaskId, setReportId  }) {
    const [params, setParams] = useState({
        target_column: "",
        task_type: "classification",
        sep: ",",
        dataset_name: "dataset",
    });

    const runPipeline = () => {
        axios
            .post(`/run_pipeline/${fileId}`, params)
            .then((response) => {
                setTaskId(response.data.task_id);
                setReportId(response.data.report_id); // Добавлено
                alert("Pipeline started!");
            })
            .catch((error) => {
                console.error(error);
                alert("Failed to start pipeline.");
            });
    };

    const handleChange = (e) => {
        setParams({ ...params, [e.target.name]: e.target.value });
    };

    return (
        <div>
            <Typography variant="h6">Configure Pipeline</Typography>
            <TextField
                label="Target Column"
                name="target_column"
                value={params.target_column}
                onChange={handleChange}
                fullWidth
                margin="normal"
            />
            <TextField
                label="Task Type"
                name="task_type"
                value={params.task_type}
                onChange={handleChange}
                fullWidth
                margin="normal"
            />
            <TextField
                label="Separator"
                name="sep"
                value={params.sep}
                onChange={handleChange}
                fullWidth
                margin="normal"
            />
            <TextField
                label="Dataset Name"
                name="dataset_name"
                value={params.dataset_name}
                onChange={handleChange}
                fullWidth
                margin="normal"
            />
            <Button variant="contained" color="primary" onClick={runPipeline}>
                Run Pipeline
            </Button>
        </div>
    );
}

export default PipelineForm;
