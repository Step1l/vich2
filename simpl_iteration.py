def simple_iteration_method(f,df, a, b, eps):
    max_iter = 10000
    xs = [a + (b - a) * i / 10 for i in range(11)]
    max_df = max([abs(df(x)) for x in xs])
    lambd = 1/max_df
    phi_der = lambda x: 1 + lambd * df(x)
    if df(a)>0:
        lambd = -lambd
    phi = lambda x: x+lambd*f(x)
    for x in xs:
        if abs(phi_der(x))>=1:
            raise ValueError(f"Условие сходимости не выполняется, {x,phi(x),lambd}")
    x0 = (a+b)/2
    for i in range(max_iter):
        x1=phi(x0)
        if abs(x0-x1)<eps:
            return x1,f(x1),i+1
        x0=x1
    raise RuntimeError("Метод не сошелся")