import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from actions import Action, ActionType
from automation import AutomationThread

class AutomationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.actions = []
        self.automation_thread = None
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('可视化自动化工具')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 创建工具栏
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 添加动作按钮
        add_click_action = QAction('添加点击', self)
        add_click_action.triggered.connect(self.add_click_action)
        toolbar.addAction(add_click_action)
        
        add_find_action = QAction('添加查找', self)
        add_find_action.triggered.connect(self.add_find_action)
        toolbar.addAction(add_find_action)
        
        add_wait_action = QAction('添加等待', self)
        add_wait_action.triggered.connect(self.add_wait_action)
        toolbar.addAction(add_wait_action)
        
        add_loop_action = QAction('添加循环', self)
        add_loop_action.triggered.connect(self.add_loop_action)
        toolbar.addAction(add_loop_action)
        
        add_condition_action = QAction('添加条件', self)
        add_condition_action.triggered.connect(self.add_condition_action)
        toolbar.addAction(add_condition_action)
        
        # 创建动作列表
        self.action_list = QListWidget()
        layout.addWidget(QLabel('动作列表:'))
        layout.addWidget(self.action_list)
        
        # 创建控制按钮
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton('开始执行')
        self.start_btn.clicked.connect(self.start_automation)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton('停止执行')
        self.stop_btn.clicked.connect(self.stop_automation)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton('清除所有')
        self.clear_btn.clicked.connect(self.clear_actions)
        control_layout.addWidget(self.clear_btn)
        
        self.save_btn = QPushButton('保存流程')
        self.save_btn.clicked.connect(self.save_workflow)
        control_layout.addWidget(self.save_btn)
        
        self.load_btn = QPushButton('加载流程')
        self.load_btn.clicked.connect(self.load_workflow)
        control_layout.addWidget(self.load_btn)
        
        layout.addLayout(control_layout)
        
        # 创建日志输出
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(QLabel('执行日志:'))
        layout.addWidget(self.log_text)
        
    def add_click_action(self):
        """添加点击动作"""
        dialog = ClickActionDialog()
        if dialog.exec_():
            action = Action(ActionType.CLICK, dialog.get_params())
            self.actions.append(action)
            self.action_list.addItem(f"点击: {dialog.template_path.text()}")
            
    def add_find_action(self):
        """添加查找动作"""
        dialog = FindActionDialog()
        if dialog.exec_():
            action = Action(ActionType.FIND, dialog.get_params())
            self.actions.append(action)
            self.action_list.addItem(f"查找: {dialog.template_path.text()}")
            
    def add_wait_action(self):
        """添加等待动作"""
        dialog = WaitActionDialog()
        if dialog.exec_():
            action = Action(ActionType.WAIT, dialog.get_params())
            self.actions.append(action)
            self.action_list.addItem(f"等待: {dialog.duration.value()} 秒")
            
    def add_loop_action(self):
        """添加循环动作"""
        dialog = LoopActionDialog()
        if dialog.exec_():
            action = Action(ActionType.LOOP, dialog.get_params())
            self.actions.append(action)
            self.action_list.addItem(f"循环: {dialog.count.value()} 次")
            
    def add_condition_action(self):
        """添加条件动作"""
        dialog = ConditionActionDialog()
        if dialog.exec_():
            action = Action(ActionType.CONDITION, dialog.get_params())
            self.actions.append(action)
            self.action_list.addItem(f"条件: {dialog.template_path.text()}")
            
    def start_automation(self):
        """开始执行自动化流程"""
        if not self.actions:
            QMessageBox.warning(self, '警告', '请先添加动作！')
            return
            
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.automation_thread = AutomationThread(self.actions)
        self.automation_thread.log_signal.connect(self.add_log)
        self.automation_thread.finished.connect(self.automation_finished)
        self.automation_thread.start()
        
    def stop_automation(self):
        """停止执行自动化流程"""
        if self.automation_thread:
            self.automation_thread.stop()
            
    def automation_finished(self):
        """自动化流程执行完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def clear_actions(self):
        """清除所有动作"""
        self.actions = []
        self.action_list.clear()
        
    def save_workflow(self):
        """保存工作流程"""
        file_path, _ = QFileDialog.getSaveFileName(self, '保存工作流程', '', 'JSON Files (*.json)')
        if file_path:
            with open(file_path, 'w') as f:
                json.dump([action.to_dict() for action in self.actions], f)
                
    def load_workflow(self):
        """加载工作流程"""
        file_path, _ = QFileDialog.getOpenFileName(self, '加载工作流程', '', 'JSON Files (*.json)')
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.actions = [Action.from_dict(item) for item in data]
                self.update_action_list()
                
    def update_action_list(self):
        """更新动作列表显示"""
        self.action_list.clear()
        for action in self.actions:
            if action.type == ActionType.CLICK:
                self.action_list.addItem(f"点击: {action.params['template_path']}")
            elif action.type == ActionType.FIND:
                self.action_list.addItem(f"查找: {action.params['template_path']}")
            elif action.type == ActionType.WAIT:
                self.action_list.addItem(f"等待: {action.params['duration']} 秒")
            elif action.type == ActionType.LOOP:
                self.action_list.addItem(f"循环: {action.params['count']} 次")
            elif action.type == ActionType.CONDITION:
                self.action_list.addItem(f"条件: {action.params['template_path']}")
                
    def add_log(self, message):
        """添加日志消息"""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

class ClickActionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化对话框界面"""
        self.setWindowTitle('添加点击动作')
        layout = QVBoxLayout()
        
        # 模板路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel('模板路径:'))
        self.template_path = QLineEdit()
        path_layout.addWidget(self.template_path)
        browse_btn = QPushButton('浏览')
        browse_btn.clicked.connect(self.browse_template)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # 阈值
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel('匹配阈值:'))
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.1, 1.0)
        self.threshold.setSingleStep(0.1)
        self.threshold.setValue(0.8)
        threshold_layout.addWidget(self.threshold)
        layout.addLayout(threshold_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def browse_template(self):
        """浏览选择模板文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, '选择模板文件', '', 'Image Files (*.png *.jpg *.bmp)')
        if file_path:
            self.template_path.setText(file_path)
            
    def get_params(self):
        """获取参数"""
        return {
            'template_path': self.template_path.text(),
            'threshold': self.threshold.value()
        }

class FindActionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化对话框界面"""
        self.setWindowTitle('添加查找动作')
        layout = QVBoxLayout()
        
        # 模板路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel('模板路径:'))
        self.template_path = QLineEdit()
        path_layout.addWidget(self.template_path)
        browse_btn = QPushButton('浏览')
        browse_btn.clicked.connect(self.browse_template)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # 阈值
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel('匹配阈值:'))
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.1, 1.0)
        self.threshold.setSingleStep(0.1)
        self.threshold.setValue(0.8)
        threshold_layout.addWidget(self.threshold)
        layout.addLayout(threshold_layout)
        
        # 多选
        self.multi_match = QCheckBox('查找所有匹配')
        layout.addWidget(self.multi_match)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def browse_template(self):
        """浏览选择模板文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, '选择模板文件', '', 'Image Files (*.png *.jpg *.bmp)')
        if file_path:
            self.template_path.setText(file_path)
            
    def get_params(self):
        """获取参数"""
        return {
            'template_path': self.template_path.text(),
            'threshold': self.threshold.value(),
            'multi_match': self.multi_match.isChecked()
        }

class WaitActionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化对话框界面"""
        self.setWindowTitle('添加等待动作')
        layout = QVBoxLayout()
        
        # 等待时间
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel('等待时间(秒):'))
        self.duration = QDoubleSpinBox()
        self.duration.setRange(0.1, 60.0)
        self.duration.setSingleStep(0.1)
        self.duration.setValue(1.0)
        duration_layout.addWidget(self.duration)
        layout.addLayout(duration_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def get_params(self):
        """获取参数"""
        return {
            'duration': self.duration.value()
        }

class LoopActionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化对话框界面"""
        self.setWindowTitle('添加循环动作')
        layout = QVBoxLayout()
        
        # 循环次数
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel('循环次数:'))
        self.count = QSpinBox()
        self.count.setRange(1, 999)
        self.count.setValue(1)
        count_layout.addWidget(self.count)
        layout.addLayout(count_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def get_params(self):
        """获取参数"""
        return {
            'count': self.count.value(),
            'actions': []  # 这里可以添加循环内的动作
        }

class ConditionActionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化对话框界面"""
        self.setWindowTitle('添加条件动作')
        layout = QVBoxLayout()
        
        # 模板路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel('模板路径:'))
        self.template_path = QLineEdit()
        path_layout.addWidget(self.template_path)
        browse_btn = QPushButton('浏览')
        browse_btn.clicked.connect(self.browse_template)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # 阈值
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel('匹配阈值:'))
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.1, 1.0)
        self.threshold.setSingleStep(0.1)
        self.threshold.setValue(0.8)
        threshold_layout.addWidget(self.threshold)
        layout.addLayout(threshold_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def browse_template(self):
        """浏览选择模板文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, '选择模板文件', '', 'Image Files (*.png *.jpg *.bmp)')
        if file_path:
            self.template_path.setText(file_path)
            
    def get_params(self):
        """获取参数"""
        return {
            'template_path': self.template_path.text(),
            'threshold': self.threshold.value(),
            'true_actions': [],  # 这里可以添加条件为真时的动作
            'false_actions': []  # 这里可以添加条件为假时的动作
        }

def main():
    app = QApplication(sys.argv)
    window = AutomationWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
