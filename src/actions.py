from typing import List, Dict, Any

class ActionType:
    CLICK = "click"
    FIND = "find"
    WAIT = "wait"
    LOOP = "loop"
    CONDITION = "condition"

class Action:
    def __init__(self, type: str, params: dict):
        self.type = type
        self.params = params

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'params': self.params
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Action':
        return Action(data['type'], data['params'])
