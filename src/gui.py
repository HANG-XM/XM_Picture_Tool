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
from typing import List
class ThemeManager:
    LIGHT_THEME = {
        'bg': '#fafafa',
        'surface': '#ffffff',
        'primary': '#1976d2',
        'primary_variant': '#1565c0',
        'secondary': '#7c4dff',
        'on_primary': '#ffffff',
        'on_secondary': '#ffffff',
        'text': '#212121',
        'text_secondary': '#757575',
        'text_hint': '#bdbdbd',
        'border': '#e0e0e0',
        'error': '#f44336',
        'warning': '#ff9800',
        'success': '#4caf50',
        'info': '#2196f3',
        'shadow': 'rgba(0, 0, 0, 0.12)',
        'divider': '#eeeeee'
    }
    
    DARK_THEME = {
        'bg': '#121212',
        'surface': '#1e1e1e',
        'primary': '#90caf9',
        'primary_variant': '#64b5f6',
        'secondary': '#7c4dff',
        'on_primary': '#000000',
        'on_secondary': '#ffffff',
        'text': '#ffffff',
        'text_secondary': '#b0b0b0',
        'text_hint': '#757575',
        'border': '#333333',
        'error': '#ef5350',
        'warning': '#ffa726',
        'success': '#66bb6a',
        'info': '#42a5f5',
        'shadow': 'rgba(0, 0, 0, 0.24)',
        'divider': '#2c2c2c'
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
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QToolBar {{
                background-color: {theme['surface']};
                border: none;
                spacing: 8px;
                padding: 8px;
                border-bottom: 1px solid {theme['divider']};
            }}
            
            QPushButton {{
                background-color: {theme['primary']};
                color: {theme['on_primary']};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 14px;
            }}
            
            QPushButton:hover {{
                background-color: {theme['primary_variant']};
            }}
            
            QPushButton:pressed {{
                background-color: {theme['primary_variant']};
            }}
            
            QPushButton:disabled {{
                background-color: {theme['border']};
                color: {theme['text_hint']};
            }}
            
            QListWidget {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 4px;
                selection-background-color: {theme['primary']};
                outline: none;
            }}
            
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }}
            
            QListWidget::item:selected {{
                background-color: {theme['primary']};
                color: {theme['on_primary']};
            }}
            
            QTextEdit {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', monospace;
                selection-background-color: {theme['primary']};
            }}
            
            QLabel {{
                color: {theme['text']};
                font-size: 14px;
                font-weight: 500;
            }}
            
            QStatusBar {{
                background-color: {theme['surface']};
                color: {theme['text_secondary']};
                border-top: 1px solid {theme['divider']};
            }}
            
            QSpinBox, QDoubleSpinBox {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                padding: 4px;
                selection-background-color: {theme['primary']};
            }}
            
            QLineEdit {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                padding: 6px 12px;
                selection-background-color: {theme['primary']};
            }}
            
            QLineEdit:focus {{
                border-color: {theme['primary']};
            }}
            
            QProgressBar {{
                border: none;
                border-radius: 4px;
                text-align: center;
                color: {theme['on_primary']};
                background-color: {theme['border']};
            }}
            
            QProgressBar::chunk {{
                background-color: {theme['primary']};
                border-radius: 4px;
            }}
            
            QCheckBox {{
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {theme['border']};
                background-color: {theme['surface']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {theme['primary']};
                border-color: {theme['primary']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTQiIHZpZXdCb3g9IjAgMCAxNCAxNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMNCAxMEwxIDciIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }}
        """
class FlowchartGenerator:
    """流程图生成器"""
    @staticmethod
    def generate_flowchart(actions: List[Action]) -> str:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                .flowchart {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                .node {
                    background-color: white;
                    border: 2px solid #2196f3;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    min-width: 200px;
                    text-align: center;
                }
                .arrow {
                    color: #666;
                    font-size: 24px;
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
        self.theme_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background: transparent;
                font-size: 18px;
                padding: 4px;
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.1);
            }}
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
        self.setGeometry(100, 100, 900, 600)  # 调整默认窗口大小为更合理的尺寸
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setSpacing(12)  # 减小间距
        layout.setContentsMargins(16, 16, 16, 16)  # 减小边距
        central_widget.setLayout(layout)
        
        # 创建工具栏
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))  # 减小图标尺寸
        self.addToolBar(toolbar)
        
        # 添加动作按钮
        actions = [
            ('添加点击', self.add_click_action),
            ('添加批量点击', self.add_batch_click_action),
            ('添加查找', self.add_find_action),
            ('添加等待', self.add_wait_action),
            ('添加循环', self.add_loop_action),
            ('添加条件', self.add_condition_action)
        ]
        
        for text, handler in actions:
            action = QAction(text, self)
            action.triggered.connect(handler)
            toolbar.addAction(action)
            
        # 添加分隔符
        toolbar.addSeparator()
        
        # 创建动作列表区域
        list_container = QWidget()
        list_container.setMaximumHeight(180)  # 限制最大高度
        list_layout = QVBoxLayout()
        list_layout.setSpacing(6)
        
        list_header = QLabel('动作列表')
        list_header.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 2px;")
        list_layout.addWidget(list_header)
        
        self.action_list = QListWidget()
        self.action_list.setMaximumHeight(150)  # 限制列表高度
        list_layout.addWidget(self.action_list)
        
        list_container.setLayout(list_layout)
        layout.addWidget(list_container)
        
        # 创建控制按钮区域
        control_container = QWidget()
        control_container.setMaximumHeight(40)  # 限制最大高度
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)
        control_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        control_container.setLayout(control_layout)
        layout.addWidget(control_container)
        # 初始化按钮引用
        self.start_btn = None
        self.stop_btn = None
        buttons = [
            ('开始执行', self.start_automation, 'primary'),
            ('停止执行', self.stop_automation, 'error'),
            ('清除所有', self.clear_actions, 'warning'),
            ('保存流程', self.save_workflow, 'success'),
            ('加载流程', self.load_workflow, 'info')
        ]
        
        for text, handler, style_type in buttons:
            btn = QPushButton(text)
            btn.setMaximumHeight(32)  # 限制按钮高度
            btn.clicked.connect(handler)
            
            # 保存按钮类型
            btn.setProperty("style_type", style_type)
            
            # 设置按钮样式
            if style_type == 'primary':
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {ThemeManager.LIGHT_THEME['primary']};
                        color: {ThemeManager.LIGHT_THEME['on_primary']};
                        border: none;
                        padding: 4px 12px;
                        border-radius: 4px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: {ThemeManager.LIGHT_THEME['primary_variant']};
                    }}
                    QPushButton:pressed {{
                        background-color: {ThemeManager.LIGHT_THEME['primary_variant']};
                    }}
                """)
            elif style_type == 'error':
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {ThemeManager.LIGHT_THEME['error']};
                        color: white;
                        border: none;
                        padding: 4px 12px;
                        border-radius: 4px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: {ThemeManager.LIGHT_THEME['error']};
                        opacity: 0.8;
                    }}
                    QPushButton:pressed {{
                        background-color: {ThemeManager.LIGHT_THEME['error']};
                        opacity: 0.6;
                    }}
                """)
            elif style_type == 'warning':
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {ThemeManager.LIGHT_THEME['warning']};
                        color: white;
                        border: none;
                        padding: 4px 12px;
                        border-radius: 4px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: {ThemeManager.LIGHT_THEME['warning']};
                        opacity: 0.8;
                    }}
                    QPushButton:pressed {{
                        background-color: {ThemeManager.LIGHT_THEME['warning']};
                        opacity: 0.6;
                    }}
                """)
            elif style_type == 'success':
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {ThemeManager.LIGHT_THEME['success']};
                        color: white;
                        border: none;
                        padding: 4px 12px;
                        border-radius: 4px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: {ThemeManager.LIGHT_THEME['success']};
                        opacity: 0.8;
                    }}
                    QPushButton:pressed {{
                        background-color: {ThemeManager.LIGHT_THEME['success']};
                        opacity: 0.6;
                    }}
                """)
            
            # 确保按钮可见
            btn.show()
            control_layout.addWidget(btn)
        layout.addWidget(control_container)
        
        # 添加流程图显示区域
        flowchart_container = QWidget()
        flowchart_container.setMaximumHeight(180)  # 限制最大高度
        flowchart_layout = QVBoxLayout()
        flowchart_layout.setSpacing(6)
        
        flowchart_header = QLabel('流程图')
        flowchart_header.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 2px;")
        flowchart_layout.addWidget(flowchart_header)
        
        self.flowchart_view = QWebEngineView()
        self.flowchart_view.setMaximumHeight(150)  # 限制高度
        self.flowchart_view.setUrl(QUrl("about:blank"))
        self.flowchart_view.setVisible(True)
        flowchart_layout.addWidget(self.flowchart_view)
        
        flowchart_container.setLayout(flowchart_layout)
        layout.addWidget(flowchart_container)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(24)  # 限制进度条高度
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # 创建日志输出区域
        log_container = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setSpacing(6)
        
        log_header = QLabel('执行日志')
        log_header.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 2px;")
        log_layout.addWidget(log_header)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)  # 限制日志区域高度
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_container.setLayout(log_layout)
        layout.addWidget(log_container)
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
            # 改为调用 update_action_list 而不是直接添加
            self.update_action_list()
            self.update_flowchart()

    def add_find_action(self):
        """添加查找动作"""
        dialog = FindActionDialog()
        if dialog.exec_():
            action = Action(ActionType.FIND, dialog.get_params())
            self.actions.append(action)
            self.update_action_list()
            self.update_flowchart()

    def add_wait_action(self):
        """添加等待动作"""
        dialog = WaitActionDialog()
        if dialog.exec_():
            action = Action(ActionType.WAIT, dialog.get_params())
            self.actions.append(action)
            self.update_action_list()
            self.update_flowchart()

    def add_loop_action(self):
        """添加循环动作"""
        dialog = LoopActionDialog()
        if dialog.exec_():
            action = Action(ActionType.LOOP, dialog.get_params())
            self.actions.append(action)
            self.update_action_list()
            self.update_flowchart()

    def add_condition_action(self):
        """添加条件动作"""
        dialog = ConditionActionDialog()
        if dialog.exec_():
            action = Action(ActionType.CONDITION, dialog.get_params())
            self.actions.append(action)
            self.update_action_list()
            self.update_flowchart()

    def add_batch_click_action(self):
        """添加批量点击动作"""
        dialog = BatchClickActionDialog()
        if dialog.exec_():
            action = Action(ActionType.BATCH_CLICK, dialog.get_params())
            self.actions.append(action)
            self.update_action_list()
            self.update_flowchart()
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
        self.action_list.setVisible(True)

        if not self.actions:
            # 如果没有动作，显示提示信息
            empty_item = QListWidgetItem("暂无动作，请添加动作")
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.action_list.addItem(empty_item)
            return

        for i, action in enumerate(self.actions):
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(5, 8, 5, 8)  # 增加上下边距
            layout.setSpacing(10)  # 增加元素间距
            
            # 添加序号
            num_label = QLabel(f"{i+1}.")
            num_label.setStyleSheet("font-weight: bold; color: #2196f3; min-width: 30px;")
            layout.addWidget(num_label)
            
            # 添加动作类型图标
            icon_label = QLabel()
            icons = {
                ActionType.CLICK: "👆",
                ActionType.FIND: "🔍",
                ActionType.WAIT: "⏰",
                ActionType.LOOP: "🔄",
                ActionType.CONDITION: "❓",
                ActionType.BATCH_CLICK: "👆👆"
            }
            icon_label.setText(icons.get(action.type, "📌"))
            icon_label.setStyleSheet("min-width: 20px;")
            layout.addWidget(icon_label)
            
            # 添加动作描述
            desc_label = QLabel()
            if action.type == ActionType.CLICK:
                template_path = action.params.get('template_path', '未知')
                desc_label.setText(f"点击: {os.path.basename(template_path)}")
            elif action.type == ActionType.FIND:
                template_path = action.params.get('template_path', '未知')
                desc_label.setText(f"查找: {os.path.basename(template_path)}")
            elif action.type == ActionType.WAIT:
                duration = action.params.get('duration', 0)
                desc_label.setText(f"等待: {duration} 秒")
            elif action.type == ActionType.LOOP:
                count = action.params.get('count', 0)
                desc_label.setText(f"循环: {count} 次")
            elif action.type == ActionType.CONDITION:
                template_path = action.params.get('template_path', '未知')
                desc_label.setText(f"条件: {os.path.basename(template_path)}")
            elif action.type == ActionType.BATCH_CLICK:
                template_path = action.params.get('template_path', '未知')
                desc_label.setText(f"批量点击: {os.path.basename(template_path)}")
            desc_label.setStyleSheet("padding: 0 10px;")
            desc_label.setWordWrap(True)  # 允许文字换行
            layout.addWidget(desc_label)
            
            # 添加弹性空间
            layout.addStretch()
            
            # 添加删除按钮
            delete_btn = QPushButton("×")
            delete_btn.setFixedSize(28, 28)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #ff4444;
                    color: white;
                    border: none;
                    border-radius: 14px;
                    font-weight: bold;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background: #cc0000;
                }
            """)
            delete_btn.clicked.connect(lambda checked, index=i: self.remove_action(index))
            layout.addWidget(delete_btn)
            
            widget.setLayout(layout)
            # 设置合适的高度，确保内容完整显示
            item.setSizeHint(QSize(widget.sizeHint().width(), 50))
            self.action_list.addItem(item)
            self.action_list.setItemWidget(item, widget)
        
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
        self.animation.setDuration(100)
        self.animation.setStartValue(0.9)
        self.animation.setEndValue(1.0)
        self.animation.start()
        
        # 为按钮添加动画效果
        for btn in self.findChildren(QPushButton):
            if btn != self.theme_btn:
                btn.installEventFilter(self)
                
    def eventFilter(self, obj, event):
        """事件过滤器，处理按钮动画"""
        if isinstance(obj, QPushButton):
            if event.type() == QEvent.Type.Enter:
                self.animate_button(obj, True)
            elif event.type() == QEvent.Type.Leave:
                self.animate_button(obj, False)
        return super().eventFilter(obj, event)
        
    def animate_button(self, button, enter):
        """按钮动画效果"""
        # 创建几何动画
        geo_animation = QPropertyAnimation(button, b"geometry")
        geo_animation.setDuration(200)
        
        if enter:
            # 鼠标进入时的动画
            cur_geo = button.geometry()
            geo_animation.setStartValue(cur_geo)
            geo_animation.setEndValue(cur_geo.adjusted(-2, -2, 2, 2))
        else:
            # 鼠标离开时的动画
            cur_geo = button.geometry()
            geo_animation.setStartValue(cur_geo)
            geo_animation.setEndValue(cur_geo.adjusted(2, 2, -2, -2))
        
        # 启动动画
        geo_animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
class BaseActionDialog(QDialog):
    """动作对话框基类"""
    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)  # 确保传入parent参数
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)  # 设置窗口标志
        self.layout = QVBoxLayout()
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(16, 16, 16, 16)
        
        # 添加说明
        info_label = QLabel(description)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; margin-bottom: 8px;")
        self.layout.addWidget(info_label)
        
        # 添加预览区域（可选）
        self.preview_label = None
        
    def add_template_selection(self, placeholder: str = "选择图像模板"):
        """添加模板选择组件"""
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel('模板路径:'))
        self.template_path = QLineEdit()
        self.template_path.setPlaceholderText(placeholder)
        path_layout.addWidget(self.template_path)
        browse_btn = QPushButton('浏览')
        browse_btn.clicked.connect(self.browse_template)
        path_layout.addWidget(browse_btn)
        self.layout.addLayout(path_layout)
        
    def add_threshold_selection(self):
        """添加阈值选择组件"""
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel('匹配阈值:'))
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.1, 1.0)
        self.threshold.setSingleStep(0.1)
        self.threshold.setValue(0.8)
        self.threshold.setSuffix(" (0.1-1.0)")
        threshold_layout.addWidget(self.threshold)
        self.layout.addLayout(threshold_layout)
        
    def add_preview_area(self):
        """添加预览区域"""
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(200, 200)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #ccc;")
        self.layout.addWidget(self.preview_label)
        
        if hasattr(self, 'template_path'):
            self.template_path.textChanged.connect(self.update_preview)
            
    def add_action_buttons(self):
        """添加确定/取消按钮"""
        button_layout = QHBoxLayout()
        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        self.layout.addLayout(button_layout)
        
    def update_preview(self):
        """更新预览图像"""
        if not self.preview_label or not hasattr(self, 'template_path'):
            return
            
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
        if file_path and hasattr(self, 'template_path'):
            self.template_path.setText(file_path)
            
    def get_common_params(self):
        """获取公共参数"""
        params = {}
        if hasattr(self, 'template_path'):
            params['template_path'] = self.template_path.text()
        if hasattr(self, 'threshold'):
            params['threshold'] = self.threshold.value()
        return params
class ClickActionDialog(BaseActionDialog):
    def __init__(self, parent=None):
        super().__init__('添加点击动作', '点击动作将在屏幕上查找指定图像并点击匹配位置', parent)
        self.add_template_selection("选择要点击的图像模板")
        self.add_threshold_selection()
        self.add_preview_area()
        self.add_action_buttons()
        self.setLayout(self.layout)
        
    def get_params(self):
        return self.get_common_params()

class FindActionDialog(BaseActionDialog):
    def __init__(self, parent=None):
        super().__init__('添加查找动作', '查找动作将在屏幕上搜索指定图像位置', parent)
        self.add_template_selection("选择要查找的图像模板")
        self.add_threshold_selection()
        
        # 多选选项
        self.multi_match = QCheckBox('查找所有匹配')
        self.layout.addWidget(self.multi_match)
        
        self.add_preview_area()
        self.add_action_buttons()
        self.setLayout(self.layout)
        
    def get_params(self):
        params = self.get_common_params()
        params['multi_match'] = self.multi_match.isChecked()
        return params

class WaitActionDialog(BaseActionDialog):
    def __init__(self, parent=None):
        super().__init__('添加等待动作', '等待动作将暂停执行指定的时间', parent)
        
        # 等待时间设置
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel('等待时间:'))
        self.duration = QDoubleSpinBox()
        self.duration.setRange(0.1, 60.0)
        self.duration.setSingleStep(0.1)
        self.duration.setValue(1.0)
        self.duration.setSuffix(" 秒")
        self.duration.setSpecialValueText("自定义等待时间")
        duration_layout.addWidget(self.duration)
        self.layout.addLayout(duration_layout)
        
        # 添加提示
        tip_label = QLabel("提示：等待时间范围在0.1秒到60秒之间")
        tip_label.setStyleSheet("color: #999; font-size: 12px; margin-top: 5px;")
        self.layout.addWidget(tip_label)
        
        self.add_action_buttons()
        self.setLayout(self.layout)
        
    def get_params(self):
        return {
            'duration': self.duration.value()
        }

class LoopActionDialog(BaseActionDialog):
    def __init__(self, parent=None):
        super().__init__('添加循环动作', '循环动作将重复执行指定的次数', parent)
        
        # 循环次数设置
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel('循环次数:'))
        self.count = QSpinBox()
        self.count.setRange(1, 999)
        self.count.setValue(1)
        self.count.setSpecialValueText("自定义循环次数")
        count_layout.addWidget(self.count)
        self.layout.addLayout(count_layout)
        
        # 添加提示
        tip_label = QLabel("提示：循环次数范围在1到999之间")
        tip_label.setStyleSheet("color: #999; font-size: 12px; margin-top: 5px;")
        self.layout.addWidget(tip_label)
        
        self.add_action_buttons()
        self.setLayout(self.layout)
        
    def get_params(self):
        return {
            'count': self.count.value(),
            'actions': []
        }

class ConditionActionDialog(BaseActionDialog):
    def __init__(self, parent=None):
        super().__init__('添加条件动作', '条件动作将根据是否找到指定图像来执行不同的操作', parent)
        self.add_template_selection("选择用于判断的图像模板")
        self.add_threshold_selection()
        self.add_preview_area()
        self.add_action_buttons()
        self.setLayout(self.layout)
        
    def get_params(self):
        params = self.get_common_params()
        params.update({
            'true_actions': [],
            'false_actions': []
        })
        return params

class BatchClickActionDialog(BaseActionDialog):
    def __init__(self, parent=None):
        super().__init__('添加批量点击动作', '批量点击动作将查找并点击所有匹配的图像位置', parent)
        self.add_template_selection("选择要批量点击的图像模板")
        self.add_threshold_selection()
        
        # 点击间隔设置
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel('点击间隔:'))
        self.interval = QDoubleSpinBox()
        self.interval.setRange(0.1, 5.0)
        self.interval.setSingleStep(0.1)
        self.interval.setValue(0.5)
        self.interval.setSuffix(" 秒")
        interval_layout.addWidget(self.interval)
        self.layout.addLayout(interval_layout)
        
        self.add_preview_area()
        self.add_action_buttons()
        self.setLayout(self.layout)
        
    def get_params(self):
        params = self.get_common_params()
        params['interval'] = self.interval.value()
        return params