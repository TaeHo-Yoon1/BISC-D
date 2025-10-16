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
        self.root.configure(bg="#f0f0f0")

        # 변수 초기화
        self.current_text = ""
        self.user_input = ""
        self.start_time = None
        self.is_typing = False
        self.current_position = 0
        self.correct_chars = 0
        self.total_chars = 0

        # 코딩 모드 관련 변수
        self.is_coding_mode = False
        self.current_language = "python"
        self.current_difficulty = "basic"
        self.coding_templates = {}
        self.load_coding_templates()

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

        self.setup_ui()

    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 제목 및 모드 선택
        title_frame = tk.Frame(main_frame, bg="#f0f0f0")
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        title_label = tk.Label(
            title_frame,
            text="드보락 키보드 타자연습 & 코딩 연습",
            font=("맑은 고딕", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50",
        )
        title_label.pack()

        # 모드 선택 버튼
        mode_frame = tk.Frame(title_frame, bg="#f0f0f0")
        mode_frame.pack(pady=(10, 0))

        self.mode_var = tk.StringVar(value="typing")
        tk.Radiobutton(
            mode_frame,
            text="일반 타자연습",
            variable=self.mode_var,
            value="typing",
            command=self.switch_mode,
            font=("맑은 고딕", 12),
            bg="#f0f0f0",
        ).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(
            mode_frame,
            text="코딩 연습",
            variable=self.mode_var,
            value="coding",
            command=self.switch_mode,
            font=("맑은 고딕", 12),
            bg="#f0f0f0",
        ).pack(side=tk.LEFT, padx=10)

        # 드보락 키보드 레이아웃 표시
        self.setup_keyboard_display(main_frame, 1)

        # 연습 텍스트 영역
        self.setup_text_area(main_frame, 2)

        # 입력 영역
        self.setup_input_area(main_frame, 3)

        # 통계 및 컨트롤 영역
        self.setup_stats_control_area(main_frame, 4)

        # 상태 표시
        self.setup_status_area(main_frame, 5)

    def setup_keyboard_display(self, parent, row):
        keyboard_frame = ttk.LabelFrame(
            parent, text="드보락 키보드 레이아웃", padding="10"
        )
        keyboard_frame.grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )

        for i, row_keys in enumerate(self.dvorak_layout):
            key_frame = tk.Frame(keyboard_frame, bg="#ecf0f1")
            key_frame.grid(row=i, column=0, pady=2)

            for j, key in enumerate(row_keys):
                if key:
                    btn = tk.Button(
                        key_frame,
                        text=key,
                        width=3,
                        height=1,
                        font=("맑은 고딕", 10, "bold"),
                        bg="#3498db",
                        fg="white",
                        relief="raised",
                        bd=2,
                    )
                    btn.grid(row=0, column=j, padx=1, pady=1)
                else:
                    # 빈 공간
                    tk.Frame(key_frame, width=30, height=30).grid(row=0, column=j)

    def setup_text_area(self, parent, row):
        text_frame = ttk.LabelFrame(parent, text="연습 텍스트", padding="10")
        text_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # 코딩 모드 설정 영역 (숨김 상태로 시작)
        self.coding_settings_frame = tk.Frame(text_frame, bg="#ecf0f1")

        # 언어 선택
        lang_frame = tk.Frame(self.coding_settings_frame, bg="#ecf0f1")
        lang_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            lang_frame, text="언어:", font=("맑은 고딕", 12, "bold"), bg="#ecf0f1"
        ).pack(side=tk.LEFT)

        self.language_var = tk.StringVar(value="python")
        languages = ["python", "java", "javascript", "cpp", "react"]
        lang_combo = ttk.Combobox(
            lang_frame, textvariable=self.language_var, values=languages, width=15
        )
        lang_combo.pack(side=tk.LEFT, padx=(10, 0))
        lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        # 난이도 선택
        diff_frame = tk.Frame(self.coding_settings_frame, bg="#ecf0f1")
        diff_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            diff_frame, text="난이도:", font=("맑은 고딕", 12, "bold"), bg="#ecf0f1"
        ).pack(side=tk.LEFT)

        self.difficulty_var = tk.StringVar(value="basic")
        difficulties = ["basic", "intermediate", "advanced"]
        diff_combo = ttk.Combobox(
            diff_frame, textvariable=self.difficulty_var, values=difficulties, width=15
        )
        diff_combo.pack(side=tk.LEFT, padx=(10, 0))
        diff_combo.bind("<<ComboboxSelected>>", self.on_difficulty_change)

        # 텍스트 표시 영역
        self.text_display = tk.Text(
            text_frame,
            height=10,
            width=100,
            font=("Consolas", 12),  # 코드용 모노스페이스 폰트
            wrap=tk.NONE,  # 코드는 줄바꿈하지 않음
            state=tk.DISABLED,
            bg="#f8f9fa",
            fg="#212529",
        )
        self.text_display.grid(row=1, column=0, columnspan=2, pady=5)

        # 스크롤바
        v_scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.text_display.yview
        )
        v_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.text_display.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(
            text_frame, orient="horizontal", command=self.text_display.xview
        )
        h_scrollbar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.text_display.configure(xscrollcommand=h_scrollbar.set)

        # 텍스트 로드 버튼들
        button_frame = tk.Frame(text_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=5)

        self.start_button = ttk.Button(
            button_frame, text="새 연습 시작", command=self.start_new_practice
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.file_button = ttk.Button(
            button_frame, text="파일에서 로드", command=self.load_text_from_file
        )
        self.file_button.pack(side=tk.LEFT, padx=5)

        self.difficulty_button = ttk.Button(
            button_frame, text="난이도 선택", command=self.select_difficulty
        )
        self.difficulty_button.pack(side=tk.LEFT, padx=5)

    def setup_input_area(self, parent, row):
        input_frame = ttk.LabelFrame(parent, text="입력 영역", padding="10")
        input_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.input_text = tk.Text(
            input_frame,
            height=4,
            width=80,
            font=("맑은 고딕", 14),
            wrap=tk.WORD,
            bg="#ecf0f1",
            fg="#2c3e50",
        )
        self.input_text.grid(row=0, column=0, columnspan=2, pady=5)
        self.input_text.bind("<KeyPress>", self.on_key_press)
        self.input_text.bind("<KeyRelease>", self.on_key_release)

        # 입력 스크롤바
        input_scrollbar = ttk.Scrollbar(
            input_frame, orient="vertical", command=self.input_text.yview
        )
        input_scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))
        self.input_text.configure(yscrollcommand=input_scrollbar.set)

        # 입력 영역 포커스 설정
        self.input_text.focus_set()

    def setup_stats_control_area(self, parent, row):
        stats_frame = ttk.LabelFrame(parent, text="통계 및 컨트롤", padding="10")
        stats_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # 왼쪽: 실시간 통계
        left_frame = tk.Frame(stats_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 20))

        tk.Label(left_frame, text="타이핑 속도:", font=("맑은 고딕", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W
        )
        self.speed_label = tk.Label(
            left_frame, text="0 WPM", font=("맑은 고딕", 12), fg="#e74c3c"
        )
        self.speed_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        tk.Label(left_frame, text="정확도:", font=("맑은 고딕", 12, "bold")).grid(
            row=1, column=0, sticky=tk.W
        )
        self.accuracy_label = tk.Label(
            left_frame, text="0%", font=("맑은 고딕", 12), fg="#27ae60"
        )
        self.accuracy_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        tk.Label(left_frame, text="진행률:", font=("맑은 고딕", 12, "bold")).grid(
            row=2, column=0, sticky=tk.W
        )
        self.progress_label = tk.Label(
            left_frame, text="0%", font=("맑은 고딕", 12), fg="#3498db"
        )
        self.progress_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

        # 오른쪽: 컨트롤 버튼
        right_frame = tk.Frame(stats_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Button(right_frame, text="리셋", command=self.reset_practice).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(right_frame, text="통계 보기", command=self.show_stats).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(right_frame, text="설정", command=self.show_settings).pack(
            side=tk.LEFT, padx=5
        )

    def setup_status_area(self, parent, row):
        status_frame = tk.Frame(parent, bg="#34495e", height=30)
        status_frame.grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0)
        )
        status_frame.grid_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="준비됨 - 새로운 연습을 시작하세요!",
            font=("맑은 고딕", 10),
            bg="#34495e",
            fg="white",
        )
        self.status_label.pack(expand=True)

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
            self.text_display.config(font=("Consolas", 12), wrap=tk.NONE, bg="#f8f9fa")
            self.difficulty_button.config(text="코드 선택")
        else:
            self.coding_settings_frame.grid_remove()
            self.text_display.config(font=("맑은 고딕", 14), wrap=tk.WORD, bg="#ffffff")
            self.difficulty_button.config(text="난이도 선택")

        # 현재 텍스트 초기화
        self.current_text = ""
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.config(state=tk.DISABLED)
        self.reset_practice()

    def on_language_change(self, event=None):
        """언어 변경 처리"""
        self.current_language = self.language_var.get()
        self.status_label.config(
            text=f"언어가 {self.current_language}로 변경되었습니다."
        )

    def on_difficulty_change(self, event=None):
        """난이도 변경 처리"""
        self.current_difficulty = self.difficulty_var.get()
        self.status_label.config(
            text=f"난이도가 {self.current_difficulty}로 변경되었습니다."
        )

    def start_new_practice(self):
        """새로운 연습 시작"""
        if self.is_coding_mode:
            self.current_text = self.generate_coding_text()
        else:
            self.current_text = self.generate_practice_text()

        self.display_text()
        self.reset_practice()
        self.status_label.config(text="연습 시작! 타이핑을 시작하세요.")
        self.input_text.focus_set()

    def generate_practice_text(self):
        """연습용 텍스트 생성"""
        # 드보락 키보드 연습용 텍스트
        practice_texts = [
            "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet at least once.",
            "Practice makes perfect. The more you type on a Dvorak keyboard, the faster you will become.",
            "Dvorak Simplified Keyboard was designed to increase typing speed and reduce finger fatigue.",
            "Learning the Dvorak layout requires patience and consistent practice to build muscle memory.",
            "Many professional typists prefer Dvorak over QWERTY because of its efficiency and ergonomics.",
            "The Dvorak keyboard places the most commonly used letters in the home row for better typing flow.",
            "Touch typing on Dvorak can significantly improve your typing speed once you master the layout.",
            "Dvorak was designed by Dr. August Dvorak and his brother-in-law Dr. William Dealey in the 1930s.",
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
            return random.choice(templates)
        else:
            return f"{language} 언어의 {difficulty} 난이도 템플릿을 찾을 수 없습니다."

    def display_text(self):
        """텍스트를 화면에 표시"""
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(1.0, self.current_text)

        # 코딩 모드일 때 문법 하이라이팅 적용
        if self.is_coding_mode:
            self.apply_syntax_highlighting()

        self.text_display.config(state=tk.DISABLED)

        # 텍스트 하이라이트 초기화
        self.highlight_text()

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
        """키 입력 처리"""
        if not self.is_typing:
            self.start_time = time.time()
            self.is_typing = True

        # Enter 키 처리
        if event.keysym == "Return":
            self.check_completion()
            return "break"

        # Backspace 처리
        if event.keysym == "BackSpace":
            if self.current_position > 0:
                self.current_position -= 1
                # 잘못된 문자가 있었는지 확인
                if self.current_position < len(self.user_input):
                    self.user_input = self.user_input[: self.current_position]
                self.update_stats()
                self.highlight_text()
            return "break"

        # 일반 문자 입력
        if len(event.char) == 1 and event.char.isprintable():
            if self.current_position < len(self.current_text):
                expected_char = self.current_text[self.current_position]
                if event.char == expected_char:
                    self.correct_chars += 1
                    self.user_input += event.char
                else:
                    # 잘못된 문자는 입력하지 않음
                    pass

                self.current_position += 1
                self.total_chars += 1
                self.update_stats()
                self.highlight_text()

            # 완료 체크
            if self.current_position >= len(self.current_text):
                self.check_completion()

            return "break"

        return None

    def on_key_release(self, event):
        """키 릴리스 처리"""
        pass

    def update_stats(self):
        """통계 업데이트"""
        if self.start_time and self.total_chars > 0:
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                # WPM 계산 (단어당 5글자 기준)
                wpm = (self.total_chars / 5) / (elapsed_time / 60)
                self.speed_label.config(text=f"{wpm:.1f} WPM")

                # 정확도 계산
                accuracy = (
                    (self.correct_chars / self.total_chars) * 100
                    if self.total_chars > 0
                    else 0
                )
                self.accuracy_label.config(text=f"{accuracy:.1f}%")

                # 진행률 계산
                progress = (
                    (self.current_position / len(self.current_text)) * 100
                    if len(self.current_text) > 0
                    else 0
                )
                self.progress_label.config(text=f"{progress:.1f}%")

    def check_completion(self):
        """완료 체크"""
        if self.current_position >= len(self.current_text):
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
            messagebox.showinfo("연습 완료", message)

            self.status_label.config(text="연습 완료! 새로운 연습을 시작하세요.")

    def reset_practice(self):
        """연습 리셋"""
        self.user_input = ""
        self.start_time = None
        self.is_typing = False
        self.current_position = 0
        self.correct_chars = 0
        self.total_chars = 0

        self.input_text.delete(1.0, tk.END)
        self.speed_label.config(text="0 WPM")
        self.accuracy_label.config(text="0%")
        self.progress_label.config(text="0%")

        if self.current_text:
            self.highlight_text()

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
                        self.status_label.config(text="파일에서 텍스트를 로드했습니다.")
                    else:
                        messagebox.showerror("오류", "파일이 비어있습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"파일을 읽을 수 없습니다: {str(e)}")

    def select_difficulty(self):
        """난이도 선택"""
        if self.is_coding_mode:
            self.select_coding_template()
        else:
            self.select_typing_difficulty()

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
                        self.status_label.config(
                            text=f"{language} {difficulty} 템플릿이 선택되었습니다."
                        )
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
        self.status_label.config(text="난이도 텍스트가 설정되었습니다.")
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
