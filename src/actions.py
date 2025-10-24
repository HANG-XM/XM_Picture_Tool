from typing import List, Dict, Any, Optional
import os

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
        self.description = self._generate_description()

    def _generate_description(self) -> str:
        """生成动作描述"""
        if self.type == ActionType.CLICK:
            return f"点击图像: {self.params.get('template_path', '')}"
        elif self.type == ActionType.FIND:
            return f"查找图像: {self.params.get('template_path', '')}"
        elif self.type == ActionType.WAIT:
            return f"等待 {self.params.get('duration', 0)} 秒"
        elif self.type == ActionType.LOOP:
            return f"循环执行 {self.params.get('count', 0)} 次"
        elif self.type == ActionType.CONDITION:
            return f"条件判断: {self.params.get('template_path', '')}"
        return "未知动作"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'params': self.params,
            'description': self.description
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Action':
        action = Action(data['type'], data['params'])
        action.description = data.get('description', action._generate_description())
        return action

    def validate(self) -> Optional[str]:
        """验证动作参数是否有效"""
        if self.type == ActionType.CLICK or self.type == ActionType.FIND or self.type == ActionType.CONDITION:
            if 'template_path' not in self.params:
                return "缺少模板路径"
            if not os.path.exists(self.params['template_path']):
                return "模板文件不存在"
        elif self.type == ActionType.WAIT:
            if 'duration' not in self.params:
                return "缺少等待时间"
            if self.params['duration'] <= 0:
                return "等待时间必须大于0"
        elif self.type == ActionType.LOOP:
            if 'count' not in self.params:
                return "缺少循环次数"
            if self.params['count'] <= 0:
                return "循环次数必须大于0"
        return None
