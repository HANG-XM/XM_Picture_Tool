import os
import sys
from ctypes import windll
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QMovie
from gui import AutomationWindow, SplashScreen
progress = 0
def set_dpi_awareness():
    """设置Windows DPI感知"""
    try:
        # Windows 10及之后版本
        windll.shcore.SetProcessDpiAwarenessContext(-2)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
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
        # 在创建QApplication之前设置高DPI属性
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        enable_high_dpi_support()
        
        app = QApplication(sys.argv)
        
        # 创建启动画面
        splash = SplashScreen()
        splash.show()
        
        # 模拟加载过程
        timer = QTimer()
        
        def update_progress():
            global progress
            progress += 20
            splash.set_progress(progress)
            if progress >= 100:
                timer.stop()
                # 创建主窗口
                window = AutomationWindow()
                # 显示主窗口
                window.show()
                # 延迟关闭启动画面
                QTimer.singleShot(100, splash.close)
        
        # 每500毫秒更新一次进度
        timer.timeout.connect(update_progress)
        timer.start(500)
        
        # 设置应用程序图标
        app.setWindowIcon(QIcon('icon.ico'))
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"程序启动错误: {e}")
        sys.exit(1)
