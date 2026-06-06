import sys
import re
import random
import tkinter as tk

class PengilInterpreter:
    def __init__(self, code):
        self.user_code = code
        self.code_len = len(code)
        self.idx = 0
        self.buffer = 0
        self.skip_next = False
        self.labels = {}
        self.steps_count = 0
        self.max_steps = 100000
        
        self.height = 25
        self.width = 80
        self.grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        self.cursor_x = 0
        self.cursor_y = 0
        self.current_indent = 0
        
        self.parse_labels()

    def parse_labels(self):
        i = 0
        while i < self.code_len:
            if self.user_code[i] == ":" and i + 1 < self.code_len and self.user_code[i + 1] == "[":
                close_bracket = self.user_code.find("]", i)
                if close_bracket != -1:
                    label_name = self.user_code[i + 2:close_bracket]
                    self.labels[label_name] = i
                    i = close_bracket + 1
                    continue
            i += 1

    def step(self):
        if self.idx >= self.code_len or self.steps_count >= self.max_steps:
            return False
        
        self.steps_count += 1

        if self.skip_next:
            self.skip_next = False
            if self.user_code[self.idx] in "pgc_r@!%^*/:iw~":
                match = re.match(r"^(p\[.*?\]|w\[.*?\]|c\[.*?\]|r\[.*?\]|@move\d+|@jump\[.*?\]|:\[.*?\]|\^\d+|_\d+|\*\d+|/\d+|[g>\\!?%i~])", self.user_code[self.idx:])
                if match:
                    self.idx += len(match.group(0))
                    return True
            self.idx += 1
            return True

        char = self.user_code[self.idx]

        if char == ">":
            self.idx += 1
        elif char == "\\":
            self.cursor_y = min(self.height - 1, self.cursor_y + 1)
            self.cursor_x = self.current_indent
            self.idx += 1
        elif char == "g":
            target_x = max(0, self.cursor_x - 1)
            self.buffer = ord(self.grid[self.cursor_y][target_x])
            self.idx += 1
        elif char == "!":
            self.buffer = 1 if self.buffer == 0 else 0
            self.idx += 1
        elif char == "%":
            self.buffer = -self.buffer
            self.idx += 1
        elif char == "?":
            if self.buffer == 0:
                self.skip_next = True
            self.idx += 1
        elif char == "~":
            self.buffer = random.randint(0, 100)
            self.idx += 1
        elif char == "i":
            global last_key
            self.buffer = 0
            if last_key == 'a': self.buffer = 1
            elif last_key == 'd': self.buffer = 2
            elif last_key == 'space': self.buffer = 3
            last_key = None
            self.idx += 1
        elif char == ":":
            close_bracket = self.user_code.find("]", self.idx)
            if close_bracket != -1:
                self.idx = close_bracket + 1
            else:
                self.idx += 1
        elif char == "^":
            match = re.match(r"^\^\d+", self.user_code[self.idx:])
            if match:
                self.buffer += int(match.group(0)[1:])
                self.idx += len(match.group(0))
        elif char == "_":
            match = re.match(r"^_\d+", self.user_code[self.idx:])
            if match:
                self.buffer -= int(match.group(0)[1:])
                self.idx += len(match.group(0))
        elif char == "*":
            match = re.match(r"^\*\d+", self.user_code[self.idx:])
            if match:
                self.buffer *= int(match.group(0)[1:])
                self.idx += len(match.group(0))
        elif char == "/":
            match = re.match(r"^/\d+", self.user_code[self.idx:])
            if match:
                divisor = int(match.group(0)[1:])
                if divisor != 0:
                    self.buffer //= divisor
                self.idx += len(match.group(0))
        elif char == "@" and self.user_code[self.idx:].startswith("@move"):
            match = re.match(r"^@move\d+", self.user_code[self.idx:])
            if match:
                steps = int(match.group(0)[5:])
                self.idx += len(match.group(0)) + steps
        elif char == "@" and self.user_code[self.idx:].startswith("@jump"):
            close_bracket = self.user_code.find("]", self.idx)
            label_name = self.user_code[self.idx + 6:close_bracket]
            if label_name in self.labels:
                self.idx = self.labels[label_name]
            else:
                return False
        elif char == "p" and self.idx + 1 < self.code_len and self.user_code[self.idx + 1] == "[":
            close_bracket = self.user_code.find("]", self.idx)
            param = self.user_code[self.idx + 2:close_bracket]
            new_char = chr(self.buffer) if param == "g" else chr(int(param))
            if self.cursor_x < self.width and self.cursor_y < self.height:
                self.grid[self.cursor_y][self.cursor_x] = new_char
                self.cursor_x += 1
            self.idx = close_bracket + 1
        elif char == "w" and self.idx + 1 < self.code_len and self.user_code[self.idx + 1] == "[":
            close_bracket = self.user_code.find("]", self.idx)
            coords = self.user_code[self.idx + 2:close_bracket].split(",")
            try:
                x = int(coords[0])
                y = int(coords[1])
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x] = chr(self.buffer)
            except (IndexError, ValueError):
                pass
            self.idx = close_bracket + 1
        elif char == "r" and self.idx + 1 < self.code_len and self.user_code[self.idx + 1] == "[":
            close_bracket = self.user_code.find("]", self.idx)
            coords = self.user_code[self.idx + 2:close_bracket].split(",")
            try:
                x = int(coords[0])
                y = int(coords[1])
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x] = " "
            except (IndexError, ValueError):
                pass
            self.idx = close_bracket + 1
        elif char == "c" and self.idx + 1 < self.code_len and self.user_code[self.idx + 1] == "[":
            close_bracket = self.user_code.find("]", self.idx)
            params = self.user_code[self.idx + 2:close_bracket].split(",")
            val1 = int(params[0])
            if val1 == 0:
                self.grid[self.cursor_y] = [" " for _ in range(self.width)]
                self.cursor_x = self.current_indent
            self.idx = close_bracket + 1
        else:
            self.idx += 1

        return True

root = tk.Tk()
root.title("PENGIL")
root.configure(bg="#FFFFFF")

last_key = None

def on_key_press(event):
    global last_key
    if event.char in ['a', 'd']:
        last_key = event.char
    elif event.keysym == 'space':
        last_key = 'space'

root.bind("<KeyPress>", on_key_press)

def force_paste(event):
    try:
        event.widget.insert(tk.INSERT, root.clipboard_get())
    except tk.TclError:
        pass
    return "break"

main_frame = tk.Frame(root, bg="#FFFFFF")
main_frame.pack(padx=15, pady=15, fill="both", expand=True)

left_frame = tk.LabelFrame(main_frame, text=" [ PENGIL CODE ] ", bg="#FFFFFF", fg="#000000", font=("Courier", 10, "bold"))
left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

code_text = tk.Text(left_frame, font=("Courier", 12), bg="#F8F9FA", fg="#000000", insertbackground="#000000", width=35, height=25, bd=1, relief="solid")
code_text.pack(padx=10, pady=10, fill="both", expand=True)

def global_key_check(event):
    if event.state & 4:
        if event.keycode == 86:
            return force_paste(event)

code_text.bind("<Key>", global_key_check)

right_frame = tk.LabelFrame(main_frame, text=" [ PENGIL CELL GRID DISPLAY ] ", bg="#FFFFFF", fg="#000000", font=("Courier", 10, "bold"))
right_frame.pack(side="right", fill="both", expand=True)

grid_text = tk.Text(right_frame, font=("Courier", 12, "bold"), bg="#F8F9FA", fg="#000000", width=80, height=25, state="disabled", bd=1, relief="solid")
grid_text.pack(padx=10, pady=10, fill="both", expand=True)

demo_code = "^88w[0,0]^94w[40,24]:[loop]i?@jump[check_d]^0_1?@jump[left]^[right]:[check_d]^0_2?@jump[right]^[left]:[left]^32w[g,24]_1w[g,24]@jump[loop]:[right]^32w[g,24]^1w[g,24]@jump[loop]"
code_text.insert("1.0", demo_code)

bottom_frame = tk.Frame(root, bg="#FFFFFF")
bottom_frame.pack(fill="x", padx=15, pady=(0, 15))

buffer_label = tk.Label(bottom_frame, text="BUFFER: 40 | STEPS: 0/100000", font=("Courier", 12, "bold"), bg="#FFFFFF", fg="#000000")
buffer_label.pack(side="left")

interpreter = None

def update_grid_ui():
    if not interpreter:
        return
    grid_text.configure(state="normal")
    grid_text.delete("1.0", tk.END)
    output = "\n".join("".join(row) for row in interpreter.grid)
    grid_text.insert("1.0", output)
    grid_text.configure(state="disabled")
    buffer_label.configure(text=f"BUFFER: {interpreter.buffer} | STEPS: {interpreter.steps_count}/100000")

def run_loop():
    if interpreter:
        for _ in range(2):
            active = interpreter.step()
            if not active:
                update_grid_ui()
                return
        update_grid_ui()
        root.after(15, run_loop)

def start_execution():
    global interpreter
    raw_code = code_text.get("1.0", tk.END).replace("\n", "").strip()
    interpreter = PengilInterpreter(raw_code)
    interpreter.buffer = 40
    run_loop()

run_button = tk.Button(bottom_frame, text="[ EXECUTE ]", font=("Courier", 11, "bold"), bg="#FFFFFF", fg="#000000",activebackground="#EEEEEE", activeforeground="#000000", bd=1, relief="solid", command=start_execution)
run_button.pack(side="right")
root.mainloop()
