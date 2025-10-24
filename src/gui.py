import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from actions import Action, ActionType
from automation import AutomationThread
from datetime import datetime
import os

class ThemeManager:
    LIGHT_THEME = {
        'bg': '#ffffff',
        'surface': '#f5f5f5',
        'primary': '#2196f3',
        'on_primary': '#ffffff',
        'text': '#333333',
        'text_secondary': '#666666',
        'border': '#e0e0e0',
        'error': '#f44336',
        'success': '#4caf50',
        'warning': '#ff9800'
    }
    
    DARK_THEME = {
        'bg': '#121212',
        'surface': '#1e1e1e',
        'primary': '#90caf9',
        'on_primary': '#000000',
        'text': '#ffffff',
        'text_secondary': '#b0b0b0',
        'border': '#333333',
        'error': '#ef5350',
        'success': '#66bb6a',
        'warning': '#ffa726'
    }

    @staticmethod
    def get_stylesheet(theme):
        return f"""
            QMainWindow {{
                background-color: {theme['bg']};
            }}
            QWidget {{
                background-color: {theme['bg']};
                color: {theme['text']};
            }}
            QToolBar {{
                background-color: {theme['surface']};
                border: none;
                spacing: 8px;
                padding: 8px;
                border-bottom: 1px solid {theme['border']};
            }}
            QPushButton {{
                background-color: {theme['primary']};
                color: {theme['on_primary']};
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme['primary']};
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                background-color: {theme['primary']};
                opacity: 0.6;
            }}
            QListWidget {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 8px;
                selection-background-color: {theme['primary']};
            }}
            QTextEdit {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', monospace;
            }}
            QLabel {{
                color: {theme['text']};
                font-size: 14px;
                font-weight: 500;
            }}
            QStatusBar {{
                background-color: {theme['surface']};
                color: {theme['text_secondary']};
                border-top: 1px solid {theme['border']};
            }}
        """
class FlowchartGenerator:
    """流程图生成器"""
    @staticmethod
    def generate_flowchart(actions: List[Action]) -> str:
        """生成流程图的HTML代码"""
        html = """
        <html>
        <head>
            <style>
                .flowchart {
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }
                .node {
                    border: 2px solid #2196f3;
                    border-radius: 5px;
                    padding: 10px;
                    margin: 10px;
                    background-color: #f5f5f5;
                    text-align: center;
                }
                .arrow {
                    text-align: center;
                    margin: 5px 0;
                }
            </style>
        </head>
        <body>
            <div class="flowchart">
        """
        
        for i, action in enumerate(actions):
            html += f'<div class="node">{i+1}. {action.description}</div>'
            if i < len(actions) - 1:
                html += '<div class="arrow">↓</div>'
                
        html += """
            </div>
        </body>
        </html>
        """
        return html
class AutomationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.actions = []
        self.automation_thread = None
        self.is_dark_mode = False
        self.init_ui()
        self.setup_status_bar()
        self.add_animation_effects()
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = self.statusBar()
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(32, 32)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 18px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
                border-radius: 16px;
            }
        """)
        self.status_bar.addPermanentWidget(self.theme_btn)
        
    def toggle_theme(self):
        """切换主题"""
        self.is_dark_mode = not self.is_dark_mode
        theme = ThemeManager.DARK_THEME if self.is_dark_mode else ThemeManager.LIGHT_THEME
        self.setStyleSheet(ThemeManager.get_stylesheet(theme))
        self.theme_btn.setText("☀️" if self.is_dark_mode else "🌙")
        
    def init_ui(self):
        """初始化用户界面"""
        # 设置现代风格
        self.setStyleSheet(ThemeManager.get_stylesheet(ThemeManager.LIGHT_THEME))
        
        self.setWindowTitle('可视化自动化工具')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
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
        # 添加流程图显示区域
        self.flowchart_view = QWebEngineView()
        self.flowchart_view.setVisible(False)
        layout.addWidget(self.flowchart_view)
        
        # 添加切换按钮
        self.toggle_flowchart_btn = QPushButton('显示流程图')
        self.toggle_flowchart_btn.clicked.connect(self.toggle_flowchart)
        control_layout.insertWidget(0, self.toggle_flowchart_btn)
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        # 创建日志输出
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(QLabel('执行日志:'))
        layout.addWidget(self.log_text)

    def toggle_flowchart(self):
        """切换流程图显示"""
        if self.flowchart_view.isVisible():
            self.flowchart_view.setVisible(False)
            self.toggle_flowchart_btn.setText('显示流程图')
        else:
            self.flowchart_view.setVisible(True)
            self.toggle_flowchart_btn.setText('隐藏流程图')
            self.update_flowchart()
            
    def update_flowchart(self):
        """更新流程图显示"""
        if self.actions:
            html = FlowchartGenerator.generate_flowchart(self.actions)
            self.flowchart_view.setHtml(html)  
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
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.automation_thread = AutomationThread(self.actions)
        self.automation_thread.log_signal.connect(self.add_log)
        self.automation_thread.progress_signal.connect(self.update_progress)
        self.automation_thread.finished.connect(self.automation_finished)
        self.automation_thread.start()
        
    def stop_automation(self):
        """停止执行自动化流程"""
        if self.automation_thread:
            self.automation_thread.stop()
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)  
    def automation_finished(self):
        """自动化流程执行完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
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
        for i, action in enumerate(self.actions):
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout()
            
            # 添加序号
            num_label = QLabel(f"{i+1}.")
            num_label.setStyleSheet("font-weight: bold; color: #2196f3;")
            layout.addWidget(num_label)
            
            # 添加动作类型图标
            icon_label = QLabel()
            icons = {
                ActionType.CLICK: "👆",
                ActionType.FIND: "🔍",
                ActionType.WAIT: "⏰",
                ActionType.LOOP: "🔄",
                ActionType.CONDITION: "❓"
            }
            icon_label.setText(icons.get(action.type, "📌"))
            layout.addWidget(icon_label)
            
            # 添加动作描述
            desc_label = QLabel()
            if action.type == ActionType.CLICK:
                desc_label.setText(f"点击: {os.path.basename(action.params['template_path'])}")
            elif action.type == ActionType.FIND:
                desc_label.setText(f"查找: {os.path.basename(action.params['template_path'])}")
            elif action.type == ActionType.WAIT:
                desc_label.setText(f"等待: {action.params['duration']} 秒")
            elif action.type == ActionType.LOOP:
                desc_label.setText(f"循环: {action.params['count']} 次")
            elif action.type == ActionType.CONDITION:
                desc_label.setText(f"条件: {os.path.basename(action.params['template_path'])}")
            layout.addWidget(desc_label)
            
            # 添加删除按钮
            delete_btn = QPushButton("×")
            delete_btn.setFixedSize(24, 24)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #ff4444;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #cc0000;
                }
            """)
            delete_btn.clicked.connect(lambda: self.remove_action(i))
            layout.addWidget(delete_btn)
            
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            self.action_list.addItem(item)
            self.action_list.setItemWidget(item, widget)
        # 更新流程图
        if self.flowchart_view.isVisible():
            self.update_flowchart()   
    def remove_action(self, index):
        """删除指定索引的动作"""
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
            self.update_action_list()
                
    def add_log(self, message, level="info"):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "info": "#2196f3",
            "warning": "#ff9800",
            "error": "#f44336",
            "success": "#4caf50"
        }
        color = colors.get(level, "#333333")
        formatted_message = f'<span style="color: {color}">[{timestamp}] {message}</span>'
        self.log_text.append(formatted_message)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    def add_animation_effects(self):
        """添加动画效果"""
        # 添加淡入效果
        self.fade_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.fade_effect)
        
        self.animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        
        # 为按钮添加悬浮动画
        for btn in self.findChildren(QPushButton):
            if btn != self.theme_btn:
                btn.installEventFilter(self)
                
    def eventFilter(self, obj, event):
        """事件过滤器，处理按钮动画"""
        if isinstance(obj, QPushButton):
            if event.type() == QEvent.Enter:
                self.animate_button(obj, True)
            elif event.type() == QEvent.Leave:
                self.animate_button(obj, False)
        return super().eventFilter(obj, event)
        
    def animate_button(self, button, enter):
        """按钮动画效果"""
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        if enter:
            cur_geo = button.geometry()
            animation.setStartValue(cur_geo)
            animation.setEndValue(cur_geo.adjusted(-2, -2, 2, 2))
        else:
            cur_geo = button.geometry()
            animation.setStartValue(cur_geo)
            animation.setEndValue(cur_geo.adjusted(2, 2, -2, -2))
        animation.start(QAbstractAnimation.DeleteWhenStopped)

class ClickActionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化对话框界面"""
        self.setWindowTitle('添加点击动作')
        layout = QVBoxLayout()
        
        # 添加说明
        info_label = QLabel("点击动作将在屏幕上查找指定图像并点击匹配位置")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # 模板路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel('模板路径:'))
        self.template_path = QLineEdit()
        self.template_path.setPlaceholderText("选择要点击的图像模板")
        path_layout.addWidget(self.template_path)
        browse_btn = QPushButton('浏览')
        browse_btn.clicked.connect(self.browse_template)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # 阈值设置
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel('匹配阈值:'))
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.1, 1.0)
        self.threshold.setSingleStep(0.1)
        self.threshold.setValue(0.8)
        self.threshold.setSuffix(" (0.1-1.0)")
        threshold_layout.addWidget(self.threshold)
        layout.addLayout(threshold_layout)
        
        # 添加预览区域
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(200, 200)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #ccc;")
        layout.addWidget(self.preview_label)
        
        # 连接信号
        self.template_path.textChanged.connect(self.update_preview)
        
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
    def update_preview(self):
        """更新预览图像"""
        path = self.template_path.text()
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.clear()      
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
