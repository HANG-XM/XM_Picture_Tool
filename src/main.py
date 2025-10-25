import os
import sys
from ctypes import windll
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import gui
from gui import AutomationWindow
from gui import main

def set_dpi_awareness():
    """设置Windows DPI感知"""
    try:
        # Windows 10及之后版本
        windll.shcore.SetProcessDpiAwarenessContext(-2)  # DPI_AWARENESS_CONTEXT_UNAWARE
    except:
        try:
            # Windows 8.1及之后版本
            windll.user32.SetProcessDPIAware()
        except:
            print("警告：无法设置DPI感知，将使用系统默认设置")

def enable_high_dpi_support():
    """启用高DPI支持"""
    # 设置Qt环境变量
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_SCALE_FACTOR'] = '1'
    
    # 设置Windows DPI感知
    try:
        set_dpi_awareness()
    except Exception as e:
        print(f"DPI设置警告: {e}")

if __name__ == '__main__':
    try:
        # 在创建QApplication之前设置DPI感知
        enable_high_dpi_support()
        
        # 创建Qt应用
        app = QApplication(sys.argv)
        
        # 创建并显示主窗口
        window = AutomationWindow()
        window.show()
        
        # 运行事件循环
        sys.exit(app.exec())
    except Exception as e:
        print(f"程序启动错误: {e}")
        sys.exit(1)
