import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Импортируем твой метод
from simple_iteration_system import simple_iteration_system
import simple_help

class SystemApp:
    def make_phi3(self, x0, y0):
        if x0 >= 0:
            phi1 = lambda x, y: math.sqrt(max(5 - y ** 2, 0))
            phi2 = lambda x, y: x - 1
        else:
            phi1 = lambda x, y: y + 1
            phi2 = lambda x, y: -math.sqrt(max(5 - x ** 2, 0))
        return phi1, phi2
    def __init__(self, parent):
        self.parent = parent

        # --- Конфигурация систем ---
        self.systems = {
            "Система 1": {
    "equations": "⎧ 2x² + y² - 2 = 0\n⎨\n⎩ x² + 3y² - 3 = 0",
    "phi1": lambda x, y: math.copysign(
        math.sqrt(max((2 - y**2) / 2, 0)), x
    ),
    "phi2": lambda x, y: math.copysign(
        math.sqrt(max((3 - x**2) / 3, 0)), y
    ),
    "f1": lambda x, y: 2 * x**2 + y**2 - 2,
    "f2": lambda x, y: x**2 + 3 * y**2 - 3,
    "note": "Решение: x≈±0.707, y≈±1.0",
    "x0": "1.0", "y0": "1.0"
},
            "Система 2": {
                "equations": "⎧ sin(x) - y = 0\n⎨\n⎩ cos(y) - x = 0",
                "phi1": lambda x, y: math.cos(y),
                "phi2": lambda x, y: math.sin(x),
                "f1": lambda x, y: math.sin(x) - y,
                "f2": lambda x, y: math.cos(y) - x,
                "note": "Решение: x≈0.6948, y≈0.7682",
                "x0": "0.5", "y0": "0.5"
            },
            "Система 3": {
    "equations": "⎧ x² + y² = 5\n⎨\n⎩ x - y = 1",
    "phi1": lambda x, y: x - 0.1 * (x**2 + y**2 - 5),
    "phi2": lambda x, y: y - 0.1 * (x - y - 1),
    "f1": lambda x, y: x**2 + y**2 - 5,
    "f2": lambda x, y: x - y - 1,
    "note": "Корни: (2, 1) и (-1, -2) — зависит от x0, y0",
    "x0": "2.0", "y0": "1.0"
}
        }

        self._setup_ui()
        self.last_result = None
        self.report_window = None

    def _setup_ui(self):
        self.parent.grid_rowconfigure(3, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)

        # --- 1. Выбор системы ---
        frame_top = ttk.Frame(self.parent)
        frame_top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        ttk.Label(frame_top, text="Выберите систему:").pack(side="left")
        self.sys_var = tk.StringVar()
        self.sys_combo = ttk.Combobox(frame_top, textvariable=self.sys_var,
                                      values=list(self.systems.keys()),
                                      state="readonly", width=35)
        self.sys_combo.pack(side="left", padx=10)
        self.sys_combo.current(0)
        self.sys_combo.bind("<<ComboboxSelected>>", self.on_system_change)

        # --- 2. Блок с формулами ---
        frame_eq = ttk.LabelFrame(self.parent, text="Вид системы уравнений")
        frame_eq.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.lbl_system_display = ttk.Label(frame_eq, text="", font=("Consolas", 13), justify="left")
        self.lbl_system_display.pack(padx=20, pady=5)

        self.lbl_note = ttk.Label(frame_eq, text="", foreground="darkorange", font=("Arial", 9, "italic"))
        self.lbl_note.pack(padx=20, pady=(0, 5))

        # --- 3. Параметры ---
        frame_params = ttk.LabelFrame(self.parent, text="Параметры метода")
        frame_params.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ttk.Label(frame_params, text="x0:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        self.x0_entry = ttk.Entry(frame_params, width=10)
        self.x0_entry.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(frame_params, text="y0:").grid(row=0, column=2, sticky="e", padx=5, pady=3)
        self.y0_entry = ttk.Entry(frame_params, width=10)
        self.y0_entry.grid(row=0, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(frame_params, text="ε:").grid(row=0, column=4, sticky="e", padx=5, pady=3)
        self.eps_entry = ttk.Entry(frame_params, width=10)
        self.eps_entry.grid(row=0, column=5, sticky="w", padx=5, pady=3)
        self.eps_entry.insert(0, "1e-6")

        ttk.Label(frame_params, text="MaxIter:").grid(row=0, column=6, sticky="e", padx=5, pady=3)
        self.max_iter_entry = ttk.Entry(frame_params, width=8)
        self.max_iter_entry.grid(row=0, column=7, sticky="w", padx=5, pady=3)
        self.max_iter_entry.insert(0, "100")

        # Кнопки
        frame_btn = ttk.Frame(frame_params)
        frame_btn.grid(row=1, column=0, columnspan=8, pady=8)
        ttk.Button(frame_btn, text="▶ Рассчитать", command=self.calculate).pack(side="left", padx=15)
        ttk.Button(frame_btn, text="📄 Отчёт", command=self.show_report).pack(side="left", padx=10)
        ttk.Button(frame_btn, text="💾 Сохранить", command=self.save_result).pack(side="left", padx=10)

        # --- 4. Статусная строка ---
        self.status_label = ttk.Label(self.parent, text="Ожидание вычислений...",
                                      font=("Arial", 10), foreground="gray")
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # --- 5. График ---
        frame_plot = ttk.Frame(self.parent)
        frame_plot.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.parent.grid_rowconfigure(3, weight=1)

        self.figure = plt.Figure(figsize=(12, 9), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=frame_plot)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.on_system_change(None)

    def parse_number(self, value_str):
        if not value_str or not value_str.strip():
            raise ValueError("Поле не может быть пустым")
        value_str = value_str.strip().replace(',', '.')
        try:
            return float(value_str)
        except ValueError:
            raise ValueError(f"Неверный формат: '{value_str}'")

    def on_system_change(self, event):
        key = self.sys_var.get()
        data = self.systems[key]
        self.lbl_system_display.config(text=data["equations"])
        self.lbl_note.config(text=data.get("note", ""))

        if hasattr(self, 'x0_entry'):
            self.x0_entry.delete(0, tk.END)
            self.x0_entry.insert(0, data.get("x0", "1.0"))
            self.y0_entry.delete(0, tk.END)
            self.y0_entry.insert(0, data.get("y0", "1.0"))

        self.status_label.config(text="Ожидание вычислений...", foreground="gray")

    def safe_phi_call(self, phi_func, x, y):
        """Безопасный вызов phi с обработкой ошибок"""
        try:
            res = phi_func(x, y)
            if isinstance(res, float) and (math.isnan(res) or math.isinf(res)):
                raise ValueError("Недопустимое значение (NaN/Inf)")
            return res
        except Exception as e:
            raise ValueError(f"Ошибка φ: {str(e)}")


    def validate_solution(self, f1, f2, x, y, eps):
        f1_val = f1(x, y)
        f2_val = f2(x, y)
        residual = max(abs(f1_val), abs(f2_val))

        return residual < eps, f1_val, f2_val, residual

    def calculate(self):
        try:
            # Парсинг входных данных
            x0 = self.parse_number(self.x0_entry.get())
            y0 = self.parse_number(self.y0_entry.get())
            eps = self.parse_number(self.eps_entry.get())
            if eps <= 0: raise ValueError("Точность должна быть > 0")
            max_iter = int(self.max_iter_entry.get())
            if max_iter <= 0: raise ValueError("Итерации должны быть > 0")

            # Получение данных системы
            sys_key = self.sys_var.get()
            data = self.systems[sys_key]
            phi1, phi2 = data["phi1"], data["phi2"]
            if sys_key == "Система 3":
                phi1, phi2 = self.make_phi3(x0,y0)  # ← добавить эту строку

            f1, f2 = data["f1"], data["f2"]
            f1, f2 = data["f1"], data["f2"]

            # Проверка сходимости (оценка нормы Якоби)
            norm_est = simple_help.check_convergence_approx(phi1, phi2, x0, y0)
            x, y, err_x, err_y, iters = simple_iteration_system(
                phi1, phi2, x0, y0, eps, max_iter
            )

            # Проверка решения
            is_valid, f1_val, f2_val, residual = self.validate_solution(f1, f2, x, y, eps)

            self.last_result = {
                "sys": sys_key, "desc": data["equations"], "x": x, "y": y,
                "f1": f1_val, "f2": f2_val, "err_x": err_x, "err_y": err_y,
                "iters": iters, "x0": x0, "y0": y0, "eps": eps, "norm": norm_est,
                "converged": True, "is_valid": is_valid, "residual": residual
            }

            # Обновление статуса
            if is_valid:
                self.status_label.config(text=f"✅ Решение найдено за {iters} итер. | x={x:.6f}, y={y:.6f}",
                                         foreground="green")
            else:
                self.status_label.config(text=f"⚠ Найдено, но проверка не пройдена | {iters} итер.",
                                         foreground="orange")

            self.update_plot(f1, f2, x, y, True)

        except RuntimeError as re:
            # Метод не сошелся
            messagebox.showwarning("Нет сходимости", str(re))
            self.status_label.config(text="❌ Метод не сошелся", foreground="red")
        except ValueError as ve:
            # Ошибка в phi или входных данных
            messagebox.showerror("Ошибка вычислений", str(ve))
            self.status_label.config(text="❌ Ошибка вычислений", foreground="red")
        except Exception as e:
            messagebox.showerror("Критическая ошибка", str(e))
            self.status_label.config(text="❌ Ошибка", foreground="red")

    def show_report(self):
        if self.last_result is None:
            messagebox.showwarning("Нет данных", "Сначала выполните вычисление")
            return

        if self.report_window:
            self.report_window.destroy()

        self.report_window = Toplevel(self.parent)
        self.report_window.title("📄 Полный отчёт")
        self.report_window.geometry("700x600")
        self.report_window.resizable(True, True)

        r = self.last_result

        header_frame = ttk.Frame(self.report_window)
        header_frame.pack(fill="x", padx=10, pady=10)

        status_icon = "✅" if r["converged"] and r["is_valid"] else "❌"
        status_text = "Сходимость достигнута" if r["converged"] else "Метод не сошелся"
        ttk.Label(header_frame, text=f"{status_icon} {status_text}",
                  font=("Arial", 14, "bold"), foreground="green" if r["converged"] else "red").pack()

        text_frame = ttk.Frame(self.report_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)

        report_text = tk.Text(text_frame, font=("Consolas", 10), wrap="word")
        report_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_frame, command=report_text.yview)
        scrollbar.pack(side="right", fill="y")
        report_text.config(yscrollcommand=scrollbar.set)

        report = []
        report.append("=" * 60)
        report.append("ОТЧЁТ: Метод простых итераций (Система уравнений)")
        report.append("=" * 60)
        report.append("")
        report.append(f"Система:\n{r['desc']}")
        report.append("")
        report.append("-" * 60)
        report.append("ПАРАМЕТРЫ")
        report.append("-" * 60)
        report.append(f"x0 = {r['x0']}, y0 = {r['y0']}")
        report.append(f"ε = {r['eps']}")
        report.append(f"Норма Якоби: {r['norm']:.4f} {'(< 1 ✅)' if r['norm'] < 1 else '(≥ 1 ⚠)'}")
        report.append("")
        report.append("-" * 60)
        report.append("РЕЗУЛЬТАТ")
        report.append("-" * 60)
        report.append(f"Статус: {'✅ Сходимость' if r['converged'] else '❌ Нет сходимости'}")
        report.append(f"Итераций: {r['iters']}")
        report.append(f"x = {r['x']:.12f}")
        report.append(f"y = {r['y']:.12f}")
        report.append(f"f1 = {r['f1']:.2e} < eps={r['eps']}, f2 = {r['f2']:.2e}< eps={r['eps']}")
        report.append(f"Проверка: {f'✅ OK' if r['is_valid'] else '❌ FAIL'}")
        report.append("")
        report.append("=" * 60)

        report_text.insert("1.0", "\n".join(report))
        report_text.config(state="disabled")

        btn_frame = ttk.Frame(self.report_window)
        btn_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(btn_frame, text="Закрыть", command=self.report_window.destroy).pack(side="right", padx=5)

    def update_plot(self, f1, f2, root_x, root_y, converged):
        self.ax.clear()

        # Авто-масштаб вокруг решения
        min_x, max_x = root_x - 2, root_x + 2
        min_y, max_y = root_y - 2, root_y + 2

        x_vals = np.linspace(min_x, max_x, 400)
        y_vals = np.linspace(min_y, max_y, 400)
        X, Y = np.meshgrid(x_vals, y_vals)

        Z1 = np.vectorize(f1)(X, Y)
        Z2 = np.vectorize(f2)(X, Y)

        self.ax.contour(X, Y, Z1, levels=[0], colors='blue', linewidths=2.5, label='f1=0')
        self.ax.contour(X, Y, Z2, levels=[0], colors='red', linewidths=2.5, label='f2=0')

        self.ax.plot(root_x, root_y, 'ko', markersize=5, label='Решение', zorder=20)

        self.ax.set_xlabel('x', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('y', fontsize=12, fontweight='bold')
        self.ax.set_title('График сходимости', fontsize=14, fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.legend(loc='best', fontsize=10)
        self.ax.set_aspect('equal')

        self.canvas.draw()

    def save_result(self):
        if self.last_result is None:
            messagebox.showwarning("Нет данных", "Сначала выполните вычисление")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not filename: return
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                r = self.last_result
                f.write(f"ОТЧЁТ: Метод простых итераций\n{'=' * 60}\n\n")
                f.write(f"Система:\n{r['desc']}\n\n")
                f.write(f"x0={r['x0']}, y0={r['y0']}, ε={r['eps']}\n\n")
                f.write(f"x = {r['x']:.12f}\n")
                f.write(f"y = {r['y']:.12f}\n")
                f.write(f"f1={r['f1']:.2e}, f2={r['f2']:.2e}\n")
                f.write(f"Проверка: {'✅ OK' if r['is_valid'] else '❌ Ошибка'}\n")
                f.write(f"Итераций: {r['iters']}\n")
            messagebox.showinfo("Успех", f"Сохранено в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))