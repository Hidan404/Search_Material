def ip_para_binario(ip):
    try:
        octetos = ip.split('.')
        binario = '.'.join(f'{int(octeto):08b}' for octeto in octetos)
        return binario
    except:
        return "Formato de IP inválido."

def binario_para_ip(binario):
    try:
        blocos = binario.split('.')
        ip = '.'.join(str(int(bloco, 2)) for bloco in blocos)
        return ip
    except:
        return "Formato binário inválido."

def decimal_para_hexadecimal(decimal):
    try:
        hexadecimal = hex(int(decimal))[2:]
        return hexadecimal.upper()
    except:
        return "Formato decimal inválido."
def numero_para_binario(numero):
    try:
        binario = bin(int(numero))[2:]
        return binario
    except:
        return "Formato inválido."    

def hexadecimal_para_binario(hexadecimal):
    try:
        decimal = int(hexadecimal, 16)
        binario = bin(decimal)[2:]
        return binario
    except:
        return "Formato hexadecimal inválido."  
# Menu

while True:
    print("Conversor IP ↔ Binário")
    print("1 - IP para Binário")
    print("2 - Binário para IP")
    print("3 - Decimal para Hexadecimal")
    print("4 - Decimal para Binário")
    print("5 - Hexadecimal para Binário")
    escolha = input("Escolha uma opção (1, 2, 3, 4 ou 5): ")

    if escolha == '1':
        ip = input("Digite o endereço IP (ex: 192.168.0.1): ")
        print("Binário:", ip_para_binario(ip))

    elif escolha == '2':
        binario = input("Digite o endereço binário (ex: 11000000.10101000.00000000.00000001): ")
        print("IP:", binario_para_ip(binario))

    elif escolha == '3':
        decimal = input("Digite um número decimal: ")
        print("Hexadecimal:", decimal_para_hexadecimal(decimal))
    elif escolha == '4':
        numero = input("Digite um número decimal: ")
        print("Binário:", numero_para_binario(numero))
    elif escolha == '5':
        hexadecimal = input("Digite um número hexadecimal: ")
        print("Binário:", hexadecimal_para_binario(hexadecimal))
    else:
        print("Opção inválida.")
    continuar = input("Deseja continuar? (s/n): ")
    if continuar.lower() != 's':
        break
