# CI Breakage Risk Scorer (Capstone 2)

## 📌 Problem Statement
In modern software development, **Continuous Integration (CI)** failures are costly bottlenecks. When a developer pushes code that breaks the build:

1. **Productivity drops:** teams get blocked from merging until the build is fixed  
2. **Resource waste:** CI runners burn compute time on failing pipelines  
3. **Release delays:** hotfixes and features get stuck behind broken pipelines

### The Solution
This project builds and deploys a Machine Learning service that predicts the **probability of a CI failure** *before* the workflow completes.  
By learning from historical GitHub Actions runs (repository patterns, author patterns, time-of-day effects, and retry behavior), we can flag **high-risk runs** for extra review or early investigation.


## 🏗️ Project Architecture
End-to-end ML pipeline:

1. **Data Collection:** `discover_repos.py` + `extract_runs.py` fetch GitHub Actions history via the GitHub API  
2. **EDA:** `notebook.ipynb` explores target imbalance and failure patterns  
3. **Modeling:** Logistic Regression vs Random Forest + hyperparameter tuning (AUC comparison)  
4. **Deployment:** Flask API (`app.py`) serves predictions; packaged in Docker (`Dockerfile`)


## 📊 Data Source
I constructed a custom dataset (not a pre-made CSV):

- **Source:** GitHub REST API (Actions / Workflow Runs)
- **Scope:** ~144 active repositories (examples: `huggingface`, `psf`, `tiangolo`)
- **Volume:** 31,000+ workflow runs
- **Target:** `conclusion` mapped to `target` (0=success, 1=failure)



## 📈 EDA Highlights (Notebook)
The dataset is **imbalanced** (failures are the minority class), and failure probability varies by time-of-day (e.g., late-night hours show higher failure rate in some repos).

Add these images to your repo under `images/` and update the links below:
- `images/target_distribution.png`
- `images/failure_by_hour.png`

![Target distribution](images/target_distribution.png)  
![Failure rate by hour](images/failure_by_hour.png)

> Notebook: `notebook.ipynb`



## 🧠 Methodology & Model Training

### 1) Feature Engineering
- **Categorical:** `repo`, `author`
- **Numerical:** `hour`, `day_of_week`, `run_attempt`

### 2) Model Selection
Trained and compared:
- **Logistic Regression (linear baseline)**
- **Random Forest (tree-based challenger)**

### 3) Hyperparameter Tuning (AUC on validation)
- **Random Forest:** tuned `max_depth` over **[5, 10, 15, 20]**  
  - Best: **max_depth = 15** (AUC ≈ **0.8498**)
- **Logistic Regression:** tuned `C` over **[0.01, 0.1, 1.0, 10.0]**  
  - Best: **C = 10.0** (AUC ≈ **0.8549**)

**Final model (production):** Logistic Regression (best AUC + fast inference)



## 📦 Local Setup (venv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


##☁️ Cloud Deployment (Google Cloud Run)

Service URL:
https://capstone2-risk-897828472012.us-central1.run.app

Test it:

curl -s -X POST "https://capstone2-risk-897828472012.us-central1.run.app/predict" \
  -H "Content-Type: application/json" \
  -d '{"repo":"DataTalksClub/machine-learning-zoomcamp","author":"someone","hour":21,"day_of_week":2,"run_attempt":1}'


Example response:

{"high_risk":false,"risk_score":0.07486680563799615}