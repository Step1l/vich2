import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Импортируем ваши методы (предположим, они в модуле methods.py)
# Замените импорты на фактические пути к вашим функциям
from chord import chord_method
from secant import secant_method
from simpl_iteration import simple_iteration_method
class NonlinearApp:
    def __init__(self, parent):
        self.parent = parent

        # Словарь предопределённых функций и их производных
        self.functions = {
            "x^2 - 2": {
                "f": lambda x: x**2 - 2,
                "df": lambda x: 2*x,
                "str": "x² - 2"
            },
            "sin(x) - x/2": {
                "f": lambda x: math.sin(x) - x/2,
                "df": lambda x: math.cos(x) - 0.5,
                "str": "sin(x) - x/2"
            },
            "e^x - 3x": {
                "f": lambda x: math.exp(x) - 3*x,
                "df": lambda x: math.exp(x) - 3,
                "str": "eˣ - 3x"
            },
            "ln(x) - 1/x": {
                "f": lambda x: math.log(x) - 1/x,
                "df": lambda x: 1/x + 1/(x*x),
                "str": "ln(x) - 1/x"
            },
            "x^3 - x - 1": {
                "f": lambda x: x**3 - x - 1,
                "df": lambda x: 3*x**2 - 1,
                "str": "x³ - x - 1"
            }
        }

        # Выбор функции
        ttk.Label(parent, text="Выберите функцию:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.func_var = tk.StringVar()
        self.func_combo = ttk.Combobox(parent, textvariable=self.func_var, values=list(self.functions.keys()), state="readonly")
        self.func_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.func_combo.current(0)

        # Ввод интервала и точности
        ttk.Label(parent, text="a:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.a_entry = ttk.Entry(parent, width=15)
        self.a_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(parent, text="b:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.b_entry = ttk.Entry(parent, width=15)
        self.b_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(parent, text="Точность ε:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.eps_entry = ttk.Entry(parent, width=15)
        self.eps_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.eps_entry.insert(0, "1e-6")

        # Выбор метода
        ttk.Label(parent, text="Метод:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.method_var = tk.StringVar(value="chord")
        methods = [("Хорд", "chord"), ("Секущих", "secant"), ("Простой итерации", "simple")]
        for i, (text, val) in enumerate(methods):
            ttk.Radiobutton(parent, text=text, variable=self.method_var, value=val).grid(row=4, column=i+1, padx=5, pady=5, sticky="w")

        # Кнопки управления
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="Загрузить из файла", command=self.load_from_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Вычислить", command=self.calculate).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сохранить результат", command=self.save_result).pack(side="left", padx=5)

        # Область вывода результата
        ttk.Label(parent, text="Результат:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.result_text = tk.Text(parent, height=10, width=80)
        self.result_text.grid(row=7, column=0, columnspan=4, padx=5, pady=5)

        # График
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().grid(row=8, column=0, columnspan=4, padx=5, pady=5)

        # Переменная для хранения последнего результата
        self.last_result = None

    def load_from_file(self):
        filename = filedialog.askopenfilename(title="Выберите файл с данными", filetypes=[("Text files", "*.txt")])
        if not filename:
            return
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                if len(lines) < 3:
                    raise ValueError("Файл должен содержать a, b, eps (каждое на отдельной строке)")
                a = float(lines[0].strip())
                b = float(lines[1].strip())
                eps = float(lines[2].strip())
                self.a_entry.delete(0, tk.END)
                self.a_entry.insert(0, str(a))
                self.b_entry.delete(0, tk.END)
                self.b_entry.insert(0, str(b))
                self.eps_entry.delete(0, tk.END)
                self.eps_entry.insert(0, str(eps))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def check_interval(self, f, a, b):
        """Проверка наличия и единственности корня на [a,b]."""
        # Проверка, что a < b
        if a >= b:
            raise ValueError("Левая граница должна быть меньше правой")
        # Проверка знаков
        fa = f(a)
        fb = f(b)
        if fa * fb > 0:
            raise ValueError("На интервале нет корня (функция не меняет знак)")
        if abs(fa) < 1e-12 or abs(fb) < 1e-12:
            raise ValueError("Корень на границе интервала, уточните интервал")

        # Проверка единственности (табуляция)
        n = 100
        dx = (b - a) / n
        x = a
        last_sign = f(x) > 0
        sign_changes = 0
        for _ in range(n):
            x += dx
            current_sign = f(x) > 0
            if current_sign != last_sign:
                sign_changes += 1
                last_sign = current_sign
            if sign_changes > 1:
                raise ValueError("На интервале больше одного корня")
        if sign_changes == 0:
            raise ValueError("На интервале нет корня (табуляция не обнаружила смену знака)")

    def check_simple_iteration_convergence(self, f, df, a, b):
        """Проверка условия сходимости для метода простой итерации: |1 + λ f'(x)| < 1 на [a,b]."""
        # Оцениваем max |f'(x)|
        xs = [a + (b - a) * i / 10 for i in range(11)]
        max_df = max(abs(df(x)) for x in xs)
        if max_df < 1e-12:
            raise ValueError("Производная близка к нулю, метод простой итерации может не сойтись")
        lambd = 1 / max_df
        if df(a) > 0:
            lambd = -lambd  # λ подбирается для обеспечения |1+λ f'| < 1
        phi_der = lambda x: 1 + lambd * df(x)
        # Проверяем |φ'(x)| < 1 на сетке
        for x in xs:
            if abs(phi_der(x)) >= 1:
                g=df(x)
                raise ValueError(f"Условие сходимости нарушено: |φ'({x:.3f})| = {abs(phi_der(x)):.4f} >= 1")
        # Возвращаем λ, чтобы потом использовать в методе
        return lambd

    def calculate(self):
        try:
            # Получение данных
            func_name = self.func_var.get()
            f = self.functions[func_name]["f"]
            df = self.functions[func_name]["df"]
            a = float(self.a_entry.get())
            b = float(self.b_entry.get())
            eps = float(self.eps_entry.get())
            method = self.method_var.get()

            # Проверка интервала
            self.check_interval(f, a, b)

            # Подготовка начальных приближений
            # Для методов, требующих x0, берём середину интервала
            x0 = (a + b) / 2
            # Для метода секущих используем a и b как начальные точки

            # Выбор метода и вычисление
            if method == "chord":
                parent, f_parent, iterations = chord_method(f, a, b, eps)
                method_name = "Хорд"
            elif method == "secant":
                parent, f_parent, iterations = secant_method(f, a, b, eps)
                method_name = "Секущих"
            elif method == "simple":
                # Проверяем сходимость для метода простой итерации
                λ = self.check_simple_iteration_convergence(f, df, a, b)
                parent, f_parent, iterations = simple_iteration_method(f, df, a, b, eps)
                method_name = "Простой итерации"
            else:
                raise ValueError("Неизвестный метод")

            self.last_result = (parent, f_parent, iterations, method_name, func_name, a, b, eps)

            # Вывод результата
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Метод: {method_name}\n")
            self.result_text.insert(tk.END, f"Функция: {self.functions[func_name]['str']}\n")
            self.result_text.insert(tk.END, f"Интервал: [{a}, {b}]\n")
            self.result_text.insert(tk.END, f"Точность: {eps}\n")
            self.result_text.insert(tk.END, f"Найденный корень: {parent:.10f}\n")
            self.result_text.insert(tk.END, f"Значение функции в корне: {f_parent:.2e}\n")
            self.result_text.insert(tk.END, f"Число итераций: {iterations}\n")

            # Обновление графика
            self.update_plot(f, a, b, parent)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_plot(self, f, a, b, parent=None):
        self.ax.clear()
        length = b - a
        expand = max(0.5 * length, 1.0)
        x_min = a - expand
        x_max = b + expand
        x_vals = np.linspace(x_min, x_max, 500)
        y_vals = [f(x) for x in x_vals]

        self.ax.plot(x_vals, y_vals, 'b-', label='f(x)')
        self.ax.axhline(0, color='black', linewidth=0.5)
        self.ax.axvline(0, color='black', linewidth=0.5)
        self.ax.axvline(a, color='gray', linestyle='--', alpha=0.7, label='граница a')
        self.ax.axvline(b, color='gray', linestyle='--', alpha=0.7, label='граница b')
        if parent is not None:
            self.ax.plot(parent, f(parent), 'ro', label='Корень')

        self.ax.set_xlim(x_min, x_max)
        y_min = min(y_vals)
        y_max = max(y_vals)
        margin_y = (y_max - y_min) * 0.1 if y_max != y_min else 1.0
        self.ax.set_ylim(y_min - margin_y, y_max + margin_y)

        self.ax.set_xlabel('x')
        self.ax.set_ylabel('f(x)')
        self.ax.set_title(f'График функции на [{a}, {b}] с окрестностью')
        self.ax.grid(True)
        self.ax.legend()
        self.canvas.draw()

    def save_result(self):
        if self.last_result is None:
            messagebox.showwarning("Нет данных", "Сначала выполните вычисление")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not filename:
            return
        try:
            with open(filename, 'w') as f:
                parent, f_parent, iterations, method_name, func_name, a, b, eps = self.last_result
                f.write(f"Метод: {method_name}\n")
                f.write(f"Функция: {self.functions[func_name]['str']}\n")
                f.write(f"Интервал: [{a}, {b}]\n")
                f.write(f"Точность: {eps}\n")
                f.write(f"Корень: {parent:.10f}\n")
                f.write(f"Значение функции: {f_parent:.2e}\n")
                f.write(f"Итераций: {iterations}\n")
            messagebox.showinfo("Сохранено", f"Результат сохранён в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
