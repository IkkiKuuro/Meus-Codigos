"""
Módulo de gerenciamento de tarefas, contatos e notas para o Kuro
"""
import json
import datetime
from pathlib import Path

class GerenciadorDados:
    def __init__(self, diretorio_base):
        self.diretorio_dados = Path(diretorio_base) / "dados"
        self.arquivo_tarefas = self.diretorio_dados / "tarefas.json"
        self.arquivo_contatos = self.diretorio_dados / "contatos.json"
        self.arquivo_notas = self.diretorio_dados / "notas.json"
        
        self.tarefas = []
        self.contatos = {}
        self.notas = []
        
        self.carregar_dados()
        
    def carregar_dados(self):
        """Carrega todos os dados salvos de sessões anteriores"""
        if not self.diretorio_dados.exists():
            self.diretorio_dados.mkdir(exist_ok=True)
            
        # Carrega tarefas
        if self.arquivo_tarefas.exists():
            try:
                with open(self.arquivo_tarefas, 'r', encoding='utf-8') as f:
                    self.tarefas = json.load(f)
            except:
                self.tarefas = []
                
        # Carrega contatos
        if self.arquivo_contatos.exists():
            try:
                with open(self.arquivo_contatos, 'r', encoding='utf-8') as f:
                    self.contatos = json.load(f)
            except:
                self.contatos = {}
                
        # Carrega notas
        if self.arquivo_notas.exists():
            try:
                with open(self.arquivo_notas, 'r', encoding='utf-8') as f:
                    self.notas = json.load(f)
            except:
                self.notas = []
                
    def salvar_dados(self):
        """Salva todos os dados para uso em sessões futuras"""
        self.diretorio_dados.mkdir(exist_ok=True)
        
        # Salva tarefas
        with open(self.arquivo_tarefas, 'w', encoding='utf-8') as f:
            json.dump(self.tarefas, f, ensure_ascii=False, indent=2)
            
        # Salva contatos
        with open(self.arquivo_contatos, 'w', encoding='utf-8') as f:
            json.dump(self.contatos, f, ensure_ascii=False, indent=2)
            
        # Salva notas
        with open(self.arquivo_notas, 'w', encoding='utf-8') as f:
            json.dump(self.notas, f, ensure_ascii=False, indent=2)
            
    def gerenciar_tarefas(self, texto):
        """Gerencia a lista de tarefas"""
        # Adicionar tarefa
        if any(palavra in texto.lower() for palavra in ["adicionar", "nova", "criar"]):
            partes = texto.lower().split("tarefa", 1)
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
        elif any(palavra in texto.lower() for palavra in ["listar", "mostrar", "ver"]):
            if not self.tarefas:
                return "Você não tem tarefas pendentes."
                
            resposta = "Suas tarefas:\n"
            for i, tarefa in enumerate(self.tarefas):
                status = "✓" if tarefa["concluida"] else "□"
                resposta += f"{i+1}. [{status}] {tarefa['descricao']} ({tarefa['data']})\n"
            return resposta
            
        # Concluir tarefa
        elif any(palavra in texto.lower() for palavra in ["concluir", "completar", "finalizar"]):
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
        elif any(palavra in texto.lower() for palavra in ["remover", "deletar", "apagar"]):
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
            
    def gerenciar_contatos(self, texto):
        """Gerencia a lista de contatos"""
        # Adicionar contato
        if any(palavra in texto.lower() for palavra in ["adicionar", "novo", "criar", "salvar"]):
            partes = texto.lower().split("contato", 1)
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
        elif any(palavra in texto.lower() for palavra in ["buscar", "procurar", "encontrar"]):
            nome_busca = ""
            for palavra in texto.split():
                if palavra.lower() in self.contatos:
                    nome_busca = palavra.lower()
                    break
            
            if nome_busca:
                return f"Contato: {nome_busca} - {self.contatos[nome_busca]}"
            else:
                return "Contato não encontrado. Use 'listar contatos' para ver todos os contatos."
        
        # Listar contatos
        elif any(palavra in texto.lower() for palavra in ["listar", "mostrar", "ver"]):
            if not self.contatos:
                return "Você não tem contatos salvos."
                
            resposta = "Seus contatos:\n"
            for nome, dados in self.contatos.items():
                resposta += f"- {nome}: {dados}\n"
            return resposta
        
        # Remover contato
        elif any(palavra in texto.lower() for palavra in ["remover", "deletar", "apagar"]):
            nome_remover = ""
            for palavra in texto.split():
                if palavra.lower() in self.contatos:
                    nome_remover = palavra.lower()
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
        """Gerencia notas e anotações"""
        # Adicionar nota
        if any(palavra in texto.lower() for palavra in ["adicionar", "nova", "criar", "salvar"]):
            partes = texto.lower().split("nota", 1)
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
        elif any(palavra in texto.lower() for palavra in ["listar", "mostrar", "ver"]):
            if not self.notas:
                return "Você não tem notas salvas."
                
            resposta = "Suas notas:\n"
            for i, nota in enumerate(self.notas):
                resposta += f"{i+1}. {nota['conteudo']} ({nota['data']})\n"
            return resposta
        
        # Remover nota
        elif any(palavra in texto.lower() for palavra in ["remover", "deletar", "apagar"]):
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
