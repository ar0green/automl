import streamlit as st
import requests
import json

API_BASE = "http://backend:8000/"

def upload_data_page():
    st.title("Upload Data")
    uploaded_file = st.file_uploader("Choose a file", type=["csv"])
    if uploaded_file is not None:
        if st.button("Upload"):
            files = {'file': (uploaded_file.name, uploaded_file, 'text/csv')}
            response = requests.post(f"{API_BASE}/upload_data", files=files)
            if response.status_code == 200:
                data = response.json()
                file_id = data.get("file_id")
                if file_id:
                    st.success(f"File uploaded successfully! File ID: {file_id}")
                    st.session_state["file_id"] = file_id
                else:
                    st.error("File uploaded but no file_id returned")
            else:
                st.error("Failed to upload file.")

def configure_pipeline_page():
    st.title("Configure Pipeline")

    datasets_resp = requests.get(f"{API_BASE}/list_datasets")
    if datasets_resp.status_code == 200:
        datasets = datasets_resp.json().get("datasets", [])
        if len(datasets) == 0:
            st.warning("No datasets found. Please upload a dataset first.")
            return
        dataset_options = {f"{d['filename']} ({d['file_id']})": d['file_id'] for d in datasets}
        selected_dataset = st.selectbox("Select Dataset", list(dataset_options.keys()))
        file_id = dataset_options[selected_dataset]

        cols_resp = requests.get(f"{API_BASE}/get_dataset_info?file_id={file_id}")
        columns = []
        if cols_resp.status_code == 200:
            columns = cols_resp.json().get("columns", [])

        task_type = st.selectbox("Task Type", ["classification", "regression"])
        sep = st.text_input("Separator", value=",")
        dataset_name = st.text_input("Dataset Name", value="dataset")
        model_name = st.selectbox("Model Name", ["Random Forest", "Logistic Regression", "XGBoost", "LightGBM"])
        target_column = st.selectbox("Target Column", columns)

        if st.button("Run Pipeline"):
            params = {
                "target_column": target_column,
                "task_type": task_type,
                "sep": sep,
                "dataset_name": dataset_name,
                "model_name": model_name
            }
            run_resp = requests.post(f"{API_BASE}/run_pipeline/{file_id}", json=params)
            if run_resp.status_code == 200:
                data = run_resp.json()
                task_id = data.get("task_id")
                report_id = data.get("report_id")
                if task_id and report_id:
                    st.success(f"Pipeline started! Task ID: {task_id}, Report ID: {report_id}")
                else:
                    st.error("Pipeline started but no task_id/report_id returned")
            else:
                st.error("Failed to start pipeline.")
    else:
        st.error("Failed to load datasets list.")

@st.fragment(run_every='10s')
def pipelines_status_page():
    st.title("Pipelines Status")

    if st.button("Refresh"):
        st.rerun(scope='fragment')

    resp = requests.get(f"{API_BASE}/list_pipelines")
    if resp.status_code == 200:
        pipelines = resp.json().get("pipelines", [])
        if len(pipelines) == 0:
            st.info("No pipelines found.")
            return

        for p in pipelines:
            with st.expander(f"Task ID: {p['task_id']} | Status: {p['status']}"):
                st.write(f"Report ID: {p['report_id']}")
                st.write(f"Dataset: {p['dataset_name']}, Model: {p['model_name']}")
                st.write(f"Created At: {p['created_at']}")
                if st.button(f"View Report {p['report_id']}", key=p['report_id']):
                    r = requests.get(f"{API_BASE}/download_report/{p['report_id']}")
                    if r.status_code == 200:
                        report_data = r.json()
                        st.json(report_data)
                    else:
                        st.error("Failed to get report.")
    else:
        st.error("Failed to list pipelines.")

def apply_model_page():
    st.title("Apply Model")

    resp = requests.get(f"{API_BASE}/list_pipelines")
    model_dict = {}
    model_details = {}
    if resp.status_code == 200:
        pipelines = resp.json().get("pipelines", [])
        for p in pipelines:
            if p['status'].lower() == 'completed':
                label = f"{p['model_name']} ({p['report_id']})"
                model_dict[label] = p['report_id']
                model_details[p['report_id']] = p

    if len(model_dict) == 0:
        st.info("No completed pipelines found. Please run a pipeline first.")
        return

    selected_model_label = st.selectbox("Select a Completed Model", list(model_dict.keys()))
    report_id = model_dict[selected_model_label]

    selected_model_info = model_details.get(report_id)
    if selected_model_info:
        st.write("**Model Info:**")
        st.write(f"- Dataset: {selected_model_info['dataset_name']}")
        st.write(f"- Created At: {selected_model_info['created_at']}")
        st.write(f"- Task ID: {selected_model_info['task_id']}")

    mode = st.radio("Input Mode", ["Upload File", "Enter JSON"])

    if mode == "Upload File":
        uploaded_file = st.file_uploader("Upload new data for prediction", type=["json"])
        if uploaded_file and st.button("Get Predictions"):
            files = {'file': (uploaded_file.name, uploaded_file, 'text/csv')}
            data = {'report_id': report_id}
            pred_resp = requests.post(f"{API_BASE}/apply_model", files=files, data=data)
            if pred_resp.status_code == 200:
                preds = pred_resp.json()
                st.write("Predictions:")
                st.json(preds)
            else:
                st.error("Failed to apply model.")
    else:
        json_input = st.text_area("Enter JSON data for prediction", value='{"examples": [ ... ]}')
        if st.button("Get Predictions"):
            try:
                json_data = json.loads(json_input)
            except json.JSONDecodeError:
                st.error("Invalid JSON")
                return
            pred_resp = requests.post(f"{API_BASE}/apply_model", json={"report_id": report_id, "data": json_data})
            if pred_resp.status_code == 200:
                preds = pred_resp.json()
                st.write("Predictions:")
                st.json(preds)
            else:
                st.error("Failed to apply model.")

def main():
    st.title("AutoML Service")

    tabs = st.tabs(["Upload Data", "Configure Pipeline", "Pipelines Status", "Apply Model"])
    with tabs[0]:
        upload_data_page()
    with tabs[1]:
        configure_pipeline_page()
    with tabs[2]:
        pipelines_status_page()
    with tabs[3]:
        apply_model_page()

if __name__ == "__main__":
    main()
