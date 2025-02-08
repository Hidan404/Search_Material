import os
import re
import yaml
import requests
import argparse
from pathlib import Path
from PyPDF2 import PdfReader
from googlesearch import search
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import nltk
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from gensim import corpora, models
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime

nltk.download('stopwords')
nltk.download('punkt')

class AdvancedKnowledgeAggregator:
    def __init__(self, subject):
        self.subject = subject
        self.base_dir = Path("knowledge_books") / subject.replace(" ", "_")
        self.raw_pdfs = self.base_dir / "raw_pdfs"
        self.processed_texts = []
        self.metadata = []
        self.structure = {}
        self.quality_scores = {}
        
        self._setup_directories()
        self._load_config()

    def _setup_directories(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.raw_pdfs.mkdir(exist_ok=True)

    def _load_config(self):
        config_path = Path("config.yaml")
        if config_path.exists():
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                'structure': {
                    'Introdução': ['Histórico', 'Conceitos Básicos'],
                    'Desenvolvimento': ['Técnicas', 'Aplicações'],
                    'Conclusão': ['Resumo', 'Próximos Passos']
                },
                'apis': {
                    'crossref': {'enable': True, 'max_results': 5},
                    'arxiv': {'enable': False}
                }
            }

    def search_content(self, num_files=15):
        """Busca conteúdo em múltiplas fontes"""
        self._search_web_pdfs(num_files)
        if self.config['apis']['crossref']['enable']:
            self._search_academic_papers()

    def _search_web_pdfs(self, num_files):
        query = f"{self.subject} filetype:pdf"
        try:
            results = search(
                query,
                num_results=num_files,
                lang='pt' if 'brasil' in self.subject.lower() else 'en',
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            )
            
            for url in results:
                if url.endswith('.pdf'):
                    self._download_pdf(url)

        except Exception as e:
            print(f"Erro na pesquisa web: {e}")

    def _search_academic_papers(self):
        """Integração com API CrossRef para artigos acadêmicos"""
        url = "https://api.crossref.org/works"
        params = {
            'query': self.subject,
            'filter': 'type:journal-article',
            'rows': self.config['apis']['crossref']['max_results']
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                for item in response.json()['message']['items']:
                    if 'link' in item and item['link'][0]['content-type'] == 'application/pdf':
                        self._download_pdf(item['link'][0]['URL'])
                        self.metadata.append({
                            'title': item.get('title', [''])[0],
                            'authors': [author['given'] + ' ' + author['family'] for author in item.get('author', [])],
                            'doi': item.get('DOI', ''),
                            'year': item.get('created', {}).get('date-parts', [[2000]])[0][0]
                        })
        except Exception as e:
            print(f"Erro na API CrossRef: {e}")

    def _download_pdf(self, url):
        """Sistema de download com verificação de qualidade"""
        try:
            filename = url.split('/')[-1][:100] + ".pdf"
            filepath = self.raw_pdfs / filename
            
            if filepath.exists():
                return

            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                
                self._assess_quality(filepath)
                print(f"✅ Baixado: {filename} [Score: {self.quality_scores.get(filename, 0):.1f}]")

        except Exception as e:
            print(f"Erro ao baixar {url}: {e}")

    def _assess_quality(self, filepath):
        """Avaliação de qualidade do PDF"""
        try:
            with open(filepath, 'rb') as f:
                reader = PdfReader(f)
                text = " ".join(page.extract_text() or '' for page in reader.pages[:5])
                
                # Critérios de qualidade
                length_score = min(len(text)/1000, 5)
                keyword_score = sum(1 for w in ['introduction', 'method', 'conclusion'] if w in text.lower())
                self.quality_scores[filepath.name] = length_score + keyword_score

        except Exception as e:
            print(f"Erro na avaliação de qualidade: {e}")
            self.quality_scores[filepath.name] = 0

    def process_content(self):
        """Processamento avançado com limpeza e análise"""
        for pdf_file in sorted(self.raw_pdfs.glob("*.pdf"), 
                             key=lambda x: self.quality_scores.get(x.name, 0), 
                             reverse=True):
            try:
                reader = PdfReader(pdf_file)
                text = " ".join(page.extract_text() or '' for page in reader.pages)
                clean_text = self._clean_text(text)
                
                if len(clean_text) > 500:  # Ignorar PDFs sem texto útil
                    self.processed_texts.append(clean_text)

            except Exception as e:
                print(f"Erro ao processar {pdf_file.name}: {e}")

        if self.processed_texts:
            self._analyze_topics()
            self._generate_index()

    def _clean_text(self, text):
        """Limpeza avançada do texto"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)  # Remover repetições
        return text.lower()

    def _analyze_topics(self):
        """Análise semântica com LDA"""
        texts = [text.split() for text in self.processed_texts]
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        
        lda_model = models.LdaModel(
            corpus,
            num_topics=5,
            id2word=dictionary,
            passes=15,
            alpha='auto'
        )
        
        self.structure = {}
        for idx, topic in lda_model.print_topics(-1):
            top_terms = re.findall(r'"(\w+)"', topic)[:3]
            self.structure[f"Capítulo {idx+1}: {' '.join(top_terms)}"] = []

    def _generate_index(self):
        """Geração de índice remissivo"""
        all_text = ' '.join(self.processed_texts)
        words = nltk.word_tokenize(all_text)
        stop_words = set(stopwords.words('english'))
        filtered_words = [w for w in words if w not in stop_words and len(w) > 4 and w.isalpha()]
        
        self.index = FreqDist(filtered_words).most_common(50)

    def generate_book(self):
        """Geração do PDF com estrutura profissional"""
        output_file = self.base_dir / f"{self.subject}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        styles = self._create_styles()
        story = []
        
        # Capa
        story += self._create_cover(styles)
        
        # Metadados
        story += self._create_metadata_table(styles)
        
        # Sumário
        story += self._create_toc(styles)
        
        # Conteúdo principal
        story += self._create_main_content(styles)
        
        # Índice Remissivo
        story += self._create_index(styles)
        
        doc.build(story)
        print(f"\n📕 Livro gerado com sucesso em: {output_file}")

    def _create_styles(self):
        """Configuração de estilos avançados"""
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='ChapterTitle',
            fontSize=16,
            leading=18,
            spaceAfter=20,
            textColor=colors.darkblue
        ))
        return styles

    def _create_cover(self, styles):
        """Criação da capa profissional"""
        elements = []
        elements.append(Paragraph(f"<b>{self.subject.upper()}</b>", styles['Title']))
        elements.append(Paragraph("<br/><br/>Relatório Gerado Automaticamente<br/>por Knowledge Aggregator 2.0", styles['Italic']))
        elements.append(PageBreak())
        return elements

    def _create_metadata_table(self, styles):
        """Tabela de metadados dos artigos"""
        data = [['Título', 'Autores', 'Ano', 'DOI']]
        for meta in self.metadata:
            data.append([
                meta['title'][:50],
                ', '.join(meta['authors'][:3]),
                str(meta['year']),
                meta['doi'][:20]
            ])
        
        table = Table(data, colWidths=[120, 120, 50, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 8)
        ]))
        
        return [Paragraph("<b>Fontes Acadêmicas Utilizadas</b>", styles['Heading2']), table, PageBreak()]

    def _create_toc(self, styles):
        """Sumário automático com numeração"""
        elements = []
        elements.append(Paragraph("Sumário", styles['Heading1']))
        
        for chapter in self.structure:
            elements.append(Paragraph(f"• {chapter}", styles['Normal']))
        
        elements.append(PageBreak())
        return elements

    def _create_main_content(self, styles):
        """Conteúdo estruturado com análise semântica"""
        elements = []
        vectorizer = TfidfVectorizer(max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(self.processed_texts)
        
        for chapter in self.structure:
            elements.append(Paragraph(chapter, styles['ChapterTitle']))
            
            # Selecionar conteúdo mais relevante
            chapter_keywords = chapter.lower().split()[1:]
            relevant_content = max(
                self.processed_texts,
                key=lambda x: sum(1 for kw in chapter_keywords if kw in x)
            )
            
            elements.append(Paragraph(relevant_content[:1500] + "...", styles['Normal']))
            elements.append(PageBreak())
        
        return elements

    def _create_index(self, styles):
        """Índice remissivo profissional"""
        elements = []
        elements.append(Paragraph("Índice Remissivo", styles['Heading1']))
        
        index_items = []
        for term, freq in self.index:
            index_items.append(f"{term} ({freq})")
        
        columns = 3
        table_data = []
        for i in range(0, len(index_items), columns):
            table_data.append(index_items[i:i+columns])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTSIZE', (0,0), (-1,-1), 9)
        ]))
        
        return [table]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Knowledge Aggregator")
    parser.add_argument("subject", type=str, help="Assunto principal do livro")
    parser.add_argument("-n", "--num-pdfs", type=int, default=10, help="Número de PDFs para baixar")
    parser.add_argument("-q", "--quality", type=float, default=3.0, help="Limite mínimo de qualidade (0-5)")
    
    args = parser.parse_args()
    
    print(f"🚀 Iniciando agregação de conhecimento sobre: {args.subject}")
    aggregator = AdvancedKnowledgeAggregator(args.subject)
    
    print("\n🔍 Buscando conteúdo relevante...")
    aggregator.search_content(args.num_pdfs)
    
    print("\n🧠 Processando e analisando conteúdo...")
    aggregator.process_content()
    
    if aggregator.processed_texts:
        print("\n📚 Gerando livro estruturado...")
        aggregator.generate_book()
    else:
        print("❌ Nenhum conteúdo válido encontrado para geração do livro.")