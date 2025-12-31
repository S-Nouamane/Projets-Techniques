import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_csv("reducteur/liste_vitesses.txt", delimiter=";")
data = pd.DataFrame(data)
wm = data["wm"]
wr = data["wr"]

a, b = np.polyfit(wm, wr, 1)
plt.scatter(wm, wr)
plt.ylabel("w_reducteur")
plt.xlabel("w_moteur")
plt.plot(wm, a*wm+b, color="red")
plt.title(f"R = {1/a}")
plt.show()
print(a)
