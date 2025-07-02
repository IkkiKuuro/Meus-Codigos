#!/usr/bin/env python3
"""
Script para inicializar modelos de machine learning para o Kuro
"""

import json
import joblib
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from pathlib import Path

# Define o diretório base
diretorio_base = Path(__file__).parent.parent
diretorio_conhecimento = diretorio_base / "aprendizado"
arquivo_conhecimento = diretorio_conhecimento / "conhecimento.json"
modelo_arquivo = diretorio_conhecimento / "modelo_ml.joblib"
vetorizador_arquivo = diretorio_conhecimento / "vetorizador.joblib"

# Baixa recursos necessários do NLTK
print("Baixando recursos do NLTK...")
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    print("Erro ao baixar recursos do NLTK. Verificar conexão com a internet.")

# Carrega o conhecimento
print("Carregando conhecimento...")
if arquivo_conhecimento.exists():
    with open(arquivo_conhecimento, 'r', encoding='utf-8') as f:
        conhecimento = json.load(f)
    print(f"Conhecimento carregado: {len(conhecimento)} itens encontrados.")
else:
    print("Arquivo de conhecimento não encontrado!")
    exit(1)

# Prepara os dados para treinamento
print("Preparando dados para treinamento...")
X = []  # Perguntas/entradas
y = []  # Categorias

for pergunta, dados in conhecimento.items():
    X.append(pergunta)
    y.append(dados.get("categoria", "geral"))

categorias = list(set(y))
print(f"Categorias encontradas: {categorias}")

# Cria e treina o modelo
print("Treinando modelo...")
try:
    # Cria um vetorizador TF-IDF
    vetorizador = TfidfVectorizer(
        tokenizer=word_tokenize, 
        stop_words=stopwords.words('portuguese'),
        min_df=1
    )
    
    # Vetoriza as perguntas
    X_vetorizado = vetorizador.fit_transform(X)
    
    # Cria e treina o modelo Naive Bayes
    modelo = MultinomialNB()
    modelo.fit(X_vetorizado, y)
    
    # Salva o modelo e o vetorizador
    joblib.dump(modelo, modelo_arquivo)
    joblib.dump(vetorizador, vetorizador_arquivo)
    
    print(f"Modelo salvo em {modelo_arquivo}")
    print(f"Vetorizador salvo em {vetorizador_arquivo}")
    print("Treinamento concluído com sucesso!")
    
except Exception as e:
    print(f"Erro durante o treinamento: {str(e)}")
