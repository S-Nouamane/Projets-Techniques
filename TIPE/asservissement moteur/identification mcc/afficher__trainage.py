import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = pd.read_csv("trainage/acquisition.txt", delimiter=";")
t, w, pwm = data["t"], data["w(t)"], data["pwm"]
t *= 1e-6

val = 10
a, b = np.polyfit(t[-val:], w[-val:], 1)
taux = -b/a
print(taux)
def f(x):
    return a*x + b

plt.plot(t, w, 'o', label="w(t)")
plt.plot(t, f(t))
plt.plot(t, pwm, label="pwm")
plt.title(f"\N{greek small letter tau} $=$ {round(taux, 3)}s")

plt.legend()
plt.grid()
plt.show()
