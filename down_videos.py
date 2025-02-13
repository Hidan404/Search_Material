import os
import re
import requests
import yt_dlp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Lista para evitar URLs repetidas na busca recursiva
urls_verificadas = set()

def criar_pasta(nome_pasta="videos"):
    """Cria uma pasta para armazenar os vídeos baixados."""
    if not os.path.exists(nome_pasta):
        os.makedirs(nome_pasta)
    return nome_pasta

def encontrar_videos_recursivo(url, dominio_base, profundidade=2):
    """Busca vídeos recursivamente dentro da estrutura do site."""
    if profundidade == 0 or url in urls_verificadas:
        return set()

    urls_verificadas.add(url)
    print(f"[🔍] Varredura na página: {url}")

    try:
        resposta = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        resposta.raise_for_status()
        
        soup = BeautifulSoup(resposta.text, "html.parser")
        links_videos = set()
        links_para_seguir = set()

        # Encontra URLs de vídeos em <video>, <source> e <a>
        for tag in soup.find_all(["video", "source", "a"]):
            src = tag.get("src") or tag.get("href")
            if src:
                src_url = urljoin(url, src)
                
                # Verifica se é um vídeo
                if re.search(r'\.(mp4|mkv|avi|mov|webm|flv|wmv)$', src_url, re.IGNORECASE):
                    links_videos.add(src_url)
                
                # Verifica se é um link interno para explorar
                elif dominio_base in src_url and src_url not in urls_verificadas:
                    links_para_seguir.add(src_url)

        # Busca recursiva nos links encontrados
        for link in links_para_seguir:
            links_videos.update(encontrar_videos_recursivo(link, dominio_base, profundidade - 1))

        return links_videos

    except Exception as e:
        print(f"[⚠] Erro ao acessar {url}: {e}")
        return set()

def baixar_video(url, pasta_destino="videos"):
    """Baixa e converte um vídeo para MP4."""
    criar_pasta(pasta_destino)

    opcoes = {
        "outtmpl": os.path.join(pasta_destino, "%(title)s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "postprocessors": [
            {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
        ],
        "quiet": False,
    }

    try:
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            ydl.download([url])
        print(f"[✔] Download concluído: {url}")
    except Exception as e:
        print(f"[❌] Erro ao baixar vídeo {url}: {e}")

if __name__ == "__main__":
    url = input("Digite a URL da página: ").strip()
    escolha = input("Deseja baixar [1] Apenas um vídeo ou [2] Todos os vídeos do site? (1/2): ").strip()

    if escolha == "1":
        video_url = input("Digite a URL do vídeo: ").strip()
        baixar_video(video_url)
    elif escolha == "2":
        dominio_base = urlparse(url).netloc
        print("[🔍] Iniciando varredura de vídeos na página...\n")
        
        videos_encontrados = encontrar_videos_recursivo(url, dominio_base, profundidade=2)

        if videos_encontrados:
            print(f"[✅] {len(videos_encontrados)} vídeos encontrados. Iniciando downloads...\n")
            for video in videos_encontrados:
                baixar_video(video)
        else:
            print("[❌] Nenhum vídeo encontrado.")
