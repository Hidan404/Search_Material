import re

# Entrada do usuário
email = input().strip()

# TODO: Verifique as regras do e-mail:

def validar_mail(email):

    padrao = r"^[\w\.-]+@[\w\.-]+\.com$"
    return re.match(padrao, email) is not None

'''if validar_mail(email):
    print("E-mail válido.")
else:
    print("E-mail inválido.")'''


matriz = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

print(matriz[0][2])
print(matriz[1][1])

lista_completa = [1, 2, 3, 4, 5, 6, 7, 8, 9]
list_parcial = [n for n in lista_completa if n % 2 == 0]
print(list_parcial)

lista_completa = lista_completa.extend(list_parcial)
print(lista_completa)