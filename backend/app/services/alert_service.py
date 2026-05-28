import structlog
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.schemas.transaction import TransactionCreate
from backend.app.db.models.alert import Alert
from backend.app.db.models.account import Account

logger = structlog.get_logger(__name__)

class AlertService:
    def __init__(self):
        self.high_threshold = 0.85
        self.medium_threshold = 0.70
        self.low_threshold = 0.50

    def evaluate_and_create_alert(
        self, 
        tx: TransactionCreate, 
        tx_id: str, 
        scoring_results: Dict[str, Any],
        session: Optional[AsyncSession] = None
    ) -> Optional[Alert]:
        """
        Evaluates scoring results and generates an alert if thresholds are breached.
        Returns the created Alert object (not saved to DB if session is None, but useful for broadcast).
        """
        final_score = scoring_results.get("final_risk_score", 0.0)
        
        severity = None
        if final_score >= self.high_threshold:
            severity = "CRITICAL"
        elif final_score >= self.medium_threshold:
            severity = "HIGH"
        elif final_score >= self.low_threshold:
            severity = "MEDIUM"
            
        # Additional checks
        alert_type = "GENERAL_FRAUD"
        if scoring_results.get("graph_risk", 0.0) > 0.6:
            severity = "HIGH" if not severity else severity # Upgrade severity
            alert_type = "MULE_ACCOUNT_RING"
            
        # 1. Auto-Escalation based on multiple risk vectors
        if final_score > self.high_threshold and scoring_results.get("graph_risk", 0.0) > 0.5:
            severity = "CRITICAL"
            
        # Blacklist hit escalation
        if scoring_results.get("rule_score", 0.0) >= 0.5:
            severity = "CRITICAL"
            
        if severity:
            logger.warning(f"ALERT GENERATED: {severity} - {alert_type} for TX {tx_id}")
            alert = Alert(
                transaction_id=tx_id,
                account_id=tx.sender_account_id,
                severity=severity,
                alert_type=alert_type,
                confidence=final_score,
                status="NEW"
            )
            
            # 2. Auto-freeze account logic
            if severity == "CRITICAL" and session:
                logger.error(f"AUTO-FREEZING ACCOUNT: {tx.sender_account_id}")
                # We should execute an update statement here or wait for transaction service
                # For this implementation, the actual freeze flag update can be done by transaction_service
                scoring_results["recommended_action"] = "freeze_account"
                
            return alert
            
        return None

alert_service = AlertService()
