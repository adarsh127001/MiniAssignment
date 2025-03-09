from typing import Dict, List
from datetime import datetime

class SessionMemory:
    def __init__(self):
        self.sessions: Dict[str, List[Dict]] = {}
    
    def add_interaction(self, session_id: str, query: str, response: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response
        })
    
    def get_session_history(self, session_id: str, k: int = 5) -> List[Dict]:
        return self.sessions.get(session_id, [])[-k:] 