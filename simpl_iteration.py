def simple_iteration_method(f, a, b, eps,phi):
    max_iter = 10000
    x0 = (a+b)/2
    for i in range(max_iter):
        x1=phi(x0)
        if abs(x0-x1)<eps:
            return x1,f(x1),i+1
        x0=x1
    raise RuntimeError("Метод не сошелся")