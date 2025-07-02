"""
Módulo de aprendizado do Kuro - Armazenamento e recuperação de conhecimento
com capacidades avançadas de processamento de linguagem natural
"""
import json
import os
import re
import numpy as np
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import joblib
import time
import random
import string
from urllib.parse import quote_plus

# Importações para machine learning
try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import RSLPStemmer, WordNetLemmatizer
    from nltk.util import ngrams
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split, GridSearchCV
    from sklearn.preprocessing import LabelEncoder
    ML_DISPONIVEL = True
except ImportError:
    ML_DISPONIVEL = False

class Aprendizado:
    def __init__(self, diretorio_base):
        self.diretorio_conhecimento = Path(diretorio_base) / "aprendizado"
        self.arquivo_conhecimento = self.diretorio_conhecimento / "conhecimento.json"
        self.modelo_arquivo = self.diretorio_conhecimento / "modelo_ml.joblib"
        self.vetorizador_arquivo = self.diretorio_conhecimento / "vetorizador.joblib"
        self.conhecimento = {}
        self.ml_inicializado = False
        self.vetorizador = None
        self.modelo = None
        self.categorias = []
        self.limiar_confianca = 0.55  # Limiar de confiança para classificação (reduzido para mais flexibilidade)
        self.contexto_recente = []  # Armazena contexto das conversas recentes
        self.memoria_curto_prazo = []  # Memória de curto prazo para contexto de conversas
        self.max_memoria_curto_prazo = 10  # Máximo de interações na memória de curto prazo
        
        # Stemmer para português
        if ML_DISPONIVEL:
            try:
                nltk.download('rslp', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('punkt', quiet=True)
                self.stemmer = RSLPStemmer()
                self.lemmatizer = WordNetLemmatizer()
            except:
                pass
        
        # Inicializa estruturas
        self.carregar_conhecimento()
        self.inicializar_ml()
        
    def carregar_conhecimento(self):
        """Carrega o conhecimento previamente armazenado"""
        if not self.diretorio_conhecimento.exists():
            self.diretorio_conhecimento.mkdir(exist_ok=True)
            
        if self.arquivo_conhecimento.exists():
            try:
                with open(self.arquivo_conhecimento, 'r', encoding='utf-8') as f:
                    self.conhecimento = json.load(f)
            except:
                self.conhecimento = {}
                
    def salvar_conhecimento(self):
        """Salva o conhecimento atual"""
        with open(self.arquivo_conhecimento, 'w', encoding='utf-8') as f:
            json.dump(self.conhecimento, f, ensure_ascii=False, indent=2)
            
    def adicionar_conhecimento(self, pergunta, resposta, fonte="usuário", categoria=None):
        """Adiciona um novo conhecimento ao banco de dados de forma mais inteligente"""
        # Normaliza a pergunta para evitar duplicatas
        pergunta_norm = pergunta.lower().strip().rstrip('?!.')
        
        # Determina a categoria, se não for fornecida
        if categoria is None:
            categoria = self.determinar_categoria(pergunta_norm)
        
        # Extrai possíveis entidades para enriquecer o conhecimento
        entidades = self.extrair_entidades(pergunta)
        
        # Gera versões alternativas da pergunta para melhorar a recuperação
        versoes_alternativas = self.gerar_versoes_alternativas(pergunta_norm)
        
        # Tokeniza e stemiza para análise
        tokens = self.tokenizar_texto(self.normalizar_texto(pergunta_norm))
        stems = self.stemizar_texto(tokens)
        
        # Adiciona o conhecimento
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conhecimento[pergunta_norm] = {
            "resposta": resposta,
            "fonte": fonte,
            "data_criacao": data_atual,
            "data_atualizacao": data_atual,
            "contador_uso": 0,
            "categoria": categoria,
            "tokens": tokens,
            "stems": stems,
            "entidades": entidades,
            "versoes_alternativas": versoes_alternativas
        }
        
        # Adiciona também versões alternativas com referência à original
        for versao in versoes_alternativas:
            if versao != pergunta_norm and versao not in self.conhecimento:
                self.conhecimento[versao] = {
                    "resposta": resposta,
                    "fonte": fonte,
                    "data_criacao": data_atual,
                    "data_atualizacao": data_atual,
                    "contador_uso": 0,
                    "categoria": categoria,
                    "referencia_original": pergunta_norm,
                    "e_versao_alternativa": True
                }
        
        self.salvar_conhecimento()
        
        # Retreina o modelo se tiver dados suficientes
        if ML_DISPONIVEL and len(self.conhecimento) >= 5:
            self.treinar_modelo()
            
        return f"Aprendi: '{pergunta}' → '{resposta}'"
        
    def gerar_versoes_alternativas(self, pergunta):
        """Gera versões alternativas da mesma pergunta para melhorar a recuperação"""
        versoes = [pergunta]
        
        # Remove pontuação e caracteres especiais
        pergunta_limpa = re.sub(r'[^\w\s]', '', pergunta)
        if pergunta_limpa != pergunta:
            versoes.append(pergunta_limpa)
            
        # Adiciona versão com interrogação se não tiver
        if not pergunta.endswith('?'):
            versoes.append(pergunta + '?')
            
        # Reformulações comuns
        reformulacoes = {
            r'^o que é': 'definição de',
            r'^definição de': 'o que é',
            r'^quem é': 'me fale sobre',
            r'^me fale sobre': 'quem é',
            r'^como': 'qual a forma de',
            r'^qual a forma de': 'como',
            r'^quando': 'em que momento',
            r'^em que momento': 'quando'
        }
        
        for padrao, substituicao in reformulacoes.items():
            if re.match(padrao, pergunta):
                nova_versao = re.sub(padrao, substituicao, pergunta, 1)
                versoes.append(nova_versao)
                
        return list(set(versoes))  # Remove duplicatas
        
    def buscar_conhecimento(self, pergunta):
        """Busca por conhecimento existente de forma avançada"""
        pergunta_norm = pergunta.lower().strip().rstrip('?!.')
        contexto_recente = self.obter_contexto_recente()
        
        # Verifica correspondência exata
        if pergunta_norm in self.conhecimento:
            self.conhecimento[pergunta_norm]["contador_uso"] += 1
            self.salvar_conhecimento()
            resposta = self.conhecimento[pergunta_norm]["resposta"]
            self.adicionar_ao_contexto(pergunta, resposta)
            return resposta
        
        # Gera versões alternativas da pergunta e verifica
        versoes_alt = self.gerar_versoes_alternativas(pergunta_norm)
        for versao in versoes_alt:
            if versao in self.conhecimento:
                self.conhecimento[versao]["contador_uso"] += 1
                self.salvar_conhecimento()
                resposta = self.conhecimento[versao]["resposta"]
                self.adicionar_ao_contexto(pergunta, resposta)
                return resposta
        
        # Utiliza machine learning para encontrar respostas similares
        if ML_DISPONIVEL and self.ml_inicializado and len(self.conhecimento) >= 5:
            resposta_ml = self.prever_resposta_ml(pergunta_norm)
            if resposta_ml:
                self.adicionar_ao_contexto(pergunta, resposta_ml)
                return resposta_ml
        
        # Busca semântica através de similaridade de tokens
        resposta_semantica = self.busca_semantica(pergunta_norm)
        if resposta_semantica:
            self.adicionar_ao_contexto(pergunta, resposta_semantica)
            return resposta_semantica
            
        # Procura por correspondência de entidades
        entidades_pergunta = self.extrair_entidades(pergunta)
        if entidades_pergunta:
            resposta_entidades = self.busca_por_entidades(entidades_pergunta)
            if resposta_entidades:
                self.adicionar_ao_contexto(pergunta, resposta_entidades)
                return resposta_entidades
        
        # Procura no contexto recente se a pergunta é relacionada
        if contexto_recente:
            resposta_contexto = self.busca_no_contexto(pergunta_norm, contexto_recente)
            if resposta_contexto:
                self.adicionar_ao_contexto(pergunta, resposta_contexto)
                return resposta_contexto
        
        # Procura por correspondência parcial como último recurso
        melhores_correspondencias = []
        for chave in self.conhecimento:
            if pergunta_norm in chave or chave in pergunta_norm:
                melhores_correspondencias.append((chave, len(set(pergunta_norm.split()) & set(chave.split()))))
                
        # Retorna a melhor correspondência se existir
        if melhores_correspondencias:
            melhor = max(melhores_correspondencias, key=lambda x: x[1])
            if melhor[1] > 0:  # Se tem pelo menos uma palavra em comum
                self.conhecimento[melhor[0]]["contador_uso"] += 1
                self.salvar_conhecimento()
                resposta = self.conhecimento[melhor[0]]["resposta"]
                self.adicionar_ao_contexto(pergunta, resposta)
                return resposta
                
        return None
        
    def busca_semantica(self, pergunta):
        """Realiza uma busca semântica baseada em tokens e stems"""
        if len(self.conhecimento) < 3:
            return None
            
        # Tokeniza e stemiza a pergunta
        tokens_pergunta = self.tokenizar_texto(self.normalizar_texto(pergunta))
        stems_pergunta = self.stemizar_texto(tokens_pergunta)
        
        # Calcula similaridade com cada conhecimento
        resultados = []
        for chave, dados in self.conhecimento.items():
            # Pula versões alternativas para evitar duplicatas
            if dados.get('e_versao_alternativa', False):
                continue
                
            # Se tem tokens armazenados, usa-os. Caso contrário, gera.
            if 'tokens' in dados:
                tokens_conhecimento = dados['tokens']
                stems_conhecimento = dados.get('stems', self.stemizar_texto(tokens_conhecimento))
            else:
                tokens_conhecimento = self.tokenizar_texto(self.normalizar_texto(chave))
                stems_conhecimento = self.stemizar_texto(tokens_conhecimento)
                
            # Calcula similaridade de tokens
            tokens_comuns = set(tokens_pergunta) & set(tokens_conhecimento)
            similaridade_tokens = len(tokens_comuns) / max(len(tokens_pergunta), len(tokens_conhecimento), 1)
            
            # Calcula similaridade de stems
            stems_comuns = set(stems_pergunta) & set(stems_conhecimento)
            similaridade_stems = len(stems_comuns) / max(len(stems_pergunta), len(stems_conhecimento), 1)
            
            # Média ponderada das similaridades
            similaridade_final = (similaridade_tokens * 0.4) + (similaridade_stems * 0.6)
            
            if similaridade_final > 0.5:  # Limiar de similaridade
                resultados.append((chave, similaridade_final, dados["resposta"]))
                
        if resultados:
            # Retorna a resposta com maior similaridade
            chave, _, resposta = max(resultados, key=lambda x: x[1])
            self.conhecimento[chave]["contador_uso"] += 1
            self.salvar_conhecimento()
            return resposta
            
        return None
        
    def busca_por_entidades(self, entidades_pergunta):
        """Busca por conhecimentos que compartilham entidades com a pergunta"""
        if not entidades_pergunta:
            return None
            
        resultados = []
        for chave, dados in self.conhecimento.items():
            # Pula versões alternativas
            if dados.get('e_versao_alternativa', False):
                continue
                
            # Se tem entidades armazenadas, usa-as. Caso contrário, extrai.
            entidades_conhecimento = dados.get('entidades', self.extrair_entidades(chave))
            
            # Conta entidades em comum
            entidades_comuns = 0
            for tipo_ent1, valor_ent1 in entidades_pergunta:
                for tipo_ent2, valor_ent2 in entidades_conhecimento:
                    if tipo_ent1 == tipo_ent2 and valor_ent1.lower() == valor_ent2.lower():
                        entidades_comuns += 1
                        
            if entidades_comuns > 0:
                similaridade = entidades_comuns / max(len(entidades_pergunta), len(entidades_conhecimento), 1)
                resultados.append((chave, similaridade, dados["resposta"]))
                
        if resultados:
            # Retorna a resposta com mais entidades em comum
            chave, _, resposta = max(resultados, key=lambda x: x[1])
            self.conhecimento[chave]["contador_uso"] += 1
            self.salvar_conhecimento()
            return resposta
            
        return None
        
    def busca_no_contexto(self, pergunta, contexto_recente):
        """Busca por respostas considerando o contexto recente da conversa"""
        if not contexto_recente:
            return None
            
        # Tokeniza a pergunta atual
        tokens_pergunta = self.tokenizar_texto(self.normalizar_texto(pergunta))
        
        # Procura por similaridade com perguntas recentes
        resultados = []
        for interacao in contexto_recente:
            pergunta_anterior = interacao.get("pergunta", "")
            resposta_anterior = interacao.get("resposta", "")
            
            tokens_pergunta_anterior = self.tokenizar_texto(self.normalizar_texto(pergunta_anterior))
            
            # Calcula similaridade
            tokens_comuns = set(tokens_pergunta) & set(tokens_pergunta_anterior)
            similaridade = len(tokens_comuns) / max(len(tokens_pergunta), len(tokens_pergunta_anterior), 1)
            
            if similaridade > 0.6:  # Alta similaridade com pergunta anterior
                # Verifica se a pergunta atual parece pedir mais detalhes
                padrao_detalhe = r'(mais|detalhe|explique|elabore|continue)'
                if re.search(padrao_detalhe, pergunta.lower()):
                    resultados.append((pergunta_anterior, similaridade, 
                                      f"Continuando sobre isso: {resposta_anterior}"))
                    
        if resultados:
            # Retorna a resposta do contexto mais relevante
            _, _, resposta = max(resultados, key=lambda x: x[1])
            return resposta
            
        return None
        
    def inicializar_ml(self):
        """Inicializa componentes de machine learning"""
        if not ML_DISPONIVEL:
            return False
            
        try:
            # Baixa recursos necessários do NLTK se não existirem
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
                
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', quiet=True)
            
            # Carrega modelos existentes ou cria novos
            if self.modelo_arquivo.exists() and self.vetorizador_arquivo.exists():
                self.modelo = joblib.load(self.modelo_arquivo)
                self.vetorizador = joblib.load(self.vetorizador_arquivo)
                self.ml_inicializado = True
            elif len(self.conhecimento) >= 5:  # Precisa de pelo menos 5 exemplos para treinar
                self.treinar_modelo()
                
            return self.ml_inicializado
        except Exception as e:
            print(f"Erro ao inicializar ML: {str(e)}")
            return False
            
    def determinar_categoria(self, texto):
        """Determina a categoria do texto com base em palavras-chave"""
        categorias = {
            "saudação": ["olá", "oi", "bom dia", "boa tarde", "boa noite", "e aí", "como vai"],
            "informação_pessoal": ["seu nome", "quem é você", "você é", "sua idade", "onde você"],
            "tecnologia": ["computador", "programação", "software", "hardware", "código", "python", "java"],
            "cotidiano": ["tempo", "clima", "horário", "data", "dia", "mês", "ano"],
            "ciência": ["física", "química", "biologia", "matemática", "ciência", "científico"],
            "entretenimento": ["filme", "música", "jogo", "série", "arte", "livro", "tv"],
            "saúde": ["doença", "remédio", "médico", "saúde", "sintoma", "tratamento"],
            "geral": []
        }
        
        texto_lower = texto.lower()
        for categoria, palavras in categorias.items():
            for palavra in palavras:
                if palavra in texto_lower:
                    return categoria
                    
        return "geral"  # Categoria padrão
        
    def preparar_dados_treinamento(self):
        """Prepara dados para treinar o modelo de ML"""
        if len(self.conhecimento) < 5:
            return None, None
            
        X = []  # Perguntas/entradas
        y = []  # Categorias/respostas
        
        # Para classificação, usamos as categorias
        for pergunta, dados in self.conhecimento.items():
            X.append(pergunta)
            
            # Se não tiver categoria definida, atribui uma
            if "categoria" not in dados:
                dados["categoria"] = self.determinar_categoria(pergunta)
                self.salvar_conhecimento()
                
            y.append(dados["categoria"])
            
        self.categorias = list(set(y))  # Lista de categorias únicas
        
        return X, y
        
    def treinar_modelo(self):
        """Treina um modelo de ML mais avançado com os dados existentes"""
        if not ML_DISPONIVEL:
            return False
            
        try:
            X, y = self.preparar_dados_treinamento()
            
            if X is None or len(X) < 5:
                return False
                
            # Cria um pipeline com vetorização TF-IDF e classificador
            # Agora usando Random Forest que é mais poderoso que Naive Bayes
            self.vetorizador = TfidfVectorizer(
                tokenizer=word_tokenize, 
                stop_words=stopwords.words('portuguese'),
                ngram_range=(1, 2),  # Inclui unigramas e bigramas
                min_df=1,
                max_features=5000
            )
            
            # Random Forest como classificador principal
            self.modelo = RandomForestClassifier(
                n_estimators=100,
                max_depth=None,
                min_samples_split=2,
                random_state=42
            )
            
            # Treina o modelo
            X_vetorizado = self.vetorizador.fit_transform(X)
            self.modelo.fit(X_vetorizado, y)
            
            # Avalia o modelo (opcional)
            if len(X) >= 10:  # Só avalia se tiver dados suficientes
                try:
                    X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)
                    X_treino_vetorizado = self.vetorizador.fit_transform(X_treino)
                    X_teste_vetorizado = self.vetorizador.transform(X_teste)
                    
                    self.modelo.fit(X_treino_vetorizado, y_treino)
                    acuracia = self.modelo.score(X_teste_vetorizado, y_teste)
                    print(f"Acurácia do modelo: {acuracia:.4f}")
                except:
                    # Se falhar na avaliação, continua com o treinamento normal
                    X_vetorizado = self.vetorizador.fit_transform(X)
                    self.modelo.fit(X_vetorizado, y)
            
            # Salva o modelo treinado
            joblib.dump(self.modelo, self.modelo_arquivo)
            joblib.dump(self.vetorizador, self.vetorizador_arquivo)
            
            self.ml_inicializado = True
            return True
        except Exception as e:
            print(f"Erro ao treinar modelo: {str(e)}")
            return False
            
    def prever_resposta_ml(self, pergunta):
        """Prevê uma resposta usando técnicas avançadas de ML"""
        if not self.ml_inicializado:
            return None
            
        try:
            # Normaliza e vetoriza a pergunta
            pergunta_norm = self.normalizar_texto(pergunta)
            pergunta_vetorizada = self.vetorizador.transform([pergunta_norm])
            
            # Prevê a categoria com probabilidades
            categorias_previstas = self.modelo.predict_proba(pergunta_vetorizada)[0]
            categorias_ordenadas = [(self.categorias[i], prob) for i, prob in enumerate(categorias_previstas)]
            categorias_ordenadas.sort(key=lambda x: x[1], reverse=True)
            
            # Considera as top 2 categorias se tiverem confiança suficiente
            categorias_potenciais = []
            for categoria, confianca in categorias_ordenadas[:2]:
                if confianca >= self.limiar_confianca:
                    categorias_potenciais.append((categoria, confianca))
            
            if not categorias_potenciais:
                return None
                
            # Para cada categoria potencial, encontra a melhor resposta
            melhores_respostas = []
            for categoria_prevista, confianca_categoria in categorias_potenciais:
                # Encontra a melhor resposta na categoria prevista
                respostas_categoria = []
                for p, dados in self.conhecimento.items():
                    # Pula versões alternativas para evitar duplicatas
                    if dados.get('e_versao_alternativa', False):
                        continue
                        
                    if dados.get("categoria") == categoria_prevista:
                        # Calcula similaridade semântica
                        p_vetorizado = self.vetorizador.transform([p])
                        similaridade = cosine_similarity(pergunta_vetorizada, p_vetorizado)[0][0]
                        
                        # Adiciona relevância por uso frequente
                        contador_uso = dados.get("contador_uso", 0)
                        fator_uso = min(contador_uso / 10, 0.2)  # Máximo 20% de boost
                        
                        # Pontuação final é a similaridade + fator de uso frequente
                        pontuacao = similaridade + fator_uso
                        
                        respostas_categoria.append((p, pontuacao, dados["resposta"], confianca_categoria))
                
                if respostas_categoria:
                    # Retorna a resposta mais similar
                    melhor_pergunta, pontuacao, melhor_resposta, confianca = max(respostas_categoria, key=lambda x: x[1])
                    melhores_respostas.append((melhor_pergunta, pontuacao, melhor_resposta, confianca))
            
            if not melhores_respostas:
                return None
                
            # Escolhe a melhor resposta entre todas as categorias
            melhor_pergunta, pontuacao, melhor_resposta, confianca = max(melhores_respostas, key=lambda x: x[1] * x[3])
            
            # Incrementa o contador de uso
            self.conhecimento[melhor_pergunta]["contador_uso"] += 1
            self.salvar_conhecimento()
            
            # Adiciona explicação sobre o aprendizado por ML de forma mais natural
            frases_ml = []
            
            # Se alta confiança, não precisa explicar
            if confianca > 0.85:
                return melhor_resposta
                
            # Se média confiança, ocasionalmente explica
            if 0.7 <= confianca <= 0.85 and random.random() < 0.15:  # 15% de chance
                frases_ml = [
                    f"Acredito que ",
                    f"Pelo que entendi, ",
                    f"Baseado no que sei, ",
                    f"Posso dizer que "
                ]
            
            # Se confiança mais baixa, explica mais frequentemente
            if self.limiar_confianca <= confianca < 0.7 and random.random() < 0.3:  # 30% de chance
                frases_ml = [
                    f"Se entendi corretamente, ",
                    f"Interpretando sua pergunta, ",
                    f"Analisando o que você perguntou, ",
                    f"Com base no meu entendimento, "
                ]
            
            if frases_ml:
                return random.choice(frases_ml) + melhor_resposta
                
            return melhor_resposta
            
        except Exception as e:
            print(f"Erro na previsão ML: {str(e)}")
            return None
        
    def pesquisar_web(self, pergunta):
        """Pesquisa informações na web de forma mais robusta e inteligente"""
        try:
            # Remove palavras muito comuns para focar na essência da pergunta
            termos = re.sub(r'\b(o que é|como|quando|onde|por que|quem|qual|me fale sobre|pesquise|busque)\b', '', pergunta, flags=re.IGNORECASE)
            termos = termos.strip()
            
            # Extrai palavras-chave importantes
            tokens = self.tokenizar_texto(self.normalizar_texto(termos))
            if len(tokens) > 2:
                # Se tiver muitas palavras, usa apenas as mais relevantes
                termos_busca = ' '.join(tokens[:5])  # Limita a 5 palavras-chave
            else:
                termos_busca = termos
                
            # Adiciona modificadores para melhorar a busca
            if "definição" in pergunta.lower() or "o que é" in pergunta.lower():
                termos_busca += " definição"
            elif "como" in pergunta.lower():
                termos_busca += " tutorial"
            elif "quando" in pergunta.lower() or "data" in pergunta.lower():
                termos_busca += " data"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            url = f"https://www.google.com/search?q={termos_busca.replace(' ', '+')}"
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tenta extrair snippets com respostas diretamente do Google
            for seletor in ['.hgKElc', '.IZ6rdc', '.kno-rdesc', '.LGOjhe', '.wDYxhc']:
                resposta_direta = soup.select(seletor)
                if resposta_direta:
                    info = resposta_direta[0].get_text().strip()
                    if info and len(info) > 20:  # Garante que é uma resposta significativa
                        # Armazena esse conhecimento para uso futuro
                        self.adicionar_conhecimento(pergunta, info, fonte="web:google")
                        return self.formatar_resposta_web(info)
                    
            # Caso não encontre snippet direto, procura nos resultados normais
            resultados = soup.select('.tF2Cxc')
            if resultados:
                # Coleta os 3 primeiros resultados para ter mais contexto
                respostas = []
                for resultado in resultados[:3]:
                    titulo = resultado.select('h3')
                    descricao = resultado.select('.VwiC3b')
                    
                    if titulo and descricao:
                        titulo_texto = titulo[0].get_text().strip()
                        descricao_texto = descricao[0].get_text().strip()
                        
                        if len(descricao_texto) > 20:  # Garante que é uma descrição significativa
                            respostas.append(f"{titulo_texto}: {descricao_texto}")
                
                if respostas:
                    # Combina as respostas em um único texto informativo
                    resposta_combinada = "\n\n".join(respostas[:2])  # Limita a 2 resultados para não ficar muito longo
                    
                    # Armazena o conhecimento para uso futuro
                    self.adicionar_conhecimento(pergunta, resposta_combinada, fonte="web:google_search")
                    return self.formatar_resposta_web(resposta_combinada)
            
            # Se chegar aqui, não encontrou nada relevante
            return "Não consegui encontrar informações específicas sobre isso na web. Poderia reformular sua pergunta?"
            
        except Exception as e:
            return f"Ocorreu um erro ao buscar informações na web: {str(e)}"
    
    def formatar_resposta_web(self, texto):
        """Formata a resposta da web para melhorar a legibilidade"""
        # Limita o tamanho da resposta
        if len(texto) > 500:
            # Tenta cortar no final de uma sentença
            posicao_corte = texto[:500].rfind('.')
            if posicao_corte > 300:  # Se encontrou um ponto final depois de pelo menos 300 caracteres
                texto = texto[:posicao_corte+1]
            else:
                texto = texto[:500] + "..."
        
        # Adiciona atribuição
        frases_intro = [
            "De acordo com a web: ",
            "Encontrei esta informação: ",
            "Segundo minha pesquisa: ",
            "Conforme as fontes online: ",
            "A web indica que: "
        ]
        
        return random.choice(frases_intro) + texto
            
    def analisar_comando_aprendizado(self, texto):
        """Analisa comandos relacionados ao aprendizado"""
        texto = texto.lower()
        
        # Comando para ensinar explicitamente
        if "aprenda que" in texto or "aprenda isso" in texto:
            padrao = r"aprenda que (.+?) é (.+)"
            match = re.search(padrao, texto)
            
            if match:
                conceito = match.group(1).strip()
                definicao = match.group(2).strip()
                return self.adicionar_conhecimento(conceito, definicao)
                
            # Formato alternativo: "aprenda isso: [pergunta] -> [resposta]"
            padrao_alt = r"aprenda isso:? (.+?) ?-> ?(.+)"
            match_alt = re.search(padrao_alt, texto)
            
            if match_alt:
                pergunta = match_alt.group(1).strip()
                resposta = match_alt.group(2).strip()
                return self.adicionar_conhecimento(pergunta, resposta)
                
        # Comando para obter conhecimento
        for padrao in ["o que é", "quem é", "me fale sobre", "definição de", "significado de"]:
            if padrao in texto:
                consulta = texto.split(padrao, 1)[1].strip()
                if consulta:
                    # Verifica se já tem o conhecimento
                    resposta = self.buscar_conhecimento(consulta)
                    if resposta:
                        return resposta
                        
                    # Caso contrário, busca na web
                    return self.pesquisar_web(consulta)
                    
        # Perguntas gerais com formato de pergunta
        if texto.endswith('?') and len(texto) > 10:
            resposta = self.buscar_conhecimento(texto)
            if resposta:
                return resposta
                
            # Se não tem o conhecimento, tenta buscar na web
            return self.pesquisar_web(texto)
            
        return None
    
    def normalizar_texto(self, texto):
        """Normaliza o texto removendo acentos, pontuação e convertendo para minúsculas"""
        # Remove acentos
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        # Converte para minúsculas
        texto = texto.lower()
        # Remove pontuação, mantendo espaços
        texto = re.sub(r'[^\w\s]', ' ', texto)
        # Remove espaços extras
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto
        
    def tokenizar_texto(self, texto):
        """Tokeniza o texto em palavras, removendo stopwords"""
        if not ML_DISPONIVEL:
            return texto.split()
            
        try:
            # Tokeniza
            tokens = word_tokenize(texto, language='portuguese')
            # Remove stopwords
            stop_words = set(stopwords.words('portuguese'))
            tokens = [token for token in tokens if token not in stop_words and len(token) > 1]
            return tokens
        except:
            return texto.split()
            
    def stemizar_texto(self, tokens):
        """Aplica stemming às palavras (reduz às raízes)"""
        if not ML_DISPONIVEL or not hasattr(self, 'stemmer'):
            return tokens
            
        try:
            return [self.stemmer.stem(token) for token in tokens]
        except:
            return tokens
            
    def extrair_entidades(self, texto):
        """Extrai possíveis entidades como nomes, locais, datas, etc."""
        entidades = []
        
        # Padrões simples de datas (dd/mm/yyyy, dd-mm-yyyy)
        padrao_data = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        datas = re.findall(padrao_data, texto)
        if datas:
            entidades.extend([('DATA', data) for data in datas])
            
        # Padrões de horas (hh:mm, hh:mm:ss)
        padrao_hora = r'\b\d{1,2}:\d{2}(:\d{2})?\b'
        horas = re.findall(padrao_hora, texto)
        if horas:
            entidades.extend([('HORA', hora) for hora in horas])
            
        # Possíveis nomes próprios (palavras capitalizadas)
        palavras = texto.split()
        for palavra in palavras:
            if palavra and palavra[0].isupper() and palavra.lower() not in stopwords.words('portuguese'):
                entidades.append(('NOME', palavra))
                
        return entidades
        
    def adicionar_ao_contexto(self, pergunta, resposta):
        """Adiciona uma interação ao contexto de curto prazo"""
        agora = datetime.now()
        self.memoria_curto_prazo.append({
            "timestamp": agora.strftime("%Y-%m-%d %H:%M:%S"),
            "pergunta": pergunta,
            "resposta": resposta
        })
        
        # Limita o tamanho da memória de curto prazo
        if len(self.memoria_curto_prazo) > self.max_memoria_curto_prazo:
            self.memoria_curto_prazo.pop(0)
            
    def obter_contexto_recente(self, n=3):
        """Obtém as últimas n interações do contexto"""
        return self.memoria_curto_prazo[-n:] if len(self.memoria_curto_prazo) > 0 else []
