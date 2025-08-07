import pyautogui
import cv2
import numpy as np
import pygetwindow as gw  # 用于窗口操作，需安装：pip install pygetwindow
import os
import logging
import time
import random
from typing import List, Tuple, Optional

def initial():
    """
    初始化函数（优化版）：高效创建缓存、图标、日志目录
    """
    # 仅获取一次当前工作目录
    current_dir = os.getcwd()

    # 定义需要创建的目录列表（可扩展）
    dirs_to_create = ["Cache", "click", "log"]

    # 批量创建目录（自动跳过已存在的目录）
    for dir_name in dirs_to_create:
        dir_path = os.path.join(current_dir, dir_name)
        try:
            # exist_ok=True：目录存在时不报错（Python 3.2+ 支持）
            os.makedirs(dir_path, exist_ok=True)
            print(f"目录已创建/已存在: {dir_path}")
        except OSError as e:
            print(f"创建目录失败 {dir_path}: {e}")

def find_template_on_screen(template_path, window ,threshold:float=0.5,multi_match:bool=False):
    """
    查找模板在窗口中的位置
    :param threshold:匹配阈值，默认0.5
    :param template_path:模板图像文件路径
    :param window: 包含窗口位置信息的对象（需有left/top/width/height属性）
    :param multi_match:是否启用多匹配模式（True=返回所有符合条件的匹配；False=仅返回最佳匹配），默认True
    :return:
    """
    try:
        # 截取窗口截图
        screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))# 截取窗口截图
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)# 转换为opencv的BGR格式
        # 读取模板图像
        template = cv2.imread(template_path,cv2.IMREAD_UNCHANGED)# 读取模板图像
        if template is None:# 如果模板图像未找到
            logging.error(f"模板图像 {template_path} 未找到")# 打印错误信息
            return None
        # 处理带Alpha通道的模板（生成掩码）
        template_height, template_width = template.shape[:2]# 获取模板的宽度和高度
        mask = None
        if template.ndim == 3 and template.shape[2] == 4:  # BGRA格式
            b, g, r, alpha = cv2.split(template)
            template = cv2.merge((b, g, r))  # 提取BGR通道
            mask = alpha  # 使用Alpha通道作为匹配掩码
        # 使用模板匹配
        match_method = cv2.TM_CCOEFF_NORMED
        result = cv2.matchTemplate(screenshot, template,match_method, mask=mask)# 使用模板匹配

        # ------------------------- 新增多匹配模式分支 -------------------------
        if multi_match:
            # 多匹配模式：收集所有超过阈值的匹配点
            loc = np.where(result >= threshold)
            matches = list(zip(*loc[::-1]))  # 转换为(x,y)坐标列表
            # 邻近点去重（同前）
            unique_matches = []
            if matches:
                neighbor_threshold = max(template_width, template_height) // 2
                unique_matches = [matches[0]]
                for x, y in matches[1:]:
                    last_x, last_y = unique_matches[-1]
                    distance = np.sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
                    if distance > neighbor_threshold:
                        unique_matches.append((x, y))
            # 计算唯一匹配的中心坐标
            centers = []
            for (x, y) in unique_matches:
                if (x + template_width > screenshot.shape[1]) or (y + template_height > screenshot.shape[0]):
                    continue
                center_x = x + template_width // 2
                center_y = y + template_height // 2
                centers.append((center_x, center_y))
            if not centers:
                logging.info(f"未找到匹配度超过{threshold}的模板图像：{template_path}（多匹配模式）")
                return None
            return centers
        else:
            # 单匹配模式：仅返回最佳匹配（匹配度最高的位置）
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)  # 获取匹配结果
            # 如果匹配度超过某个阈值，则认为找到了模板
            if max_val > threshold:# 如果匹配度超过阈值
                # 计算模板中心位置
                center_x = max_loc[0] + template_width // 2# 计算模板中心位置
                center_y = max_loc[1] + template_height // 2# 计算模板中心位置
                return (center_x, center_y)# 返回模板中心位置
            else:
                logging.info(f"未找到模板图像 {template_path}")# 打印提示信息
                return None# 返回None
    except FileNotFoundError:
        logging.error(f"模板文件不存在：{template_path}")
        return None
    except Exception as e:
        logging.error(f"查找模板图像时出错: {e}")# 打印错误信息
        return None

def click_on_template(template_path, window ,position=None)->bool:
    """
    点击模板
    :param position:
    :param template_path:
    :param window:
    :return:
    """
    if position is None:# 如果未指定点击位置
        # 查找模板位置
        position = find_template_on_screen(template_path, window)# 查找模板位置

    if position:# 如果找到模板位置
        x, y = position## 获取模板位置
        # 将窗口内的坐标转换为屏幕坐标
        screen_x = window.left + x
        screen_y = window.top + y
        pyautogui.click(screen_x, screen_y)# 点击
        # logging.info(f"在位置 ({screen_x}, {screen_y}) 点击")
        return True
    else:
        logging.info("未找到要点击的模板")
        return False

def click_on_template2(template_path, window,position=None)->bool:
    import keyboard

    # 初始化坐标变量（初始为 None）
    left_top = None
    right_bottom = None

    def on_key_press(event):
        """按键按下时的回调函数"""
        global left_top, right_bottom

        # 按下 's' 键：记录左上角坐标
        if event.name == 's':
            x, y = pyautogui.position()
            left_top = (x, y)
            print(f"左上角已记录：{left_top}")
        # 按下 'e' 键：记录右下角坐标并退出
        elif event.name == 'e':
            x, y = pyautogui.position()
            right_bottom = (x, y)
            print(f"右下角已记录：{right_bottom}")
            print("坐标记录完成，程序退出。")
            exit()  # 直接退出程序

        # 按下 'q' 键：直接退出
        elif event.name == 'q':
            print("检测到'q'键，程序退出。")
            exit()

    # 启动键盘监听（监听所有按键）
    keyboard.on_press(on_key_press)

    # 主循环：实时显示鼠标坐标
    print("开始记录坐标...（按 's' 记左上角，'e' 记右下角，'q' 退出）")
    while True:
        x, y = pyautogui.position()
        print(f"当前坐标：X={x}, Y={y}", end="\r")  # 覆盖上一行显示
        time.sleep(0.1)  # 降低循环频率，减少 CPU 占用

def __text():
    import pyautogui
    import cv2
    import numpy as np
    # 定义区域坐标
    region = (457, 301, 899, 437)

    width = region[2] - region[0]
    height = region[3] - region[1]
    screenshot_roi = pyautogui.screenshot(region=(region[0], region[1], width, height))
    # 转换为OpenCV格式并显示
    cv2.imshow("ROI", cv2.cvtColor(np.array(screenshot_roi), cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
    cv2.destroyAllWindows()