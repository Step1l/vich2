def secant_method(f,a:float,b:float,eps:float):
    x0 = (a+b)/2
    x1 = x0+eps
    max_iter = 100000
    for i in range(max_iter):
        x2 = x1-f(x1)*(x1-x0)/(f(x1)-f(x0))
        f2=f(x2)
        if abs(f2)<eps or abs(x1-x2)<eps:
            return x2,f2,i+1
        x0,x1=x1,x2
    raise RuntimeError("Метод не сошелся")