import pandas as pd

data = pd.read_csv("reducteur/liste_vitesses.txt", delimiter=";")
wm, wr = data["wm"], data["wr"]

for i in range(len(wm)):
    print(f"{wm[i]};{wm[i]/18.8}")