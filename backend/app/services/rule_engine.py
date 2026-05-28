import structlog
from typing import Dict, Any
from backend.app.schemas.transaction import TransactionCreate
from backend.app.services.feed_ingestion import feed_service

logger = structlog.get_logger(__name__)

class RuleEngine:
    def __init__(self):
        # Base weights for each rule
        self.weights = {
            "excessive_velocity": 0.2,
            "repeated_failed": 0.15,
            "dormant_activation": 0.25,
            "high_fan_out": 0.3,
            "geo_anomaly": 0.2,
            "blacklisted_entity": 0.5,
            "rapid_cash_out": 0.35,
        }

    def evaluate(self, tx: TransactionCreate, historical_context: Dict[str, Any]) -> float:
        """
        Evaluates a transaction against heuristic rules.
        Returns a normalized score between 0.0 and 1.0.
        """
        score = 0.0
        
        # 1. Excessive Velocity (e.g., > 10 txs in 5 mins)
        velocity_count = historical_context.get("velocity_5m", 0)
        if velocity_count > 10:
            score += self.weights["excessive_velocity"]
            
        # 2. Repeated Failed Transfers
        failed_count = historical_context.get("failed_24h", 0)
        if failed_count > 3:
            score += self.weights["repeated_failed"]
            
        # 3. Dormant Account Activation
        days_since_last_tx = historical_context.get("days_since_last_tx", 0)
        if days_since_last_tx > 90 and tx.amount > 5000:
            score += self.weights["dormant_activation"]
            
        # 4. High Fan-out Behavior
        fan_out = historical_context.get("fan_out_24h", 0)
        if fan_out > 15:
            score += self.weights["high_fan_out"]
            
        # 5. Geo Anomaly (e.g., Impossible travel)
        # Mocked checking if IP is blacklisted or geo shifts rapidly
        if historical_context.get("geo_shift_flag", False):
            score += self.weights["geo_anomaly"]
            
        # 6. Blacklisted Entity Interaction
        if feed_service.is_blacklisted(tx.sender_account_id) or \
           feed_service.is_blacklisted(tx.receiver_account_id) or \
           (tx.ip_address and feed_service.is_blacklisted(tx.ip_address)) or \
           (tx.device_id and feed_service.is_blacklisted(tx.device_id)):
            score += self.weights["blacklisted_entity"]
            
        # 7. Rapid Cash-out Pattern
        cash_out_ratio = historical_context.get("cash_out_ratio", 0.0)
        if cash_out_ratio > 0.9 and tx.amount > 10000:
            score += self.weights["rapid_cash_out"]
            
        # Ensure score is capped at 1.0
        final_score = min(score, 1.0)
        logger.debug(f"Rule Engine Score: {final_score:.4f} for TX: {tx.sender_account_id}->{tx.receiver_account_id}")
        return final_score

rule_engine = RuleEngine()
