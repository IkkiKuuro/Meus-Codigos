"""
Módulo de personalidade do Kuro - Gerenciamento do comportamento e estilo de comunicação
"""
import json
import random
from pathlib import Path
import datetime

class Personalidade:
    def __init__(self, diretorio_base, nome_usuario="Ikki"):
        self.diretorio_dados = Path(diretorio_base) / "dados"
        self.arquivo_personalidade = self.diretorio_dados / "personalidade.json"
        self.nome_usuario = nome_usuario
        self.preferencia_nome_usuario = "Ikki"  # Nome preferido (Ikki em vez de Iranildo)
        
        # Personalidade padrão (será sobrescrita se houver arquivo salvo)
        self.tracos = {
            "humor": "animado",       # neutro, animado, sério, engraçado
            "formalidade": "casual",  # formal, casual, descontraído
            "emoji": True,            # True/False
            "verbosidade": "média",   # concisa, média, detalhada
            "proatividade": 0.6,      # 0.0 a 1.0 (chance de oferecer sugestões proativamente)
            "adaptabilidade": 0.7     # 0.0 a 1.0 (velocidade com que adapta a personalidade)
        }
        
        self.expressoes = {
            "neutro": [
                "Entendido.",
                "Compreendido.",
                "Prosseguindo.",
                "Continuando.",
                "Vamos lá."
            ],
            "animado": [
                "Com certeza!",
                "Vamos nessa!",
                "Pode deixar comigo!",
                "Estou animado para ajudar!",
                "Vamos fazer isso acontecer!",
                "Ao seu dispor!",
                "Com todo prazer!",
                "É pra já!",
                "Conte comigo!",
                "Considere feito!"
            ],
            "sério": [
                "Compreendido.",
                "Vou proceder.",
                "Entendido, continuando.",
                "Avançando.",
                "Executando."
            ],
            "engraçado": [
                "É pra já, chefe!",
                "Seus desejos são ordens!",
                "Tá na mão!",
                "Dito e feito!",
                "Mais rápido que Flash!",
                "Capiche, patrão!",
                "E lá vamos nós!",
                "Ah, essa é comigo!",
                "Molezinha!"
            ]
        }
        
        self.respostas_humor = {
            "neutro": [
                "Estou funcionando normalmente.",
                "Tudo em ordem.",
                "Operando conforme esperado.",
                "Estou bem, obrigado por perguntar."
            ],
            "animado": [
                "Estou ótimo hoje! Pronto para ajudar! 😊",
                "Super animado para trabalhar com você!",
                "Hoje está sendo um dia incrível!",
                "Melhor impossível! E você?",
                "Estou radiante hoje! Pronto para qualquer desafio!",
                "Cheio de energia e pronto para o que der e vier!",
                "Excelente! Animado para tornar seu dia mais produtivo!"
            ],
            "sério": [
                "Funcionando dentro dos parâmetros esperados.",
                "Todos os sistemas operacionais.",
                "Condição operacional satisfatória.",
                "Pronto para executar tarefas."
            ],
            "engraçado": [
                "Tô tinindo! Pronto pra qualquer parada! 😎",
                "Se eu fosse mais feliz, seria dois!",
                "Na melhor forma possível (tá, não tenho forma, mas você entendeu)!",
                "Melhor que café pela manhã!",
                "Estou tão bem que daria pra iluminar uma cidade!",
                "Mais ligado que tomada dupla!",
                "Na paz! Suave na nave!",
                "100% carregado e pronto para arrasar!",
                "De boa na lagoa!"
            ]
        }
        
        self.emojis = {
            "neutro": ["👍", "✓", "➤", "⚙️", "📝"],
            "animado": ["✨", "🚀", "😊", "⭐", "💯", "🎯", "🌟", "🤩", "💪", "👏", "🔥"],
            "sério": ["📊", "📑", "🔍", "⏱️", "📌"],
            "engraçado": ["😎", "🤩", "🤪", "🥳", "🤓", "🤘", "👻", "😂", "🎮", "🎭", "🍕", "🎈"]
        }
        
        # Carrega dados salvos
        self.carregar_personalidade()
        
    def carregar_personalidade(self):
        """Carrega a personalidade salva ou usa a padrão"""
        if not self.diretorio_dados.exists():
            self.diretorio_dados.mkdir(exist_ok=True)
            
        if self.arquivo_personalidade.exists():
            try:
                with open(self.arquivo_personalidade, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.tracos = dados.get("tracos", self.tracos)
                    self.nome_usuario = dados.get("nome_usuario", self.nome_usuario)
                    self.preferencia_nome_usuario = dados.get("preferencia_nome_usuario", self.preferencia_nome_usuario)
            except:
                # Em caso de erro, mantém os valores padrão
                pass
                
    def salvar_personalidade(self):
        """Salva a personalidade atual"""
        dados = {
            "tracos": self.tracos,
            "nome_usuario": self.nome_usuario,
            "preferencia_nome_usuario": self.preferencia_nome_usuario
        }
        
        with open(self.arquivo_personalidade, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
            
    def adaptar_humor(self, texto):
        """Adapta o humor com base na interação do usuário"""
        # Palavras que indicam diferentes humores
        indicadores = {
            "animado": ["legal", "ótimo", "incrível", "amei", "adoro", "bacana", "top", "fantástico"],
            "sério": ["sério", "importante", "urgente", "crítico", "preciso", "necessito", "formal"],
            "engraçado": ["engraçado", "divertido", "brincadeira", "zoeira", "meme", "haha", "rsrs", "kkkk"],
            "neutro": ["normal", "neutro", "padrão", "básico", "simples"]
        }
        
        texto_lower = texto.lower()
        
        # Verifica se há uma solicitação direta de mudança de humor
        if "mude seu humor para" in texto_lower or "seja mais" in texto_lower:
            for humor, _ in indicadores.items():
                if humor in texto_lower:
                    self.tracos["humor"] = humor
                    self.salvar_personalidade()
                    return f"Humor alterado para {humor}."
        
        # Adaptação gradual baseada no texto do usuário
        for humor, palavras in indicadores.items():
            for palavra in palavras:
                if palavra in texto_lower:
                    # Ajusta gradualmente o humor com base na adaptabilidade
                    if self.tracos["humor"] != humor:
                        chance_mudanca = self.tracos["adaptabilidade"]
                        if random.random() < chance_mudanca:
                            self.tracos["humor"] = humor
                            self.salvar_personalidade()
                    break
        
        return None
        
    def adaptar_formalidade(self, texto):
        """Adapta o nível de formalidade com base na interação"""
        texto_lower = texto.lower()
        
        # Solicitação direta de mudança
        if "seja mais formal" in texto_lower:
            self.tracos["formalidade"] = "formal"
            self.salvar_personalidade()
            return "Aumentei meu nível de formalidade."
            
        if "seja mais casual" in texto_lower or "seja menos formal" in texto_lower:
            self.tracos["formalidade"] = "casual"
            self.salvar_personalidade()
            return "Reduzi meu nível de formalidade."
            
        if "seja descontraído" in texto_lower:
            self.tracos["formalidade"] = "descontraído"
            self.salvar_personalidade()
            return "Agora estou bem descontraído."
            
        # Adaptação gradual
        # Indicadores de formalidade alta
        formal_indicators = ["por favor", "poderia", "gostaria", "senhor", "senhora"]
        # Indicadores de casualidade
        casual_indicators = ["e aí", "beleza", "tranquilo", "valeu", "blz", "vlw", "cara", "mano"]
        
        formal_count = sum(1 for word in formal_indicators if word in texto_lower)
        casual_count = sum(1 for word in casual_indicators if word in texto_lower)
        
        if formal_count > casual_count and formal_count > 0:
            if self.tracos["formalidade"] != "formal" and random.random() < self.tracos["adaptabilidade"]:
                self.tracos["formalidade"] = "formal"
                self.salvar_personalidade()
        elif casual_count > formal_count and casual_count > 0:
            if self.tracos["formalidade"] != "casual" and random.random() < self.tracos["adaptabilidade"]:
                self.tracos["formalidade"] = "casual"
                self.salvar_personalidade()
                
        return None
        
    def adaptar_verbosidade(self, texto):
        """Adapta o nível de detalhes das respostas"""
        texto_lower = texto.lower()
        
        # Solicitação direta
        if "seja mais conciso" in texto_lower or "seja breve" in texto_lower:
            self.tracos["verbosidade"] = "concisa"
            self.salvar_personalidade()
            return "Agora serei mais conciso nas respostas."
            
        if "seja mais detalhado" in texto_lower or "dê mais detalhes" in texto_lower:
            self.tracos["verbosidade"] = "detalhada"
            self.salvar_personalidade()
            return "Fornecerei respostas mais detalhadas a partir de agora."
            
        # Adaptação baseada no padrão de perguntas
        # Perguntas curtas geralmente esperam respostas concisas
        if len(texto.split()) < 5 and "?" in texto:
            if self.tracos["verbosidade"] != "concisa" and random.random() < self.tracos["adaptabilidade"]:
                self.tracos["verbosidade"] = "concisa"
                self.salvar_personalidade()
                
        # Perguntas longas ou com palavras como "explique" geralmente esperam mais detalhes
        if len(texto.split()) > 15 or any(word in texto_lower for word in ["explique", "detalhe", "elabore"]):
            if self.tracos["verbosidade"] != "detalhada" and random.random() < self.tracos["adaptabilidade"]:
                self.tracos["verbosidade"] = "detalhada"
                self.salvar_personalidade()
                
        return None
        
    def adaptar_emoji(self, texto):
        """Adapta o uso de emojis"""
        texto_lower = texto.lower()
        
        # Solicitação direta
        if "use emojis" in texto_lower or "coloque emojis" in texto_lower:
            self.tracos["emoji"] = True
            self.salvar_personalidade()
            return "Ativei o uso de emojis! 😊"
            
        if "não use emojis" in texto_lower or "sem emojis" in texto_lower:
            self.tracos["emoji"] = False
            self.salvar_personalidade()
            return "Desativei o uso de emojis."
            
        # Adaptação gradual
        # Se o usuário usar emojis, aumenta a chance do assistente também usar
        emoji_count = sum(1 for char in texto if ord(char) > 8000)  # Verificação simples para emojis
        if emoji_count > 0:
            if not self.tracos["emoji"] and random.random() < self.tracos["adaptabilidade"]:
                self.tracos["emoji"] = True
                self.salvar_personalidade()
        elif len(texto) > 30 and emoji_count == 0:
            # Mensagens longas sem emojis podem indicar preferência por comunicação sem emojis
            if self.tracos["emoji"] and random.random() < self.tracos["adaptabilidade"]:
                self.tracos["emoji"] = False
                self.salvar_personalidade()
                
        return None
        
    def resposta_personalizada(self, mensagem):
        """Adiciona personalidade à resposta"""
        # Ajusta com base na verbosidade
        if self.tracos["verbosidade"] == "concisa" and len(mensagem.split()) > 20:
            # Tenta deixar a mensagem mais concisa
            mensagem = self.tornar_conciso(mensagem)
            
        # Adiciona expressão característica com base no humor
        humor_atual = self.tracos["humor"]
        if random.random() < 0.5:  # Aumentado para 50% de chance
            prefixo = random.choice(self.expressoes[humor_atual])
            mensagem = f"{prefixo} {mensagem}"
            
        # Ajusta formalidade
        if self.tracos["formalidade"] == "formal":
            mensagem = self.formalizar(mensagem)
        elif self.tracos["formalidade"] == "descontraído":
            mensagem = self.descontrair(mensagem)
            
        # Adiciona emoji se ativado
        if self.tracos["emoji"] and random.random() < 0.6:  # Aumentado para 60% de chance
            mensagem += f" {random.choice(self.emojis[humor_atual])}"
            
        # Personaliza com o nome do usuário ocasionalmente
        if random.random() < 0.25:  # Aumentado para 25% de chance
            if mensagem[-1] in [".", "!", "?"]:
                mensagem = mensagem[:-1] + f", {self.preferencia_nome_usuario}" + mensagem[-1]
            else:
                mensagem += f", {self.preferencia_nome_usuario}"
                
        return mensagem
        
    def tornar_conciso(self, texto):
        """Simplifica uma mensagem para torná-la mais concisa"""
        # Implementação simples - remove expressões verbosas comuns
        verboso = [
            "como você deve saber", 
            "por favor note que", 
            "eu gostaria de informar que",
            "é importante mencionar que",
            "gostaria de destacar que",
            "vale a pena mencionar que",
            "para sua informação"
        ]
        
        resultado = texto
        for expr in verboso:
            resultado = resultado.replace(expr, "")
            
        # Remove redundâncias
        resultado = resultado.replace("atualmente", "")
        resultado = resultado.replace("no momento", "")
        resultado = resultado.replace("basicamente", "")
        
        return resultado.strip()
        
    def formalizar(self, texto):
        """Torna o texto mais formal"""
        # Substituições para aumentar formalidade
        informal_to_formal = {
            "tá": "está",
            "ok": "correto",
            "beleza": "excelente",
            "e aí": "como vai",
            "cara": "senhor",
            "valeu": "agradeço",
            "bora": "vamos",
            "pra": "para",
            "pro": "para o"
        }
        
        resultado = texto
        for informal, formal in informal_to_formal.items():
            resultado = re.sub(r'\b' + informal + r'\b', formal, resultado, flags=re.IGNORECASE)
            
        return resultado
        
    def descontrair(self, texto):
        """Torna o texto mais descontraído"""
        # Substituições para diminuir formalidade
        formal_to_informal = {
            "obrigado": "valeu",
            "correto": "beleza",
            "afirmativo": "sim",
            "negativo": "não",
            "excelente": "incrível",
            "certamente": "claro",
            "compreendo": "entendi"
        }
        
        resultado = texto
        for formal, informal in formal_to_informal.items():
            resultado = re.sub(r'\b' + formal + r'\b', informal, resultado, flags=re.IGNORECASE)
            
        return resultado
        
    def obter_saudacao(self):
        """Gera uma saudação adequada para o horário com a personalidade atual"""
        hora_atual = datetime.datetime.now().hour
        
        if 5 <= hora_atual < 12:
            periodo = "Bom dia"
        elif 12 <= hora_atual < 18:
            periodo = "Boa tarde"
        else:
            periodo = "Boa noite"
            
        humor_atual = self.tracos["humor"]
        
        if humor_atual == "neutro":
            respostas = [
                f"{periodo}, {self.preferencia_nome_usuario}. Em que posso ajudar?",
                f"{periodo}. Como posso ser útil hoje?",
                f"{periodo}. Estou pronto para ajudar.",
                f"Olá. {periodo}."
            ]
        elif humor_atual == "animado":
            respostas = [
                f"{periodo}, {self.preferencia_nome_usuario}! Em que posso ajudar você hoje?",
                f"{periodo}! Como posso ser útil para você hoje?",
                f"{periodo}! Estou animado para ajudar no que precisar!",
                f"Olá! {periodo}. Que bom ver você novamente!"
            ]
        elif humor_atual == "sério":
            respostas = [
                f"{periodo}, {self.preferencia_nome_usuario}. Aguardando suas instruções.",
                f"{periodo}. Como posso auxiliá-lo hoje?",
                f"{periodo}. Estou operacional e pronto para assistência.",
                f"Saudações. {periodo}. Pronto para executar comandos."
            ]
        else:  # engraçado
            respostas = [
                f"{periodo}, {self.preferencia_nome_usuario}! O que vai ser hoje? Estou tinindo!",
                f"{periodo}! Seu assistente preferido está na área!",
                f"{periodo}! Pronto para mais um dia de aventuras digitais?",
                f"E aí! {periodo}. Qual é a boa de hoje?"
            ]
            
        saudacao = random.choice(respostas)
        
        # Adiciona emoji se ativado
        if self.tracos["emoji"] and random.random() < 0.5:
            saudacao += f" {random.choice(self.emojis[humor_atual])}"
            
        return saudacao
        
    def processar_comandos_personalidade(self, texto):
        """Processa comandos relacionados à personalidade"""
        texto_lower = texto.lower()
        
        # Verificar e processar comandos específicos de personalidade
        if "seu nome é" in texto_lower:
            return "Meu nome é Kuro, fui criado por Ikki (Iranildo)."
            
        # Verificar alterações de humor explícitas
        humor_resultado = self.adaptar_humor(texto)
        if humor_resultado:
            return humor_resultado
            
        # Verificar alterações de formalidade explícitas
        formalidade_resultado = self.adaptar_formalidade(texto)
        if formalidade_resultado:
            return formalidade_resultado
            
        # Verificar alterações de verbosidade explícitas
        verbosidade_resultado = self.adaptar_verbosidade(texto)
        if verbosidade_resultado:
            return verbosidade_resultado
            
        # Verificar alterações de emoji explícitas
        emoji_resultado = self.adaptar_emoji(texto)
        if emoji_resultado:
            return emoji_resultado
            
        # Perguntas sobre a personalidade
        if "como você está" in texto_lower or "tudo bem" in texto_lower:
            humor_atual = self.tracos["humor"]
            resposta = random.choice(self.respostas_humor[humor_atual])
            return self.resposta_personalizada(resposta)
            
        # Perguntas sobre identidade
        if "quem é você" in texto_lower or "se apresente" in texto_lower:
            resposta = f"Eu sou Kuro, seu assistente virtual pessoal criado por Ikki. "
            resposta += f"Estou aqui para ajudar com tarefas, responder perguntas e aprender com nossas interações."
            return self.resposta_personalizada(resposta)
            
        # Adapta gradualmente a personalidade com base na interação
        self.adaptar_humor(texto)
        self.adaptar_formalidade(texto)
        self.adaptar_verbosidade(texto)
        self.adaptar_emoji(texto)
        
        return None
