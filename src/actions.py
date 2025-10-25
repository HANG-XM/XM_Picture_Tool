from typing import List, Dict, Any, Optional
import os
import json
class ActionType:
    # 基础动作
    CLICK = "click"
    FIND = "find"
    WAIT = "wait"
    
    # 流程控制
    LOOP = "loop"
    CONDITION = "condition"
    PARALLEL = "parallel"  # 新增并行执行
    
    # 复合动作
    SEQUENCE = "sequence"  # 新增动作序列
    CUSTOM = "custom"      # 新增自定义动作

class Action:
    def __init__(self, type: str, params: dict):
        self.type = type
        self.params = params
        self.description = self._generate_description()

    def _generate_description(self) -> str:
        """生成动作描述"""
        if self.type == ActionType.CLICK:
            return f"点击图像: {self.params.get('template_path', '')}"
        elif self.type == ActionType.BATCH_CLICK:
            return f"批量点击图像: {self.params.get('template_path', '')}"
        elif self.type == ActionType.FIND:
            return f"查找图像: {self.params.get('template_path', '')}"
        elif self.type == ActionType.WAIT:
            return f"等待 {self.params.get('duration', 0)} 秒"
        elif self.type == ActionType.LOOP:
            return f"循环执行 {self.params.get('count', 0)} 次"
        elif self.type == ActionType.CONDITION:
            return f"条件判断: {self.params.get('template_path', '')}"
        elif self.type == ActionType.PARALLEL:
            return f"并行执行 {len(self.params.get('actions', []))} 个动作"
        elif self.type == ActionType.SEQUENCE:
            return f"顺序执行 {len(self.params.get('actions', []))} 个动作"
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
        elif self.type == ActionType.PARALLEL or self.type == ActionType.SEQUENCE:
            if 'actions' not in self.params:
                return "缺少动作列表"
            if not isinstance(self.params['actions'], list):
                return "动作列表必须是数组"
        return None
class ActionTemplate:
    """动作模板类，用于保存可重用的动作组合"""
    def __init__(self, name: str, actions: List[Action], description: str = ""):
        self.name = name
        self.actions = actions
        self.description = description
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'actions': [action.to_dict() for action in self.actions]
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ActionTemplate':
        return ActionTemplate(
            data['name'],
            [Action.from_dict(action_data) for action_data in data['actions']],
            data.get('description', '')
        )