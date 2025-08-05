import os
import cv2
import numpy as np
import pyautogui
import logging
import time

def initial():
    """
    初始化函数，用于创建缓存目录
    """
    # 获取当前运行目录
    current_directory = os.getcwd()
    # 构建缓存子目录的完整路径
    subdirectory_path = os.path.join(current_directory, "Cache")
    # 检查子目录是否存在，如果不存在则创建
    if not os.path.exists(subdirectory_path):
        os.makedirs(subdirectory_path)
    # 构建图标子目录的完整路径
    subdirectory_path = os.path.join(current_directory, "click")
    # 检查子目录是否存在，如果不存在则创建
    if not os.path.exists(subdirectory_path):
        os.makedirs(subdirectory_path)

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

def preprocess_image(image):
    """
    对图像进行预处理
    """
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    return blurred


def find_template_on_screen_ex(template_path, window, threshold: float = 0.5):
    """
    查找模板在窗口中的位置
    :param threshold:
    :param template_path:
    :param window:
    :return:匹配结果，返回模板在窗口中的位置坐标，如果没有找到则返回None
    """
    try:
        # 读取模板图像
        template = cv2.imread(template_path)
        if template is None:
            print(f"模板图像路径错误或图像不存在: {template_path}")
            return None
        # 截取窗口截图
        screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # 预处理图像
        processed_image = preprocess_image(screenshot)
        # 初始化ORB检测器
        orb = cv2.ORB_create()
        # 检测模板中的特征点和描述符
        keypoints_template, descriptors_template = orb.detectAndCompute(template, None)
        if descriptors_template is None:
            logging.error("无法提取模板图像的特征描述符")
            return None
        # 检测截图中的特征点和描述符
        keypoints_screenshot, descriptors_screenshot = orb.detectAndCompute(processed_image, None)
        if descriptors_screenshot is None:
            logging.error("无法提取截图图像的特征描述符")
            return None
        # 使用BFMatcher匹配描述符
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(descriptors_template, descriptors_screenshot)
        # 如果找到匹配结果
        if len(matches) > 0:
            # 根据距离排序
            matches = sorted(matches, key = lambda x:x.distance)
            # 获取匹配点的坐标
            src_pts = np.float32([keypoints_template[m.queryIdx].pt for m in matches]).reshape(-1, 2)
            dst_pts = np.float32([keypoints_screenshot[m.trainIdx].pt for m in matches]).reshape(-1, 2)
            # 计算变换矩阵
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if M is not None:
                h, w = template.shape[:2]
                pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)
                top_left = tuple(dst[0][0])
                center_x = (top_left[0] + dst[2][0][0]) // 2
                center_y = (top_left[1] + dst[2][0][1]) // 2
                logging.info(f"找到模板，位置坐标为: ({center_x}, {center_y})")
                return center_x, center_y
            else:
                logging.error("未找到有效的变换矩阵")
        else:
            logging.error("未找到匹配的特征点")
    except Exception as e:
        logging.error(f"查找模板图像时出错: {e}")
        return None

def click_on_template_ex(template_path, window, position=None):
    """
    点击模板
    :param position:
    :param template_path:
    :param window:
    :return:
    """
    if position is None:
        # 查找模板位置
        position = find_template_on_screen_ex(template_path, window)

    if position:
        x, y = position
        # 将窗口内的坐标转换为屏幕坐标
        screen_x = window.left + x
        screen_y = window.top + y
        pyautogui.click(screen_x, screen_y)
        logging.info(f"在位置 ({screen_x}, {screen_y}) 点击")
    else:
        logging.info("未找到要点击的模板")