import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from collections import defaultdict
import os

# Define paths
QUESTIONS_PATH = "ml/career_quiz_questions.json"
MODEL_PATH = "ml/model.pkl"
DATASET_PATH = "ml/hikari006_dataset.csv"

# Load questions
with open(QUESTIONS_PATH, "r") as f:
    questions = json.load(f)

# Define traits
personality_traits = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
aptitude_traits = [f"aptitude_{i}" for i in range(1, 7)]
all_features = personality_traits + aptitude_traits

# Load or train model
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    df = pd.read_csv(DATASET_PATH)
    X = df[all_features]
    y = df["recommended_field"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)


def get_feature_vector(user_responses):
    """Converts quiz responses to Hikari006 feature vector."""
    trait_scores = {trait: {"sum": 0, "weight": 0} for trait in personality_traits}
    aptitude_correct = {trait: 0 for trait in aptitude_traits}

    for q in questions:
        qid = str(q["id"])
        cat = q["category"]
        wt = q["weight"]
        if qid not in user_responses:
            continue
        ans = user_responses[qid]

        if q["type"] == "likert":
            trait_scores[cat]["sum"] += int(ans) * wt
            trait_scores[cat]["weight"] += wt

        elif q["type"] == "mcq":
            if str(ans).strip().lower() == str(q["correct_answer"]).strip().lower():
                aptitude_correct[cat] += 1

    vector = []
    for trait in personality_traits:
        total = trait_scores[trait]["sum"]
        weight = trait_scores[trait]["weight"]
        avg = total / weight if weight else 0
        vector.append(round(avg / 5, 2))

    for trait in aptitude_traits:
        vector.append(round(aptitude_correct[trait] / 2, 2))

    return np.array(vector).reshape(1, -1)


def predict_career(feature_vector):
    """Predicts the career path using the trained ML model."""
    return model.predict(feature_vector)[0]
