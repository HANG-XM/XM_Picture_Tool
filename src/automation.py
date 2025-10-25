import time
import cv2
import numpy as np
import pyautogui
import logging
from typing import List, Tuple, Optional
from PyQt5.QtCore import QThread, pyqtSignal
from actions import Action, ActionType
import os
import json
class ImageMatcher:
    @staticmethod
    def find_template(template_path: str, threshold: float = 0.8, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        """在屏幕上查找模板图像"""
        try:
            screenshot = pyautogui.screenshot(region=region)
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            template = cv2.imread(template_path)
            if template is None:
                return None
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val >= threshold:
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                if region:
                    center_x += region[0]
                    center_y += region[1]
                return (center_x, center_y)
            return None
        except Exception as e:
            logging.error(f"图像匹配错误: {e}")
            return None

    @staticmethod
    def find_all_templates(template_path: str, threshold: float = 0.8, region: Optional[Tuple[int, int, int, int]] = None) -> List[Tuple[int, int]]:
        """在屏幕上查找所有匹配的模板图像"""
        try:
            screenshot = pyautogui.screenshot(region=region)
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            template = cv2.imread(template_path)
            if template is None:
                return []
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            positions = []
            h, w = template.shape[:2]
            for pt in zip(*locations[::-1]):
                center_x = pt[0] + w // 2
                center_y = pt[1] + h // 2
                if region:
                    center_x += region[0]
                    center_y += region[1]
                positions.append((center_x, center_y))
            return positions
        except Exception as e:
            logging.error(f"图像匹配错误: {e}")
            return []

class AutomationThread(QThread):
    log_signal = pyqtSignal(str, str)  # 添加日志级别参数
    progress_signal = pyqtSignal(int)  # 添加进度信号
    finished = pyqtSignal()
    
    def __init__(self, actions: List[Action]):
        super().__init__()
        self.actions = actions
        self.running = True
        self.current_action_index = 0
        
    def run(self):
        """执行自动化流程"""
        try:
            total_actions = len(self.actions)
            for i, action in enumerate(self.actions):
                if not self.running:
                    break
                    
                self.current_action_index = i
                self.progress_signal.emit(int((i / total_actions) * 100))
                
                # 验证动作参数
                error = action.validate()
                if error:
                    self.log_signal.emit(f"动作验证失败: {error}", "error")
                    continue
                    
                self.log_signal.emit(f"执行动作: {action.description}", "info")
                
                if action.type == ActionType.CLICK:
                    self._handle_click(action.params)
                elif action.type == ActionType.BATCH_CLICK:
                    self._handle_batch_click(action.params)
                elif action.type == ActionType.FIND:
                    self._handle_find(action.params)
                elif action.type == ActionType.WAIT:
                    self._handle_wait(action.params)
                elif action.type == ActionType.LOOP:
                    self._handle_loop(action.params)
                elif action.type == ActionType.CONDITION:
                    self._handle_condition(action.params)
                elif action.type == ActionType.PARALLEL:
                    self._handle_parallel(action.params)
                elif action.type == ActionType.SEQUENCE:
                    self._handle_sequence(action.params)
                    
                self.log_signal.emit(f"动作完成: {action.description}", "success")
                
        except Exception as e:
            self.log_signal.emit(f"执行错误: {str(e)}", "error")
        finally:
            self.finished.emit()
            
    def _handle_click(self, params):
        """处理点击动作"""
        template_path = params['template_path']
        threshold = params.get('threshold', 0.8)
        region = params.get('region', None)
        position = ImageMatcher.find_template(template_path, threshold, region)
        if position:
            pyautogui.click(position[0], position[1])
            self.log_signal.emit(f"点击位置: {position}")
        else:
            self.log_signal.emit(f"未找到图像: {template_path}")
            
    def _handle_find(self, params):
        """处理查找动作"""
        template_path = params['template_path']
        threshold = params.get('threshold', 0.8)
        region = params.get('region', None)
        multi_match = params.get('multi_match', False)
        if multi_match:
            positions = ImageMatcher.find_all_templates(template_path, threshold, region)
            self.log_signal.emit(f"找到 {len(positions)} 个匹配位置")
        else:
            position = ImageMatcher.find_template(template_path, threshold, region)
            if position:
                self.log_signal.emit(f"找到位置: {position}")
            else:
                self.log_signal.emit(f"未找到图像: {template_path}")
                
    def _handle_wait(self, params):
        """处理等待动作"""
        duration = params['duration']
        time.sleep(duration)
        self.log_signal.emit(f"等待 {duration} 秒")
        
    def _handle_loop(self, params):
        """处理循环动作"""
        loop_actions = params['actions']
        loop_count = params.get('count', 1)
        for _ in range(loop_count):
            if not self.running:
                break
            for action in loop_actions:
                if not self.running:
                    break
                if action.type == ActionType.CLICK:
                    self._handle_click(action.params)
                elif action.type == ActionType.FIND:
                    self._handle_find(action.params)
                elif action.type == ActionType.WAIT:
                    self._handle_wait(action.params)
                    
    def _handle_condition(self, params):
        """处理条件动作"""
        template_path = params['template_path']
        threshold = params.get('threshold', 0.8)
        region = params.get('region', None)
        true_actions = params.get('true_actions', [])
        false_actions = params.get('false_actions', [])
        position = ImageMatcher.find_template(template_path, threshold, region)
        if position:
            for action in true_actions:
                if not self.running:
                    break
                if action.type == ActionType.CLICK:
                    self._handle_click(action.params)
                elif action.type == ActionType.FIND:
                    self._handle_find(action.params)
                elif action.type == ActionType.WAIT:
                    self._handle_wait(action.params)
        else:
            for action in false_actions:
                if not self.running:
                    break
                if action.type == ActionType.CLICK:
                    self._handle_click(action.params)
                elif action.type == ActionType.FIND:
                    self._handle_find(action.params)
                elif action.type == ActionType.WAIT:
                    self._handle_wait(action.params)
    def _handle_batch_click(self, params):
        """处理批量点击动作"""
        template_path = params['template_path']
        threshold = params.get('threshold', 0.8)
        region = params.get('region', None)
        positions = ImageMatcher.find_all_templates(template_path, threshold, region)
        if positions:
            for position in positions:
                if not self.running:
                    break
                pyautogui.click(position[0], position[1])
                self.log_signal.emit(f"点击位置: {position}")
        else:
            self.log_signal.emit(f"未找到图像: {template_path}")   
    def _handle_parallel(self, params):
        """处理并行动作"""
        actions = params.get('actions', [])
        executor = ParallelExecutor()
        executor.execute(actions)
        
    def _handle_sequence(self, params):
        """处理序列动作"""
        actions = params.get('actions', [])
        for action in actions:
            if not self.running:
                break
            if action.type == ActionType.CLICK:
                self._handle_click(action.params)
            elif action.type == ActionType.FIND:
                self._handle_find(action.params)
            elif action.type == ActionType.WAIT:
                self._handle_wait(action.params)
    def stop(self):
        """停止执行"""
        self.running = False
class ParallelExecutor:
    """并行执行器"""
    def __init__(self):
        self.threads = []
        self.log_signal = pyqtSignal(str, str)
        self.progress_signal = pyqtSignal(int)
        
    def execute(self, actions: List[Action]):
        """并行执行多个动作"""
        for action in actions:
            thread = AutomationThread([action])
            thread.log_signal.connect(self.log_signal)
            thread.progress_signal.connect(self.progress_signal)
            self.threads.append(thread)
            thread.start()
            
        # 等待所有线程完成
        for thread in self.threads:
            thread.wait()
            
    def stop(self):
        """停止所有执行线程"""
        for thread in self.threads:
            thread.stop()