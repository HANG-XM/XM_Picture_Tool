import pyautogui
import cv2
import numpy as np
import os
import logging
import time
from typing import List, Tuple, Optional
import datetime
import json

def initial(account:str) -> bool:
    """
    初始化函数（优化版）：高效创建缓存、图标、日志目录
    :param account:account (str): 统计账户名（非空字符串）
    :return:bool: 初始化是否成功（True=成功，False=失败）
    """
    # ------------------------------ 参数校验 ------------------------------
    if not isinstance(account, str) or len(account.strip()) == 0:
        print("错误：账户名必须为非空字符串")
        return False
    # ------------------------------ 基础路径预计算 ------------------------------
    current_dir = os.getcwd()   # 仅获取一次当前工作目录
    dirs_to_create = ["Cache", "click", "log"]  # 目录列表保持简洁
    log_dir = os.path.join(current_dir, "log")  # 提前计算日志目录路径（避免后续重复拼接）

    # ------------------------------ 高效目录创建 ------------------------------
    for dir_name in dirs_to_create:
        dir_path = os.path.join(current_dir, dir_name)
        try:
            os.makedirs(dir_path, exist_ok=True)    # 原子操作：存在则跳过，不存在则创建
            print(f"目录就绪: {dir_path}")
        except PermissionError:
            print(f"错误：无权限创建目录 {dir_path}，请检查用户权限")
            return False
        except OSError as e:
            print(f"创建目录失败 {dir_path}: {e}")
            return False
    # ------------------------------ 日志文件初始化/更新 ------------------------------
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 当前日期（YYYY-MM-DD）
    log_filepath = os.path.join(log_dir, f"{current_date}_log.json" )  # 日志文件绝对路径
    try:
        # ------------------------------ 读取或初始化日志数据 ------------------------------
        file_exists = os.path.isfile(log_filepath)  # 标记文件是否存在
        log_data = {}
        if file_exists:
            # 读取现有数据并验证格式
            with open(log_filepath, "r", encoding="utf-8") as f:
                log_data = json.load(f)
            # 基础格式校验（根节点必须为字典）
            if not isinstance(log_data, dict):
                raise ValueError("日志文件根节点必须为字典类型（现有数据格式错误）")
        else:
            # 新文件初始化空字典
            log_data = {}

        # ------------------------------ 添加/更新当前账户数据 ------------------------------
        # 检查账户是否已存在
        if account in log_data:
            print(f"提示：账户 '{account}' 已存在，保留原有数据")
        else:
            # 新账户添加初始数据（不覆盖已有账户）
            log_data[account] = {"player_count": 0, "gift_count": 0}
            print(f"成功：账户 '{account}' 初始化完成（首次添加）")

        # ------------------------------ 写回更新后的数据 ------------------------------
        with open(log_filepath, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=4)
        print(f"日志文件更新成功: {log_filepath}（当前包含账户数：{len(log_data)}）")
    except PermissionError:
        print(f"错误：无权限访问日志文件 {log_filepath}（请检查文件读写权限）")
        return False
    except json.JSONDecodeError:
        print(f"错误：日志文件 {log_filepath} 格式异常（非合法JSON），请手动修复")
        return False
    except IsADirectoryError:
        print(f"错误：{log_filepath} 是目录而非文件（请清理冲突文件）")
        return False
    except ValueError as ve:
        print(f"日志文件格式验证失败: {ve}")
        return False
    except Exception as e:
        print(f"日志文件初始化/更新失败: {str(e)}（未知异常）")
        return False
    return True

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

def increment_metric(metric_type: str,account:str) -> bool:
    """
    增加指定账户的指定指标数量（支持"player_count"或"gift_count"）
    :param metric_type:要增加的指标类型（"player_count"/"gift_count"）
    :param account:要操作的账户名（非空字符串）
    日志文件路径规则：当前运行目录/log/{YYYY-MM-DD}_log.json
    """
    global log_file_path
    try:
        # ------------------------------ 自动生成日志文件路径 ------------------------------
        current_dir = os.getcwd()  # 获取当前工作目录
        log_dir = os.path.join(current_dir, "log")  # 日志目录路径
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 当前日期（YYYY-MM-DD）
        log_file_path = os.path.join(log_dir, f"{current_date}_log.json")  # 完整日志文件路径

        # ------------------------------ 读取日志数据 ------------------------------
        # 读取现有数据
        with open(log_file_path, "r", encoding="utf-8") as f:
            log_data = json.load(f)

        # ------------------------------ 验证账户存在性 ------------------------------
        if account not in log_data:
            raise ValueError(f"账户 '{account}' 不存在（请先通过initial函数初始化该账户）")

        # 验证指标类型有效性
        if metric_type not in ["player_count", "gift_count"]:
            raise ValueError(f"无效的指标类型：{metric_type}（仅支持'player_count'或'gift_count'）")

        # ------------------------------ 提取账户指标并校验类型 ------------------------------
        account_metrics = log_data[account]
        if not isinstance(account_metrics, dict):
            raise TypeError(f"账户 '{account}' 的指标数据格式错误（需为字典类型）")
        if metric_type not in account_metrics:
            raise ValueError(f"账户 '{account}' 缺少指标 '{metric_type}'（数据格式错误）")

        current_value = account_metrics[metric_type]
        if not isinstance(current_value, int):
            raise TypeError(
                f"账户 '{account}' 的 {metric_type} 类型错误（需为整数，当前类型：{type(current_value).__name__}）")
        # ------------------------------ 执行指标增量操作 ------------------------------
        new_value = current_value + 1
        account_metrics[metric_type] = new_value  # 显式赋值（提高可读性）

        # ------------------------------ 写回更新后的数据 ------------------------------
        with open(log_file_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=4)

        # 成功提示（明确账户、指标和新值）
        print(f"成功！账户 [{account}] 的 {metric_type} 数量已更新为：{new_value}")
        return True

    except FileNotFoundError:
        print(f"错误：日志文件 [{log_file_path}] 未找到（请先初始化日志文件）")
    except json.JSONDecodeError:
        print(f"错误：日志文件 [{log_file_path}] 格式异常（非合法JSON）")
    except ValueError as ve:
        print(f"操作失败：{ve}")
    except TypeError as te:
        print(f"类型错误：{te}")
    except PermissionError:
        print(f"错误：无权限访问日志文件 [{log_file_path}]，请检查文件读写权限")
    except Exception as e:
        print(f"未知错误：{str(e)}")
    return False