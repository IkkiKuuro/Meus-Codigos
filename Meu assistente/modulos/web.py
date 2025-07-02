"""
Módulo de web para o Kuro - Funções relacionadas à internet
"""
import webbrowser
import requests
from bs4 import BeautifulSoup
import re

class NavegadorWeb:
    def __init__(self):
        self.sites_comuns = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "gmail": "https://mail.google.com",
            "github": "https://www.github.com",
            "linkedin": "https://www.linkedin.com",
            "whatsapp": "https://web.whatsapp.com",
            "instagram": "https://www.instagram.com",
            "amazon": "https://www.amazon.com.br",
            "netflix": "https://www.netflix.com",
            "wikipedia": "https://pt.wikipedia.org",
        }
    
    def abrir_site(self, texto):
        """Abre um site baseado no texto do usuário"""
        # Verifica se é um site conhecido
        for site, url in self.sites_comuns.items():
            if site in texto.lower():
                webbrowser.open(url)
                return f"Abrindo {site.capitalize()}..."
        
        # Verifica se é uma URL
        if "www." in texto or ".com" in texto or ".br" in texto:
            partes = texto.split("abrir", 1)
            if len(partes) > 1:
                url = partes[1].strip()
                # Adicionar https:// se não tiver
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                webbrowser.open(url)
                return f"Abrindo {url}..."
                
        return None
    
    def pesquisar_web(self, texto):
        """Realiza uma pesquisa na web"""
        termos = ""
        
        # Extrai os termos de pesquisa
        if "pesquisar" in texto.lower():
            termos = texto.lower().split("pesquisar", 1)[1].strip()
        elif "buscar" in texto.lower():
            termos = texto.lower().split("buscar", 1)[1].strip()
        elif "procurar" in texto.lower():
            termos = texto.lower().split("procurar", 1)[1].strip()
            
        if termos:
            url = f"https://www.google.com/search?q={termos.replace(' ', '+')}"
            webbrowser.open(url)
            return f"Pesquisando por '{termos}'..."
        else:
            return "Por favor, especifique o que deseja pesquisar."
            
    def obter_resumo_site(self, url):
        """Obtém um resumo do conteúdo principal de uma página web"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return f"Não foi possível acessar o site. Código de status: {response.status_code}"
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts e estilos
            for script in soup(["script", "style"]):
                script.extract()
                
            # Obtém texto da página
            texto = soup.get_text()
            
            # Limpa texto
            linhas = (linha.strip() for linha in texto.splitlines())
            chunks = (frase.strip() for linha in linhas for frase in linha.split("  "))
            texto = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limita a um resumo
            palavras = texto.split()
            if len(palavras) > 100:
                resumo = ' '.join(palavras[:100]) + "..."
            else:
                resumo = texto
                
            return resumo
            
        except Exception as e:
            return f"Erro ao acessar o site: {str(e)}"
