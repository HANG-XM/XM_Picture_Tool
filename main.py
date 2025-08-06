from model.model import initial, find_template_on_screen, click_on_template,click_pos,find_image
import time
import logging
import keyboard
import pygetwindow as gw

def return_game_main():
    pass

def stop_recognition():
    global running, continue_click
    running = False
    continue_click = False
    logging.info("识图程序已中止")

def sample_pic():
    global running, continue_click
    try:
        # 获取游戏窗口
        game_window_title = "BlueStacks 5"  # 请将此替换为你的游戏窗口的实际标题
        game_window = gw.getWindowsWithTitle(game_window_title)[0]
        game_window.activate()  # 激活游戏窗口
        while running:
            # 查找聊天大厅
            position = find_template_on_screen(r"F:\Work\Know_Pic\click\Chat.png", game_window)
            if not position is None:
                # 点击聊天大厅
                logging.info("点击聊天大厅")
                click_on_template(r"F:\Work\Know_Pic\click\Chat.png", game_window, position)
                time.sleep(0.5)  # 等待聊天大厅完全加载
                # 点击礼物大厅
                logging.info("点击礼物大厅")
                click_on_template(r"F:\Work\Know_Pic\click\Gift.png", game_window)
                time.sleep(0.5)  # 等待礼物大厅完全加载
                position = find_template_on_screen(r"F:\Work\Know_Pic\click\Rob.png", game_window)
                if not position is None:
                    # 点击可抢
                    logging.info("点击可抢")
                    click_on_template(r"F:\Work\Know_Pic\click\Rob.png", game_window, position)
                    time.sleep(1.7)  # 等待可抢完全加载
                    local_continue_click = continue_click
                    while continue_click:
                        # 循环单个玩家的礼物
                        position = find_template_on_screen(r"F:\Work\Know_Pic\click\Treasure_chest.png",
                                                           game_window, 0.5)
                        if not position is None:
                            # 点击礼物
                            time.sleep(1.5)  # 等待礼物完全加载
                            logging.info("点击礼物")
                            click_on_template(r"F:\Work\Know_Pic\click\Treasure_chest.png", game_window, position)
                            # 点击确认
                            time.sleep(0.8)  # 等待确认完全加载
                            logging.info("点击确认")
                            if not click_on_template(r"F:\Work\Know_Pic\click\Confirm.png", game_window):
                                continue_click = False
                                running = False
                                logging.info("今日礼物已经抢完！")
                        else:
                            continue_click = False
                            logging.info("该玩家已抢完礼物，开始返回主界面！")
                    # 点击返回
                    logging.info("点击返回")
                    click_on_template(r"F:\Work\Know_Pic\click\Return.png", game_window)
                    time.sleep(1)
                    # 返回主界面
                    logging.info("返回主界面")
                    click_on_template(r"F:\Work\Know_Pic\click\Return_Main.png", game_window)
                else:
                    logging.info("礼物大厅未找到可抢按钮，开始返回主界面！")
                    click_on_template(r"F:\Work\Know_Pic\click\Return_Main.png", game_window)
            else:
                running = False
                logging.info("游戏窗口未找到聊天大厅！结束程序！")
    except KeyboardInterrupt:
        logging.info("程序被手动中断，正在退出...")
    except Exception as e:
        logging.error(f"程序运行时出错: {e}")

def complex_pic(threshold,scale):
    try:
        global running, continue_click
        while running:
            pos = find_image(r"F:\Work\Know_Pic\click\Chat.png", threshold=threshold, scale=scale)  # 适配1440P屏幕
            if pos:
                # 点击聊天大厅
                click_pos(pos[0], pos[1], offset=3)  # 添加3像素随机偏移
                time.sleep(0.5)
                # 点击礼物大厅
                pos = find_image(r"F:\Work\Know_Pic\click\Gift.png", threshold=threshold, scale=scale)  # 适配1440P屏幕
                click_pos(pos[0], pos[1], offset=3)
                time.sleep(0.5)
                pos = find_image(r"F:\Work\Know_Pic\click\Rob.png", threshold=threshold, scale=scale)  # 适配1440P屏幕
                if pos:
                    # 点击可抢
                    click_pos(pos[0], pos[1], offset=3)
                    time.sleep(0.5)
                    # 点击礼物
                    while continue_click:
                        pos = find_image(r"F:\Work\Know_Pic\click\Treasure_chest.png", threshold=0.3,
                                         scale=scale)  # 适配1440P屏幕
                        if pos:
                            click_pos(pos[0], pos[1], offset=3)
                            time.sleep(1)
                            # 点击确认
                            pos = find_image(r"F:\Work\Know_Pic\click\Confirm.png", threshold=threshold, scale=scale)
                            if not pos:
                                click_pos(pos[0], pos[1], offset=3)
                            else:
                                # 今日礼物已经抢完
                                continue_click = False
                        else:
                            continue_click = False
                    logging.info("该玩家没有礼物可以抢了！")
                    pos = find_image(r"F:\Work\Know_Pic\click\Return.png", threshold=threshold, scale=scale)
                    click_pos(pos[0], pos[1], offset=3)
                    time.sleep(0.5)
                    pos = find_image(r"F:\Work\Know_Pic\click\Return_Main.png", threshold=threshold, scale=scale)
                    click_pos(pos[0], pos[1], offset=3)

                else:
                    logging.info("礼物大厅未找到可抢按钮，开始返回主界面！")
                    pos = find_image(r"F:\Work\Know_Pic\click\Return_Main.png", threshold=threshold, scale=scale)
                    click_pos(pos[0], pos[1], offset=3)
            else:
                print("未检测到游戏主界面，结束运行...")
                running = False
    except KeyboardInterrupt:
        logging.info("程序被手动中断")
    except Exception as e:
        logging.error(f"发生错误: {str(e)}", exc_info=True)  # 记录堆栈


RESOLUTIONS = {
    "1920x1080": {"scale": 1.0, "threshold": 0.75},
    "1440x900": {"scale": 0.75, "threshold": 0.6},
    "2560x1440": {"scale": 1.33, "threshold": 0.8}
}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 初始化目录
    initial()
    # 绑定热键
    keyboard.add_hotkey('p', stop_recognition)

    running = True
    continue_click = True

    complex_pic(threshold=RESOLUTIONS["2560x1440"]["threshold"],scale=RESOLUTIONS["2560x1440"]["scale"])