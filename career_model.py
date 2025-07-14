import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

# Load dataset with tab delimiter
df = pd.read_csv("dataset/career_data.csv", delimiter='\t')  # Fix here

# Clean up column names
df.columns = df.columns.str.strip()

# (Optional Debug)
print("🔍 Available Columns:", df.columns.tolist())

# Define features and target (only OCEAN scores to match quiz)
feature_columns = [
    "O_score", "C_score", "E_score", "A_score", "N_score"
]

X = df[feature_columns]
y = df["Career"]

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model
with open("career_model.pkl", "wb") as f:
    pickle.dump((model, label_encoder), f)

print("✅ Model trained and saved as 'career_model.pkl'")