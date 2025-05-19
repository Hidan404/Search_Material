import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


#Ronald 
def criar_pasta(nome_pasta="downloads"):
    if not os.path.exists(nome_pasta):
        os.makedirs(nome_pasta)
    return nome_pasta

def baixar_arquivo(url, pasta_destino):
    nome_arquivo = os.path.join(pasta_destino, url.split("/")[-1])
    try:
        resposta = requests.get(url, stream=True)
        if resposta.status_code == 200:
            with open(nome_arquivo, 'wb') as f:
                for chunk in resposta.iter_content(1024):
                    f.write(chunk)
            print(f"[✔] Baixado: {nome_arquivo}")
        else:
            print(f"[✖] Erro ao baixar: {url}")
    except Exception as e:
        print(f"[⚠] Falha ao baixar {url}: {e}")

def encontrar_midia(url, tipo):
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        soup = BeautifulSoup(resposta.text, "html.parser")
        
        if tipo == "imagens":
            extensoes = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
            tags = soup.find_all("img")
        else:
            extensoes = [".gif"]
            tags = soup.find_all("img") + soup.find_all("source")  # Algumas páginas colocam GIFs ,lembrar disso sempre

        urls_midia = []

        for tag in tags:
            src = tag.get("src") or tag.get("data-src") or tag.get("data-original")
            if src:
                src = urljoin(url, src)
                if any(src.lower().endswith(ext) for ext in extensoes):
                    urls_midia.append(src)

        return urls_midia

    except Exception as e:
        print(f"[⚠] Erro ao acessar {url}: {e}")
        return []

if __name__ == "__main__":
    url = input("Digite a URL da página: ").strip()
    tipo = input("Deseja baixar [1] Imagens ou [2] GIFs? (1/2): ").strip()

    tipo_escolhido = "imagens" if tipo == "1" else "gifs"
    pasta_destino = criar_pasta(tipo_escolhido)

    print(f"\n[🔍] Buscando {tipo_escolhido} em {url}...\n")
    midias_encontradas = encontrar_midia(url, tipo_escolhido)

    if midias_encontradas:
        print(f"[✅] {len(midias_encontradas)} arquivos encontrados. Iniciando download...\n")
        for midia_url in midias_encontradas:
            baixar_arquivo(midia_url, pasta_destino)
    else:
        print("[❌] Nenhuma mídia encontrada.")
