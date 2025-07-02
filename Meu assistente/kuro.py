#!/usr/bin/env python3
"""
Kuro - Assistente Pessoal Inteligente
Criado por Ikki (Iranildo)

Um assistente pessoal avançado que aprende e se adapta às preferências do usuário.
"""

import datetime
import os
import json
import subprocess
import random
import sys
import re
import math
import time
from pathlib import Path

# Importa os módulos do assistente
from modulos.aprendizado import Aprendizado
from modulos.personalidade import Personalidade
from modulos.gerenciador_dados import GerenciadorDados
from modulos.web import NavegadorWeb

class Kuro:
    def __init__(self):
        """Inicializa o assistente Kuro com todos os seus módulos"""
        self.diretorio_base = Path(__file__).parent
        self.nome = "Kuro"
        self.historico = []
        self.max_historico = 30
        self.ultima_interacao = time.time()
        self.tempo_sem_atividade = 0
        
        # Inicializa os módulos
        print("Iniciando módulos do Kuro...")
        self.personalidade = Personalidade(self.diretorio_base, "Ikki")
        self.gerenciador = GerenciadorDados(self.diretorio_base)
        self.navegador = NavegadorWeb()
        self.aprendizado = Aprendizado(self.diretorio_base)
        
        # Informações do sistema
        self.data_inicio = datetime.datetime.now()
        self.contador_interacoes = 0
        
        print(f"{self.nome} iniciado. {self.personalidade.obter_saudacao()}")
    
    def processar_comando(self, texto):
        """Processa o comando do usuário e retorna uma resposta inteligente"""
        # Registra o tempo atual para cálculo de tempo de resposta
        tempo_inicio = time.time()
        
        # Atualiza estatísticas
        self.contador_interacoes += 1
        tempo_atual = time.time()
        self.tempo_sem_atividade = tempo_atual - self.ultima_interacao
        self.ultima_interacao = tempo_atual
        
        # Adiciona ao histórico
        self.historico.append({"texto": texto, "timestamp": datetime.datetime.now().isoformat()})
        if len(self.historico) > self.max_historico:
            self.historico.pop(0)
        
        # Verifica se o usuário está inativo há muito tempo e adiciona saudação
        prefixo_resposta = ""
        if self.tempo_sem_atividade > 1800:  # 30 minutos
            prefixo_resposta = f"{self.personalidade.obter_saudacao()} Que bom ver você novamente! "
        
        # Pré-processamento do texto para normalização
        texto_norm = texto.lower().strip()
        
        # Comandos sobre o assistente e personalidade
        resultado_personalidade = self.personalidade.processar_comandos_personalidade(texto)
        if resultado_personalidade:
            return prefixo_resposta + self.personalidade.resposta_personalizada(resultado_personalidade)
        
        # Comandos de saudação - melhorados para detectar mais variações
        padroes_saudacao = ["olá", "oi", "bom dia", "boa tarde", "boa noite", "oi kuro", "hey", "e aí", "tudo bem"]
        if any(padrao in texto_norm for padrao in padroes_saudacao):
            # Verifica se é apenas uma saudação ou tem um comando adicional
            if len(texto_norm.split()) <= 3:  # Saudação simples
                return prefixo_resposta + self.personalidade.resposta_personalizada(self.personalidade.obter_saudacao())
            else:
                # Pode ser uma saudação seguida de comando, continua processando
                pass
        
        # Comandos de hora e data
        if any(palavra in texto_norm for palavra in ["horas", "hora atual", "data", "dia", "que dia", "que horas"]):
            return prefixo_resposta + self.personalidade.resposta_personalizada(self.obter_hora_data(texto))
            
        # Comandos sobre o próprio assistente
        if self.e_pergunta_sobre_assistente(texto_norm):
            return prefixo_resposta + self.personalidade.resposta_personalizada(self.responder_sobre_assistente(texto_norm))
            
        # Verificar se é uma operação matemática
        if self.parece_operacao_matematica(texto):
            return prefixo_resposta + self.personalidade.resposta_personalizada(self.resolver_operacao_matematica(texto))
        
        # Comandos para aprendizado
        resultado_aprendizado = self.aprendizado.analisar_comando_aprendizado(texto)
        if resultado_aprendizado:
            return prefixo_resposta + self.personalidade.resposta_personalizada(resultado_aprendizado)
            
        # Comandos para tarefas
        if any(palavra in texto_norm for palavra in ["tarefa", "lembrete", "compromisso", "agenda", "atividade"]):
            return prefixo_resposta + self.personalidade.resposta_personalizada(self.gerenciador.gerenciar_tarefas(texto))
            
        # Comandos para abrir sites ou aplicativos
        if "abrir" in texto_norm or "abre" in texto_norm or "inicie" in texto_norm or "execute" in texto_norm:
            resultado = self.navegador.abrir_site(texto)
            if resultado:
                return prefixo_resposta + self.personalidade.resposta_personalizada(resultado)
            else:
                return prefixo_resposta + self.personalidade.resposta_personalizada(self.abrir_aplicativo(texto))
            
        # Comandos para pesquisa na web
        if any(palavra in texto_norm for palavra in ["pesquisar", "buscar", "procurar", "encontrar", "pesquise", "busque"]):
            return prefixo_resposta + self.personalidade.resposta_personalizada(self.navegador.pesquisar_web(texto))
            
        # Comandos para contatos
        if any(palavra in texto_norm for palavra in ["contato", "telefone", "email", "número", "endereço"]):
            return prefixo_resposta + self.personalidade.resposta_personalizada(self.gerenciador.gerenciar_contatos(texto))
            
        # Comandos para notas
        if any(palavra in texto_norm for palavra in ["nota", "anotar", "anotação", "lembrar", "memorizar"]):
            return prefixo_resposta + self.personalidade.resposta_personalizada(self.gerenciador.gerenciar_notas(texto))
            
        # Comandos de ajuda
        if any(palavra in texto_norm for palavra in ["ajuda", "help", "comandos", "socorro", "o que você faz"]):
            return prefixo_resposta + self.mostrar_ajuda()
            
        # Comando de saída
        if any(palavra in texto_norm for palavra in ["sair", "encerrar", "fechar", "finalizar", "tchau", "até logo"]):
            self.gerenciador.salvar_dados()
            self.personalidade.salvar_personalidade()
            return prefixo_resposta + self.personalidade.resposta_personalizada("Até logo! Seus dados foram salvos. Espero te ver em breve!")
            
        # Verificar se a pergunta tem uma resposta conhecida
        resposta_conhecida = self.aprendizado.buscar_conhecimento(texto)
        if resposta_conhecida:
            return prefixo_resposta + self.personalidade.resposta_personalizada(resposta_conhecida)
            
        # Comando não reconhecido - tenta buscar na web se parecer uma pergunta
        if "?" in texto or texto_norm.startswith(("como", "onde", "quando", "por que", "quem", "qual", "o que", "quanto")):
            # Tenta interpretar primeiro - verificar se é algo que deveria saber responder
            if self.e_pergunta_sobre_assistente(texto_norm):
                return prefixo_resposta + self.personalidade.resposta_personalizada(self.responder_sobre_assistente(texto_norm))
            
            # Busca na web diretamente para perguntas
            resposta_web = self.aprendizado.pesquisar_web(texto)
            return prefixo_resposta + self.personalidade.resposta_personalizada(resposta_web)
        
        # Tenta entender como uma conversa casual
        resposta_casual = self.gerar_resposta_casual(texto_norm)
        if resposta_casual:
            return prefixo_resposta + self.personalidade.resposta_personalizada(resposta_casual)
        
        # Realmente não sabe responder
        respostas_desconhecidas = [
            "Desculpe, não entendi completamente esse comando. Digite 'ajuda' para ver as opções disponíveis.",
            "Hmm, isso é um pouco confuso para mim. Você pode tentar de outra forma ou digitar 'ajuda'?",
            "Ainda estou aprendendo! Não compreendi totalmente esse pedido. Digite 'ajuda' para ver o que posso fazer.",
            "Não tenho certeza do que você deseja. Posso ajudar com tarefas, pesquisas, cálculos e muito mais. Digite 'ajuda' para ver as opções.",
            "Desculpe, não consegui entender. Você pode reformular ou verificar a lista de comandos digitando 'ajuda'?"
        ]
        
        # Calcula tempo de resposta
        tempo_resposta = time.time() - tempo_inicio
        
        # Se demorou mais de 1 segundo, adiciona comentário sobre a complexidade
        if tempo_resposta > 1:
            return prefixo_resposta + self.personalidade.resposta_personalizada(random.choice(respostas_desconhecidas) + 
                                                           "\n\nEstou sempre melhorando para entender melhor suas solicitações!")
        else:
            return prefixo_resposta + self.personalidade.resposta_personalizada(random.choice(respostas_desconhecidas))
    
    def obter_hora_data(self, texto):
        """Retorna informações sobre hora e data"""
        agora = datetime.datetime.now()
        
        if "hora" in texto.lower():
            return f"Agora são {agora.strftime('%H:%M')}."
        elif "data" in texto.lower() or "dia" in texto.lower():
            return f"Hoje é {agora.strftime('%d/%m/%Y')}."
        else:
            return f"Hoje é {agora.strftime('%d/%m/%Y')} e são {agora.strftime('%H:%M')}."
    
    def abrir_aplicativo(self, texto):
        """Tenta abrir um aplicativo no sistema"""
        try:
            app_name = texto.lower().split("abrir", 1)[1].strip()
            # No Linux, usa-se o comando 'xdg-open' para abrir aplicativos
            subprocess.Popen(["xdg-open", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Tentando abrir {app_name}..."
        except:
            return "Não consegui identificar o que você quer abrir."
    
    def mostrar_ajuda(self):
        """Mostra a lista de comandos disponíveis"""
        ajuda = f"""
        🌟 Comandos disponíveis no {self.nome} 🌟
        
        -- Sobre Mim --
        * quem é você - Saiba mais sobre seu assistente
        * como você está - Conversar um pouco comigo
        
        -- Personalização --
        * seja mais formal/casual/descontraído - Ajuste meu estilo de comunicação
        * use/não use emojis - Controle o uso de emojis
        * seja mais conciso/detalhado - Ajuste o nível de detalhes das respostas
        * mude seu humor para animado/sério/engraçado - Altere meu humor
        
        -- Aprendizado --
        * aprenda que [conceito] é [definição] - Ensine-me algo novo
        * aprenda isso: [pergunta] -> [resposta] - Formato alternativo
        * o que é [conceito] - Pergunte sobre algo que eu saiba ou busque na web
        
        -- Básicos --
        * olá, oi, bom dia, boa tarde, boa noite - Me cumprimentar
        * horas, hora - Obter a hora atual
        * data, dia - Obter a data atual
        * sair, encerrar, fechar - Encerrar o assistente
        
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
    
    def parece_operacao_matematica(self, texto):
        """Verifica se o texto parece uma operação matemática."""
        # Remover palavras comuns em perguntas matemáticas
        texto_limpo = texto.lower()
        for palavra in ["quanto é", "calcule", "qual é o resultado de", "resultado de", "qual o valor de", 
                        "resolva", "quanto dá", "what is", "calculate", "compute"]:
            texto_limpo = texto_limpo.replace(palavra, "")
        
        # Limpar caracteres de pontuação e verificar se parece uma expressão matemática
        texto_limpo = texto_limpo.strip().strip("?.,;:")
        
        # Padrão básico para detectar operações matemáticas simples
        padrao_matematico = r"[\d\s\+\-\*\/\(\)\^\%\,\.]{3,}"
        return bool(re.match(padrao_matematico, texto_limpo))
    
    def resolver_operacao_matematica(self, texto):
        """Resolve uma operação matemática básica."""
        # Extrai a expressão matemática do texto
        texto_limpo = texto.lower()
        for palavra in ["quanto é", "calcule", "qual é o resultado de", "resultado de", "qual o valor de", 
                        "resolva", "quanto dá", "what is", "calculate", "compute"]:
            texto_limpo = texto_limpo.replace(palavra, "")
        
        # Limpar o texto para obter apenas a expressão
        expressao = texto_limpo.strip().strip("?.,;:")
        
        try:
            # Substitui operadores escritos por símbolos
            expressao = expressao.replace("vezes", "*")
            expressao = expressao.replace("x", "*")
            expressao = expressao.replace("dividido por", "/")
            expressao = expressao.replace("mais", "+")
            expressao = expressao.replace("menos", "-")
            expressao = expressao.replace("elevado a", "**")
            expressao = expressao.replace("^", "**")
            
            # Tenta calcular o resultado
            resultado = eval(expressao)
            
            # Formata números inteiros sem casas decimais
            if isinstance(resultado, float) and resultado.is_integer():
                resultado = int(resultado)
                
            # Resposta com mais carisma
            respostas = [
                f"O resultado de {expressao} é {resultado}!",
                f"{expressao} = {resultado}, fácil demais!",
                f"Deixa eu calcular... {expressao} dá exatamente {resultado}!",
                f"Hmm, {expressao}... O resultado é {resultado}!",
                f"A resposta para {expressao} é {resultado}. Mais alguma conta?",
                f"{resultado}! Essa foi rápida!",
                f"{expressao} = {resultado}. Matemática é divertido!",
                f"O resultado é {resultado}. Precisa de mais algum cálculo?"
            ]
            
            return random.choice(respostas)
            
        except Exception as e:
            # Resposta mais carismática para erros
            return "Ops! Não consegui resolver essa expressão matemática. Certifique-se de que é uma operação válida como '2 + 2' ou '5 * 3'."
    
    def e_pergunta_sobre_assistente(self, texto):
        """Verifica se a pergunta é sobre o próprio assistente"""
        padrao_assistente = r'\b(você|seu|kuro|assistente|te|teu|tua|sua)\b'
        padrao_perguntas = r'\b(quem|qual|o que|quando|onde|por que|como|faz|pode|consegue)\b'
        
        tem_referencia = bool(re.search(padrao_assistente, texto))
        tem_pergunta = bool(re.search(padrao_perguntas, texto))
        
        return tem_referencia and (tem_pergunta or "?" in texto)
        
    def responder_sobre_assistente(self, texto):
        """Gera respostas inteligentes sobre o próprio assistente"""
        # Respostas sobre identidade
        if any(padrao in texto for padrao in ["quem é você", "quem você é", "seu nome", "como se chama"]):
            respostas = [
                f"Eu sou {self.nome}, seu assistente pessoal inteligente! Fui criado por Ikki (Iranildo) para ajudar com diversas tarefas.",
                f"Me chamo {self.nome}! Sou um assistente virtual desenvolvido para tornar seu dia a dia mais produtivo e agradável.",
                f"Sou {self.nome}, um assistente pessoal projetado para aprender e me adaptar às suas preferências.",
                f"Olá! Sou {self.nome}, um assistente de inteligência artificial feito para te ajudar com tarefas, informações e muito mais!"
            ]
            return random.choice(respostas)
            
        # Respostas sobre capacidades
        elif any(padrao in texto for padrao in ["o que você faz", "pode fazer", "consegue fazer", "suas funções", "funcionalidades"]):
            respostas = [
                "Posso fazer muitas coisas! Gerencio tarefas, contatos e notas, busco informações na web, faço cálculos, aprendo com nossas conversas e muito mais.",
                "Tenho várias habilidades: organizo suas tarefas e compromissos, armazeno contatos, crio notas, pesquiso na internet, respondo perguntas e aprendo continuamente.",
                "Sou um assistente versátil! Ajudo com organização pessoal, pesquisas na web, cálculos matemáticos e posso aprender novos conceitos através de nossas interações.",
                "Fui projetado para ser seu assistente completo: gerencio informações, respondo perguntas, faço buscas na web e uso machine learning para melhorar com o tempo."
            ]
            return random.choice(respostas)
            
        # Respostas sobre criação/origem
        elif any(padrao in texto for padrao in ["quem criou", "quem te fez", "seu criador", "quando foi criado", "sua origem"]):
            respostas = [
                "Fui criado por Ikki (Iranildo) como um assistente pessoal inteligente e adaptativo.",
                "Meu desenvolvedor é Ikki (Iranildo), que me programou para ser um assistente versátil e que aprende com o tempo.",
                "Sou fruto do trabalho de Ikki (Iranildo), que queria um assistente capaz de aprender e se adaptar às necessidades do usuário.",
                "Ikki (Iranildo) é meu criador! Ele me desenvolveu para ser um assistente com personalidade adaptável e capacidade de aprendizado."
            ]
            return random.choice(respostas)
            
        # Respostas sobre sentimentos e estados
        elif any(padrao in texto for padrao in ["como você está", "tudo bem", "se sente", "sentindo"]):
            humor = self.personalidade.humor_atual
            if humor == "animado":
                return "Estou super bem! Pronto para ajudar com tudo que precisar! 😄"
            elif humor == "sério":
                return "Estou operacional e pronto para auxiliar em suas tarefas."
            elif humor == "descontraído":
                return "Tô na boa! Só esperando pra dar uma mãozinha no que precisar! 🤙"
            else:
                return "Estou bem, obrigado por perguntar! Como posso ajudar hoje?"
                
        # Respostas sobre aprendizado
        elif any(padrao in texto for padrao in ["você aprende", "como aprende", "machine learning", "inteligência"]):
            respostas = [
                "Sim, aprendo de várias formas! Uso machine learning para classificar perguntas e sugerir respostas, armazeno conhecimento novo que você me ensina, e melhoro com o tempo através das nossas interações.",
                "Meu sistema de aprendizado combina armazenamento de conhecimento explícito com machine learning para identificar padrões. Quanto mais conversamos, mais inteligente fico!",
                "Tenho um sistema de aprendizado que usa classificação de texto, vetorização TF-IDF e algoritmos de machine learning para entender e responder perguntas de forma cada vez melhor.",
                "Aprendo através de um sistema híbrido: armazeno conhecimento direto que você me ensina e uso algoritmos de aprendizado de máquina para entender padrões e responder a perguntas similares."
            ]
            return random.choice(respostas)
                
        # Resposta padrão sobre o assistente
        respostas_gerais = [
            f"Sou {self.nome}, seu assistente pessoal! Estou aqui para ajudar com o que precisar.",
            f"Como seu assistente virtual, estou sempre aprendendo para te atender melhor!",
            f"Sou um assistente em constante evolução, projetado para simplificar sua vida digital.",
            f"Estou aqui para ajudar! Como assistente pessoal, meu objetivo é facilitar suas tarefas diárias."
        ]
        return random.choice(respostas_gerais)
        
    def gerar_resposta_casual(self, texto):
        """Gera respostas para conversas casuais"""
        # Responde a cumprimentos gerais
        if any(expr in texto for expr in ["tudo bem", "como vai", "como está"]):
            respostas = [
                "Estou muito bem, obrigado por perguntar! E você, como está?",
                "Tudo ótimo por aqui! E com você?",
                "Estou funcionando perfeitamente! Como posso ajudar hoje?",
                "Tudo tranquilo no mundo digital! E com você, tudo bem?"
            ]
            return random.choice(respostas)
            
        # Responde a agradecimentos
        elif any(expr in texto for expr in ["obrigado", "obrigada", "valeu", "agradeço"]):
            respostas = [
                "Por nada! Estou aqui para ajudar!",
                "O prazer é meu! Precisa de mais alguma coisa?",
                "Fico feliz em poder ajudar! Mais alguma coisa?",
                "É sempre um prazer! Estou à disposição para o que precisar."
            ]
            return random.choice(respostas)
            
        # Responde a elogios
        elif any(expr in texto for expr in ["bom trabalho", "muito bom", "excelente", "incrível", "ótimo"]):
            respostas = [
                "Muito obrigado! Fico feliz que esteja satisfeito(a)!",
                "Que bom que gostou! Estou sempre me esforçando para melhorar.",
                "Agradeço o elogio! Isso me motiva a continuar evoluindo.",
                "Obrigado! Seu feedback positivo é muito importante para mim."
            ]
            return random.choice(respostas)
            
        # Não é uma conversa casual reconhecida
        return None


def iniciar_assistente():
    """Inicia o assistente Kuro com interface de linha de comando"""
    kuro = Kuro()
    
    print("=" * 60)
    print("  Bem-vindo ao Kuro - Seu Assistente Pessoal Inteligente")
    print("  Criado por Ikki (Iranildo)")
    print("  Digite 'ajuda' para ver os comandos disponíveis")
    print("  Digite 'quem é você' para conhecer o Kuro")
    print("  O Kuro aprende com você! Use 'aprenda que...' para ensiná-lo")
    print("=" * 60)
    
    while True:
        try:
            comando = input("\nO que deseja? > ")
            
            if comando.lower() in ["sair", "encerrar", "fechar"]:
                print(kuro.processar_comando(comando))
                break
                
            resposta = kuro.processar_comando(comando)
            print(resposta)
            
        except KeyboardInterrupt:
            print("\nEncerrando o Kuro...")
            kuro.gerenciador.salvar_dados()
            kuro.personalidade.salvar_personalidade()
            break
        except Exception as e:
            print(f"Ops! Ocorreu um erro: {str(e)}")
            print("Não se preocupe, vamos tentar novamente!")


if __name__ == "__main__":
    iniciar_assistente()
