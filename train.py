import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression

# Config
OUTPUT_FILE = "model.bin"
C_PARAM = 1.0

print("1. Loading data...")
df = pd.read_csv("data/runs.csv")

# 2. Cleaning (Must match Notebook exactly)
valid_outcomes = ["success", "failure"]
df = df[df["conclusion"].isin(valid_outcomes)].copy()
df["target"] = (df["conclusion"] == "failure").astype(int)

df["created_at"] = pd.to_datetime(df["created_at"])
df["hour"] = df["created_at"].dt.hour
df["day_of_week"] = df["created_at"].dt.dayofweek

# 3. Preparation
categorical = ["repo", "author"]
numerical = ["hour", "day_of_week", "run_attempt"]

# We train on Full Train (80%) to maximize performance
df_full_train, df_test = train_test_split(df, test_size=0.2, random_state=1)
y_train = df_full_train.target.values

# Vectorize
dv = DictVectorizer(sparse=False)
train_dicts = df_full_train[categorical + numerical].to_dict(orient="records")
X_train = dv.fit_transform(train_dicts)

# 4. Train Final Model
print(f"2. Training Logistic Regression (C={C_PARAM})...")
model = LogisticRegression(solver="liblinear", C=C_PARAM)
model.fit(X_train, y_train)

# 5. Save
print(f"3. Saving model to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, "wb") as f_out:
    pickle.dump((dv, model), f_out)

print("Done.")
