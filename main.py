import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import time
import json
import os
from datetime import datetime
import re


class DvorakTypingTrainer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("드보락 키보드 타자연습 & 코딩 연습")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a1a")

        # 변수 초기화
        self.current_text = ""
        self.user_input = ""
        self.start_time = None
        self.is_typing = False
        self.current_position = 0
        self.correct_chars = 0
        self.total_chars = 0

        # 텍스트 줄별 관리
        self.text_lines = []
        self.user_lines = []
        self.current_line = 0
        self.current_char_in_line = 0

        # 코딩 모드 관련 변수
        self.is_coding_mode = False
        self.current_language = "python"
        self.current_difficulty = "basic"
        self.coding_templates = {}
        self.load_coding_templates()

        # 드보락 키보드 매핑
        # 주의: OS에서 이미 드보락 레이아웃을 사용 중이라면 추가 매핑을 적용하면 이중 변환이 발생합니다.
        # 기본값을 활성화로 하여 QWERTY 레이아웃에서도 드보락 입력처럼 타이핑되도록 함
        self.use_dvorak_mapping = True
        self.dvorak_mapping = {
            "q": "q",
            "w": "w",
            "e": "e",
            "r": "p",
            "t": "y",
            "y": "f",
            "u": "g",
            "i": "c",
            "o": "r",
            "p": "l",
            "a": "a",
            "s": "o",
            "d": "e",
            "f": "u",
            "g": "i",
            "h": "d",
            "j": "h",
            "k": "t",
            "l": "n",
            ";": "s",
            "z": ";",
            "x": "q",
            "c": "j",
            "v": "k",
            "b": "x",
            "n": "b",
            "m": "m",
            ",": "w",
            ".": "v",
            "/": "z",
            "'": "-",
            '"': "_",
            "[": "]",
            "]": "\\",
            "\\": "`",
            "₩": "'",
            "`": "`",
            "1": "1",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8",
            "9": "9",
            "0": "0",
            "-": "]",
            "=": "\\",
            "+": "=",  # Shift+='=' 입력 시 '=' 출력되도록 추가
        }

        # 통계 데이터
        self.stats_file = "typing_stats.json"
        self.load_stats()

        # 드보락 레이아웃 표시
        self.dvorak_layout = [
            ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "[", "]", "\\"],
            ["", "q", "w", "e", ".", "p", "y", "f", "g", "c", "r", "l", "", ""],
            ["", "a", "o", "e", "u", "i", "d", "h", "t", "n", "s", "-", "", ""],
            ["", ";", "q", "j", "k", "x", "b", "m", "w", "v", "z", "", "", ""],
        ]

        # 사이즈 설정 (사이드 패널과 키 표시 확대용)
        self.side_panel_width = 340  # 기존 250에서 확대
        self.keyboard_key_width = 3  # 기존 2에서 확대
        self.keyboard_key_height = 2  # 기존 1에서 확대
        self.keyboard_font_size = 9  # 기존 7에서 확대
        self.keyboard_gap_px = 2  # 키 간격
        self.keyboard_empty_size = 26  # 빈 공간 크기(기존 20에서 확대)

        self.setup_ui()

        # 초기 언어 선택 화면 표시
        self.show_language_selection()

    def setup_ui(self):
        # 메인 컨테이너 및 레이아웃 가중치
        # 헤더(행 0)는 고정 높이, 메인(행 1)만 확장, 하단(행 2)은 고정
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        # 상단 헤더
        self.setup_header()

        # 메인 콘텐츠 영역 (좌우 분할)
        main_container = tk.Frame(self.root, bg="#1a1a1a")
        main_container.grid(
            row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5
        )
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=0)

        # 왼쪽: 타자연습 영역
        self.setup_typing_area(main_container)

        # 오른쪽: 사이드 패널
        self.setup_side_panel(main_container)

        # 하단: 통계 및 컨트롤
        self.setup_bottom_panel()

    def setup_header(self):
        """상단 헤더 설정"""
        self.header_frame = tk.Frame(self.root, bg="#2d2d2d", height=100)
        self.header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=0, pady=0)
        self.header_frame.grid_propagate(False)

        # 로고 및 제목
        title_frame = tk.Frame(self.header_frame, bg="#2d2d2d")
        title_frame.pack(side=tk.LEFT, padx=20, pady=20)

        # 프로그램 제목
        title_label = tk.Label(
            title_frame,
            text="드보락 키보드 타자연습",
            font=("맑은 고딕", 18, "bold"),
            bg="#2d2d2d",
            fg="#00ff00",
        )
        title_label.pack(side=tk.LEFT)

        # 뒤로가기 버튼
        self.back_button = tk.Button(
            self.header_frame,
            text="뒤로",
            command=self.show_language_selection,
            font=("맑은 고딕", 11),
            bg="#404040",
            fg="#00ff00",
            relief="flat",
            padx=12,
            pady=6,
            activebackground="#505050",
            activeforeground="#00ff00",
        )
        self.back_button.pack(side=tk.RIGHT, padx=12)

        # 라이브 통계 바 (헤더 하단)
        stats_bar = tk.Frame(self.header_frame, bg="#2d2d2d")
        stats_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 10))

        self.live_time_label = tk.Label(
            stats_bar,
            text="00:00",
            font=("맑은 고딕", 12, "bold"),
            bg="#2d2d2d",
            fg="#00ff00",
        )
        self.live_time_label.pack(side=tk.LEFT)

        tk.Label(stats_bar, text="  |  ", bg="#2d2d2d", fg="#00ff00").pack(side=tk.LEFT)

        self.live_speed_label = tk.Label(
            stats_bar,
            text="0타/분",
            font=("맑은 고딕", 12, "bold"),
            bg="#2d2d2d",
            fg="#00ff00",
        )
        self.live_speed_label.pack(side=tk.LEFT)

        tk.Label(stats_bar, text="  |  ", bg="#2d2d2d", fg="#00ff00").pack(side=tk.LEFT)

        self.live_acc_label = tk.Label(
            stats_bar,
            text="0%",
            font=("맑은 고딕", 12, "bold"),
            bg="#2d2d2d",
            fg="#00ff00",
        )
        self.live_acc_label.pack(side=tk.LEFT)

    def show_language_selection(self):
        """화면 정중앙에 언어 선택 화면 표시"""
        # 기존 텍스트 위젯 숨기기
        self.text_display.grid_remove()
        # 스크롤바도 함께 숨김
        if hasattr(self, "v_scrollbar"):
            self.v_scrollbar.grid_remove()
        if hasattr(self, "h_scrollbar"):
            self.h_scrollbar.grid_remove()
        # 좌/우/하단 패널도 숨김
        if hasattr(self, "typing_frame"):
            self.typing_frame.grid_remove()
        if hasattr(self, "side_frame"):
            self.side_frame.grid_remove()
        if hasattr(self, "bottom_frame"):
            self.bottom_frame.grid_remove()

        # 언어 선택 프레임 생성 (전체 창 기준 중앙 배치)
        self.language_selection_frame = tk.Frame(self.root, bg="#1a1a1a")
        # 정확히 창 중앙에 배치
        self.language_selection_frame.place(relx=0.5, rely=0.5, anchor="center")
        # 헤더 항상 최상단 유지
        if hasattr(self, "header_frame"):
            self.header_frame.lift()

        # 제목
        title_label = tk.Label(
            self.language_selection_frame,
            text="언어를 선택하세요",
            font=("맑은 고딕", 24, "bold"),
            bg="#1a1a1a",
            fg="#00ff00",
        )
        title_label.pack(pady=(0, 30))

        # 언어 선택 버튼들
        languages = [("Python", "python"), ("Java", "java"), ("C++", "cpp")]

        self.language_var = tk.StringVar()

        for lang_name, lang_value in languages:
            btn = tk.Button(
                self.language_selection_frame,
                text=lang_name,
                font=("맑은 고딕", 16, "bold"),
                bg="#1a1a1a",
                fg="#00ff00",
                activebackground="#2d2d2d",
                activeforeground="#00ff00",
                relief="raised",
                bd=2,
                padx=40,
                pady=15,
                highlightbackground="#00ff00",
                highlightcolor="#00ff00",
                command=lambda val=lang_value: self.select_language_and_difficulty(val),
            )
            btn.pack(pady=10)

        # 설명 텍스트
        desc_label = tk.Label(
            self.language_selection_frame,
            text="드보락 키보드로 코딩 연습을 시작합니다",
            font=("맑은 고딕", 12),
            bg="#1a1a1a",
            fg="#00cc00",
        )
        desc_label.pack(pady=(20, 0))

    def select_language_and_difficulty(self, language):
        """언어 선택 후 난이도 선택 창을 표시하고 시작"""
        self.current_language = language

        # 난이도 선택 창
        difficulty_window = tk.Toplevel(self.root)
        difficulty_window.title("난이도 선택")
        difficulty_window.configure(bg="#2a2a2a")
        difficulty_window.resizable(False, False)

        # 창을 콘텐츠 크기에 맞춘 뒤 중앙 정렬
        def center_window(win):
            win.update_idletasks()
            w = win.winfo_width() or 480
            h = win.winfo_height() or 240
            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = int((sw - w) / 2)
            y = int((sh - h) / 3)
            win.geometry(f"{w}x{h}+{x}+{y}")

        # 컨테이너
        container = tk.Frame(difficulty_window, bg="#2a2a2a")
        container.pack(padx=24, pady=20, fill=tk.BOTH, expand=True)

        title = tk.Label(
            container,
            text=f"{language.upper()} 난이도를 선택하세요",
            font=("맑은 고딕", 18, "bold"),
            bg="#2a2a2a",
            fg="#00ff66",
        )
        title.pack(pady=(0, 16))

        buttons_frame = tk.Frame(container, bg="#2a2a2a")
        buttons_frame.pack(pady=4)

        def proceed_with_difficulty(difficulty_key):
            # 선택한 난이도로 코딩 연습 시작
            self.current_difficulty = difficulty_key
            self.is_coding_mode = True

            # 언어 선택 화면 닫기
            if hasattr(self, "language_selection_frame"):
                try:
                    self.language_selection_frame.destroy()
                except Exception:
                    pass

            # 좌/우/하단 패널 복원
            if hasattr(self, "typing_frame"):
                self.typing_frame.grid(
                    row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10)
                )
            if hasattr(self, "side_frame"):
                self.side_frame.grid(
                    row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 0)
                )
            if hasattr(self, "bottom_frame"):
                self.bottom_frame.grid(
                    row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5
                )

            # 텍스트 위젯 다시 표시 (스크롤바는 숨김 유지)
            self.text_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            if hasattr(self, "header_frame"):
                self.header_frame.lift()

            # 새 연습 시작 (coding_templates.json 사용)
            self.start_new_practice()

            # 라이브 통계 초기화
            if hasattr(self, "live_time_label"):
                self.live_time_label.config(text="00:00")
            if hasattr(self, "live_speed_label"):
                self.live_speed_label.config(text="0타/분")
            if hasattr(self, "live_acc_label"):
                self.live_acc_label.config(text="0%")

            difficulty_window.destroy()

        # 난이도 버튼들 (균일 간격, 다크 테마 스타일)
        diff_defs = [
            ("기본", "basic"),
            ("중급", "intermediate"),
            ("고급", "advanced"),
        ]
        for label, key in diff_defs:
            tk.Button(
                buttons_frame,
                text=label,
                width=12,
                height=2,
                font=("맑은 고딕", 12, "bold"),
                bg="#1f1f1f",
                fg="#00ff66",
                activebackground="#333333",
                activeforeground="#00ff99",
                relief="raised",
                bd=2,
                highlightbackground="#00ff66",
                highlightcolor="#00ff66",
                command=lambda k=key: proceed_with_difficulty(k),
            ).pack(side=tk.LEFT, padx=12)

        # 단축키: 1/2/3로 선택, Esc로 닫기
        difficulty_window.bind("1", lambda e: proceed_with_difficulty("basic"))
        difficulty_window.bind("2", lambda e: proceed_with_difficulty("intermediate"))
        difficulty_window.bind("3", lambda e: proceed_with_difficulty("advanced"))
        difficulty_window.bind("<Escape>", lambda e: difficulty_window.destroy())

        # 초기 중앙 배치
        center_window(difficulty_window)

    def load_meaningful_code(self):
        """의미있는 코드만 로드"""
        if self.current_language == "python":
            self.current_text = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

numbers = [1, 2, 3, 4, 5]
squared = [x**2 for x in numbers]
print("Squared numbers:", squared)"""
        elif self.current_language == "java":
            self.current_text = """public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        
        int[] numbers = {1, 2, 3, 4, 5};
        for (int num : numbers) {
            System.out.println("Number: " + num);
        }
    }
}"""
        elif self.current_language == "cpp":
            self.current_text = """#include <iostream>
#include <vector>

int main() {
    std::cout << "Hello, World!" << std::endl;
    
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    for (int num : numbers) {
        std::cout << "Number: " << num << std::endl;
    }
    
    return 0;
}"""
        else:
            self.current_text = "기본 타자 연습 텍스트입니다."

        # 텍스트를 줄 단위로 분리
        self.text_lines = self.current_text.split("\n")
        self.user_lines = [""] * len(self.text_lines)

        # 통계 초기화
        self.reset_practice()

        # 텍스트 표시
        self.display_text()

    def setup_typing_area(self, parent):
        """타자연습 메인 영역"""
        self.typing_frame = tk.Frame(parent, bg="#1a1a1a", relief="sunken", bd=2)
        self.typing_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10)
        )
        self.typing_frame.grid_rowconfigure(0, weight=1)
        self.typing_frame.grid_columnconfigure(0, weight=1)

        # 코딩 모드 설정은 이제 중앙 언어 선택 화면에서 처리

        # 텍스트 표시 영역 (한컴타자연습 스타일)
        text_container = tk.Frame(self.typing_frame, bg="#1a1a1a")
        text_container.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=15, pady=15
        )
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)

        # 텍스트 위젯 (줄별 표시용)
        self.text_display = tk.Text(
            text_container,
            font=("Consolas", 14),
            wrap=tk.NONE,
            state=tk.DISABLED,
            bg="#000000",
            fg="#00ff00",
            relief="flat",
            bd=0,
            padx=20,
            pady=20,
            spacing1=5,
            spacing2=3,
            spacing3=5,
            insertbackground="#00ff00",
            selectbackground="#404040",
        )
        self.text_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 스크롤바 (인스턴스 변수로 저장하여 필요 시 숨김/표시)
        self.v_scrollbar = ttk.Scrollbar(
            text_container, orient="vertical", command=self.text_display.yview
        )
        # 기본은 숨김
        # self.v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.text_display.configure(yscrollcommand=self.v_scrollbar.set)

        self.h_scrollbar = ttk.Scrollbar(
            text_container, orient="horizontal", command=self.text_display.xview
        )
        # self.h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.text_display.configure(xscrollcommand=self.h_scrollbar.set)

        # 컨트롤 버튼은 이제 필요 없음 (언어 선택으로 대체)

    def setup_side_panel(self, parent):
        """오른쪽 사이드 패널"""
        self.side_frame = tk.Frame(
            parent, bg="#2d2d2d", width=self.side_panel_width, relief="sunken", bd=1
        )
        self.side_frame.grid(
            row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 0)
        )
        self.side_frame.grid_propagate(False)

        # 사용자 정보
        user_frame = tk.Frame(self.side_frame, bg="#2d2d2d")
        user_frame.pack(fill=tk.X, padx=15, pady=15)

        tk.Label(
            user_frame,
            text="사용자",
            font=("맑은 고딕", 14, "bold"),
            bg="#2d2d2d",
            fg="#00ff00",
        ).pack()
        tk.Label(
            user_frame,
            text="드보락 연습자",
            font=("맑은 고딕", 12),
            bg="#2d2d2d",
            fg="#00cc00",
        ).pack()

        # 연습 정보
        info_frame = tk.Frame(self.side_frame, bg="#2d2d2d")
        info_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(
            info_frame,
            text="연습 정보",
            font=("맑은 고딕", 12, "bold"),
            bg="#2d2d2d",
            fg="#00ff00",
        ).pack(anchor=tk.W)

        self.timer_label = tk.Label(
            info_frame,
            text="00:00",
            font=("맑은 고딕", 16, "bold"),
            bg="#2d2d2d",
            fg="#00ff00",
        )
        self.timer_label.pack(anchor=tk.W, pady=5)

        self.progress_info = tk.Label(
            info_frame,
            text="진행률: 0%",
            font=("맑은 고딕", 11),
            bg="#2d2d2d",
            fg="#00cc00",
        )
        self.progress_info.pack(anchor=tk.W)

        # 드보락 키보드 레이아웃 (전체)
        keyboard_frame = tk.Frame(self.side_frame, bg="#2d2d2d")
        keyboard_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(
            keyboard_frame,
            text="드보락 레이아웃",
            font=("맑은 고딕", 12, "bold"),
            bg="#2d2d2d",
            fg="#00ff00",
        ).pack(anchor=tk.W)

        # 전체 드보락 키보드 표시
        key_container = tk.Frame(keyboard_frame, bg="#1a1a1a", relief="sunken", bd=1)
        key_container.pack(fill=tk.X, pady=6)

        # 드보락 레이아웃 정의
        dvorak_rows = [
            ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "[", "]", "\\"],
            ["", "q", "w", "e", ".", "p", "y", "f", "g", "c", "r", "l", "", ""],
            ["", "a", "o", "e", "u", "i", "d", "h", "t", "n", "s", "-", "", ""],
            ["", ";", "q", "j", "k", "x", "b", "m", "w", "v", "z", "", "", ""],
        ]

        for row_keys in dvorak_rows:
            row_frame = tk.Frame(key_container, bg="#1a1a1a")
            row_frame.pack(pady=self.keyboard_gap_px)
            for key in row_keys:
                if key:
                    btn = tk.Label(
                        row_frame,
                        text=key,
                        width=self.keyboard_key_width,
                        height=self.keyboard_key_height,
                        font=("맑은 고딕", self.keyboard_font_size),
                        bg="#404040",
                        fg="#00ff00",
                        relief="raised",
                        bd=1,
                    )
                    btn.pack(side=tk.LEFT, padx=self.keyboard_gap_px)
                else:
                    # 빈 공간
                    tk.Frame(
                        row_frame,
                        width=self.keyboard_empty_size,
                        height=self.keyboard_empty_size,
                    ).pack(side=tk.LEFT, padx=self.keyboard_gap_px)

    def setup_bottom_panel(self):
        """하단 패널 (통계 및 키보드 시각화)"""
        self.bottom_frame = tk.Frame(self.root, bg="#2d2d2d", height=120)
        self.bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        self.bottom_frame.grid_propagate(False)

        # 통계 정보
        stats_frame = tk.Frame(self.bottom_frame, bg="#2d2d2d")
        stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)

        # 타이핑 속도
        speed_frame = tk.Frame(stats_frame, bg="#2d2d2d")
        speed_frame.pack(side=tk.LEFT, padx=20)

        tk.Label(
            speed_frame,
            text="타 수",
            font=("맑은 고딕", 10),
            bg="#2d2d2d",
            fg="#00cc00",
        ).pack()
        self.speed_label = tk.Label(
            speed_frame,
            text="0타/분",
            font=("맑은 고딕", 16, "bold"),
            bg="#2d2d2d",
            fg="#00ff00",
        )
        self.speed_label.pack()

        # 정확도
        acc_frame = tk.Frame(stats_frame, bg="#2d2d2d")
        acc_frame.pack(side=tk.LEFT, padx=20)

        tk.Label(
            acc_frame, text="정확도", font=("맑은 고딕", 10), bg="#2d2d2d", fg="#00cc00"
        ).pack()
        self.accuracy_label = tk.Label(
            acc_frame,
            text="0%",
            font=("맑은 고딕", 16, "bold"),
            bg="#2d2d2d",
            fg="#00ff00",
        )
        self.accuracy_label.pack()

        # 진행률 바
        progress_frame = tk.Frame(stats_frame, bg="#2d2d2d")
        progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)

        tk.Label(
            progress_frame,
            text="진행률",
            font=("맑은 고딕", 10),
            bg="#2d2d2d",
            fg="#00cc00",
        ).pack(anchor=tk.W)

        progress_bg = tk.Frame(progress_frame, bg="#404040", height=8)
        progress_bg.pack(fill=tk.X, pady=5)

        self.progress_bar = tk.Frame(progress_bg, bg="#00ff00", height=8)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.Y)

        # 컨트롤 버튼
        control_frame = tk.Frame(self.bottom_frame, bg="#2d2d2d")
        control_frame.pack(side=tk.RIGHT, padx=20, pady=15)

        tk.Button(
            control_frame,
            text="통계 보기",
            command=self.show_stats,
            font=("맑은 고딕", 11),
            bg="#004466",
            fg="#00ff00",
            relief="flat",
            padx=15,
            pady=8,
            activebackground="#006688",
            activeforeground="#00ff00",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            control_frame,
            text="설정",
            command=self.show_settings,
            font=("맑은 고딕", 11),
            bg="#404040",
            fg="#00ff00",
            relief="flat",
            padx=15,
            pady=8,
            activebackground="#505050",
            activeforeground="#00ff00",
        ).pack(side=tk.LEFT, padx=5)

    def setup_input_area(self, parent, row):
        # 입력 영역은 이제 별도로 필요하지 않음 (텍스트 위젯에서 직접 처리)
        pass

    def load_coding_templates(self):
        """코딩 템플릿 로드"""
        try:
            with open("coding_templates.json", "r", encoding="utf-8") as file:
                self.coding_templates = json.load(file)
        except FileNotFoundError:
            self.coding_templates = {}
            print("코딩 템플릿 파일을 찾을 수 없습니다.")
        except Exception as e:
            self.coding_templates = {}
            print(f"코딩 템플릿 로드 오류: {e}")

    def switch_mode(self):
        """모드 전환"""
        mode = self.mode_var.get()
        self.is_coding_mode = mode == "coding"

        if self.is_coding_mode:
            self.coding_settings_frame.grid(
                row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5
            )
            self.text_display.config(
                font=("Consolas", 14), wrap=tk.NONE, bg="#000000", fg="#00ff00"
            )
            self.difficulty_button.config(text="코드 선택")
        else:
            self.coding_settings_frame.grid_remove()
            self.text_display.config(
                font=("Consolas", 14), wrap=tk.NONE, bg="#000000", fg="#00ff00"
            )
            self.difficulty_button.config(text="난이도 선택")

        # 현재 텍스트 초기화
        self.current_text = ""
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.config(state=tk.DISABLED)
        self.reset_practice()

    def on_difficulty_change(self, event=None):
        """난이도 변경 처리"""
        self.current_difficulty = self.difficulty_var.get()
        # 난이도 변경 시 자동으로 새 텍스트 로드
        if self.is_coding_mode:
            self.start_new_practice()

    def start_new_practice(self):
        """새로운 연습 시작"""
        if self.is_coding_mode:
            self.current_text = self.generate_coding_text()
        else:
            self.current_text = self.generate_practice_text()

        if self.current_text:
            self.display_text()
            self.reset_practice()
        # status_label 제거됨

    def generate_practice_text(self):
        """연습용 텍스트 생성 (실제적인 드보락 연습용)"""
        # 드보락 키보드 연습용 텍스트 - 실제 사용에 가까운 내용
        practice_texts = [
            "def calculate_fibonacci(n):\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)\n\nresult = calculate_fibonacci(10)\nprint(f'Fibonacci of 10 is {result}')",
            "import requests\nfrom typing import Dict, List\n\ndef fetch_user_data(user_id: int) -> Dict[str, str]:\n    url = f'https://api.example.com/users/{user_id}'\n    response = requests.get(url)\n    return response.json()\n\nusers = [1, 2, 3, 4, 5]\nfor user_id in users:\n    data = fetch_user_data(user_id)\n    print(data['name'])",
            "class DatabaseConnection:\n    def __init__(self, host: str, port: int):\n        self.host = host\n        self.port = port\n        self.connected = False\n    \n    def connect(self) -> bool:\n        try:\n            # Connection logic here\n            self.connected = True\n            return True\n        except Exception as e:\n            print(f'Connection failed: {e}')\n            return False",
            "async def process_large_dataset(data: List[Dict]) -> List[Dict]:\n    results = []\n    async with aiohttp.ClientSession() as session:\n        tasks = [process_item(session, item) for item in data]\n        results = await asyncio.gather(*tasks)\n    return results\n\nasync def process_item(session, item):\n    async with session.post('/api/process', json=item) as response:\n        return await response.json()",
            "from dataclasses import dataclass\nfrom datetime import datetime\n\n@dataclass\nclass UserProfile:\n    user_id: int\n    username: str\n    email: str\n    created_at: datetime\n    is_active: bool = True\n    \n    def update_last_login(self):\n        self.last_login = datetime.now()\n    \n    def deactivate(self):\n        self.is_active = False\n        self.updated_at = datetime.now()",
        ]
        return random.choice(practice_texts)

    def generate_coding_text(self):
        """코딩 텍스트 생성"""
        if not self.coding_templates:
            return "코딩 템플릿을 로드할 수 없습니다."

        language = self.current_language
        difficulty = self.current_difficulty

        if (
            language in self.coding_templates
            and difficulty in self.coding_templates[language]
        ):
            templates = self.coding_templates[language][difficulty]
            # 기본(basic)은 한 번에 더 길게: 해당 레벨의 앞부분 예문만 연결하여 표시
            if (
                difficulty == "basic"
                and isinstance(templates, list)
                and len(templates) > 0
            ):
                # 너무 길지 않도록 앞의 3개만 사용 (3개 미만이면 가능한 만큼)
                return "\n\n".join(templates[:2])
            # 그 외 레벨은 첫 번째 예문을 사용
            if isinstance(templates, list) and len(templates) > 0:
                return templates[0]
            return f"{language} 언어의 {difficulty} 난이도 템플릿이 비어있습니다."
        else:
            return f"{language} 언어의 {difficulty} 난이도 템플릿을 찾을 수 없습니다."

    def display_text(self):
        """텍스트를 한컴타자연습 스타일로 표시"""
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)

        # 텍스트를 줄별로 분리
        self.text_lines = self.current_text.split("\n")
        self.user_lines = [""] * len(self.text_lines)

        # 태그 설정
        self.setup_text_tags()

        # 각 줄을 원문-사용자입력 쌍으로 표시
        display_lines = []
        for i, line in enumerate(self.text_lines):
            # 원문 줄
            display_lines.append(line)
            # 사용자 입력 줄 (빈 줄)
            display_lines.append("")

        # 전체 텍스트 삽입
        full_text = "\n".join(display_lines)
        self.text_display.insert(1.0, full_text)

        # 태그 적용
        for i, line in enumerate(self.text_lines):
            # 원문 줄 태그
            line_start = f"{i*2 + 1}.0"
            line_end = f"{i*2 + 1}.end"
            self.text_display.tag_add("original", line_start, line_end)

            # 사용자 입력 줄 태그
            user_line_start = f"{i*2 + 2}.0"
            user_line_end = f"{i*2 + 2}.end"
            self.text_display.tag_add("user_input", user_line_start, user_line_end)

            # 사용자 입력 줄을 원문 들여쓰기와 정렬되도록 왼쪽 마진을 부여
            try:
                import tkinter.font as tkfont

                font = tkfont.Font(font=("Consolas", 14))
                leading_spaces = len(self.text_lines[i]) - len(
                    self.text_lines[i].lstrip(" ")
                )
                indent_px = font.measure(" " * leading_spaces)
                indent_tag = f"user_indent_{i}"
                self.text_display.tag_configure(
                    indent_tag, lmargin1=indent_px, lmargin2=indent_px
                )
                self.text_display.tag_add(indent_tag, user_line_start, user_line_end)
            except Exception:
                pass

        # 코딩 모드일 때 문법 하이라이팅 적용
        if self.is_coding_mode:
            self.apply_syntax_highlighting()

        self.text_display.config(state=tk.DISABLED)

        # 현재 위치 초기화
        self.current_line = 0
        self.current_char_in_line = 0

        # 키보드 이벤트 바인딩
        self.text_display.bind("<KeyPress>", self.on_key_press)
        self.text_display.bind("<Button-1>", lambda e: self.text_display.focus_set())
        self.text_display.focus_set()

        # 첫 줄 들여쓰기 자동 적용
        self.apply_auto_indent_for_current_line()
        # 캐럿 깜빡임 시작
        self.start_caret_blink()
        # 초기 캐럿 표시를 위해 한 번 라인 갱신
        self.update_user_line()

    def setup_text_tags(self):
        """텍스트 태그 설정 (다크 테마)"""
        # 원문 텍스트 (어두운 초록)
        self.text_display.tag_configure(
            "original", foreground="#006600", background="#0a0a0a"
        )

        # 사용자 입력 텍스트 (밝은 초록)
        self.text_display.tag_configure(
            "user_input", foreground="#00ff00", background="#000000"
        )

        # 올바른 입력 (밝은 초록)
        self.text_display.tag_configure(
            "correct", foreground="#00ff00", background="#003300"
        )

        # 잘못된 입력 (빨강)
        self.text_display.tag_configure(
            "incorrect", foreground="#ff0000", background="#330000"
        )

        # 현재 입력 위치 (노랑 배경)
        self.text_display.tag_configure(
            "current", background="#333300", foreground="#ffff00"
        )

        # 코딩 모드 태그들
        self.text_display.tag_configure(
            "keyword", foreground="#00ffff", font=("Consolas", 14, "bold")
        )
        self.text_display.tag_configure("string", foreground="#00ff00")
        self.text_display.tag_configure(
            "comment", foreground="#666666", font=("Consolas", 14, "italic")
        )
        self.text_display.tag_configure("number", foreground="#ffaa00")
        self.text_display.tag_configure("function", foreground="#ff00ff")
        # 캐럿(깜빡임) 표시용
        self.text_display.tag_configure(
            "caret", background="#666600", foreground="#ffff00"
        )

    def start_caret_blink(self):
        """현재 위치에서 캐럿 깜빡임 시작"""
        self.caret_blink_on = True
        self._blink_caret()

    def stop_caret_blink(self):
        """캐럿 깜빡임 중지"""
        self.caret_blink_on = False
        self.text_display.config(state=tk.NORMAL)
        self.text_display.tag_remove("caret", "1.0", tk.END)
        self.text_display.config(state=tk.DISABLED)

    def _blink_caret(self):
        if not getattr(self, "caret_blink_on", False):
            return
        # 현재 위치에 caret 토글
        if self.current_line < len(self.text_lines):
            user_line_num = self.current_line * 2 + 2
            start = f"{user_line_num}.{self.current_char_in_line}"
            end = f"{user_line_num}.{self.current_char_in_line + 1}"
            self.text_display.config(state=tk.NORMAL)
            # 토글 방식: 있으면 제거, 없으면 추가
            ranges = self.text_display.tag_ranges("caret")
            has_tag = False
            for i in range(0, len(ranges), 2):
                if str(ranges[i]) == start and str(ranges[i + 1]) == end:
                    has_tag = True
                    break
            if has_tag:
                self.text_display.tag_remove("caret", start, end)
            else:
                self.text_display.tag_add("caret", start, end)
            self.text_display.config(state=tk.DISABLED)
        # 500ms 후 반복
        self.root.after(500, self._blink_caret)

    def apply_auto_indent_for_current_line(self):
        """현재 줄의 선행 공백만큼 자동 들여쓰기 및 캐럿 위치 보정"""
        if self.current_line >= len(self.text_lines):
            return

        line_text = self.text_lines[self.current_line]
        leading_spaces = len(line_text) - len(line_text.lstrip(" "))

        # 사용자 입력 버퍼에 선행 공백을 자동 삽입하고 현재 위치를 첫 글자에 놓음
        if self.current_line < len(self.user_lines):
            # 이미 들여써졌으면 중복으로 넣지 않음
            if len(self.user_lines[self.current_line]) < leading_spaces:
                self.user_lines[self.current_line] = " " * leading_spaces
            # 커서/현재 위치 보정
            self.current_char_in_line = max(self.current_char_in_line, leading_spaces)

        # 텍스트 위젯에 들여쓰기 반영
        try:
            import tkinter.font as tkfont

            user_line_num = self.current_line * 2 + 2
            user_line_start = f"{user_line_num}.0"
            user_line_end = f"{user_line_num}.end"
            font = tkfont.Font(font=("Consolas", 14))
            indent_px = font.measure(" " * leading_spaces)
            indent_tag = f"user_indent_{self.current_line}"
            self.text_display.config(state=tk.NORMAL)
            self.text_display.tag_configure(
                indent_tag, lmargin1=indent_px, lmargin2=indent_px
            )
            self.text_display.tag_add(indent_tag, user_line_start, user_line_end)
            self.text_display.config(state=tk.DISABLED)
        except Exception:
            pass

    def apply_syntax_highlighting(self):
        """문법 하이라이팅 적용"""
        if not self.current_text:
            return

        # 태그 설정
        self.text_display.tag_configure(
            "keyword", foreground="#0000FF", font=("Consolas", 12, "bold")
        )
        self.text_display.tag_configure("string", foreground="#008000")
        self.text_display.tag_configure(
            "comment", foreground="#808080", font=("Consolas", 12, "italic")
        )
        self.text_display.tag_configure("number", foreground="#FF8000")
        self.text_display.tag_configure("function", foreground="#800080")

        # 언어별 키워드 정의
        keywords = self.get_language_keywords()

        # 키워드 하이라이팅
        for keyword in keywords:
            start = "1.0"
            while True:
                pos = self.text_display.search(
                    rf"\b{keyword}\b", start, tk.END, regexp=True
                )
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                self.text_display.tag_add("keyword", pos, end)
                start = end

        # 문자열 하이라이팅
        string_patterns = [r'"[^"]*"', r"'[^']*'", r"`[^`]*`"]
        for pattern in string_patterns:
            start = "1.0"
            while True:
                pos = self.text_display.search(pattern, start, tk.END, regexp=True)
                if not pos:
                    break
                end = self.text_display.index(f"{pos} lineend")
                self.text_display.tag_add("string", pos, end)
                start = end

        # 주석 하이라이팅
        comment_patterns = self.get_comment_patterns()
        for pattern in comment_patterns:
            start = "1.0"
            while True:
                pos = self.text_display.search(pattern, start, tk.END, regexp=True)
                if not pos:
                    break
                end = self.text_display.index(f"{pos} lineend")
                self.text_display.tag_add("comment", pos, end)
                start = end

    def get_language_keywords(self):
        """언어별 키워드 반환"""
        keyword_map = {
            "python": [
                "def",
                "class",
                "if",
                "else",
                "elif",
                "for",
                "while",
                "import",
                "from",
                "return",
                "try",
                "except",
                "finally",
                "with",
                "as",
                "lambda",
                "yield",
                "async",
                "await",
                "True",
                "False",
                "None",
            ],
            "java": [
                "public",
                "private",
                "protected",
                "class",
                "interface",
                "extends",
                "implements",
                "if",
                "else",
                "for",
                "while",
                "switch",
                "case",
                "break",
                "continue",
                "return",
                "try",
                "catch",
                "finally",
                "throw",
                "throws",
                "static",
                "final",
                "abstract",
                "synchronized",
                "volatile",
                "transient",
                "native",
                "strictfp",
            ],
            "javascript": [
                "function",
                "var",
                "let",
                "const",
                "if",
                "else",
                "for",
                "while",
                "do",
                "switch",
                "case",
                "break",
                "continue",
                "return",
                "try",
                "catch",
                "finally",
                "throw",
                "typeof",
                "instanceof",
                "new",
                "this",
                "true",
                "false",
                "null",
                "undefined",
            ],
            "cpp": [
                "int",
                "float",
                "double",
                "char",
                "bool",
                "void",
                "if",
                "else",
                "for",
                "while",
                "do",
                "switch",
                "case",
                "break",
                "continue",
                "return",
                "try",
                "catch",
                "throw",
                "class",
                "struct",
                "public",
                "private",
                "protected",
                "virtual",
                "static",
                "const",
                "volatile",
                "extern",
                "inline",
                "template",
                "namespace",
                "using",
                "new",
                "delete",
            ],
            "react": [
                "import",
                "export",
                "default",
                "function",
                "const",
                "let",
                "var",
                "if",
                "else",
                "for",
                "while",
                "do",
                "switch",
                "case",
                "break",
                "continue",
                "return",
                "try",
                "catch",
                "finally",
                "throw",
                "typeof",
                "instanceof",
                "new",
                "this",
                "true",
                "false",
                "null",
                "undefined",
                "useState",
                "useEffect",
                "useContext",
                "useReducer",
                "useMemo",
                "useCallback",
                "React",
                "Component",
            ],
        }
        return keyword_map.get(self.current_language, [])

    def get_comment_patterns(self):
        """언어별 주석 패턴 반환"""
        comment_map = {
            "python": [r"#.*"],
            "java": [r"//.*", r"/\*.*?\*/"],
            "javascript": [r"//.*", r"/\*.*?\*/"],
            "cpp": [r"//.*", r"/\*.*?\*/"],
            "react": [r"//.*", r"/\*.*?\*/", r"\{/\*.*?\*/\}"],
        }
        return comment_map.get(self.current_language, [])

    def highlight_text(self):
        """입력한 부분 하이라이트"""
        self.text_display.config(state=tk.NORMAL)

        # 모든 하이라이트 제거
        self.text_display.tag_remove("correct", "1.0", tk.END)
        self.text_display.tag_remove("incorrect", "1.0", tk.END)
        self.text_display.tag_remove("current", "1.0", tk.END)

        # 입력한 부분까지 하이라이트
        if self.current_position > 0:
            self.text_display.tag_add("correct", "1.0", f"1.{self.correct_chars}")
            self.text_display.tag_config(
                "correct", background="#d5f4e6", foreground="#2c3e50"
            )

        # 현재 위치 표시
        if self.current_position < len(self.current_text):
            self.text_display.tag_add(
                "current",
                f"1.{self.current_position}",
                f"1.{self.current_position + 1}",
            )
            self.text_display.tag_config(
                "current", background="#3498db", foreground="white"
            )

        self.text_display.config(state=tk.DISABLED)

    def on_key_press(self, event):
        """키 입력 처리 (한컴타자연습 스타일)"""
        if not self.is_typing and len(self.text_lines) > 0:
            self.start_time = time.time()
            self.is_typing = True
            self.start_timer()

        # Enter 키 처리
        if event.keysym == "Return":
            if self.current_line < len(
                self.text_lines
            ) and self.current_char_in_line >= len(self.text_lines[self.current_line]):
                # 현재 줄 완료, 다음 줄로
                self.move_to_next_line()
            return "break"

        # Backspace 처리
        if event.keysym == "BackSpace":
            self.handle_backspace()
            return "break"

        # 일반 문자 입력
        if (
            len(event.char) == 1
            and event.char.isprintable()
            and len(self.text_lines) > 0
        ):
            self.handle_char_input(event.char)
            return "break"

        return None

    def handle_char_input(self, char):
        """문자 입력 처리 (드보락 키보드 지원)"""
        if self.current_line >= len(self.text_lines):
            return

        # 드보락 키보드 매핑 적용
        if self.use_dvorak_mapping:
            dvorak_char = self.dvorak_mapping.get(char.lower(), char)
            if char.isupper():
                dvorak_char = dvorak_char.upper()
        else:
            dvorak_char = char

        current_line_text = self.text_lines[self.current_line]

        # 현재 줄이 가득 찼으면 자동 개행 후 시각적 피드백(깜빡임)
        if self.current_char_in_line >= len(current_line_text):
            prev_line = self.current_line
            self.move_to_next_line()
            # 모든 줄을 마친 경우 종료
            if self.current_line == prev_line:
                return
            self.flash_current_input_line()
            current_line_text = self.text_lines[self.current_line]

        # 현재 줄 길이를 초과하면 더 이상 입력하지 않음
        if self.current_char_in_line >= len(current_line_text):
            self.move_to_next_line()
            self.flash_current_input_line()
            # 새 줄의 자동 들여쓰기 적용
            self.apply_auto_indent_for_current_line()
            return

        if self.current_char_in_line < len(current_line_text):
            expected_char = current_line_text[self.current_char_in_line]

            # 사용자 입력 줄 업데이트 (드보락 문자로)
            self.user_lines[self.current_line] += dvorak_char

            # 텍스트 위젯 업데이트
            self.update_user_line()

            if dvorak_char == expected_char:
                self.correct_chars += 1
                self.total_chars += 1
                self.current_char_in_line += 1
            else:
                # 잘못된 입력 (빨간색 표시)
                self.total_chars += 1
                self.current_char_in_line += 1

            self.update_stats()
            self.update_progress_bar()

            # 줄 완료 체크: 자동으로 다음 줄 이동 및 자동 스크롤
            if self.current_char_in_line >= len(current_line_text):
                self.move_to_next_line()
                self.flash_current_input_line()
                # 새 줄의 자동 들여쓰기 적용
                self.apply_auto_indent_for_current_line()

    def handle_backspace(self):
        """백스페이스 처리"""
        if self.current_char_in_line > 0:
            self.current_char_in_line -= 1
            if len(self.user_lines[self.current_line]) > 0:
                self.user_lines[self.current_line] = self.user_lines[self.current_line][
                    :-1
                ]
                self.update_user_line()
                self.update_stats()
                self.update_progress_bar()

    def move_to_next_line(self):
        """다음 줄로 이동"""
        if self.current_line < len(self.text_lines) - 1:
            self.current_line += 1
            self.current_char_in_line = 0
            self.update_stats()
            self.update_progress_bar()
            # 새 줄 시작 위치로 자동 스크롤 및 현재 위치 하이라이트
            user_line_num = self.current_line * 2 + 2
            pos = f"{user_line_num}.0"
            self.text_display.see(pos)
            # 자동 들여쓰기 적용
            self.apply_auto_indent_for_current_line()
        else:
            # 모든 줄 완료
            self.check_completion()

    def flash_current_input_line(self):
        """현재 입력 줄을 짧게 깜빡여 개행을 알림"""
        if self.current_line < len(self.text_lines):
            user_line_num = self.current_line * 2 + 2
            start = f"{user_line_num}.0"
            end = f"{user_line_num}.end"
            self.text_display.config(state=tk.NORMAL)
            # 임시 하이라이트 태그
            self.text_display.tag_configure("line_flash", background="#333333")
            self.text_display.tag_add("line_flash", start, end)
            self.text_display.config(state=tk.DISABLED)

            # 150ms 후 원상복구
            def _clear_flash():
                self.text_display.config(state=tk.NORMAL)
                self.text_display.tag_remove("line_flash", start, end)
                self.text_display.config(state=tk.DISABLED)

            self.root.after(150, _clear_flash)

    def update_user_line(self):
        """사용자 입력 줄 업데이트"""
        if self.current_line < len(self.text_lines):
            user_line_num = self.current_line * 2 + 2  # 사용자 입력 줄 번호
            user_line_start = f"{user_line_num}.0"
            user_line_end = f"{user_line_num}.end"

            # 기존 태그 제거
            self.text_display.tag_remove("correct", user_line_start, user_line_end)
            self.text_display.tag_remove("incorrect", user_line_start, user_line_end)
            self.text_display.tag_remove("current", user_line_start, user_line_end)

            # 사용자 입력 텍스트 업데이트
            self.text_display.config(state=tk.NORMAL)
            self.text_display.delete(user_line_start, user_line_end)
            self.text_display.insert(
                user_line_start, self.user_lines[self.current_line]
            )

            # 정오 표기 적용
            current_line_text = self.text_lines[self.current_line]
            user_input = self.user_lines[self.current_line]
            # 라인 길이를 초과해 그려지지 않도록 사용자 입력을 제한해서 표시
            if len(user_input) > len(current_line_text):
                user_input = user_input[: len(current_line_text)]

            # 아래줄과 위줄의 좌우 간격을 맞추기 위해, 문자폭이 고정이 아닌 경우에도
            # 문자 단위로 동일 위치에 태그를 적용한다
            for i, (expected, actual) in enumerate(zip(current_line_text, user_input)):
                char_start = f"{user_line_num}.{i}"
                char_end = f"{user_line_num}.{i+1}"

                if expected == actual:
                    self.text_display.tag_add("correct", char_start, char_end)
                else:
                    self.text_display.tag_add("incorrect", char_start, char_end)

            # 부족한 영역(아직 입력하지 않은 위치)은 원문과 간격을 맞추기 위해 공백 태그를 적용
            remaining = len(current_line_text) - len(user_input)
            if remaining > 0:
                pad_start = f"{user_line_num}.{len(user_input)}"
                pad_end = f"{user_line_num}.{len(current_line_text)}"
                # 패딩은 아무 색도 칠하지 않지만 caret 위치 보정에 도움이 됨
                self.text_display.tag_add("user_input", pad_start, pad_end)

            # 현재 위치 표시 (더 명확하게)
            if self.current_char_in_line <= len(current_line_text):
                current_pos_start = f"{user_line_num}.{self.current_char_in_line}"
                current_pos_end = f"{user_line_num}.{self.current_char_in_line + 1}"
                self.text_display.tag_add("current", current_pos_start, current_pos_end)

                # 커서 위치로 자동 스크롤
                self.text_display.see(current_pos_start)
                # 캐럿 위치 갱신을 위해 즉시 한 번 토글하여 위치 동기화
                if hasattr(self, "caret_blink_on") and self.caret_blink_on:
                    # 잠깐 caret 제거 후 현재 위치에 다시 추가
                    self.text_display.tag_remove("caret", "1.0", tk.END)
                    self.text_display.tag_add(
                        "caret", current_pos_start, current_pos_end
                    )

            self.text_display.config(state=tk.DISABLED)

    def on_key_release(self, event):
        """키 릴리스 처리"""
        pass

    def start_timer(self):
        """타이머 시작"""
        if not hasattr(self, "timer_running") or not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        """타이머 업데이트"""
        if self.is_typing and self.start_time:
            elapsed_time = time.time() - self.start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            # 헤더의 라이브 타이머 업데이트
            if hasattr(self, "live_time_label"):
                self.live_time_label.config(text=f"{minutes:02d}:{seconds:02d}")
            # 속도/정확도 표시를 1초마다 갱신하여 실시간으로 보이도록 함
            self.update_stats()

            if self.timer_running:
                self.root.after(1000, self.update_timer)
        else:
            self.timer_running = False

    def update_stats(self):
        """통계 업데이트"""
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                # 타수/분 계산 (한글 기준)
                if self.total_chars > 0:
                    chars_per_minute = (self.total_chars / elapsed_time) * 60
                    self.speed_label.config(text=f"{int(chars_per_minute)}타/분")
                    if hasattr(self, "live_speed_label"):
                        self.live_speed_label.config(
                            text=f"{int(chars_per_minute)}타/분"
                        )
                else:
                    self.speed_label.config(text="0타/분")
                    if hasattr(self, "live_speed_label"):
                        self.live_speed_label.config(text="0타/분")

                # 정확도 계산
                if self.total_chars > 0:
                    accuracy = (self.correct_chars / self.total_chars) * 100
                    self.accuracy_label.config(text=f"{accuracy:.1f}%")
                    if hasattr(self, "live_acc_label"):
                        self.live_acc_label.config(text=f"{accuracy:.1f}%")
                else:
                    self.accuracy_label.config(text="0%")
                    if hasattr(self, "live_acc_label"):
                        self.live_acc_label.config(text="0%")

    def update_progress_bar(self):
        """진행률 바 업데이트"""
        if len(self.text_lines) > 0:
            # 전체 문자 수 계산
            total_chars = sum(len(line) for line in self.text_lines)
            completed_chars = sum(
                len(self.user_lines[i]) for i in range(len(self.user_lines))
            )

            # 현재 줄의 진행 상황도 포함
            if self.current_line < len(self.text_lines):
                completed_chars += self.current_char_in_line

            progress = (completed_chars / total_chars) * 100 if total_chars > 0 else 0

            # 진행률 바 업데이트
            progress_width = int((progress / 100) * 300)  # 300픽셀 기준
            self.progress_bar.config(width=progress_width)

            # 진행률 정보 업데이트
            self.progress_info.config(text=f"진행률: {progress:.1f}%")

    def check_completion(self):
        """완료 체크"""
        # 모든 줄이 완료되었는지 검사: 마지막 줄의 마지막 문자까지 입력되었을 때 완료 처리
        all_done = self.current_line == len(
            self.text_lines
        ) - 1 and self.current_char_in_line >= len(self.text_lines[-1])
        if all_done:
            self.is_typing = False
            final_time = time.time() - self.start_time if self.start_time else 0

            # 최종 통계 계산
            final_wpm = (
                (self.total_chars / 5) / (final_time / 60) if final_time > 0 else 0
            )
            final_accuracy = (
                (self.correct_chars / self.total_chars) * 100
                if self.total_chars > 0
                else 0
            )

            # 통계 저장
            self.save_session_stats(final_wpm, final_accuracy, final_time)

            # 완료 메시지
            message = f"연습 완료!\n\n타이핑 속도: {final_wpm:.1f} WPM\n정확도: {final_accuracy:.1f}%\n시간: {final_time:.1f}초"
            try:
                messagebox.showinfo("연습 완료", message)
            except Exception:
                pass

            # status_label 제거됨

    def reset_practice(self):
        """연습 리셋"""
        self.user_input = ""
        self.user_lines = []
        self.start_time = None
        self.is_typing = False
        self.current_position = 0
        self.current_line = 0
        self.current_char_in_line = 0
        self.correct_chars = 0
        self.total_chars = 0
        self.timer_running = False

        # 통계 초기화
        self.speed_label.config(text="0타/분")
        self.accuracy_label.config(text="0%")
        self.timer_label.config(text="00:00")
        self.progress_info.config(text="진행률: 0%")

        # 진행률 바 초기화
        self.progress_bar.config(width=0)

        # 텍스트 재표시
        if self.current_text:
            self.display_text()
            # 키보드 이벤트 다시 바인딩
            self.text_display.bind("<KeyPress>", self.on_key_press)
            self.text_display.bind(
                "<Button-1>", lambda e: self.text_display.focus_set()
            )
            self.text_display.focus_set()

    def load_text_from_file(self):
        """파일에서 텍스트 로드"""
        file_path = filedialog.askopenfilename(
            title="텍스트 파일 선택",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.current_text = file.read().strip()
                    if self.current_text:
                        self.display_text()
                        self.reset_practice()
                        # status_label 제거됨
                    else:
                        messagebox.showerror("오류", "파일이 비어있습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"파일을 읽을 수 없습니다: {str(e)}")

    # 난이도 선택 기능 제거됨 (언어 선택으로 통합)

    def select_typing_difficulty(self):
        """타이핑 난이도 선택"""
        difficulty_window = tk.Toplevel(self.root)
        difficulty_window.title("난이도 선택")
        difficulty_window.geometry("400x300")
        difficulty_window.resizable(False, False)

        tk.Label(
            difficulty_window,
            text="연습 난이도를 선택하세요",
            font=("맑은 고딕", 16, "bold"),
        ).pack(pady=20)

        # 난이도별 텍스트
        difficulties = {
            "초급": "The cat sat on the mat. The dog ran in the yard.",
            "중급": "Practice typing with the Dvorak keyboard layout for improved efficiency.",
            "고급": "The Dvorak Simplified Keyboard was designed to increase typing speed and reduce finger fatigue through optimized key placement.",
        }

        for level, text in difficulties.items():
            btn = tk.Button(
                difficulty_window,
                text=level,
                width=20,
                height=2,
                font=("맑은 고딕", 12),
                command=lambda t=text: self.set_difficulty_text(t, difficulty_window),
            )
            btn.pack(pady=10)

    def select_coding_template(self):
        """코딩 템플릿 선택"""
        if not self.coding_templates:
            messagebox.showerror("오류", "코딩 템플릿을 로드할 수 없습니다.")
            return

        template_window = tk.Toplevel(self.root)
        template_window.title("코딩 템플릿 선택")
        template_window.geometry("600x500")
        template_window.resizable(False, False)

        # 언어 선택
        lang_frame = tk.Frame(template_window)
        lang_frame.pack(pady=10)

        tk.Label(lang_frame, text="언어:", font=("맑은 고딕", 12, "bold")).pack(
            side=tk.LEFT
        )

        lang_var = tk.StringVar(value=self.current_language)
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=lang_var,
            values=list(self.coding_templates.keys()),
            width=15,
        )
        lang_combo.pack(side=tk.LEFT, padx=(10, 0))

        # 난이도 선택
        diff_frame = tk.Frame(template_window)
        diff_frame.pack(pady=10)

        tk.Label(diff_frame, text="난이도:", font=("맑은 고딕", 12, "bold")).pack(
            side=tk.LEFT
        )

        diff_var = tk.StringVar(value=self.current_difficulty)
        diff_combo = ttk.Combobox(
            diff_frame,
            textvariable=diff_var,
            values=["basic", "intermediate", "advanced"],
            width=15,
        )
        diff_combo.pack(side=tk.LEFT, padx=(10, 0))

        # 템플릿 목록
        list_frame = tk.Frame(template_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(
            list_frame, text="사용 가능한 템플릿:", font=("맑은 고딕", 12, "bold")
        ).pack(anchor=tk.W)

        listbox_frame = tk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        listbox = tk.Listbox(listbox_frame, height=10, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(
            listbox_frame, orient="vertical", command=listbox.yview
        )
        listbox.configure(yscrollcommand=scrollbar.set)

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def update_templates():
            language = lang_var.get()
            difficulty = diff_var.get()

            if (
                language in self.coding_templates
                and difficulty in self.coding_templates[language]
            ):
                templates = self.coding_templates[language][difficulty]
                listbox.delete(0, tk.END)

                for i, template in enumerate(templates):
                    # 템플릿의 첫 줄만 표시
                    first_line = (
                        template.split("\n")[0][:50] + "..."
                        if len(template.split("\n")[0]) > 50
                        else template.split("\n")[0]
                    )
                    listbox.insert(tk.END, f"{i+1}. {first_line}")

        def select_template():
            selection = listbox.curselection()
            if selection:
                language = lang_var.get()
                difficulty = diff_var.get()
                template_index = selection[0]

                if (
                    language in self.coding_templates
                    and difficulty in self.coding_templates[language]
                ):
                    templates = self.coding_templates[language][difficulty]
                    if template_index < len(templates):
                        self.current_text = templates[template_index]
                        self.current_language = language
                        self.current_difficulty = difficulty
                        self.display_text()
                        self.reset_practice()
                        # status_label 제거됨
                        template_window.destroy()

        # 이벤트 바인딩
        lang_combo.bind("<<ComboboxSelected>>", lambda e: update_templates())
        diff_combo.bind("<<ComboboxSelected>>", lambda e: update_templates())
        listbox.bind("<Double-Button-1>", lambda e: select_template())

        # 버튼
        button_frame = tk.Frame(template_window)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="선택", command=select_template).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="취소", command=template_window.destroy).pack(
            side=tk.LEFT, padx=5
        )

        # 초기 템플릿 로드
        update_templates()

    def set_difficulty_text(self, text, window):
        """난이도 텍스트 설정"""
        self.current_text = text
        self.display_text()
        self.reset_practice()
        # status_label 제거됨
        window.destroy()

    def show_stats(self):
        """통계 보기"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("타이핑 통계")
        stats_window.geometry("600x400")

        # 통계 표시
        stats_text = tk.Text(stats_window, wrap=tk.WORD, font=("맑은 고딕", 11))
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 통계 데이터 포맷팅
        stats_content = "=== 타이핑 & 코딩 연습 통계 ===\n\n"

        if hasattr(self, "stats_data") and self.stats_data:
            total_sessions = len(self.stats_data["sessions"])
            typing_sessions = [
                s for s in self.stats_data["sessions"] if s.get("mode") == "typing"
            ]
            coding_sessions = [
                s for s in self.stats_data["sessions"] if s.get("mode") == "coding"
            ]

            # 전체 통계
            avg_wpm = (
                sum(s["wpm"] for s in self.stats_data["sessions"]) / total_sessions
            )
            avg_accuracy = (
                sum(s["accuracy"] for s in self.stats_data["sessions"]) / total_sessions
            )

            stats_content += f"총 연습 세션: {total_sessions}회\n"
            stats_content += f"  - 일반 타자연습: {len(typing_sessions)}회\n"
            stats_content += f"  - 코딩 연습: {len(coding_sessions)}회\n"
            stats_content += f"전체 평균 속도: {avg_wpm:.1f} WPM\n"
            stats_content += f"전체 평균 정확도: {avg_accuracy:.1f}%\n\n"

            # 일반 타자연습 통계
            if typing_sessions:
                typing_avg_wpm = sum(s["wpm"] for s in typing_sessions) / len(
                    typing_sessions
                )
                typing_avg_accuracy = sum(s["accuracy"] for s in typing_sessions) / len(
                    typing_sessions
                )
                stats_content += f"일반 타자연습 평균: {typing_avg_wpm:.1f} WPM, {typing_avg_accuracy:.1f}%\n"

            # 코딩 연습 통계
            if coding_sessions:
                coding_avg_wpm = sum(s["wpm"] for s in coding_sessions) / len(
                    coding_sessions
                )
                coding_avg_accuracy = sum(s["accuracy"] for s in coding_sessions) / len(
                    coding_sessions
                )
                stats_content += f"코딩 연습 평균: {coding_avg_wpm:.1f} WPM, {coding_avg_accuracy:.1f}%\n"

                # 언어별 통계
                languages = {}
                for session in coding_sessions:
                    lang = session.get("language", "unknown")
                    if lang not in languages:
                        languages[lang] = []
                    languages[lang].append(session)

                if languages:
                    stats_content += "\n언어별 통계:\n"
                    for lang, sessions in languages.items():
                        lang_avg_wpm = sum(s["wpm"] for s in sessions) / len(sessions)
                        lang_avg_accuracy = sum(s["accuracy"] for s in sessions) / len(
                            sessions
                        )
                        stats_content += f"  {lang}: {lang_avg_wpm:.1f} WPM, {lang_avg_accuracy:.1f}% ({len(sessions)}회)\n"

            stats_content += "\n최근 10회 연습 기록:\n"
            stats_content += "-" * 70 + "\n"

            for i, session in enumerate(self.stats_data["sessions"][-10:], 1):
                mode = session.get("mode", "typing")
                lang_info = (
                    f" ({session.get('language', '')})" if mode == "coding" else ""
                )
                stats_content += f"{i:2d}. [{mode.upper()}{lang_info}] {session['wpm']:5.1f} WPM | {session['accuracy']:5.1f}% | {session['time']:5.1f}초 | {session['date']}\n"
        else:
            stats_content += "아직 연습 기록이 없습니다.\n"
            stats_content += "연습을 시작하여 통계를 쌓아보세요!"

        stats_text.insert(1.0, stats_content)
        stats_text.config(state=tk.DISABLED)

    def show_settings(self):
        """설정 창"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("설정")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)

        tk.Label(settings_window, text="설정", font=("맑은 고딕", 16, "bold")).pack(
            pady=20
        )

        # 설정 옵션들
        options_frame = tk.Frame(settings_window)
        options_frame.pack(pady=20)

        # 통계 초기화 버튼
        clear_stats_btn = tk.Button(
            options_frame,
            text="통계 초기화",
            width=20,
            command=lambda: self.clear_stats(settings_window),
        )
        clear_stats_btn.pack(pady=10)

        # 정보 버튼
        info_btn = tk.Button(
            options_frame, text="프로그램 정보", width=20, command=self.show_info
        )
        info_btn.pack(pady=10)

    def clear_stats(self, window):
        """통계 초기화"""
        if messagebox.askyesno("확인", "모든 통계를 삭제하시겠습니까?"):
            self.stats_data = {"sessions": []}
            self.save_stats()
            messagebox.showinfo("완료", "통계가 초기화되었습니다.")
            window.destroy()

    def show_info(self):
        """프로그램 정보"""
        info_text = """드보락 키보드 타자연습 v1.0

개발자: AI Assistant
목적: 드보락 키보드 레이아웃 연습을 통한 타이핑 속도 향상

특징:
- 드보락 키보드 레이아웃 표시
- 실시간 타이핑 속도 및 정확도 측정
- 연습 기록 저장 및 통계 제공
- 다양한 난이도의 연습 텍스트
- 사용자 정의 텍스트 파일 로드

사용법:
1. '새 연습 시작' 버튼으로 연습 시작
2. 텍스트를 보고 입력창에 타이핑
3. 실시간으로 속도와 정확도 확인
4. 완료 후 통계에서 기록 확인"""

        messagebox.showinfo("프로그램 정보", info_text)

    def load_stats(self):
        """통계 로드"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, "r", encoding="utf-8") as file:
                    self.stats_data = json.load(file)
            else:
                self.stats_data = {"sessions": []}
        except Exception as e:
            self.stats_data = {"sessions": []}

    def save_stats(self):
        """통계 저장"""
        try:
            with open(self.stats_file, "w", encoding="utf-8") as file:
                json.dump(self.stats_data, file, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"통계 저장 오류: {e}")

    def save_session_stats(self, wpm, accuracy, time_taken):
        """세션 통계 저장"""
        session_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "wpm": wpm,
            "accuracy": accuracy,
            "time": time_taken,
            "mode": "coding" if self.is_coding_mode else "typing",
            "language": self.current_language if self.is_coding_mode else None,
            "difficulty": self.current_difficulty if self.is_coding_mode else None,
        }

        self.stats_data["sessions"].append(session_data)
        self.save_stats()

    def run(self):
        """프로그램 실행"""
        self.root.mainloop()


if __name__ == "__main__":
    app = DvorakTypingTrainer()
    app.run()
