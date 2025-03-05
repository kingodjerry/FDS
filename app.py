import os
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import logging
from datetime import datetime
import pandas as pd
from fraud_detection import FraudDetector

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# SQLite 데이터베이스 설정
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fraud_detection.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# 부정 거래 탐지기 초기화
fraud_detector = FraudDetector()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    from models import Transaction
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(100).all()
    return jsonify([{
        'id': t.id,
        'amount': t.amount,
        'timestamp': t.timestamp.isoformat(),
        'source': t.source_account,
        'destination': t.destination_account,
        'risk_score': t.risk_score,
        'risk_level': t.risk_level
    } for t in transactions])

@app.route('/api/upload', methods=['POST'])
def upload_transactions():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        df = pd.read_csv(file)
        from models import Transaction
        
        for _, row in df.iterrows():
            transaction = Transaction(
                amount=float(row['amount']),
                timestamp=datetime.now(),
                source_account=row['source_account'],
                destination_account=row['destination_account']
            )
            
            # 위험도 평가
            risk_score = fraud_detector.calculate_risk_score(transaction)
            transaction.risk_score = risk_score
            transaction.risk_level = fraud_detector.get_risk_level(risk_score)
            
            db.session.add(transaction)
        
        db.session.commit()
        return jsonify({'message': 'Transactions uploaded successfully'})
    
    except Exception as e:
        logging.error(f"Error uploading transactions: {str(e)}")
        return jsonify({'error': 'Error processing file'}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    from models import Transaction
    total_transactions = Transaction.query.count()
    high_risk = Transaction.query.filter_by(risk_level='HIGH').count()
    medium_risk = Transaction.query.filter_by(risk_level='MEDIUM').count()
    low_risk = Transaction.query.filter_by(risk_level='LOW').count()

    return jsonify({
        'total_transactions': total_transactions,
        'risk_distribution': {
            'high': high_risk,
            'medium': medium_risk,
            'low': low_risk
        }
    })

@app.route('/transaction/<int:transaction_id>')
def transaction_detail(transaction_id):
    from models import Transaction
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template('transaction_detail.html', transaction=transaction)

@app.route('/transactions/risk_level/<risk_level>')
def risk_level_transactions(risk_level):
    from models import Transaction

    # 위험도 레벨 매핑
    level_mapping = {
        'high': 'HIGH',
        'medium': 'MEDIUM',
        'low': 'LOW'
    }

    # URL 파라미터 검증
    if risk_level.lower() not in level_mapping:
        return "Invalid risk level", 400

    # 해당 위험도의 거래 목록 조회
    transactions = Transaction.query.filter_by(
        risk_level=level_mapping[risk_level.lower()]
    ).order_by(Transaction.timestamp.desc()).all()

    return render_template(
        'risk_level_transactions.html',
        transactions=transactions,
        risk_level=level_mapping[risk_level.lower()]
    )

with app.app_context():
    import models
    db.create_all()