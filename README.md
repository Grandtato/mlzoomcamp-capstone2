# CI Breakage Risk Scorer (Capstone 2)

## 📌 Problem Statement
In modern software development, **Continuous Integration (CI)** failures are costly bottlenecks. When a developer pushes code that breaks the build:
1.  **Productivity Drops:** The entire team is blocked from merging until the build is fixed.
2.  **Resource Waste:** CI runners (GitHub Actions, Jenkins) burn expensive compute time on doomed builds.
3.  **Release Delays:** Critical hotfixes get stuck behind broken pipelines.

**The Solution:**
This project deploys a Machine Learning service that predicts the **probability of a CI failure** *before* the code is even run. By analyzing historical metadata (repository stability, author history, time of day, and retry patterns), we can flag "High Risk" commits for extra review or deprioritized testing.

---

## 🏗️ Project Architecture
The solution follows a complete end-to-end ML pipeline:
1.  **Data Collection:** Custom scrapers (`discover_repos.py` & `extract_runs.py`) fetch real-world CI history from the GitHub API.
2.  **Data Analysis:** Exploratory Data Analysis (EDA) identifies key failure drivers (e.g., "fatigue pushes" late at night).
3.  **Modeling:** Two models (Logistic Regression vs. Random Forest) were trained and compared to maximize AUC.
4.  **Deployment:** The winning model is containerized with Docker and served via a Flask API.

---

## 📊 Data Source
I constructed a **custom dataset** specifically for this problem rather than using a pre-made CSV.
- **Source:** GitHub REST API (Actions/Workflow Runs).
- **Scope:** **144 Active Repositories** (including major open source projects like `huggingface`, `psf`, `tiangolo`).
- **Volume:** **31,000+** CI Workflow Runs extracted.
- **Target Variable:** `conclusion` (Success vs. Failure).

---

## 🧠 Methodology & Model Training
I evaluated two distinct model architectures to ensure robustness.

### 1. Feature Engineering
- **Categorical:** `repository_name` (captures project complexity), `author_id` (captures developer patterns).
- **Numerical:** `hour_of_day`, `day_of_week` (captures temporal risk factors), `run_attempt` (captures panic retries).

### 2. Model Selection
| Model | AUC Score | Verdict |
|-------|-----------|---------|
| **Logistic Regression** | **0.8504** | ✅ **Selected** (Best performance, fast inference, lightweight). |
| Random Forest | 0.8327 | Strong baseline, but slightly overfit on high-cardinality features. |

*Note: The final model is exported as `model.bin` using `pickle` for production use.*

---

## 🚀 How to Run (Dockerized)
This project is fully containerized for easy deployment on any machine.

### Prerequisites
- Docker Desktop (or Docker Engine) installed.

### 1. Build the Image
```bash
docker build -t capstone2-risk .