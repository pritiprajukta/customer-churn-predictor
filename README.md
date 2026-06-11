# 🔍 ChurnAI Pro — Customer Churn Intelligence Platform

> AI-powered web app to predict, analyze and prevent customer churn with 83.6% accuracy



![Python](https://img.shields.io/badge/Python-3.14-blue)




![Flask](https://img.shields.io/badge/Flask-Web%20App-green)




![XGBoost](https://img.shields.io/badge/XGBoost-ML%20Model-orange)




![MySQL](https://img.shields.io/badge/MySQL-Database-blue)



## 🚀 Live Demo
[Click here to view](https://churnai-pro-jatm.onrender.com)

## ✨ Features
- 🔐 Login/Signup Authentication
- ⚡ Single Customer Churn Prediction
- 📈 Animated Risk Score Gauge
- 🤖 AI Explanation for predictions
- 🎯 Retention Strategies suggestions
- 📤 Bulk CSV Upload (predict 100s at once)
- 📊 Power BI Style KPI Dashboard
- 🗺️ Customer Segmentation (K-Means)
- 🌙 Dark/Light Mode toggle
- 📧 Export predictions as CSV
- 💾 MySQL database integration

## 🛠️ Tech Stack
| Layer | Technology |
|---|---|
| ML Model | XGBoost (AUC-ROC: 83.6%) |
| Backend | Python Flask |
| Database | MySQL |
| Frontend | HTML, CSS, Chart.js |
| Data Processing | Pandas, NumPy, Scikit-learn |

## 📁 Project Structure

​```
customer-churn-predictor/
├── notebooks/
│   ├── 01_EDA.ipynb
│   ├── 02_Preprocessing.ipynb
│   └── 03_Model_Training.ipynb
├── app/
│   ├── app.py
│   └── templates/
│       ├── index.html
│       ├── login.html
│       ├── signup.html
│       ├── dashboard.html
│       └── segmentation.html
├── data/
│   └── churn_raw.csv
└── requirements.txt
​```

## 🚀 How to Run
```bash
# Clone repo
git clone https://github.com/pritiprajukta/customer-churn-predictor.git

# Install dependencies
pip install -r requirements.txt

# Run app
cd app
python app.py
```

📊 Model Performance
Algorithm: XGBoost Classifier
AUC-ROC Score: 83.6%
Class Imbalance: Fixed with SMOTE
Features: 30 engineered features
👩‍💻 Developer
Priti Prajukta
🎓 B.Tech Data Science, Centurion University
💼 LinkedIn: linkedin.com/in/priti-prajukta
🐙 GitHub: github.com/pritiprajukta