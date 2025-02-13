import os
import re
import sqlite3
import threading
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin
from duckduckgo_search import ddg


# Configuração do banco de dados SQLite
DB_FILE = "arquivos_expostos.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS arquivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        status TEXT
    )
""")
conn.commit()

# Configuração do diretório de downloads
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Lista de extensões de arquivos para busca
EXTENSOES = ["pdf", "txt", "sql", "db", "bak"]

# Lock para evitar conflitos em multithreading
lock = threading.Lock()

# Headers aleatórios para evitar bloqueios
HEADERS_LIST = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"},
]

def buscar_no_duckduckgo(dork, num_results=10):
    """Realiza a busca utilizando DuckDuckGo para evitar bloqueios do Google."""
    try:
        resultados = ddg(dork, max_results=num_results)
        return [res["href"] for res in resultados if res["href"].startswith("http")]
    except Exception as e:
        print(f"[❌] Erro ao buscar no DuckDuckGo: {e}")
        return []

def baixar_arquivo(url):
    """Baixa arquivos encontrados e salva no banco de dados."""
    headers = HEADERS_LIST[0]  # Usa um dos headers para evitar bloqueios

    try:
        resposta = requests.get(url, headers=headers, stream=True, timeout=10)
        resposta.raise_for_status()

        nome_arquivo = os.path.join(DOWNLOAD_DIR, url.split("/")[-1])
        
        with open(nome_arquivo, "wb") as f:
            for chunk in resposta.iter_content(1024):
                f.write(chunk)

        with lock:
            cursor.execute("INSERT OR IGNORE INTO arquivos (url, status) VALUES (?, ?)", (url, "baixado"))
            conn.commit()
            print(f"[✔] Download concluído: {nome_arquivo}")

    except Exception as e:
        with lock:
            print(f"[❌] Erro ao baixar {url}: {e}")

def buscar_e_baixar(dork, num_results=10):
    """Busca arquivos na internet e baixa os encontrados."""
    print(f"[🔍] Buscando: {dork}")

    urls_encontradas = buscar_no_duckduckgo(dork, num_results)
    
    if not urls_encontradas:
        print(f"[❌] Nenhum resultado encontrado para {dork}.")
        return

    print(f"[✅] {len(urls_encontradas)} arquivos encontrados. Iniciando downloads...")

    threads = []
    for url in urls_encontradas:
        t = threading.Thread(target=baixar_arquivo, args=(url,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def gerar_dorks():
    """Gera dorks para encontrar arquivos expostos."""
    dorks = [
        f'intitle:"index of" ext:{ext}' for ext in EXTENSOES
    ] + [
        f'site:pastebin.com "password"',
        f'site:github.com "db_password"',
        f'site:drive.google.com ext:sql',
        f'intext:"mysql dump" filetype:sql',
        f'intext:"backup database" filetype:bak',
        f'intext:"password" ext:txt',
    ]
    return dorks

if __name__ == "__main__":
    print("\n[🚀] Iniciando busca de arquivos expostos...\n")
    
    dorks = gerar_dorks()
    num_resultados = 15  # Número de resultados por dork

    threads = []
    for dork in dorks:
        t = threading.Thread(target=buscar_e_baixar, args=(dork, num_resultados))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n[✅] Busca concluída. Todos os arquivos foram armazenados na pasta 'downloads'.")
