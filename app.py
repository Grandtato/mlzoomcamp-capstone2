import pickle
from flask import Flask, request, jsonify

# 1. Load the model
with open("model.bin", "rb") as f_in:
    dv, model = pickle.load(f_in)

app = Flask("ci-risk")
from flask import jsonify


@app.get("/")
def home():
    return jsonify({"message": "CI Breakage Risk Scorer is running. Use POST /predict"})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    run_data = request.get_json()

    # 2. Preprocess (Vectorize)
    # The input JSON must have: repo, author, hour, day_of_week, run_attempt
    X = dv.transform([run_data])

    # 3. Predict
    y_pred = model.predict_proba(X)[0, 1]
    breakage = y_pred >= 0.5

    result = {"risk_score": float(y_pred), "high_risk": bool(breakage)}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)

## ✅ How to Use the API

This service is an API (not a UI). To get a prediction, send a **POST** request to `/predict` with JSON.

### Example request (Cloud Run)


curl -s -X POST "https://capstone2-risk-897828472012.us-central1.run.app/predict" \
  -H "Content-Type: application/json" \
  -d '{"repo":"DataTalksClub/machine-learning-zoomcamp","author":"someone","hour":21,"day_of_week":2,"run_attempt":1}'

##example rsponse
{"high_risk":false,"risk_score":0.07486680563799615}

##Field meanings

#repo (string): GitHub repo in owner/name format

#author (string): GitHub username/login of the actor

#hour (int): hour of day (0–23)

#day_of_week (int): 0=Mon … 6=Sun

#run_attempt (int): workflow attempt number (1+)