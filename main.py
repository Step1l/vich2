import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from Nonlinear import NonlinearApp
from syst import SystemApp


def main():
    root = tk.Tk()
    root.title("Численные методы")
    root.geometry("1000x800")

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Вкладка "Нелинейные уравнения"
    frame1 = ttk.Frame(notebook)
    notebook.add(frame1, text="Нелинейные уравнения")
    nonlinear_app = NonlinearApp(frame1)

    # Вкладка "Системы уравнений"
    frame2 = ttk.Frame(notebook)
    notebook.add(frame2, text="Системы уравнений")
    system_app = SystemApp(frame2)

    root.mainloop()

if __name__ == "__main__":
    main()