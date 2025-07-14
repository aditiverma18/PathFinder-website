import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import pickle
import numpy as np

# Load dataset with tab delimiter
df = pd.read_csv("dataset/career_data.csv", delimiter='\t')

# Clean up column names
df.columns = df.columns.str.strip()

# Debug info
print("🔍 Available Columns:", df.columns.tolist())
print("📊 Dataset shape:", df.shape)
print("🎯 Career distribution:\n", df["Career"].value_counts())

# Define features and target (all 10 features)
feature_columns = [
    "O_score", "C_score", "E_score", "A_score", "N_score",
    "Numerical Aptitude", "Spatial Aptitude", "Perceptual Aptitude",
    "Abstract Reasoning", "Verbal Reasoning"
]

X = df[feature_columns]
y = df["Career"]

print("📈 Feature statistics:")
print(X.describe())

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Scale features for better performance
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split (remove stratification due to small class sizes)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# Train model with better hyperparameters
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    class_weight='balanced'
)
model.fit(X_train, y_train)

# Test model performance
y_pred = model.predict(X_test)
print("🎯 Model Accuracy:", accuracy_score(y_test, y_pred))
print("📊 Classification Report:")
# Get unique labels in test set to avoid mismatch
test_labels = sorted(list(set(y_test) | set(y_pred)))
test_class_names = [label_encoder.classes_[i] for i in test_labels]
print(classification_report(y_test, y_pred, labels=test_labels, target_names=test_class_names, zero_division=0))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("🔍 Feature Importance:")
print(feature_importance)

# Save model with scaler
with open("career_model.pkl", "wb") as f:
    pickle.dump((model, label_encoder, scaler), f)

print("✅ Model, label encoder, and scaler saved as 'career_model.pkl'")