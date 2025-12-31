import pandas as pd
import numpy as np
data = pd.read_csv("ressources/acquisition12v.txt", delimiter=";")

t = data["t"]
w = data["w(t)"]


for i in range(len(w)):
    print(f"{round(t[i]*1e-6, 3)};{w[i]}")