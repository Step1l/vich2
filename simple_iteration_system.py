def simple_iteration_system(phi1, phi2, x0, y0, eps=1e-6, max_iter=100):
    x, y = x0, y0
    for i in range(max_iter):
        x_new=phi1(x, y)
        y_new=phi2(x, y)
        dx=abs(x_new - x)
        dy = abs(y_new - y)
        if max(dx, dy) < eps:
            return x_new, y_new, dx, dy, i+1
        x, y = x_new, y_new
    raise RuntimeError("Метод не сошелся за максимальное число итераций")