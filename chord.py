def chord_method(f,a,b,eps):
    max_it = 100000
    for i in range(max_it):
        x = a-f(a)*(b-a)/(f(b)-f(a))
        fx=f(x)
        if abs(fx)< eps or abs(b-a)<eps:
            h=5
            return x,fx,i+1
        if f(a)*fx<0:
            b=x
        else:

            a=x
    raise RuntimeError("Метод не сошелся")