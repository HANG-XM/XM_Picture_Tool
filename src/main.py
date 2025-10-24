import os
import sys
from gui import main

if __name__ == '__main__':
    # 设置环境变量
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
    os.environ['QT_SCALE_FACTOR'] = 'auto'
    
    main()