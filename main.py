import pyautogui
import pyperclip
import time
import pygetwindow as gw
import tkinter as tk
from tkinter import messagebox
from threading import Thread

# selenium 모듈
from web_driver import *


# ld 플레이어 윈도우 핸들 이름
LD_PLAYER = 'LDPlayer'
# 프로그램 윈도우 핸들 이름
TKINTER_TITLE = '오픈카톡 자동화'
# 카카오톡 작업의 딜레이
KAKAO_DELAY = 0.2
# 윈도우 핸들 작업의 딜레이
WINDOW_DELAY = 0.1

# 채팅방 입장 --- chat_number: ld 플레이어에서 매크로로 설정된 번호


def get_in_chat(chat_number: int):
    pyautogui.press(str(chat_number))
    time.sleep(0.5)


# 채팅방의 링크 추출
def get_link():
    pyautogui.press('t')
    time.sleep(0.5)
    pyautogui.press('c')
    time.sleep(0.5)
    return pyperclip.paste()


# 채팅방의 이름 추출 --- link: 채팅방 링크
def get_title(link: str):
    web_driver.driver.get(link)
    return web_driver.find_element_without_wait('.tit_room', is_except=True).text


# 작성된 메세지 복사
def copy_message():
    # 프로그램 창과 ld 플레이어 창을 번갈아가며 복사해야함.
    global tkinter_window, message
    tkinter_window.activate()
    time.sleep(WINDOW_DELAY)
    pyperclip.copy(message)
    time.sleep(WINDOW_DELAY)
    kakao_window.activate()
    time.sleep(WINDOW_DELAY)


# 첫 번째 채팅방으로
def to_top():
    prev_link = ''
    while True:
        # 위로 스크롤
        pyautogui.press('e')
        time.sleep(1.5)
        get_in_chat(1)
        cur_link = get_link()
        exit_chat()
        if prev_link == cur_link:
            # 2번의 확인 후 동일 링크면 첫 번째 채팅방이므로 break
            break
        prev_link = cur_link


# 카카오톡에 메세지 붙여넣기
def write_message():
    global count
    for _ in range(count):
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(KAKAO_DELAY)
        pyautogui.press('enter')
        time.sleep(KAKAO_DELAY)


# 채팅방 나오기
def exit_chat():
    pyautogui.press('esc')
    time.sleep(1)


# 메세지 작성 쓰레드 타겟
def write_do():
    global tkinter_window, message, count, chats
    # 프로그램 윈도우 핸들
    tkinter_window = gw.getWindowsWithTitle(TKINTER_TITLE)[0]
    # 텍스트 박스로부터 메세지 추출
    message = text_box.get('1.0', 'end-1c')
    # 스핀박스로부터 횟수 추출
    count = int(count_spin.get())

    # 선택된 채팅방 목록 추출
    chats_items = list(chats.items())
    target_links = [chats_items[chat_index][0]
                    for chat_index in chats_list_box.curselection()]

    # 선택된 채팅방이 없으면 알림과 함께 종료
    if not target_links:
        messagebox.showinfo('알림', '채팅방 지정 필요')
        return

    # ld 플레이어 활성화
    kakao_window.activate()
    time.sleep(WINDOW_DELAY)

    # 완료 될 때까지 반복
    while True:
        # 채팅방이 8개 보다 작은 지 여부 변수
        is_less_than_8 = False

        # 맨 위로
        to_top()

        # 스크롤로 아래로 내리기 전 작업
        prev_link = ''
        for i in range(1, 9):
            # 더 이상 타겟이 없으면 종료
            if not target_links:
                messagebox.showinfo('알림', '쓰기 완료')
                return

            get_in_chat(i)
            cur_link = get_link()
            # 채팅방이 8개보다 작은 지 확인
            if prev_link == cur_link:
                if i > 4:
                    exit_chat()
                is_less_than_8 = True
                break
            # 선택된 채팅방이 타겟인지 확인
            if cur_link in target_links:
                copy_message()
                write_message()
                target_links.remove(cur_link)
            exit_chat()
            prev_link = cur_link

        # 8개보다 채팅방이 적다면 스크롤을 하지 않는다.
        if is_less_than_8:
            continue

        # 스크롤을 하며 하단의 채팅방 작업
        prev_link = ''
        while True:
            if not target_links:
                messagebox.showinfo('알림', '쓰기 완료')
                return
            pyautogui.press('i')
            time.sleep(KAKAO_DELAY)
            get_in_chat(8)
            cur_link = get_link()

            # 스크롤을 했으나 클릭 미스로 인해 채팅방에 들어가지 않았을 때
            if 'http' not in cur_link:
                continue
            # 선택된 채팅방이 타겟인지 확인
            if cur_link in target_links:
                copy_message()
                write_message()
                target_links.remove(cur_link)
            exit_chat()
            # 마지막 채팅방이라면 break
            if prev_link == cur_link:
                break
            prev_link = cur_link


# 메세지 작성 쓰레드
def write_job():
    Thread(target=write_do).start()


# 채팅방 목록화 쓰레드 타겟
def get_chats_do():
    global chats
    # 채팅방 목록 초기화
    chats = {}
    chats_list_box.delete(0, tk.END)

    # ld 플레이어 활성화
    kakao_window.activate()
    time.sleep(WINDOW_DELAY)

    # 맨 위로
    to_top()

    # 채팅방이 8개 보다 작은 지 여부 변수
    is_less_than_8 = False
    prev_link = ''
    for i in range(1, 9):
        get_in_chat(i)
        cur_link = get_link()
        # 채팅방이 8개보다 작은 지 확인
        if prev_link == cur_link:
            if i > 4:
                exit_chat()
            is_less_than_8 = True
            break
        exit_chat()
        # 선택된 채팅방이 이미 목록화 된 것인 지 확인
        if cur_link in list(chats.keys()):
            print('continue')
            continue
        # 제목 추출
        title = get_title(cur_link)
        chats[cur_link] = title
        prev_link = cur_link

    # 8개보다 채팅방이 적다면 스크롤을 하지 않는다.
    if not is_less_than_8:
        while True:
            pyautogui.press('i')
            time.sleep(KAKAO_DELAY)
            get_in_chat(8)
            cur_link = get_link()
            # 스크롤을 했으나 클릭 미스로 인해 채팅방에 들어가지 않았을 때
            if 'http' not in cur_link:
                continue
            exit_chat()
            # 선택된 채팅방이 이미 목록화 된 것인 지 확인
            if cur_link in list(chats.keys()):
                # 마지막 채팅방이라면 break
                if prev_link == cur_link:
                    break
            else:
                # 제목 추출
                title = get_title(cur_link)
                chats[cur_link] = title
            prev_link = cur_link

    # 채팅방 목록 작성
    count = 1
    for k, v in chats.items():
        chats_list_box.insert(count, v)
        count += 1

    messagebox.showinfo('안내', '채팅방 목록화 완료')


# 채팅방 목록화 쓰레드
def get_chats_job():
    Thread(target=get_chats_do).start()


# 선택된 채팅방 목록 초기화
def clean_selected_do():
    chats_list_box.selection_clear(0, tk.END)


if __name__ == '__main__':
    # 글로벌 변수 지정
    web_driver = Web_driver()
    kakao_window = gw.getWindowsWithTitle(LD_PLAYER)[0]
    chats = {}

    # tkinter
    root = tk.Tk()
    root.title(TKINTER_TITLE)

    # message part
    tk.Label(root, text='메세지').pack()
    text_box = tk.Text(root, width=60, height=20)
    text_box.pack()

    # button part
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    count_spin = tk.Spinbox(button_frame, from_=1, to=999, wrap=True, width=5)
    count_spin.grid(row=0, column=0, padx=5)

    chats_btn = tk.Button(button_frame, text='채팅방 목록화', command=get_chats_job)
    chats_btn.grid(row=0, column=1, padx=5)

    write_btn = tk.Button(button_frame, text='쓰기', command=write_job)
    write_btn.grid(row=0, column=2, padx=5)

    clean_selected_btn = tk.Button(
        button_frame, text='선택된 채팅목록 해제', command=clean_selected_do)
    clean_selected_btn.grid(row=0, column=3, padx=5)

    # 채팅방 목록 part
    tk.Label(root, text='채팅방 목록').pack()
    yscrollbar = tk.Scrollbar(root)
    yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    chats_list_box = tk.Listbox(
        root, width=60, height=20, selectmode=tk.MULTIPLE, yscrollcommand=yscrollbar.set)
    chats_list_box.pack(expand=tk.YES, fill=tk.BOTH)

    root.mainloop()
