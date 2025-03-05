import numpy as np
from sklearn.ensemble import IsolationForest

class FraudDetector:
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.training_data = []

    def calculate_risk_score(self, transaction):
        # 간단한 규칙 기반 위험도 계산
        amount = transaction.amount
        
        # 금액 기반 기본 위험도
        if amount > 10000000:  # 1천만원 초과
            base_score = 0.8
        elif amount > 5000000:  # 500만원 초과
            base_score = 0.6
        elif amount > 1000000:  # 100만원 초과
            base_score = 0.4
        else:
            base_score = 0.2

        # 랜덤 노이즈 추가 (실제 구현에서는 더 복잡한 로직 사용)
        noise = np.random.normal(0, 0.1)
        risk_score = min(max(base_score + noise, 0), 1)
        
        return float(risk_score)

    def get_risk_level(self, risk_score):
        if risk_score >= 0.7:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'

    def train_model(self, transactions):
        # 실제 구현에서는 더 많은 피처 사용
        features = [[t.amount] for t in transactions]
        self.isolation_forest.fit(features)

    def detect_anomalies(self, transactions):
        features = [[t.amount] for t in transactions]
        predictions = self.isolation_forest.predict(features)
        return [pred == -1 for pred in predictions]  # -1은 이상치를 나타냄
