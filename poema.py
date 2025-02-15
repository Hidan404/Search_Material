import math

def poema(data_extenso, *args, **kwargs):
    texto = "\n".join(args)
    metadados = "\n".join(f"{chave}: {valor}" for chave, valor in kwargs.items())

    mensagem = f"\n📅 {data_extenso}\n\n{texto}\n\n{metadados}"

    print(mensagem)

poema("10 de setembro de 2021", "A vida é bela", "O sol brilha", autor="Desconhecido", ano=2021)



def criar_carro(marca, ano, modelo, /,placa, combustivel):
    print("\n\n")
    print(marca, ano, modelo, placa, combustivel)
    carro = f"Marca: {marca}\nAno: {ano}\nModelo: {modelo}\nPlaca: {placa}\nCombustível: {combustivel}"
    return carro

print(criar_carro("Fiat", 2021, "Uno", placa= "ABC-1234", combustivel="Gasolina")) 


salario = 1000
def salario_bonus( bonus):
    return salario + bonus

print(salario_bonus(500))

lista_numeros = [5,8,6,12,14,7]
pares = [x for x in lista_numeros if x % 2 == 0]
quadrado = [math.pow(x, 2) for x in lista_numeros]
print(pares, quadrado)



lista = [n**2 if n > 6 else n for n in range(10) if n % 2 == 0]
print(lista)