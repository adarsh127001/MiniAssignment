from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pass 