import datetime
import webbrowser
import os
import json
import random
import subprocess
from pathlib import Path

class AssistenteVirtual:
    def __init__(self, nome="Luna"):
        self.nome = nome
        self.tarefas = []
        self.contatos = {}
        self.notas = []
        self.historico = []
        self.personalidade = {
            "humor": "amigável",
            "formalidade": "casual",
            "emoji": True,
            "expressoes": [
                "Com certeza!", 
                "Entendido!", 
                "Feito!", 
                "Pode deixar comigo!", 
                "Às suas ordens!",
                "Sem problemas!",
                "Vamos lá!"
            ],
            "humor_respostas": [
                "Estou aqui para ajudar e tornar seu dia mais produtivo! 😊",
                "Espero que esteja tendo um ótimo dia!",
                "Sempre animada para ajudar você!",
                "O que seria da tecnologia sem um toque de diversão? 😉",
                "Preparada para qualquer desafio hoje!"
            ]
        }
        self.carregar_dados()
        print(f"{self.nome} iniciada. Como posso ajudar hoje?")
        
    def resposta_personalizada(self, mensagem):
        """Adiciona um toque de personalidade às respostas."""
        # Adiciona expressões características aleatórias
        if random.random() < 0.3:  # 30% de chance de adicionar uma expressão
            prefixo = random.choice(self.personalidade["expressoes"])
            mensagem = f"{prefixo} {mensagem}"
            
        # Adiciona emojis se estiver ativado
        if self.personalidade["emoji"] and random.random() < 0.4:  # 40% de chance
            emojis = ["✨", "👍", "🚀", "😊", "👌", "⭐", "💡", "🔍", "📝", "⏰", "📅", "💼"]
            mensagem += f" {random.choice(emojis)}"
            
        return mensagem
    
    def carregar_dados(self):
        """Carrega dados salvos de sessões anteriores."""
        diretorio_dados = Path.home() / "assistente_dados"
        
        # Cria diretório de dados se não existir
        if not diretorio_dados.exists():
            diretorio_dados.mkdir(exist_ok=True)
            return
            
        # Carrega tarefas
        arquivo_tarefas = diretorio_dados / "tarefas.json"
        if arquivo_tarefas.exists():
            try:
                with open(arquivo_tarefas, 'r', encoding='utf-8') as f:
                    self.tarefas = json.load(f)
            except:
                self.tarefas = []
                
        # Carrega contatos
        arquivo_contatos = diretorio_dados / "contatos.json"
        if arquivo_contatos.exists():
            try:
                with open(arquivo_contatos, 'r', encoding='utf-8') as f:
                    self.contatos = json.load(f)
            except:
                self.contatos = {}
                
        # Carrega notas
        arquivo_notas = diretorio_dados / "notas.json"
        if arquivo_notas.exists():
            try:
                with open(arquivo_notas, 'r', encoding='utf-8') as f:
                    self.notas = json.load(f)
            except:
                self.notas = []
    
    def salvar_dados(self):
        """Salva dados para sessões futuras."""
        diretorio_dados = Path.home() / "assistente_dados"
        diretorio_dados.mkdir(exist_ok=True)
        
        # Salva tarefas
        with open(diretorio_dados / "tarefas.json", 'w', encoding='utf-8') as f:
            json.dump(self.tarefas, f, ensure_ascii=False, indent=2)
            
        # Salva contatos
        with open(diretorio_dados / "contatos.json", 'w', encoding='utf-8') as f:
            json.dump(self.contatos, f, ensure_ascii=False, indent=2)
            
        # Salva notas
        with open(diretorio_dados / "notas.json", 'w', encoding='utf-8') as f:
            json.dump(self.notas, f, ensure_ascii=False, indent=2)
    
    def processar_comando(self, texto):
        """Processa o comando do usuário e retorna uma resposta."""
        texto = texto.lower()
        self.historico.append(texto)
        
        # Comandos sobre o assistente e personalidade
        if any(palavra in texto for palavra in ["quem é você", "seu nome", "se apresente"]):
            return self.resposta_personalizada(f"Eu sou {self.nome}, sua assistente virtual pessoal! Estou aqui para ajudar com suas tarefas, lembretes, pesquisas e muito mais.")
            
        # Comandos de saudação
        elif any(palavra in texto for palavra in ["olá", "oi", "bom dia", "boa tarde", "boa noite"]):
            return self.resposta_personalizada(self.gerar_saudacao())
            
        # Comandos de humor/como está
        elif any(expressao in texto for expressao in ["como você está", "tudo bem", "como vai"]):
            return self.resposta_personalizada(random.choice(self.personalidade["humor_respostas"]))
            
        # Comandos de hora e data
        elif any(palavra in texto for palavra in ["horas", "hora", "data", "dia"]):
            return self.resposta_personalizada(self.obter_hora_data(texto))
            
        # Comandos para tarefas
        elif any(palavra in texto for palavra in ["tarefa", "lembrete", "compromisso"]):
            return self.resposta_personalizada(self.gerenciar_tarefas(texto))
            
        # Comandos para abrir sites ou aplicativos
        elif "abrir" in texto:
            return self.resposta_personalizada(self.abrir_site_ou_aplicativo(texto))
            
        # Comandos para pesquisa na web
        elif any(palavra in texto for palavra in ["pesquisar", "buscar", "procurar"]):
            return self.resposta_personalizada(self.pesquisar_web(texto))
            
        # Comandos para contatos
        elif any(palavra in texto for palavra in ["contato", "telefone", "email"]):
            return self.resposta_personalizada(self.gerenciar_contatos(texto))
            
        # Comandos para notas
        elif any(palavra in texto for palavra in ["nota", "anotar", "anotação"]):
            return self.resposta_personalizada(self.gerenciar_notas(texto))
            
        # Comandos de ajuda
        elif any(palavra in texto for palavra in ["ajuda", "help", "comandos"]):
            return self.mostrar_ajuda()
            
        # Comando de saída
        elif any(palavra in texto for palavra in ["sair", "encerrar", "fechar"]):
            self.salvar_dados()
            return self.resposta_personalizada("Até logo! Seus dados foram salvos.")
            
        # Comando não reconhecido
        else:
            return self.resposta_personalizada("Desculpe, não entendi esse comando. Digite 'ajuda' para ver os comandos disponíveis.")
    
    def gerar_saudacao(self):
        """Gera uma saudação adequada para o horário."""
        hora_atual = datetime.datetime.now().hour
        
        if 5 <= hora_atual < 12:
            periodo = "Bom dia"
        elif 12 <= hora_atual < 18:
            periodo = "Boa tarde"
        else:
            periodo = "Boa noite"
            
        respostas = [
            f"{periodo}! Em que posso ajudar você hoje?",
            f"{periodo}! Como posso ser útil para você hoje?",
            f"{periodo}! Estou pronta para ajudar no que precisar.",
            f"Olá! {periodo}. Estou aqui para facilitar o seu dia.",
            f"{periodo}! O que vamos fazer hoje?",
            f"Olá! {periodo}. Que bom ver você novamente!"
        ]
        
        return random.choice(respostas)
    
    def obter_hora_data(self, texto):
        """Retorna informações sobre hora e data."""
        agora = datetime.datetime.now()
        
        if "hora" in texto:
            return f"Agora são {agora.strftime('%H:%M')}."
        elif "data" in texto or "dia" in texto:
            return f"Hoje é {agora.strftime('%d/%m/%Y')}."
        else:
            return f"Hoje é {agora.strftime('%d/%m/%Y')} e são {agora.strftime('%H:%M')}."
    
    def gerenciar_tarefas(self, texto):
        """Gerencia a lista de tarefas."""
        # Adicionar tarefa
        if any(palavra in texto for palavra in ["adicionar", "nova", "criar"]):
            partes = texto.split("tarefa", 1)
            if len(partes) > 1 and partes[1].strip():
                descricao = partes[1].strip()
                self.tarefas.append({
                    "descricao": descricao,
                    "data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "concluida": False
                })
                self.salvar_dados()
                return f"Tarefa adicionada: {descricao}"
            else:
                return "Por favor, especifique a descrição da tarefa."
                
        # Listar tarefas
        elif any(palavra in texto for palavra in ["listar", "mostrar", "ver"]):
            if not self.tarefas:
                return "Você não tem tarefas pendentes."
                
            resposta = "Suas tarefas:\n"
            for i, tarefa in enumerate(self.tarefas):
                status = "✓" if tarefa["concluida"] else "□"
                resposta += f"{i+1}. [{status}] {tarefa['descricao']} ({tarefa['data']})\n"
            return resposta
            
        # Concluir tarefa
        elif any(palavra in texto for palavra in ["concluir", "completar", "finalizar"]):
            try:
                # Tenta extrair o número da tarefa
                for palavra in texto.split():
                    if palavra.isdigit():
                        indice = int(palavra) - 1
                        if 0 <= indice < len(self.tarefas):
                            self.tarefas[indice]["concluida"] = True
                            self.salvar_dados()
                            return f"Tarefa '{self.tarefas[indice]['descricao']}' marcada como concluída!"
                
                return "Por favor, especifique o número da tarefa a concluir."
            except:
                return "Não foi possível concluir a tarefa. Verifique o número informado."
                
        # Remover tarefa
        elif any(palavra in texto for palavra in ["remover", "deletar", "apagar"]):
            try:
                # Tenta extrair o número da tarefa
                for palavra in texto.split():
                    if palavra.isdigit():
                        indice = int(palavra) - 1
                        if 0 <= indice < len(self.tarefas):
                            tarefa_removida = self.tarefas.pop(indice)
                            self.salvar_dados()
                            return f"Tarefa '{tarefa_removida['descricao']}' removida!"
                
                return "Por favor, especifique o número da tarefa a remover."
            except:
                return "Não foi possível remover a tarefa. Verifique o número informado."
        else:
            return "Comando de tarefa não reconhecido. Tente 'adicionar tarefa', 'listar tarefas', 'concluir tarefa' ou 'remover tarefa'."
    
    def abrir_site_ou_aplicativo(self, texto):
        """Abre um site ou aplicativo."""
        # Sites comuns
        sites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "gmail": "https://mail.google.com",
            "github": "https://www.github.com",
            "linkedin": "https://www.linkedin.com",
            "whatsapp": "https://web.whatsapp.com"
        }
        
        # Verificar se é um site conhecido
        for site, url in sites.items():
            if site in texto:
                webbrowser.open(url)
                return f"Abrindo {site.capitalize()}..."
        
        # Verificar se é uma URL
        if "www." in texto or ".com" in texto or ".br" in texto:
            partes = texto.split("abrir", 1)
            if len(partes) > 1:
                url = partes[1].strip()
                # Adicionar https:// se não tiver
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                webbrowser.open(url)
                return f"Abrindo {url}..."
        
        # Tentar abrir um aplicativo
        try:
            app_name = texto.split("abrir", 1)[1].strip()
            # No Linux, usa-se o comando 'xdg-open' para abrir aplicativos
            subprocess.Popen(["xdg-open", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Tentando abrir {app_name}..."
        except:
            return "Não consegui identificar o que você quer abrir."
    
    def pesquisar_web(self, texto):
        """Realiza uma pesquisa na web."""
        termos = ""
        
        # Extrai os termos de pesquisa
        if "pesquisar" in texto:
            termos = texto.split("pesquisar", 1)[1].strip()
        elif "buscar" in texto:
            termos = texto.split("buscar", 1)[1].strip()
        elif "procurar" in texto:
            termos = texto.split("procurar", 1)[1].strip()
            
        if termos:
            url = f"https://www.google.com/search?q={termos.replace(' ', '+')}"
            webbrowser.open(url)
            return f"Pesquisando por '{termos}'..."
        else:
            return "Por favor, especifique o que deseja pesquisar."
    
    def gerenciar_contatos(self, texto):
        """Gerencia a lista de contatos."""
        # Adicionar contato
        if any(palavra in texto for palavra in ["adicionar", "novo", "criar", "salvar"]):
            partes = texto.split("contato", 1)
            if len(partes) > 1 and partes[1].strip():
                info = partes[1].strip()
                
                # Tenta extrair nome e número/email
                partes_info = info.split(":")
                if len(partes_info) >= 2:
                    nome = partes_info[0].strip()
                    dados = partes_info[1].strip()
                    
                    if nome and dados:
                        self.contatos[nome] = dados
                        self.salvar_dados()
                        return f"Contato adicionado: {nome} - {dados}"
                
                return "Formato para adicionar contato: 'adicionar contato Nome: telefone/email'"
            else:
                return "Por favor, especifique os dados do contato."
        
        # Buscar contato
        elif any(palavra in texto for palavra in ["buscar", "procurar", "encontrar"]):
            nome_busca = ""
            for palavra in texto.split():
                if palavra in self.contatos:
                    nome_busca = palavra
                    break
            
            if nome_busca:
                return f"Contato: {nome_busca} - {self.contatos[nome_busca]}"
            else:
                return "Contato não encontrado. Use 'listar contatos' para ver todos os contatos."
        
        # Listar contatos
        elif any(palavra in texto for palavra in ["listar", "mostrar", "ver"]):
            if not self.contatos:
                return "Você não tem contatos salvos."
                
            resposta = "Seus contatos:\n"
            for nome, dados in self.contatos.items():
                resposta += f"- {nome}: {dados}\n"
            return resposta
        
        # Remover contato
        elif any(palavra in texto for palavra in ["remover", "deletar", "apagar"]):
            nome_remover = ""
            for palavra in texto.split():
                if palavra in self.contatos:
                    nome_remover = palavra
                    break
            
            if nome_remover:
                dados = self.contatos.pop(nome_remover)
                self.salvar_dados()
                return f"Contato removido: {nome_remover} - {dados}"
            else:
                return "Contato não encontrado. Use 'listar contatos' para ver todos os contatos."
        
        else:
            return "Comando de contato não reconhecido. Tente 'adicionar contato', 'buscar contato', 'listar contatos' ou 'remover contato'."
    
    def gerenciar_notas(self, texto):
        """Gerencia notas e anotações."""
        # Adicionar nota
        if any(palavra in texto for palavra in ["adicionar", "nova", "criar", "salvar"]):
            partes = texto.split("nota", 1)
            if len(partes) > 1 and partes[1].strip():
                conteudo = partes[1].strip()
                self.notas.append({
                    "conteudo": conteudo,
                    "data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                self.salvar_dados()
                return f"Nota adicionada: {conteudo}"
            else:
                return "Por favor, especifique o conteúdo da nota."
        
        # Listar notas
        elif any(palavra in texto for palavra in ["listar", "mostrar", "ver"]):
            if not self.notas:
                return "Você não tem notas salvas."
                
            resposta = "Suas notas:\n"
            for i, nota in enumerate(self.notas):
                resposta += f"{i+1}. {nota['conteudo']} ({nota['data']})\n"
            return resposta
        
        # Remover nota
        elif any(palavra in texto for palavra in ["remover", "deletar", "apagar"]):
            try:
                # Tenta extrair o número da nota
                for palavra in texto.split():
                    if palavra.isdigit():
                        indice = int(palavra) - 1
                        if 0 <= indice < len(self.notas):
                            nota_removida = self.notas.pop(indice)
                            self.salvar_dados()
                            return f"Nota removida: {nota_removida['conteudo']}"
                
                return "Por favor, especifique o número da nota a remover."
            except:
                return "Não foi possível remover a nota. Verifique o número informado."
        
        else:
            return "Comando de nota não reconhecido. Tente 'adicionar nota', 'listar notas' ou 'remover nota'."
    
    def mostrar_ajuda(self):
        """Mostra a lista de comandos disponíveis."""
        ajuda = f"""
        🌟 Comandos disponíveis na {self.nome} 🌟
        
        -- Sobre Mim --
        * quem é você - Saiba mais sobre sua assistente
        * como você está - Conversar um pouco comigo
        
        -- Básicos --
        * olá, oi, bom dia, boa tarde, boa noite - Me cumprimentar
        * horas, hora - Obter a hora atual
        * data, dia - Obter a data atual
        * sair, encerrar, fechar - Encerrar a assistente
        
        -- Tarefas --
        * adicionar tarefa [descrição] - Adiciona uma nova tarefa
        * listar tarefas - Mostra todas as suas tarefas
        * concluir tarefa [número] - Marca uma tarefa como concluída
        * remover tarefa [número] - Remove uma tarefa
        
        -- Contatos --
        * adicionar contato [nome]: [telefone/email] - Adiciona um novo contato
        * buscar contato [nome] - Busca um contato pelo nome
        * listar contatos - Mostra todos os seus contatos
        * remover contato [nome] - Remove um contato
        
        -- Notas --
        * adicionar nota [conteúdo] - Adiciona uma nova nota
        * listar notas - Mostra todas as suas notas
        * remover nota [número] - Remove uma nota
        
        -- Web --
        * abrir [site/aplicativo] - Abre um site ou aplicativo
        * pesquisar [termos] - Realiza uma pesquisa no Google
        """
        return ajuda


def iniciar_assistente():
    """Inicia o assistente virtual com interface de linha de comando."""
    assistente = AssistenteVirtual("Luna")
    
    print("=" * 50)
    print("  Bem-vindo(a) à Luna - Sua Assistente Virtual Pessoal")
    print("  Digite 'ajuda' para ver os comandos disponíveis")
    print("  Digite 'quem é você' para conhecer a Luna")
    print("  Digite 'sair' para encerrar")
    print("=" * 50)
    
    while True:
        try:
            comando = input("\nO que deseja? > ")
            
            if comando.lower() in ["sair", "encerrar", "fechar"]:
                print(assistente.processar_comando(comando))
                break
                
            resposta = assistente.processar_comando(comando)
            print(resposta)
            
        except KeyboardInterrupt:
            print("\nEncerrando a Luna...")
            assistente.salvar_dados()
            break
        except Exception as e:
            print(f"Ops! Ocorreu um erro: {str(e)}")
            print("Não se preocupe, vamos tentar novamente!")


if __name__ == "__main__":
    iniciar_assistente()