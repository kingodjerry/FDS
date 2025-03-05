import random
from datetime import datetime, timedelta
import numpy as np
from app import app, db
from models import Transaction
from fraud_detection import FraudDetector

def generate_account_number():
    """계좌번호 생성"""
    return f"{random.randint(100, 999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

def generate_amount():
    """거래금액 생성 (로그 정규 분포 사용)"""
    return round(np.exp(np.random.normal(12, 1.5)))  # 대부분 10만원 ~ 1000만원 사이

def generate_dummy_transactions(num_transactions=100):
    """더미 거래 데이터 생성"""
    fraud_detector = FraudDetector()
    accounts = [generate_account_number() for _ in range(20)]  # 20개의 고유 계좌
    
    now = datetime.now()
    transactions = []
    
    for _ in range(num_transactions):
        # 거래 기본 정보 생성
        amount = generate_amount()
        timestamp = now - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # 출발지와 도착지 계좌는 서로 다르게
        source = random.choice(accounts)
        destination = random.choice([acc for acc in accounts if acc != source])
        
        # 거래 객체 생성
        transaction = Transaction(
            amount=amount,
            timestamp=timestamp,
            source_account=source,
            destination_account=destination
        )
        
        # 위험도 평가
        risk_score = fraud_detector.calculate_risk_score(transaction)
        transaction.risk_score = risk_score
        transaction.risk_level = fraud_detector.get_risk_level(risk_score)
        
        transactions.append(transaction)
    
    return transactions

if __name__ == "__main__":
    with app.app_context():
        # 기존 데이터 삭제
        Transaction.query.delete()
        
        # 새로운 더미 데이터 생성 및 저장
        transactions = generate_dummy_transactions(100)
        db.session.bulk_save_objects(transactions)
        db.session.commit()
        
        print(f"{len(transactions)}개의 더미 거래 데이터가 생성되었습니다.")
