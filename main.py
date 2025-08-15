import cv2
import time
import subprocess
import threading
import colorama as ca
import numpy as np
import os
from PIL import Image
"""
1.打开rtsp服务器,接受larix手机端的推流
2.执行模型,prosses_frame()
"""
ca.init(autoreset=True)

def change_to_strs(frame):
    # 将OpenCV的BGR帧转为PIL的灰度图像
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sample_rate = 0.15

    # 计算字符画的宽高
    aspect_ratio = 0.5
    new_width = int(img.shape[1] * sample_rate)
    new_height = int(img.shape[0] * sample_rate * aspect_ratio)
    img = cv2.resize(img, (new_width, new_height))

    symbols = np.array(list(" .-lTM#@■"))
    # 归一化到[0, symbols.size-1]
    img = (img - img.min()) / (img.max() - img.min()) * (symbols.size - 1)

    # 生成字符画，每一行是一个字符串
    ascii = symbols[img.astype(int)]
    lines = "\n".join("".join(r) for r in ascii)
    # 清屏
    os.system('cls' if os.name == 'nt' else 'clear')
    print(lines)


class PhoneStreamProcessor:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = None
        self.last_frame = None
        self.connect()
    
    def connect(self): 
        """建立RTSP连接"""
        print(f"{ca.Fore.CYAN}Connecting to the {ca.Fore.LIGHTBLUE_EX}[RTSP] {ca.Fore.CYAN}stream...: {ca.Fore.GREEN}{self.rtsp_url}{ca.Style.RESET_ALL}")
        retry_count = 0
        max_retry = 30
        while True:
            self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if self.cap.isOpened():
                break
            retry_count += 1
            if retry_count > max_retry:
                raise ConnectionError(ca.Fore.RED + "Faile to reconnect to the stream.")
            print(ca.Fore.RED + "Faile to connect to the stream, retrying... :" + f"{ca.Fore.GREEN}{retry_count}/{ca.Fore.MAGENTA}{max_retry}" + ca.Style.RESET_ALL)
            self.cap.release()
            time.sleep(1)
        print(ca.Fore.CYAN + "Successfully connecting.")
    
    
    def get_frame(self):
        """获取当前帧"""
        ret, frame = self.cap.read()
        if not ret:
            print(ca.Fore.RED+"The stream is interupted, trying to reconnect..." + ca.Style.RESET_ALL)
            self.reconnect()
            return self.last_frame if self.last_frame is not None else None
        
        self.last_frame = frame
        return frame
    
    def reconnect(self):
        """重新连接逻辑"""
        self.cap.release()
        time.sleep(2)  # 等待后重连
        self.connect()
    
    def process_frame(self, frame):
        """自定义帧处理函数"""
        change_to_strs(frame)
        return frame
    
    def run(self):
        """主运行循环"""
        while True:
            frame = self.get_frame()
            if frame is None:
                continue
                
            processed_frame = self.process_frame(frame)
            
            # 显示结果
            cv2.imshow('Phone Stream', processed_frame)
            
            # 按'ESC'退出
            if cv2.waitKey(1) == 27:
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

def print_auptor_logo():
    aup = [
        "           █████╗   ██╗   ██╗  ██████╗  ",
        "          ██╔══██╗  ██║   ██║  ██╔══██╝ ",
        "          ███████║  ██║   ██║  ██████╔╝ ",
        "          ██╔══██║  ██║   ██║  ██╔═══╝  ",
        "          ██║  ██║  ╚██████╔╝  ██║      ",
        "          ╚═╝  ╚═╝   ╚═════╝   ╚═╝      "
    ]
    t = [
        "   ████████╗   ",
        "   ╚══██╔══╝   ",
        "     ╔██║      ",
        "     ║██║      ",
        "     ║██║      ",
        "     ╚═╝       "
    ]
    o = [
        "  ██████╗   ",
        " ██╔═████╗  ",
        " ██║██╔██║  ",
        " ████╔╝██║  ",
        " ╚██████╔╝  ",
        "  ╚═════╝   "
    ]
    r = [
        "██████╗      ",
        "██╔══██╗     ",
        "██████╔╝     ",
        "██╔══██╗     ",
        "██║  ██║     ",
        "╚═╝  ╚═╝     "
    ]
    # 颜色
    aup_color = ca.Fore.LIGHTBLUE_EX
    t_color = ca.Fore.BLUE
    o_color = ca.Fore.CYAN
    r_color = ca.Fore.CYAN

    for i in range(len(aup)):
        print(
            aup_color + aup[i] +
            t_color + t[i] +
            o_color + o[i] +
            r_color + r[i] +
            ca.Style.RESET_ALL
        )

def start_meadiamtx():
    mediamtx_dir = r"f:\Auptor\VISION\mediamtx"
    exe_path = rf"{mediamtx_dir}\mediamtx.exe"
    yml_path = rf"{mediamtx_dir}\mediamtx.yml"
    commands = [exe_path, yml_path]
    proc = subprocess.Popen(
        commands,
        cwd=mediamtx_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    def print_output():
        for line in proc.stdout:
            colored_line = line
            colored_line = colored_line.replace(
                "MediaMTX v1.14.0", "\033[38;5;19mMediaMTX v1.14.0\033[0m"
            )
            colored_line = colored_line.replace(
                "configuration loaded from f:\\Auptor\\VISION\\mediamtx\\mediamtx.yml",
                "\033[35mconfiguration loaded from f:\\Auptor\\VISION\\mediamtx\\mediamtx.yml\033[0m"
            )
            colored_line = colored_line.replace("INF", "\033[32mINF\033[0m")
            colored_line = colored_line.replace("RTSP", "\033[34mRTSP\033[0m")
            colored_line = colored_line.replace("RTMP", "\033[33mRTMP\033[0m")
            colored_line = colored_line.replace("HLS", "\033[38;5;208mHLS\033[0m")
            colored_line = colored_line.replace("WebRTC", "\033[96mWebRTC\033[0m")
            colored_line = colored_line.replace("SRT", "\033[38;5;94mSRT\033[0m")
            print(colored_line, end="")
    # 线程启动
    threading.Thread(target=print_output, daemon=True).start()
    return proc
    
if __name__ == "__main__":
    print('\n')
    print_auptor_logo()
    print("\033[38;5;19mStarting the mediamtx service...\033[0m")

    mediamtx_proc = start_meadiamtx()

    time.sleep(2)

    rtsp_url = "rtsp://192.168.0.17:8554/live"
    processor = PhoneStreamProcessor(rtsp_url)
    try:
        processor.run()
    finally:
        # 关闭mediamtx进程
        if mediamtx_proc and mediamtx_proc.poll() is None:
            print("\033[31mStopping the mediamtx service...\033[0m")
            mediamtx_proc.terminate()
        print("\033[31mDone!\033[0m")
           




    