
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

# Group careers into broader categories for better prediction
career_mapping = {
    # Engineering & Technology
    'Software Developer': 'Technology',
    'Web Developer': 'Technology',
    'Game Developer': 'Technology',
    'IT Support Specialist': 'Technology',
    'IT Project Manager': 'Technology',
    'Data Analyst': 'Technology',
    'Database Administrator': 'Technology',
    'Database Analyst': 'Technology',
    'Software Quality Assurance Tester': 'Technology',
    'Biomedical Engineer': 'Engineering',
    'Aerospace Engineer': 'Engineering',
    'Mechanical Engineer': 'Engineering',
    'Civil Engineer': 'Engineering',
    'Environmental Engineer': 'Engineering',
    'Electrical Engineer': 'Engineering',
    'Industrial Engineer': 'Engineering',
    'Robotics Engineer': 'Engineering',
    'Electronics Design Engineer': 'Engineering',
    'Mechanical Designer': 'Engineering',
    'Construction Engineer': 'Engineering',
    
    # Healthcare
    'Physician': 'Healthcare',
    'Nurse': 'Healthcare',
    'Pediatric Nurse': 'Healthcare',
    'Pharmacist': 'Healthcare',
    'Physical Therapist': 'Healthcare',
    'Occupational Therapist': 'Healthcare',
    'Speech Therapist': 'Healthcare',
    'Speech Pathologist': 'Healthcare',
    'Dental Hygienist': 'Healthcare',
    'Pediatrician': 'Healthcare',
    'Chiropractor': 'Healthcare',
    'Radiologic Technologist': 'Healthcare',
    'Rehabilitation Counselor': 'Healthcare',
    
    # Science & Research
    'Research Scientist': 'Science',
    'Biologist': 'Science',
    'Environmental Scientist': 'Science',
    'Forensic Scientist': 'Science',
    'Wildlife Biologist': 'Science',
    'Marine Biologist': 'Science',
    'Zoologist': 'Science',
    'Biotechnologist': 'Science',
    'Biomedical Researcher': 'Science',
    'Astronomer': 'Science',
    'Geologist': 'Science',
    'Wildlife Conservationist': 'Science',
    'Forensic Psychologist': 'Science',
    'Forestry Technician': 'Science',
    'Public Health Analyst': 'Science',
    
    # Business & Finance
    'Accountant': 'Business',
    'Financial Analyst': 'Business',
    'Financial Planner': 'Business',
    'Financial Advisor': 'Business',
    'Financial Auditor': 'Business',
    'Tax Accountant': 'Business',
    'Investment Banker': 'Business',
    'Insurance Underwriter': 'Business',
    'Tax Collector': 'Business',
    'Marketing Manager': 'Business',
    'Marketing Coordinator': 'Business',
    'Marketing Analyst': 'Business',
    'Market Research Analyst': 'Business',
    'Market Researcher': 'Business',
    'Product Manager': 'Business',
    'Administrative Officer': 'Business',
    
    # Education & Social Services
    'Teacher': 'Education',
    'Elementary School Teacher': 'Education',
    'Human Resources Manager': 'Education',
    'HR Recruiter': 'Education',
    'Social Worker': 'Education',
    'Psychologist': 'Education',
    'Marriage Counselor': 'Education',
    'Genetic Counselor': 'Education',
    
    # Creative & Media
    'Artist': 'Creative',
    'Graphic Designer': 'Creative',
    'Fashion Designer': 'Creative',
    'Interior Designer': 'Creative',
    'Architect': 'Creative',
    'Musician': 'Creative',
    'Fashion Stylist': 'Creative',
    'Event Photographer': 'Creative',
    'Video Game Tester': 'Creative',
    'Film Director': 'Creative',
    
    # Legal & Government
    'Lawyer': 'Legal',
    'Human Rights Lawyer': 'Legal',
    'Diplomat': 'Legal',
    'Foreign Service Officer': 'Legal',
    'Police Officer': 'Legal',
    'Police Detective': 'Legal',
    'Customs and Border Protection Officer': 'Legal',
    
    # Communication & Media
    'Journalist': 'Communication',
    'Technical Writer': 'Communication',
    'Marketing Copywriter': 'Communication',
    'Public Relations Specialist': 'Communication',
    'Social Media Manager': 'Communication',
    'Advertising Executive': 'Communication',
    
    # Service & Sales
    'Salesperson': 'Service',
    'Real Estate Agent': 'Service',
    'Chef': 'Service',
    'Event Planner': 'Service',
    'Sports Coach': 'Service',
    'Air Traffic Controller': 'Service',
    'Airline Pilot': 'Service',
    'Quality Control Inspector': 'Service',
    'Urban Planner': 'Service'
}

# Apply career mapping
df['Career_Category'] = df['Career'].map(career_mapping)

# Remove rows where mapping failed
df = df.dropna(subset=['Career_Category'])

print("📊 Career Category distribution:\n", df["Career_Category"].value_counts())

# Define features and target (all 10 features)
feature_columns = [
    "O_score", "C_score", "E_score", "A_score", "N_score",
    "Numerical Aptitude", "Spatial Aptitude", "Perceptual Aptitude",
    "Abstract Reasoning", "Verbal Reasoning"
]

X = df[feature_columns]
y = df["Career_Category"]

print("📈 Feature statistics:")
print(X.describe())

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Scale features for better performance
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split (no stratification needed now with grouped categories)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# Train model with better hyperparameters
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=8,
    min_samples_split=3,
    min_samples_leaf=2,
    random_state=42,
    class_weight='balanced'
)
model.fit(X_train, y_train)

# Test model performance
y_pred = model.predict(X_test)
print("🎯 Model Accuracy:", accuracy_score(y_test, y_pred))
print("📊 Classification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_, zero_division=0))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("🔍 Feature Importance:")
print(feature_importance)

# Save model with scaler and career mapping
with open("career_model.pkl", "wb") as f:
    pickle.dump((model, label_encoder, scaler, career_mapping), f)

print("✅ Model, label encoder, scaler, and career mapping saved as 'career_model.pkl'")
