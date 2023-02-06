# cargamos la plantilla
f = open("ex_snippet.html", "r")
data = f.read()

version = "80D" # ejemplo de variable extraida del .conf
data = data.replace("%var1%", str(version))
data = data.replace("%var2%", "suda el valor")

