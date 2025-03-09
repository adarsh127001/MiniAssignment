import logging
from typing import Any, Dict
import json
from datetime import datetime

class AgentLogger:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('agent_logs.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AgentSystem')
    
    def log_agent_decision(self, agent_type: str, query: str, decision: str):
        self.logger.info(
            json.dumps({
                "timestamp": datetime.now().isoformat(),
                "agent_type": agent_type,
                "query": query,
                "decision": decision
            })
        )
    
    def log_error(self, agent_type: str, error: Exception, context: Dict[str, Any]):
        self.logger.error(
            json.dumps({
                "timestamp": datetime.now().isoformat(),
                "agent_type": agent_type,
                "error": str(error),
                "context": context
            })
        ) 