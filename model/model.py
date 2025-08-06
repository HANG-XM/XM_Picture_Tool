import os
import cv2
import numpy as np
import pyautogui
from pyautogui import PyAutoGUIException
import logging
import random
import threading
import psutil
import pygetwindow as gw
import time

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

def find_template_on_screen(template_path, window ,threshold:float=0.5):
    """
    查找模板在窗口中的位置
    :param threshold:
    :param template_path:
    :param window:
    :return:
    """
    try:
        # 截取窗口截图
        screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))# 截取窗口截图
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)# 转换为opencv的BGR格式
        # 读取模板图像
        template = cv2.imread(template_path)# 读取模板图像
        if template is None:# 如果模板图像未找到
            logging.error(f"模板图像 {template_path} 未找到")# 打印错误信息
            return None
        # 获取模板的宽度和高度
        template_height, template_width = template.shape[:2]# 获取模板的宽度和高度

        # 使用模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)# 使用模板匹配
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)# 获取匹配结果

        # 如果匹配度超过某个阈值，则认为找到了模板
        threshold = threshold# 设定匹配度阈值
        if max_val > threshold:# 如果匹配度超过阈值
            # 计算模板中心位置
            center_x = max_loc[0] + template_width // 2# 计算模板中心位置
            center_y = max_loc[1] + template_height // 2# 计算模板中心位置
            return center_x, center_y# 返回模板中心位置
        else:
            logging.info(f"未找到模板图像 {template_path}")# 打印提示信息
            return None# 返回None
    except Exception as e:
        logging.error(f"查找模板图像时出错: {e}")# 打印错误信息
        return None# 返回None

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

def find_image(image_path, threshold=0.8, scale=1.0):
    """
    在屏幕中查找目标图像并返回中心坐标
    :param image_path: 目标图像文件路径（如'icon.png'）
    :param threshold: 匹配置信度阈值（0-1，值越高越严格）
    :param scale: 屏幕缩放比例（默认1.0，适配高分辨率设备）
    :return: (x, y)坐标元组或None
    """
    try:
        # 截取屏幕并缩放
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        h, w = screenshot.shape[:2]
        scaled_img = cv2.resize(screenshot, (int(w * scale), int(h * scale)))

        # 加载目标图像并缩放
        template = cv2.imread(image_path)
        template_h, template_w = template.shape[:2]
        scaled_template = cv2.resize(template, (int(template_w * scale), int(template_h * scale)))

        # 模板匹配
        res = cv2.matchTemplate(scaled_img, scaled_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            # 计算实际坐标（反缩放）
            center_x = int(max_loc[0] / scale + template_w / 2)
            center_y = int(max_loc[1] / scale + template_h / 2)
            return center_x, center_y
        return None
    except Exception as e:
        print(f"图像搜索异常: {str(e)}")
        return None


def find_image_ex(image_path, threshold=0.8, scale=1.0, roi=None):
    """
    高效图像查找函数（替代 TM_SQDIFF_FAST）
    :param image_path: 目标图像路径
    :param threshold: 匹配置信度阈值（0-1）
    :param scale: 屏幕缩放比例（适配高分辨率）
    :param roi: 搜索区域 (x, y, width, height)，默认全屏
    :return: (x, y)坐标元组或None
    """
    try:
        # -------------------- 步骤1：获取并预处理屏幕 --------------------
        # 截取屏幕（全屏或指定ROI）
        screen = pyautogui.screenshot(region=roi) if roi else pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)  # 转为OpenCV格式（BGR）

        # 转换为灰度图（减少75%计算量）
        gray_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        # 动态缩放屏幕（根据scale参数）
        if scale != 1.0:
            target_width = int(gray_screen.shape[1] * scale)
            target_height = int(gray_screen.shape[0] * scale)
            gray_screen = cv2.resize(gray_screen, (target_width, target_height), interpolation=cv2.INTER_AREA)  # 高效缩小

        # -------------------- 步骤2：预处理目标模板 --------------------
        # 加载模板并转为灰度图（直接读取为灰度图，减少计算量）
        template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise FileNotFoundError(f"模板文件不存在: {image_path}")

        # 缩放模板（与屏幕缩放比例一致）
        if scale != 1.0:
            template_width = int(template.shape[1] * scale)
            template_height = int(template.shape[0] * scale)
            template = cv2.resize(template, (template_width, template_height), interpolation=cv2.INTER_AREA)

        # -------------------- 步骤3：模板匹配（优化版） --------------------
        # 使用归一化互相关系数（TM_CCOEFF_NORMED）：适用于亮度/对比度变化场景
        method = cv2.TM_CCOEFF_NORMED
        res = cv2.matchTemplate(gray_screen, template, method)

        # 计算匹配阈值（直接使用置信度阈值）
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        match_val = max_val  # TM_CCOEFF_NORMED 越大表示匹配越好

        # 检查是否达到阈值
        if match_val >= threshold:
            # 计算实际坐标（反缩放回原屏幕尺寸）
            if scale != 1.0:
                x = int(max_loc[0] / scale)
                y = int(max_loc[1] / scale)
            else:
                x, y = max_loc[0], max_loc[1]
            return x, y

        return None

    except Exception as e:
        print(f"图像搜索异常: {str(e)}")
        return None

def click_pos(x, y, offset=5, base_interval=0.1):
    """优化后的带随机偏移点击函数（非阻塞）"""

    def _perform_click():
        try:
            # 动态计算偏移量
            dx = random.randint(-offset, offset)
            dy = random.randint(-offset, offset)
            # 合并移动与点击操作
            pyautogui.click(x + dx, y + dy, duration=0.05)
        except PyAutoGUIException as e:
            print(f"点击失败: {str(e)}")

    # 动态调整点击间隔（根据CPU负载）
    interval = max(0.05, base_interval * (1 - psutil.cpu_percent(interval=0.1) / 100))

    # 启动后台线程执行点击
    threading.Thread(target=_perform_click).start()
    return True

def get_game_roi(window_title="BlueStacks 5", title_tolerance=0.8):
    """
    自动获取游戏窗口的ROI（位置+尺寸）
    :param window_title: 游戏窗口标题（支持模糊匹配）
    :param title_tolerance: 标题匹配容忍度（0-1，值越高越宽松）
    :return: (x, y, width, height) 或 None（未找到窗口）
    """
    try:
        # 获取所有可见窗口
        all_windows = gw.getAllTitles()
        target_windows = []

        # 模糊匹配窗口标题（支持部分匹配）
        for title in all_windows:
            if title is None:
                continue
            # 计算标题相似度（简单实现：公共子串长度占比）
            common_len = len(set(title) & set(window_title))
            similarity = common_len / max(len(title), len(window_title))
            if similarity >= title_tolerance:
                target_windows.append(gw.getWindowsWithTitle(title)[0])

        if not target_windows:
            print(f"未找到标题包含 '{window_title}' 的窗口")
            return None

        # 选择最匹配的窗口（优先选择尺寸最大的）
        game_window = max(target_windows, key=lambda w: w.width * w.height)

        # 激活窗口并等待前置（确保截图完整）
        game_window.activate()
        time.sleep(0.5)  # 等待窗口激活

        # 获取窗口坐标和尺寸（注意：包含标题栏和边框）
        x, y = game_window.left, game_window.top
        width, height = game_window.width, game_window.height

        # 调整ROI（可选）：排除标题栏（假设标题栏高度30px）
        # 实际需根据窗口实际布局调整，可通过截图对比验证
        content_x = x
        content_y = y + 30  # 标题栏高度
        content_width = width
        content_height = height - 30  # 总高度 - 标题栏高度

        return (content_x, content_y, content_width, content_height)

    except Exception as e:
        print(f"获取游戏窗口失败: {str(e)}")
        return None