def get_noline_phi(a,b,df,f):
    xs = [a + (b - a) * i / 10 for i in range(11)]
    max_df = max([abs(df(x)) for x in xs])
    lambd = 1 / max_df
    if df(a) > 0:
        lambd = -lambd
    phi = lambda x: x + lambd * f(x)
    phi_der = lambda x: 1 + lambd * df(x)
    for x in xs:
        if abs(phi_der(x))>=1:
            raise ValueError(f"Условие сходимости не выполняется, {x,phi(x),lambd}")
    return phi

def check_interval(f, a, b):
    if a >= b:
        raise ValueError("a должно быть меньше b")
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        raise ValueError("Нет корня (функция не меняет знак на [a,b])")
    n = 100
    dx = (b - a) / n
    sign_changes = 0
    last_sign = fa > 0
    x=a
    for i in range(1, n + 1):
        x = x+dx
        try:
            current_sign = f(x) > 0
            if current_sign != last_sign:
                sign_changes += 1
                last_sign = current_sign
        except:
            pass
    if sign_changes > 1:
        raise ValueError("На интервале более одного корня!")
    if sign_changes == 0:
        raise ValueError("Корень не найден (табуляция)")

def check_convergence_approx(phi1, phi2, x0, y0):
    x, y = x0, y0
    h = 0.0000001
    try:
        dphi1dx = ((phi1( x + h, y)) - phi1(x, y)) / (h)
        dphi1dy = ((phi1( x , y+h)) - phi1(x, y)) / (h)
        dphi2dx = ((phi2( x + h, y)) - phi2(x, y)) / (h)
        dphi2dy = ((phi2( x, y+h)) - phi2(x, y)) / (h)
        return max(abs(dphi1dx) + abs(dphi1dy), abs(dphi2dx) + abs(dphi2dy))
    except:
        return float('inf')