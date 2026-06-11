from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
import joblib
import pandas as pd
import numpy as np
import io
import csv
from datetime import datetime
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'churnai_secret_2026'

model = joblib.load('../models/xgb_model.pkl')
scaler = joblib.load('../models/scaler.pkl')
columns = joblib.load('../models/columns.pkl')

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Priti@1234',
    'database': 'churn_db'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def save_user(username, email, password):
    conn = get_db()
    c = conn.cursor()
    hashed = generate_password_hash(password)
    c.execute('INSERT INTO users (username,email,password) VALUES (%s,%s,%s)',
              (username, email, hashed))
    conn.commit()
    c.close(); conn.close()

def get_user(username):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=%s', (username,))
    user = c.fetchone()
    c.close(); conn.close()
    return user

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def save_to_db(record):
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO predictions
        (time,tenure,monthly,contract,probability,result,user_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s)''',
        (record['time'], record['tenure'], record['monthly'],
         record['contract'], round(float(record['probability']),2),
         record['result'], session.get('user_id', 1)))
    conn.commit()
    c.close(); conn.close()

def load_from_db():
    conn = get_db()
    c = conn.cursor()
    uid = session.get('user_id', 1)
    c.execute('''SELECT time,tenure,monthly,contract,
                 probability,result FROM predictions
                 WHERE user_id=%s ORDER BY id DESC''', (uid,))
    rows = c.fetchall()
    c.close(); conn.close()
    return [{'time':r[0],
             'tenure':int(r[1]),
             'monthly':round(float(r[2]),2),
             'contract':r[3],
             'probability':round(float(r[4]),2),
             'result':r[5]}
            for r in rows]

def make_prediction(tenure, monthly, total, senior, contract):
    input_dict = {col: 0 for col in columns}
    input_dict['tenure'] = tenure
    input_dict['MonthlyCharges'] = monthly
    input_dict['TotalCharges'] = total
    input_dict['SeniorCitizen'] = senior
    if f'Contract_{contract}' in input_dict:
        input_dict[f'Contract_{contract}'] = 1
    input_df = pd.DataFrame([input_dict])
    input_scaled = scaler.transform(input_df)
    prediction = int(model.predict(input_scaled)[0])
    probability = round(float(
        model.predict_proba(input_scaled)[0][1]) * 100, 2)
    return prediction, probability

def get_ai_explanation(tenure, monthly, total, contract, probability):
    reasons = []
    if contract == 'Month-to-month':
        reasons.append("📌 Month-to-month contract — easiest to cancel")
    if monthly > 70:
        reasons.append("💰 High monthly charges increase churn risk")
    if tenure < 12:
        reasons.append("⏱️ New customer — loyalty not yet established")
    if total < monthly * 6:
        reasons.append("📉 Low total spend suggests short relationship")
    if probability > 60:
        reasons.append("🔴 Very high risk score detected by model")
    if not reasons:
        reasons.append("✅ Customer shows strong loyalty indicators")
        reasons.append("📊 Long tenure and stable contract type")
    return reasons

def get_retention_strategies(tenure, monthly, contract, probability):
    strategies = []
    if probability > 60:
        strategies.append({
            'icon': '🎁',
            'title': 'Offer Loyalty Discount',
            'desc': 'Provide 20-30% discount on next 3 months bill',
            'priority': 'HIGH'
        })
    if contract == 'Month-to-month':
        strategies.append({
            'icon': '📋',
            'title': 'Upgrade to Annual Contract',
            'desc': 'Offer free months if customer switches to yearly plan',
            'priority': 'HIGH'
        })
    if monthly > 70:
        strategies.append({
            'icon': '💳',
            'title': 'Downgrade Plan Option',
            'desc': 'Suggest a lower cost plan that still meets needs',
            'priority': 'MEDIUM'
        })
    if tenure < 12:
        strategies.append({
            'icon': '🤝',
            'title': 'Assign Dedicated Support',
            'desc': 'Personal account manager for first year customers',
            'priority': 'MEDIUM'
        })
    strategies.append({
        'icon': '📞',
        'title': 'Proactive Outreach Call',
        'desc': 'Schedule a satisfaction call within 48 hours',
        'priority': 'HIGH' if probability > 50 else 'LOW'
    })
    strategies.append({
        'icon': '⭐',
        'title': 'Loyalty Rewards Program',
        'desc': 'Enroll customer in points-based rewards system',
        'priority': 'LOW'
    })
    return strategies

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and check_password_hash(user[3], password):
            session['user'] = username
            session['user_id'] = user[0]
            return redirect(url_for('home'))
        return render_template('login.html', error='Invalid credentials!')
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        try:
            save_user(request.form['username'],
                     request.form['email'],
                     request.form['password'])
            return redirect(url_for('login'))
        except:
            return render_template('signup.html',
                error='Username/email already exists!')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    history = load_from_db()
    return render_template('index.html',
                         history=history,
                         probability=None,
                         result=None,
                         reasons=[],
                         strategies=[],
                         username=session.get('user'))

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    form = request.form
    tenure = int(form['tenure'])
    monthly = float(form['MonthlyCharges'])
    total = float(form['TotalCharges'])
    senior = int(form['SeniorCitizen'])
    contract = form['Contract']

    prediction, probability = make_prediction(
        tenure, monthly, total, senior, contract)

    result = "⚠️ Customer is likely to CHURN" if prediction == 1 \
             else "✅ Customer will NOT Churn"
    result_short = "CHURN" if prediction == 1 else "SAFE"
    reasons = get_ai_explanation(
        tenure, monthly, total, contract, probability)
    strategies = get_retention_strategies(
        tenure, monthly, contract, probability)

    record = {
        'time': datetime.now().strftime("%H:%M:%S"),
        'tenure': tenure,
        'monthly': monthly,
        'contract': contract,
        'probability': probability,
        'result': result_short
    }
    save_to_db(record)
    history = load_from_db()

    return render_template('index.html',
                         result=result,
                         probability=probability,
                         history=history,
                         reasons=reasons,
                         strategies=strategies,
                         username=session.get('user'))

@app.route('/dashboard')
@login_required
def dashboard():
    history = load_from_db()
    return render_template('dashboard.html',
                         history=history,
                         username=session.get('user'))

@app.route('/segmentation')
@login_required
def segmentation():
    history = load_from_db()
    segments = []
    for h in history:
        prob = h['probability']
        if prob >= 60:
            h['segment_label'] = '🔴 High Risk'
        elif prob >= 30:
            h['segment_label'] = '🟡 Medium Risk'
        else:
            h['segment_label'] = '🟢 Low Risk'
        segments.append(h)
    return render_template('segmentation.html',
                         segments=segments,
                         username=session.get('user'))

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['csvfile']
    df = pd.read_csv(file)
    results = []
    for _, row in df.iterrows():
        try:
            pred, prob = make_prediction(
                int(row.get('tenure', 0)),
                float(row.get('MonthlyCharges', 0)),
                float(row.get('TotalCharges', 0)),
                int(row.get('SeniorCitizen', 0)),
                str(row.get('Contract', 'Month-to-month'))
            )
            record = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'tenure': int(row.get('tenure', 0)),
                'monthly': float(row.get('MonthlyCharges', 0)),
                'contract': str(row.get('Contract', 'N/A')),
                'probability': prob,
                'result': 'CHURN' if pred == 1 else 'SAFE'
            }
            results.append(record)
            save_to_db(record)
        except:
            continue
    history = load_from_db()
    return render_template('index.html',
                         history=history,
                         bulk_results=results,
                         probability=None,
                         result=None,
                         reasons=[],
                         strategies=[],
                         username=session.get('user'))

@app.route('/dashboard-data')
@login_required
def dashboard_data():
    history = load_from_db()
    if not history:
        return jsonify({'churn':0,'safe':0,'avg_prob':0,
                       'contracts':{},'timeline':[],'monthly_avg':0})
    churn = sum(1 for h in history if h['result']=='CHURN')
    safe = len(history) - churn
    avg_prob = round(
        sum(h['probability'] for h in history)/len(history), 2)
    contracts = {}
    for h in history:
        c = h['contract']
        contracts[c] = contracts.get(c, 0) + 1
    timeline = [{'time':h['time'],'prob':h['probability']}
                for h in history[-10:]]
    monthly_avg = round(
        sum(h['monthly'] for h in history)/len(history), 2)
    return jsonify({'churn':churn,'safe':safe,
                   'avg_prob':avg_prob,
                   'contracts':contracts,
                   'timeline':timeline,
                   'monthly_avg':monthly_avg})

@app.route('/export')
@login_required
def export():
    history = load_from_db()
    if not history:
        return "No data", 400
    output = io.StringIO()
    writer = csv.DictWriter(output,
        fieldnames=['time','tenure','monthly',
                   'contract','probability','result'])
    writer.writeheader()
    writer.writerows(history)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='churn_report.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)