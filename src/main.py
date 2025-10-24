import os
import sys
from gui import main

if __name__ == '__main__':
    # 设置DPI感知
    if sys.platform == 'win32':
        import ctypes
        try:
            # 尝试设置为Per Monitor V2
            ctypes.windll.shcore.SetProcessDpiAwarenessContext(-4)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        except:
            try:
                # 如果失败，尝试设置为Per Monitor
                ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            except:
                try:
                    # 如果还是失败，尝试设置为系统DPI感知
                    ctypes.windll.user32.SetProcessDPIAware()
                except:
                    pass
    main()
