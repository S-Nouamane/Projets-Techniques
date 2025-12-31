import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv("ressources/liste U(w).txt", delimiter=";")
x, y = np.array(data['w']), np.array(data["U"])
[a, b] = np.polyfit(x, y, 1)
def fct(x):
    return a*x + b
R = 9.3 # Par multimètre
Cm = b*a/R
print(f"a = K = {a} V.s/rad, Cm = b.K/R = {Cm} N.m")

x2 = np.linspace(min(x), max(x), 2)

plt.plot(x, y, 'o', label="acquisition U(w)")
plt.plot(x2, fct(x2), label="polyfit")
plt.title(f"$K$=a={round(a, 2)} V.s/rad, $C_m$=b.K/R={round(Cm, 3)} N.m")
plt.legend()
plt.grid()
plt.show()

