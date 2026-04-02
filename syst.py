import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SystemApp:
    def __init__(self, parent):
        self.parent = parent

        # --- Конфигурация систем ---
        self.systems = {
            "Система 1 (Устойчивая нелинейная)": {
                "equations": "⎧ 2x² + y² - 2 = 0\n⎨\n⎩ x² + 3y² - 3 = 0",
                "phi1": lambda x, y: math.sqrt(max(0, 1 - 0.5 * y ** 2)),
                "phi2": lambda x, y: math.sqrt(max(0, 1 - (x ** 2) / 3)),
                "f1": lambda x, y: 2 * x ** 2 + y ** 2 - 2,
                "f2": lambda x, y: x ** 2 + 3 * y ** 2 - 3,
                "note": "✅ Сходится при x0∈[0,1.5], y0∈[0,1.5]. Решение: x≈0.707, y≈1.0",
                "x0": "1.0", "y0": "1.0"
            },
            "Система 2 (Тригонометрическая)": {
                "equations": "⎧ sin(x) - y = 0\n⎨\n⎩ cos(y) - x = 0",
                "phi1": lambda x, y: math.cos(y),
                "phi2": lambda x, y: math.sin(x),
                "f1": lambda x, y: math.sin(x) - y,
                "f2": lambda x, y: math.cos(y) - x,
                "note": "✅ Классический пример. Решение: x≈0.6948, y≈0.7682",
                "x0": "0.5", "y0": "0.5"
            },
            "Система 3 (С параметром релаксации)": {
                "equations": "⎧ x² + y² = 5\n⎨\n⎩ x - y = 1",
                "phi1": lambda x, y: x + 0.1 * (5 - x ** 2 - y ** 2),
                "phi2": lambda x, y: x - 1,
                "f1": lambda x, y: x ** 2 + y ** 2 - 5,
                "f2": lambda x, y: x - y - 1,
                "note": "⚠ Использован метод релаксации (τ=0.1). Решение: x≈2.23, y≈1.23",
                "x0": "2.0", "y0": "1.0"
            }
        }

        self._setup_ui()
        self.last_result = None
        self.iteration_history = []
        self.report_window = None  # Для хранения ссылки на окно отчёта

    def _setup_ui(self):
        # Настройка весов для правильного растягивания
        self.parent.grid_rowconfigure(3, weight=1)  # График растягивается
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
        ttk.Button(frame_btn, text="📄 Показать отчёт", command=self.show_report).pack(side="left", padx=10)
        ttk.Button(frame_btn, text="💾 Сохранить", command=self.save_result).pack(side="left", padx=10)

        # --- 4. Статусная строка (компактная) ---
        self.status_label = ttk.Label(self.parent, text="Ожидание вычислений...",
                                      font=("Arial", 10), foreground="gray")
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # --- 5. График (БОЛЬШОЙ) ---
        frame_plot = ttk.Frame(self.parent)
        frame_plot.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.parent.grid_rowconfigure(3, weight=1)  # График занимает всё оставшееся место

        self.figure = plt.Figure(figsize=(12, 9), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=frame_plot)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # --- 6. Инициализация ---
        self.on_system_change(None)

    def parse_number(self, value_str):
        if not value_str or not value_str.strip():
            raise ValueError("Поле не может быть пустым")
        value_str = value_str.strip().replace(',', '.')
        try:
            return float(value_str)
        except ValueError:
            raise ValueError(f"Неверный формат: '{value_str}'. Используйте точку или запятую.")

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
        try:
            res = phi_func(x, y)
            if isinstance(res, float) and (math.isnan(res) or math.isinf(res)):
                raise ValueError("Недопустимое значение (NaN/Inf)")
            return res
        except Exception as e:
            raise ValueError(f"Ошибка φ: {str(e)}")

    def run_simple_iteration(self, phi1, phi2, x0, y0, eps, max_iter):
        x, y = x0, y0
        history = []

        for i in range(max_iter):
            try:
                x_new = self.safe_phi_call(phi1, x, y)
                y_new = self.safe_phi_call(phi2, x, y)
            except ValueError as e:
                raise e

            dx = abs(x_new - x)
            dy = abs(y_new - y)

            history.append({"iter": i + 1, "x": x_new, "y": y_new, "dx": dx, "dy": dy})

            if max(dx, dy) < eps:
                return x_new, y_new, dx, dy, i + 1, history, True

            x, y = x_new, y_new

        return x, y, dx, dy, max_iter, history, False

    def check_convergence_approx(self, phi1, phi2, x0, y0):
        x, y = x0, y0
        h = 1e-6
        try:
            dphi1dx = (self.safe_phi_call(phi1, x + h, y) - self.safe_phi_call(phi1, x - h, y)) / (2 * h)
            dphi1dy = (self.safe_phi_call(phi1, x, y + h) - self.safe_phi_call(phi1, x, y - h)) / (2 * h)
            dphi2dx = (self.safe_phi_call(phi2, x + h, y) - self.safe_phi_call(phi2, x - h, y)) / (2 * h)
            dphi2dy = (self.safe_phi_call(phi2, x, y + h) - self.safe_phi_call(phi2, x, y - h)) / (2 * h)
            return max(abs(dphi1dx) + abs(dphi1dy), abs(dphi2dx) + abs(dphi2dy))
        except:
            return float('inf')

    def validate_solution(self, f1, f2, x, y, eps):
        f1_val = f1(x, y)
        f2_val = f2(x, y)
        residual = max(abs(f1_val), abs(f2_val))
        threshold = eps * 100
        return residual < threshold, f1_val, f2_val, residual, threshold

    def calculate(self):
        try:
            x0 = self.parse_number(self.x0_entry.get())
            y0 = self.parse_number(self.y0_entry.get())
            eps = self.parse_number(self.eps_entry.get())
            if eps <= 0: raise ValueError("Точность должна быть > 0")
            max_iter = int(self.max_iter_entry.get())
            if max_iter <= 0: raise ValueError("Итерации должны быть > 0")

            sys_key = self.sys_var.get()
            data = self.systems[sys_key]
            phi1, phi2 = data["phi1"], data["phi2"]
            f1, f2 = data["f1"], data["f2"]

            norm_est = self.check_convergence_approx(phi1, phi2, x0, y0)
            x, y, err_x, err_y, iters, history, converged = self.run_simple_iteration(
                phi1, phi2, x0, y0, eps, max_iter
            )
            self.iteration_history = history
            is_valid, f1_val, f2_val, residual, threshold = self.validate_solution(f1, f2, x, y, eps)

            self.last_result = {
                "sys": sys_key, "desc": data["equations"], "x": x, "y": y,
                "f1": f1_val, "f2": f2_val, "err_x": err_x, "err_y": err_y,
                "iters": iters, "x0": x0, "y0": y0, "eps": eps, "norm": norm_est,
                "converged": converged, "is_valid": is_valid, "residual": residual,
                "threshold": threshold, "history": history
            }

            # Обновление статусной строки
            if converged and is_valid:
                self.status_label.config(text=f"✅ Решение найдено за {iters} итер. | x={x:.6f}, y={y:.6f}",
                                         foreground="green")
            elif converged:
                self.status_label.config(text=f"⚠ Найдено, но проверка не пройдена | {iters} итер.",
                                         foreground="orange")
            else:
                self.status_label.config(text=f"❌ Не сошелся за {iters} итераций",
                                         foreground="red")

            self.update_plot(f1, f2, x, y, converged)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.status_label.config(text="❌ Ошибка вычислений", foreground="red")

    def show_report(self):
        """Открывает отдельное окно с полным отчётом"""
        if self.last_result is None:
            messagebox.showwarning("Нет данных", "Сначала выполните вычисление")
            return

        # Закрываем старое окно отчёта если есть
        if self.report_window is not None:
            self.report_window.destroy()

        # Создаём новое окно
        self.report_window = Toplevel(self.parent)
        self.report_window.title("📄 Полный отчёт о решении")
        self.report_window.geometry("700x600")
        self.report_window.resizable(True, True)

        r = self.last_result

        # Заголовок
        header_frame = ttk.Frame(self.report_window)
        header_frame.pack(fill="x", padx=10, pady=10)

        status_icon = "✅" if r["converged"] and r["is_valid"] else "❌"
        status_text = "Сходимость достигнута" if r["converged"] else "Метод не сошелся"
        ttk.Label(header_frame, text=f"{status_icon} {status_text}",
                  font=("Arial", 14, "bold"), foreground="green" if r["converged"] else "red").pack()

        # Текст отчёта
        text_frame = ttk.Frame(self.report_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)

        report_text = tk.Text(text_frame, font=("Consolas", 10), wrap="word")
        report_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_frame, command=report_text.yview)
        scrollbar.pack(side="right", fill="y")
        report_text.config(yscrollcommand=scrollbar.set)

        # Формирование отчёта
        report = []
        report.append("=" * 60)
        report.append("ОТЧЁТ: Метод простых итераций для системы нелинейных уравнений")
        report.append("=" * 60)
        report.append("")
        report.append(f"Система уравнений:\n{r['desc']}")
        report.append("")
        report.append("-" * 60)
        report.append("ПАРАМЕТРЫ ВЫЧИСЛЕНИЯ")
        report.append("-" * 60)
        report.append(f"Начальные приближения: x0 = {r['x0']}, y0 = {r['y0']}")
        report.append(f"Точность (ε): {r['eps']}")
        report.append(f"Макс. итераций: {r['iters']}")
        report.append(f"Оценка нормы Якоби: {r['norm']:.4f} {'(< 1 ✅)' if r['norm'] < 1 else '(≥ 1 ⚠)'}")
        report.append("")
        report.append("-" * 60)
        report.append("РЕЗУЛЬТАТ")
        report.append("-" * 60)
        report.append(f"Статус: {'✅ Сходимость достигнута' if r['converged'] else '❌ Метод не сошелся'}")
        report.append(f"Количество итераций: {r['iters']}")
        report.append("")
        report.append("Найденное решение:")
        report.append(f"  x = {r['x']:.12f}")
        report.append(f"  y = {r['y']:.12f}")
        report.append("")
        report.append("Невязки:")
        report.append(f"  f1(x,y) = {r['f1']:.2e}")
        report.append(f"  f2(x,y) = {r['f2']:.2e}")
        report.append(f"  Макс. невязка = {r['residual']:.2e}")
        report.append("")
        report.append("Погрешности на последнем шаге:")
        report.append(f"  |dx| = {r['err_x']:.2e}")
        report.append(f"  |dy| = {r['err_y']:.2e}")
        report.append("")
        report.append("-" * 60)
        report.append("ПРОВЕРКА РЕШЕНИЯ")
        report.append("-" * 60)
        report.append(f"Допустимая невязка (threshold): {r['threshold']:.2e}")
        report.append(f"Фактическая невязка (residual): {r['residual']:.2e}")
        report.append(f"Результат: {'✅ Решение корректно' if r['is_valid'] else '❌ Решение может быть некорректно'}")
        report.append("")
        report.append("=" * 60)

        report_text.insert("1.0", "\n".join(report))
        report_text.config(state="disabled")  # Только для чтения

        # Кнопки внизу
        btn_frame = ttk.Frame(self.report_window)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="📊 Показать таблицу итераций",
                   command=lambda: self.show_iteration_table(r)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Закрыть",
                   command=self.report_window.destroy).pack(side="right", padx=5)

    def show_iteration_table(self, result):
        """Открывает окно с таблицей итераций"""
        table_window = Toplevel(self.parent)
        table_window.title("📊 Таблица итераций")
        table_window.geometry("600x400")

        columns = ("iter", "x", "y", "dx", "dy")
        tree = ttk.Treeview(table_window, columns=columns, show="headings", height=20)

        tree.heading("iter", text="№")
        tree.heading("x", text="x_k")
        tree.heading("y", text="y_k")
        tree.heading("dx", text="|dx|")
        tree.heading("dy", text="|dy|")

        tree.column("iter", width=50, anchor="center")
        tree.column("x", width=120, anchor="e")
        tree.column("y", width=120, anchor="e")
        tree.column("dx", width=120, anchor="e")
        tree.column("dy", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(table_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for row in result["history"]:
            tree.insert("", "end", values=(
                row["iter"],
                f"{row['x']:.10f}",
                f"{row['y']:.10f}",
                f"{row['dx']:.2e}",
                f"{row['dy']:.2e}"
            ))

    def update_plot(self, f1, f2, root_x, root_y, converged):
        self.ax.clear()

        if not self.iteration_history:
            self.canvas.draw()
            return

        hist_x = [p["x"] for p in self.iteration_history]
        hist_y = [p["y"] for p in self.iteration_history]

        # Авто-масштаб с запасом
        min_x, max_x = min(hist_x), max(hist_x)
        min_y, max_y = min(hist_y), max(hist_y)
        pad_x = max((max_x - min_x) * 2.0, 1)
        pad_y = max((max_y - min_y) * 2.0, 1)

        # Сетка для контуров
        x_vals = np.linspace(min_x - pad_x, max_x + pad_x, 400)
        y_vals = np.linspace(min_y - pad_y, max_y + pad_y, 400)
        X, Y = np.meshgrid(x_vals, y_vals)

        Z1 = np.vectorize(f1)(X, Y)
        Z2 = np.vectorize(f2)(X, Y)

        # Линии функций
        self.ax.contour(X, Y, Z1, levels=[0], colors='blue', linewidths=2.5,
                        linestyles='solid', label='f1(x,y)=0')
        self.ax.contour(X, Y, Z2, levels=[0], colors='red', linewidths=2.5,
                        linestyles='dashed', label='f2(x,y)=0')

        # Путь итераций
        line_color = 'green' if converged else 'magenta'
        self.ax.plot(hist_x, hist_y, f'{line_color[0]}o-', linewidth=2, markersize=5,
                     label='Путь итераций', alpha=0.8, zorder=10)
        self.ax.plot(hist_x[0], hist_y[0], 'yx', markersize=12, markeredgewidth=2, label='Старт')
        self.ax.plot(root_x, root_y, 'ko', markersize=12, label='Решение', zorder=20)

        # Оформление
        self.ax.set_xlabel('x', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('y', fontsize=12, fontweight='bold')
        self.ax.set_title('График сходимости и линии функций', fontsize=14, fontweight='bold')
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
                f.write(f"Параметры: x0={r['x0']}, y0={r['y0']}, ε={r['eps']}\n\n")
                f.write(f"Результат: x={r['x']:.12f}, y={r['y']:.12f}\n")
                f.write(f"Невязки: f1={r['f1']:.2e}, f2={r['f2']:.2e}\n")
                f.write(f"Проверка: {'✅ OK' if r['is_valid'] else '❌ Ошибка'}\n")
                f.write(f"Итераций: {r['iters']}\n")
            messagebox.showinfo("Успех", f"Сохранено в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))