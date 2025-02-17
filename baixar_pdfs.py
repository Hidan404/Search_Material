import os
import re
import requests
import PyPDF2
from io import BytesIO
from googlesearch import search
from urllib.parse import urljoin
from tqdm import tqdm

# Diretório para salvar PDFs
PASTA_DOWNLOADS = "livros_pdf"
os.makedirs(PASTA_DOWNLOADS, exist_ok=True)

# Sites confiáveis para buscar PDFs
SITES_BUSCA = [
    "site:scholar.google.com",
    "site:pdfdrive.com",
    "site:academia.edu",
    "site:archive.org",
    "site:bdtd.ibict.br",
    "site:repositorio.unicamp.br",
    "site:repositorio.ufrj.br",
    "site:bibliotecadigital.ufmg.br",
    "site:bndigital.bn.br",
    "site:booksc.org",
    "site:scielo.org",
    "site:libgen.rs",
    "site:edisciplinas.usp.br",
    "site:docplayer.com.br",
    "site:slideshare.net",
    "site:gutenberg.org",
    "site:openlibrary.org",
    "site:manybooks.net",
    "site:repositorio.unb.br"
]

def buscar_links_google(termo):
    """Realiza uma busca no Google para encontrar links de PDFs."""
    links_encontrados = []
    consulta = f"{termo} filetype:pdf " + " OR ".join(SITES_BUSCA)

    print(f"🔍 Buscando: {termo}")
    try:
        for resultado in search(consulta, num_results=15):  # Busca mais resultados
            links_encontrados.append(resultado)
    except Exception as e:
        print(f"❌ Erro ao buscar no Google: {e}")

    return links_encontrados

def verificar_pdf(url):
    """Verifica se o link é um PDF válido e lê o título."""
    try:
        resposta = requests.get(url, timeout=10, stream=True)
        content_type = resposta.headers.get("Content-Type", "")

        if "application/pdf" not in content_type:
            return False, None

        # Lê o conteúdo do PDF para verificar se é o livro correto
        pdf_reader = PyPDF2.PdfReader(BytesIO(resposta.content))
        if pdf_reader.pages:
            primeiro_texto = pdf_reader.pages[0].extract_text()
        else:
            primeiro_texto = ""

        return True, primeiro_texto.strip()

    except requests.RequestException:
        return False, None
    except Exception:
        return False, None

def baixar_pdf(url, nome_arquivo):
    """Faz o download de um arquivo PDF."""
    try:
        resposta = requests.get(url, stream=True, timeout=15)
        tamanho_total = int(resposta.headers.get("content-length", 0))

        caminho_arquivo = os.path.join(PASTA_DOWNLOADS, nome_arquivo)
        with open(caminho_arquivo, "wb") as arquivo, tqdm(
            desc=nome_arquivo, total=tamanho_total, unit="B", unit_scale=True, unit_divisor=1024
        ) as barra_progresso:
            for chunk in resposta.iter_content(chunk_size=1024):
                arquivo.write(chunk)
                barra_progresso.update(len(chunk))

        print(f"✅ Download concluído: {caminho_arquivo}")
    except Exception as e:
        print(f"❌ Erro ao baixar {url}: {e}")

def buscar_e_baixar_livro(livro):
    """Busca e baixa o livro correto verificando o título do PDF."""
    termo_busca = f"{livro} pdf em português"
    links = buscar_links_google(termo_busca)

    if not links:
        print("❌ Nenhum link encontrado.")
        return

    for link in links:
        valido, texto_pdf = verificar_pdf(link)
        
        if valido:
            # Confere se o título do PDF contém o nome do livro
            if livro.lower() in texto_pdf.lower():
                nome_arquivo = re.sub(r'\W+', '_', livro) + ".pdf"
                baixar_pdf(link, nome_arquivo)
                return  # Sai do loop após encontrar o PDF correto

    print("❌ Nenhum PDF correspondente foi encontrado.")

if __name__ == "__main__":
    print("📚 Buscador de Livros PDF")
    livro_desejado = input("Digite o nome do livro que deseja baixar: ")
    buscar_e_baixar_livro(livro_desejado)
    print("🎯 Processo finalizado!")
