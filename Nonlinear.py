import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import simple_help
from chord import chord_method
from secant import secant_method
from simpl_iteration import simple_iteration_method



class NonlinearApp:
    def __init__(self, parent):
        self.parent = parent

        # --- Конфигурация функций ---
        self.functions = {
            "x² - 2": {
                "f": lambda x: x ** 2 - 2,
                "df": lambda x: 2 * x,
                "str": "x² - 2 = 0",
                "note": "Корень: √2 ≈ 1.414"
            },
            "sin(x) - x/2": {
                "f": lambda x: math.sin(x) - x / 2,
                "df": lambda x: math.cos(x) - 0.5,
                "str": "sin(x) - x/2 = 0",
                "note": "Корень: ≈ 1.895"
            },
            "eˣ - 3x": {
                "f": lambda x: math.exp(x) - 3 * x,
                "df": lambda x: math.exp(x) - 3,
                "str": "eˣ - 3x = 0",
                "note": "Корни: ≈ 0.619 и ≈ 1.512"
            },
            "ln(x) - 1/x": {
                "f": lambda x: math.log(x) - 1 / x,
                "df": lambda x: 1 / x + 1 / (x * x),
                "str": "ln(x) - 1/x = 0",
                "note": "Корень: ≈ 1.763 (x > 0)"
            },
            "x³ - x - 1": {
                "f": lambda x: x ** 3 - x - 1,
                "df": lambda x: 3 * x ** 2 - 1,
                "str": "x³ - x - 1 = 0",
                "note": "Корень: ≈ 1.325"
            }
        }

        self._setup_ui()
        self.last_result = None
        self.report_window = None

    def _setup_ui(self):
        # Настройка весов для растягивания
        self.parent.grid_rowconfigure(4, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)

        # --- 1. Выбор функции ---
        frame_top = ttk.Frame(self.parent)
        frame_top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        ttk.Label(frame_top, text="Функция:").pack(side="left")
        self.func_var = tk.StringVar()
        self.func_combo = ttk.Combobox(frame_top, textvariable=self.func_var,
                                       values=list(self.functions.keys()),
                                       state="readonly", width=35)
        self.func_combo.pack(side="left", padx=10)
        self.func_combo.current(0)
        self.func_combo.bind("<<ComboboxSelected>>", self.on_function_change)

        # --- 2. Блок с формулой ---
        frame_eq = ttk.LabelFrame(self.parent, text="Уравнение")
        frame_eq.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.lbl_func_display = ttk.Label(frame_eq, text="", font=("Consolas", 14))
        self.lbl_func_display.pack(padx=20, pady=5)

        self.lbl_note = ttk.Label(frame_eq, text="", foreground="darkorange", font=("Arial", 9, "italic"))
        self.lbl_note.pack(padx=20, pady=(0, 5))

        # --- 3. Параметры ---
        frame_params = ttk.LabelFrame(self.parent, text="Параметры вычисления")
        frame_params.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ttk.Label(frame_params, text="a:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        self.a_entry = ttk.Entry(frame_params, width=10)
        self.a_entry.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        self.a_entry.insert(0, "1.0")

        ttk.Label(frame_params, text="b:").grid(row=0, column=2, sticky="e", padx=5, pady=3)
        self.b_entry = ttk.Entry(frame_params, width=10)
        self.b_entry.grid(row=0, column=3, sticky="w", padx=5, pady=3)
        self.b_entry.insert(0, "2.0")

        ttk.Label(frame_params, text="ε:").grid(row=0, column=4, sticky="e", padx=5, pady=3)
        self.eps_entry = ttk.Entry(frame_params, width=10)
        self.eps_entry.grid(row=0, column=5, sticky="w", padx=5, pady=3)
        self.eps_entry.insert(0, "1e-6")

        # Выбор метода
        method_frame = ttk.LabelFrame(frame_params, text="Метод")
        method_frame.grid(row=1, column=0, columnspan=6, sticky="ew", padx=5, pady=5)

        self.method_var = tk.StringVar(value="chord")
        methods = [("Хорд", "chord"), ("Секущих", "secant"), ("Простой итерации", "simple")]
        for i, (text, val) in enumerate(methods):
            ttk.Radiobutton(method_frame, text=text, variable=self.method_var, value=val).grid(row=0, column=i, padx=15,
                                                                                               sticky="w")

        # --- 4. Кнопки ---
        frame_btn = ttk.Frame(self.parent)
        frame_btn.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(frame_btn, text="▶ Рассчитать", command=self.calculate).pack(side="left", padx=15)
        ttk.Button(frame_btn, text="📄 Отчёт", command=self.show_report).pack(side="left", padx=10)
        ttk.Button(frame_btn, text="💾 Сохранить", command=self.save_result).pack(side="left", padx=10)
        ttk.Button(frame_btn, text="📂 Загрузить", command=self.load_from_file).pack(side="left", padx=10)

        # --- 5. Статусная строка ---
        self.status_label = ttk.Label(self.parent, text="Ожидание вычислений...",
                                      font=("Arial", 10), foreground="gray")
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # --- 6. График (БОЛЬШОЙ) ---
        frame_plot = ttk.Frame(self.parent)
        frame_plot.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.parent.grid_rowconfigure(4, weight=1)

        self.figure = plt.Figure(figsize=(12, 9), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=frame_plot)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # --- 7. Инициализация (ТЕПЕРЬ, когда все виджеты созданы!) ---
        self.on_function_change(None)

    def parse_number(self, value_str):
        """Парсит число с поддержкой запятой"""
        if not value_str or not value_str.strip():
            raise ValueError("Поле не может быть пустым")
        value_str = value_str.strip().replace(',', '.')
        try:
            return float(value_str)
        except ValueError:
            raise ValueError(f"Неверный формат: '{value_str}'")

    def on_function_change(self, event):
        key = self.func_var.get()
        data = self.functions[key]
        self.lbl_func_display.config(text=data["str"])
        self.lbl_note.config(text=data.get("note", ""))

        # Проверка на существование виджета
        if hasattr(self, 'status_label'):
            self.status_label.config(text="Ожидание вычислений...", foreground="gray")

    def load_from_file(self):
        filename = filedialog.askopenfilename(title="Выберите файл", filetypes=[("Text files", "*.txt")])
        if not filename:
            return
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) < 3:
                    raise ValueError("Файл должен содержать a, b, eps")
                self.a_entry.delete(0, tk.END)
                self.a_entry.insert(0, lines[0].strip().replace(',', '.'))
                self.b_entry.delete(0, tk.END)
                self.b_entry.insert(0, lines[1].strip().replace(',', '.'))
                self.eps_entry.delete(0, tk.END)
                self.eps_entry.insert(0, lines[2].strip().replace(',', '.'))
            messagebox.showinfo("Успех", "Данные загружены")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))



    def calculate(self):
        try:
            func_name = self.func_var.get()
            data = self.functions[func_name]
            f, df = data["f"], data["df"]

            a = self.parse_number(self.a_entry.get())
            b = self.parse_number(self.b_entry.get())
            eps = self.parse_number(self.eps_entry.get())
            if eps <= 0: raise ValueError("Точность > 0")

            method = self.method_var.get()


            if func_name == "ln(x) - 1/x":
                if a <= 0 or b <= 0:
                    messagebox.showerror("Ошибка области определения",
                        "Функция ln(x) определена только при x > 0!\n"
                        f"Ваши значения: a={a}, b={b}")
                    return
                if a < 0 < b:
                    messagebox.showerror("Ошибка области определения",
                        "Интервал не должен содержать 0!")
                    return

            simple_help.check_interval(f, a, b)

            simple_help.check_interval(f, a, b)


            if method == "chord":
                try:
                    root, f_val, iters = chord_method(f, a, b, eps)
                except:
                    raise ValueError(f"Метод хорд не может продолжить")
                method_name = "Хорд"
            elif method == "secant":
                root, f_val, iters = secant_method(f, a, b, eps)
                method_name = "Секущих"
            elif method == "simple":
                phi=simple_help.get_noline_phi(a,b,df,f)
                root, f_val, iters = simple_iteration_method(f, a, b, eps,phi)
                method_name = "Простой итерации"
            else:
                raise ValueError("Неизвестный метод")

            self.last_result = {
                "method": method_name, "func": data["str"],
                "root": root, "f_val": f_val, "iters": iters,
                "a": a, "b": b, "eps": eps,
            }

            if abs(f_val) < eps:
                self.status_label.config(text=f"✅ Корень найден: {root:.8f} за {iters} итер.", foreground="green")
            else:
                self.status_label.config(text=f"⚠ Невязка {f_val:.2e}", foreground="orange")

            self.update_plot(f, a, b, root)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.status_label.config(text="❌ Ошибка вычислений", foreground="red")

    def show_report(self):
        if self.last_result is None:
            messagebox.showwarning("Нет данных", "Сначала выполните вычисление")
            return

        if self.report_window:
            self.report_window.destroy()

        self.report_window = Toplevel(self.parent)
        self.report_window.title("📄 Отчёт")
        self.report_window.geometry("600x500")

        r = self.last_result
        text = tk.Text(self.report_window, font=("Consolas", 10))
        text.pack(fill="both", expand=True, padx=10, pady=10)

        report = [
            "=" * 50,
            "ОТЧЁТ: Решение нелинейного уравнения",
            "=" * 50,
            f"Уравнение: {r['func']}",
            f"Метод: {r['method']}",
            "-" * 50,
            f"Интервал: [{r['a']}, {r['b']}]",
            f"Точность: {r['eps']}",
            "-" * 50,
            f"✅ КОРЕНЬ НАЙДЕН",
            f"x = {r['root']:.12f}",
            f"f(x) = {r['f_val']:.2e}",
            f"Итераций: {r['iters']}",
            "=" * 50
        ]
        text.insert("1.0", "\n".join(report))
        text.config(state="disabled")

    def update_plot(self, f, a, b, root=None):
        self.ax.clear()

        # --- 1. Безопасное вычисление функции с обработкой ошибок ---
        def safe_f(x):
            try:
                y = f(x)
                # Проверка на бесконечность и NaN
                if math.isnan(y) or math.isinf(y):
                    return None
                return y
            except (ValueError, ZeroDivisionError, OverflowError):
                return None

        # --- 2. Умное определение границ (чтобы не уйти в минус для ln(x)) ---
        pad = max((b - a) * 0.3, 0.5)
        x_min = a - pad
        x_max = b + pad

        # Если левая граница уходит в отрицательные числа, а корень положительный — обрезаем
        if x_min < 0 and a > 0:
            x_min = 0.01  # Оставляем небольшой зазор от 0
        if x_min < 0 and root is not None and root > 0:
            x_min = min(0.01, root / 2)

        # --- 3. Генерация точек и фильтрация ошибок ---
        x_vals = np.linspace(x_min, x_max, 500)
        y_vals = []
        valid_x = []

        for x in x_vals:
            y = safe_f(x)
            if y is not None:
                valid_x.append(x)
                y_vals.append(y)

        # Если все точки отвалились (совсем плохой интервал)
        if not valid_x:
            self.ax.text(0.5, 0.5, 'Нет данных для графика (область определения)',
                         transform=self.ax.transAxes, ha='center', va='center')
            self.canvas.draw()
            return

        # --- 4. Построение графика ---
        self.ax.plot(valid_x, y_vals, 'b-', linewidth=2, label='f(x)')
        self.ax.axhline(0, color='black', linewidth=1)
        self.ax.axvline(a, color='gray', linestyle='--', alpha=0.5, label=f'Границы [{a},{b}]')
        self.ax.axvline(b, color='gray', linestyle='--', alpha=0.5)

        if root is not None:
            # Проверяем, попадает ли корень в отрисованную область
            if min(valid_x) <= root <= max(valid_x):
                self.ax.plot(root, f(root), 'ro', markersize=10, label=f'Корень: {root:.6f}')

        # --- 5. Настройка осей ---
        self.ax.set_xlabel('x', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('f(x)', fontsize=12, fontweight='bold')
        self.ax.set_title('График функции', fontsize=14, fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.legend(loc='best')

        # Авто-масштаб по Y
        y_min, y_max = min(y_vals), max(y_vals)
        y_pad = (y_max - y_min) * 0.1 if y_max != y_min else 1.0
        self.ax.set_ylim(y_min - y_pad, y_max + y_pad)

        # Явно задаем границы по X (чтобы matplotlib не рисовал за пределами valid_x)
        self.ax.set_xlim(x_min, x_max)

        self.canvas.draw()

    def save_result(self):
        if self.last_result is None:
            messagebox.showwarning("Нет данных", "Сначала выполните вычисление")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not filename:
            return
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                r = self.last_result
                f.write(f"ОТЧЁТ: Нелинейное уравнение\n{'=' * 50}\n\n")
                f.write(f"Уравнение: {r['func']}\n")
                f.write(f"Метод: {r['method']}\n")
                f.write(f"Интервал: [{r['a']}, {r['b']}]\n")
                f.write(f"Точность: {r['eps']}\n\n")
                f.write(f"Корень: {r['root']:.12f}\n")
                f.write(f"f(x): {r['f_val']:.2e}\n")
                f.write(f"Итераций: {r['iters']}\n")
            messagebox.showinfo("Успех", f"Сохранено в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))