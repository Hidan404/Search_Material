# Lista para armazenar os produtos e preços
carrinho = []
total = 0.0

# Entrada do número de itens
n = int(input().strip())

# Loop para adicionar itens ao carrinho
for _ in range(n):
    linha = input().strip()
    print(linha)
    # Encontra a última ocorrência de espaço para separar nome e preço
    posicao_espaco = linha.rfind(" ")
    print(posicao_espaco)
    
    # Separa o nome do produto e o preço
    item = linha[:posicao_espaco]
    print(item)
    preco = float(linha[posicao_espaco + 1:])
    print(preco)

    # Adiciona ao carrinho
    carrinho.append((item, preco))
    total += preco

# TODO: Exiba os itens e o total da compra
for item, preco in carrinho:
    print(f"{item}: R${preco:.2f}")
print(f"Total: R${total:.2f}")    