import pickle
from flask import Flask, request, jsonify

# 1. Load the model
with open("model.bin", "rb") as f_in:
    dv, model = pickle.load(f_in)

app = Flask("ci-risk")


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
