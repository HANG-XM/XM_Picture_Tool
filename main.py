from model.model import initial, find_template_on_screen, click_on_template,increment_metric
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

def sample_pic(account:str):
    global running, continue_click
    try:
        while running:

            position = find_template_on_screen(r"F:\Work\Know_Pic\click\Chat.png", game_window)
            if position is None:
                # 查找聊天大厅，未找到直接结束循环
                logging.info("游戏窗口未找到聊天大厅！结束程序！")
                return -1

            # 点击聊天大厅
            logging.info("点击聊天大厅")
            click_on_template(r"F:\Work\Know_Pic\click\Chat.png", game_window, position)
            time.sleep(0.5)  # 等待聊天大厅完全加载
            # 点击礼物大厅
            logging.info("点击礼物大厅")
            click_on_template(r"F:\Work\Know_Pic\click\Gift.png", game_window)
            time.sleep(0.5)  # 等待礼物大厅完全加载
            positions = find_template_on_screen(r"F:\Work\Know_Pic\click\Rob.png", game_window,multi_match=True)
            for position in positions:
                # 点击可抢
                logging.info("点击可抢")
                click_on_template(r"F:\Work\Know_Pic\click\Rob.png", game_window, position)
                time.sleep(1.6)  # 等待可抢完全加载
                increment_metric("玩家数",account)
                while continue_click:
                    # 循环单个玩家的礼物
                    position = find_template_on_screen(r"F:\Work\Know_Pic\click\Treasure_chest.png",
                                                               game_window, 0.5)
                    if not position is None:
                        # 点击礼物
                        logging.info("点击礼物")
                        click_on_template(r"F:\Work\Know_Pic\click\Treasure_chest.png", game_window,
                                          position)
                        # 点击确认
                        time.sleep(1.2)  # 等待确认完全加载
                        logging.info("点击确认")
                        if not click_on_template(r"F:\Work\Know_Pic\click\Confirm.png", game_window):
                            logging.info("今日礼物已经抢完！")
                            return 0
                        increment_metric("礼物数",account)
                        time.sleep(0.8)
                    else:
                        continue_click = False
                        logging.info("该玩家已抢完礼物，开始返回主界面！")
                continue_click = True
                # 点击返回
                logging.info("点击返回")
                click_on_template(r"F:\Work\Know_Pic\click\Return.png", game_window)
                time.sleep(0.5)
            # 返回主界面
            logging.info("返回主界面")
            click_on_template(r"F:\Work\Know_Pic\click\Return_Main.png", game_window)
            time.sleep(0.5)
    except KeyboardInterrupt:
        logging.info("程序被手动中断，正在退出...")
    except Exception as e:
        logging.error(f"程序运行时出错: {e}")

def complex_pic(threshold,title):
    try:
        global running, continue_click
        while running:
            pos = find_image_ex(r"F:\Work\Know_Pic\click\Chat.png", threshold=threshold,window_title=title)
            if pos is not None:
                # 点击聊天大厅
                click_pos(x=pos[0], y=pos[1], offset=3)  # 添加3像素随机偏移
                time.sleep(0.5)
                # 点击礼物大厅
                pos = find_image_ex(r"F:\Work\Know_Pic\click\Gift.png", threshold=threshold,window_title=title)
                click_pos(pos[0], pos[1], offset=3)
                time.sleep(0.5)
                pos = find_image_ex(r"F:\Work\Know_Pic\click\Rob.png", threshold=threshold,window_title=title)
                # 点击可抢
                click_pos(pos[0], pos[1], offset=3)
                time.sleep(0.5)
                # 点击礼物
                while continue_click:
                    pos = find_image_ex(r"F:\Work\Know_Pic\click\Treasure_chest.png", threshold=0.3,window_title=title)
                    if pos is not None:
                        click_pos(pos[0], pos[1], offset=3)
                        time.sleep(1.2)
                        # 点击确认
                        pos = find_image_ex(r"F:\Work\Know_Pic\click\Confirm.png", threshold=0.3,window_title=title)
                        if pos:
                            # 今日礼物已经抢完
                            continue_click = False
                        else:
                            pass
                            click_pos(pos[0], pos[1], offset=3)
                    else:
                        continue_click = False
                        logging.info("该玩家没有礼物可以抢了！")
                pos = find_image_ex(r"F:\Work\Know_Pic\click\Return.png", threshold=threshold,window_title=title)
                click_pos(pos[0], pos[1], offset=3)
                time.sleep(0.5)
                pos = find_image_ex(r"F:\Work\Know_Pic\click\Return_Main.png", threshold=threshold,window_title=title)
                click_pos(pos[0], pos[1], offset=3)
            else:
                print("未检测到游戏主界面，结束运行...")
                running = False
        running = True
        continue_click = True
    except KeyboardInterrupt:
        logging.info("程序被手动中断")
    except Exception as e:
        logging.error(f"发生错误: {str(e)}", exc_info=True)  # 记录堆栈

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    account = input("请输入当前游戏账号")
    # 初始化目录
    initial(account)
    # 绑定热键
    keyboard.add_hotkey('p', stop_recognition)

    running = True
    continue_click = True
    # 获取游戏窗口
    game_window_title = "BlueStacks 5"  # 请将此替换为你的游戏窗口的实际标题
    game_window = gw.getWindowsWithTitle(game_window_title)[0]
    game_window.activate()  # 激活游戏窗口

    sample_pic(account)