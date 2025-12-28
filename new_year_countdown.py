#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨年倒计时时钟程序（增加：播放声音 & 整点/半点报时）
"""
import tkinter as tk
from tkinter import font
import math
from datetime import datetime
import random
import subprocess
import os
import threading
import time


class NewYearCountdown:
    def __init__(self, root):
        self.root = root
        self.root.title("跨年倒计时时钟 🎉")
        self.root.geometry("800x600")

        # 去掉窗口边框和标题栏
        self.root.overrideredirect(True)

        # 尝试设置透明（macOS 优先）
        self.transparent_color = None
        self.transparent_supported = False
        try:
            self.root.wm_attributes('-transparent', True)
            self.transparent_color = 'systemTransparent'
            self.root.configure(bg=self.transparent_color)
            self.transparent_supported = True
        except Exception:
            try:
                self.root.attributes('-alpha', 0.99)
                self.transparent_color = self.root.cget('bg')
                self.root.configure(bg=self.transparent_color)
            except Exception as e:
                print(f"透明设置失败，使用默认背景: {e}")
                self.transparent_color = '#000000'
                self.root.configure(bg=self.transparent_color)
        self.root = root
        self.root.title("跨年倒计时时钟 🎉")
        self.root.geometry("800x600")


        # 窗口拖动相关变量
        self.start_x = 0
        self.start_y = 0

        self.root.resizable(True, True)

        # 基准尺寸
        self.base_width = 800
        self.base_height = 600
        self.base_radius = 155

        # 画布背景
        canvas_bg = self.transparent_color if self.transparent_color else '#000000'
        self.canvas = tk.Canvas(root, width=800, height=600, bg=canvas_bg, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 烟花粒子列表
        self.fireworks = []

        # 声音相关
        # sound.wav 用于跨年祝贺（如果没有则不会播放）
        # chime.wav 可用于报时（如果不存在则回退到 sound.wav）
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sound_path = os.path.join(base_dir, "sound.mp3")
        self.chime_path = os.path.join(base_dir, "chime.mp3")
        if not os.path.isfile(self.chime_path):
            # 若没有单独的 chime.wav，则使用 sound.wav 作为报时音（如果存在）
            self.chime_path = self.sound_path
        self.sound_played = False  # 新年声音只播放一次
        # 记录上一次报时的时间 (year, month, day, hour, minute)，防止同一分钟内重复报时
        self.last_chime_time = None

        # 绑定事件
        self.canvas.bind('<Configure>', self.on_resize)
        self.canvas.bind('<Button-1>', self.start_move)
        self.canvas.bind('<B1-Motion>', self.on_move)
        self.canvas.bind('<Button-3>', self.show_context_menu)

        self.canvas.update_idletasks()
        self.create_ui()
        self.update_clock()

    def start_move(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_move(self, event):
        x = self.root.winfo_x() + event.x - self.start_x
        y = self.root.winfo_y() + event.y - self.start_y
        self.root.geometry(f"+{x}+{y}")

    def show_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="关闭窗口", command=self.root.quit)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def on_resize(self, event):
        self.canvas.delete("all")
        self.create_ui()

    def get_scale_factor(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            return 1.0, 1.0
        scale_x = canvas_width / self.base_width
        scale_y = canvas_height / self.base_height
        scale = min(scale_x, scale_y)
        return scale, scale

    def create_ui(self):
        scale, _ = self.get_scale_factor()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            return

        center_x = canvas_width / 2
        center_y = canvas_height * 0.42
        radius = self.base_radius * scale

        title_font = font.Font(family='Arial', size=int(24 * scale), weight='bold')
        # 阴影
        self.canvas.create_text(center_x + 2, canvas_height * 0.08 + 2,
                                text="跨年倒计时时钟", fill='#000000', font=title_font, tags="static")
        self.canvas.create_text(center_x, canvas_height * 0.08,
                                text="跨年倒计时时钟", fill='#FF0000', font=title_font, tags="static")

        self.draw_clock_face(center_x, center_y, radius, scale)

    def draw_clock_face(self, center_x, center_y, radius, scale):
        # 表盘外圈透明填充，只画边框
        self.canvas.create_oval(center_x - radius, center_y - radius,
                                center_x + radius, center_y + radius,
                                outline='#FFD700', width=max(int(3 * scale), 1), fill='', tags="static")
        for i in range(2):
            r = radius + 10 * scale + i * 5 * scale
            self.canvas.create_oval(center_x - r, center_y - r,
                                    center_x + r, center_y + r,
                                    outline='#FFD700', width=max(int(2 * scale), 1), fill='', tags="static")
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = center_x + (radius - 20 * scale) * math.cos(angle)
            y1 = center_y + (radius - 20 * scale) * math.sin(angle)
            x2 = center_x + (radius - 10 * scale) * math.cos(angle)
            y2 = center_y + (radius - 10 * scale) * math.sin(angle)
            self.canvas.create_line(x1, y1, x2, y2,
                                    fill='#FFD700', width=max(int(3 * scale), 1), tags="static")
            num_x = center_x + (radius - 35 * scale) * math.cos(angle)
            num_y = center_y + (radius - 35 * scale) * math.sin(angle)
            hour_num = 12 if i == 0 else i
            self.canvas.create_text(num_x, num_y,
                                    text=str(hour_num),
                                    fill='#FFFFFF',
                                    font=font.Font(family='Arial', size=max(int(16 * scale), 8), weight='bold'),
                                    tags="static")
        for i in range(60):
            if i % 5 != 0:
                angle = math.radians(i * 6 - 90)
                x1 = center_x + (radius - 10 * scale) * math.cos(angle)
                y1 = center_y + (radius - 10 * scale) * math.sin(angle)
                x2 = center_x + (radius - 5 * scale) * math.cos(angle)
                y2 = center_y + (radius - 5 * scale) * math.sin(angle)
                self.canvas.create_line(x1, y1, x2, y2,
                                        fill='#00FF88', width=max(int(1 * scale), 1), tags="static") # #888888

    def draw_hand(self, angle, length, width, color, center_x, center_y, scale):
        angle_rad = math.radians(angle - 90)
        end_x = center_x + length * math.cos(angle_rad)
        end_y = center_y + length * math.sin(angle_rad)
        self.canvas.create_line(center_x, center_y, end_x, end_y,
                                fill=color, width=max(int(width * scale), 1),
                                capstyle=tk.ROUND, tags="hand")
        self.canvas.create_oval(end_x - 3 * scale, end_y - 3 * scale,
                                end_x + 3 * scale, end_y + 3 * scale,
                                fill=color, outline=color, tags="hand")

    def draw_center(self, center_x, center_y, scale):
        self.canvas.create_oval(center_x - 8 * scale, center_y - 8 * scale,
                                center_x + 8 * scale, center_y + 8 * scale,
                                fill='#FFD700', outline='#FFA500',
                                width=max(int(2 * scale), 1), tags="hand")

    def _play_file_afplay(self, path):
        """用 afplay 非阻塞播放（在子线程中调用）"""
        try:
            subprocess.Popen(["afplay", path])
        except Exception as e:
            raise

    def _play_file_playsound(self, path):
        """用 playsound 在子线程播放（阻塞在子线程）"""
        try:
            from playsound import playsound
            playsound(path)
        except Exception:
            raise

    def play_sound_once(self, path):
        """尝试播放指定音频文件一次（非阻塞调用）。在后台线程中处理 afplay 或 playsound 回退。"""
        if not path or not os.path.isfile(path):
            print(f"声音文件未找到: {path}")
            return

        def _worker(p):
            # 先尝试 afplay
            try:
                subprocess.Popen(["afplay", p])
                return
            except Exception:
                pass
            # 回退到 playsound（需 pip install playsound）
            try:
                from playsound import playsound
                playsound(p)
            except Exception as e:
                print(f"播放音频失败: {e}")

        t = threading.Thread(target=_worker, args=(path,), daemon=True)
        t.start()

    def play_chime_sequence(self, path, count, interval=0.6):
        """在后台线程里连续播放 count 次指定音频，每次间隔 interval 秒。
        如果 count <=0 则不播放。"""
        if not path or not os.path.isfile(path) or count <= 0:
            return

        def _worker(p, n, itv):
            # 优先使用 afplay 非阻塞地多次调用
            for i in range(n):
                try:
                    subprocess.Popen(["afplay", p])
                except Exception:
                    # 回退：用 playsound（会阻塞当前线程）
                    try:
                        from playsound import playsound
                        playsound(p)
                    except Exception as e:
                        print(f"报时播放失败: {e}")
                # 最后一次后不必要等待太久
                if i != n - 1:
                    time.sleep(itv)

        t = threading.Thread(target=_worker, args=(path, count, interval), daemon=True)
        t.start()

    def update_clock(self):
        # 清除动态元素
        self.canvas.delete("hand")
        self.canvas.delete("time_text")
        self.canvas.delete("countdown")
        self.canvas.delete("firework")

        scale, _ = self.get_scale_factor()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.update_clock)
            return

        center_x = canvas_width / 2
        center_y = canvas_height * 0.42
        radius = self.base_radius * scale

        now = datetime.now()
        hour = now.hour % 12
        minute = now.minute
        second = now.second

        # 指针角度（小时时按12小时制）
        hour_angle = (hour * 30) + (minute * 0.5)
        minute_angle = minute * 6
        second_angle = second * 6

        # 绘制指针
        self.draw_hand(hour_angle, radius * 0.5, 6, '#FFD700', center_x, center_y, scale)
        self.draw_hand(minute_angle, radius * 0.7, 4, '#FFA500', center_x, center_y, scale)
        self.draw_hand(second_angle, radius * 0.85, 2, '#FF4444', center_x, center_y, scale)
        self.draw_center(center_x, center_y, scale)

        # 时间与日期显示
        time_str = now.strftime("%H:%M:%S")
        time_font = font.Font(family='Courier', size=max(int(32 * scale), 10), weight='bold')
        # 阴影
        self.canvas.create_text(center_x + 2, canvas_height * 0.75 + 2,
                                text=time_str, fill='#000000', font=time_font, tags="time_text")
        self.canvas.create_text(center_x, canvas_height * 0.75,
                                text=time_str, fill='#00FF00', font=time_font, tags="time_text")

        date_str = now.strftime("%Y年%m月%d日")
        date_font = font.Font(family='Arial', size=max(int(18 * scale), 8))
        self.canvas.create_text(center_x + 2, canvas_height * 0.82 + 2,
                                text=date_str, fill='#000000', font=date_font, tags="time_text")
        self.canvas.create_text(center_x, canvas_height * 0.82,
                                text=date_str, fill='#FFFFFF', font=date_font, tags="time_text")

        # 倒计时到新年
        current_year = now.year
        new_year = datetime(current_year + 1, 1, 1, 0, 0, 0)
        # new_year = datetime(current_year, 12, 28, 13, 00, 0)  # 修改为新年钟声
        if now < new_year:
            delta = new_year - now
            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            seconds = delta.seconds % 60

            countdown_str = f"距离{current_year + 1}年还有: {days}天 {hours:02d}时 {minutes:02d}分 {seconds:02d}秒"
            countdown_font = font.Font(family='Arial', size=max(int(16 * scale), 8), weight='bold')
            self.canvas.create_text(center_x + 2, canvas_height * 0.88 + 2,
                                    text=countdown_str, fill='#000000', font=countdown_font, tags="countdown")
            self.canvas.create_text(center_x, canvas_height * 0.88,
                                    text=countdown_str, fill='#FF69B4', font=countdown_font, tags="countdown")

            # 距离跨年不到1分钟，开始烟花效果
            if delta.total_seconds() < 60:
                self.create_fireworks(canvas_width, canvas_height)
        else:
            celebration_str = f"🎉 新年快乐！{current_year}年 🎉"
            celebration_font = font.Font(family='Arial', size=max(int(20 * scale), 10), weight='bold')
            self.canvas.create_text(center_x + 2, canvas_height * 0.88 + 2,
                                    text=celebration_str, fill='#000000', font=celebration_font, tags="countdown")
            self.canvas.create_text(center_x, canvas_height * 0.88,
                                    text=celebration_str, fill='#FFD700', font=celebration_font, tags="countdown")
            self.create_fireworks(canvas_width, canvas_height)

            # 新年播放一次声音（只播放一次）
            if not self.sound_played:
                if os.path.isfile(self.sound_path):
                    self.play_sound_once(self.sound_path)
                self.sound_played = True

        # 整点 & 半点报时逻辑（在秒为 0 时触发一次）
        # 记录上次报时的 (year, month, day, hour, minute) 防止多次触发
        chime_time_tuple = (now.year, now.month, now.day, now.hour, now.minute)
        if second == 0 and (minute == 0 or minute == 30):
            if self.last_chime_time != chime_time_tuple:
                # 半点只播放一次短音；整点按12小时制播放次数
                if minute == 30:
                    # 半点：播放一次
                    if os.path.isfile(self.chime_path):
                        self.play_chime_sequence(self.chime_path, 1, interval=0.4)
                else:
                    # 整点：按12小时制播放报时次数（0点/12点播放12下）
                    hour_12 = now.hour % 12
                    count = hour_12 if hour_12 != 0 else 12
                    if os.path.isfile(self.chime_path):
                        # 间隔稍长一点以便分辨
                        self.play_chime_sequence(self.chime_path, count, interval=0.6)
                self.last_chime_time = chime_time_tuple

        # 更新烟花
        self.update_fireworks(scale)

        # 100ms 后再次更新
        self.root.after(100, self.update_clock)

    def create_fireworks(self, canvas_width, canvas_height):
        if len(self.fireworks) < 50:
            for _ in range(3):
                x = random.randint(int(canvas_width * 0.1), int(canvas_width * 0.9))
                y = random.randint(int(canvas_height * 0.1), int(canvas_height * 0.7))
                color = random.choice(['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFD700'])
                for i in range(12):
                    angle = (360 / 12) * i
                    speed = random.uniform(2, 5)
                    self.fireworks.append({
                        'x': x, 'y': y,
                        'vx': speed * math.cos(math.radians(angle)),
                        'vy': speed * math.sin(math.radians(angle)),
                        'color': color, 'life': 30, 'size': random.randint(2, 4)
                    })

    def update_fireworks(self, scale):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        new_fireworks = []
        for fw in self.fireworks:
            fw['x'] += fw['vx']
            fw['y'] += fw['vy']
            fw['vy'] += 0.2
            fw['life'] -= 1
            if fw['life'] > 0 and 0 < fw['x'] < canvas_width and 0 < fw['y'] < canvas_height:
                size = fw['size'] * scale
                self.canvas.create_oval(fw['x'] - size, fw['y'] - size,
                                        fw['x'] + size, fw['y'] + size,
                                        fill=fw['color'], outline=fw['color'], tags="firework")
                new_fireworks.append(fw)
        self.fireworks = new_fireworks


def main():
    root = tk.Tk()
    app = NewYearCountdown(root)
    root.mainloop()


if __name__ == "__main__":
    main()

