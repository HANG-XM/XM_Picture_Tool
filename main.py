# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。


from model.model import initial, find_template_on_screen, click_on_template
import pygetwindow as gw
import time
import logging
import keyboard

running = True
continue_click = True
def stop_recognition():
    global running
    global continue_click
    running = False
    continue_click = False
    print("识图程序已中止")

keyboard.add_hotkey('p', stop_recognition)
# 初始化日志记录
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        # 初始化缓存目录
        initial()

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
                click_on_template(r"F:\Work\Know_Pic\click\Chat.png", game_window,position)
                time.sleep(1)  # 等待聊天大厅完全加载
                # 点击礼物大厅
                logging.info("点击礼物大厅")
                click_on_template(r"F:\Work\Know_Pic\click\Gift.png", game_window)
                time.sleep(1)  # 等待礼物大厅完全加载
                position = find_template_on_screen(r"F:\Work\Know_Pic\click\Rob.png", game_window)
                if not position is None:
                    # 点击可抢
                    logging.info("点击可抢")
                    click_on_template(r"F:\Work\Know_Pic\click\Rob.png", game_window,position)
                    time.sleep(1.8)  # 等待可抢完全加载
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
                            time.sleep(1)  # 等待确认完全加载
                            logging.info("点击确认")
                            if not click_on_template(r"F:\Work\Know_Pic\click\Confirm.png", game_window):
                                continue_click = False
                                running=False
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
                running=False
                logging.info("游戏窗口未找到聊天大厅！结束程序！")
    except KeyboardInterrupt:
        logging.info("程序被手动中断，正在退出...")
    except Exception as e:
        logging.error(f"程序运行时出错: {e}")