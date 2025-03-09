from typing import Dict


class AgentErrorHandler:
    def __init__(self, logger):
        self.logger = logger
        self.fallback_responses = {
            "sql": "I'm having trouble accessing the database. Please try rephrasing your question or try again later.",
            "rag": "I couldn't access the policy documents. Please try asking about a specific policy topic.",
            "search": "I'm unable to search the internet right now. Please try again later."
        }
    
    def handle_error(self, agent_type: str, error: Exception, context: Dict) -> str:
        self.logger.log_error(agent_type, error, context)
        return self.fallback_responses.get(agent_type, "An error occurred. Please try again.") 