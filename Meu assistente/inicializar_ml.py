#!/usr/bin/env python3
"""
Script manual para inicializar modelos de machine learning para o Kuro
"""

import json
import os
import sys
import pickle
from pathlib import Path

# Cria diretórios se não existirem
diretorio_base = Path(__file__).parent
diretorio_aprendizado = diretorio_base / "aprendizado"
diretorio_aprendizado.mkdir(exist_ok=True)

# Informações do modelo simulado
modelo_info = {
    "tipo": "MultinomialNB",
    "versao": "1.0",
    "categorias": ["saudação", "informação_pessoal", "tecnologia", "cotidiano", 
                  "ciência", "entretenimento", "saúde", "geral"],
    "n_features": 100,
    "criado_em": "2023-11-09"
}

# Salva um modelo simulado
with open(diretorio_aprendizado / "modelo_ml.joblib", "wb") as f:
    pickle.dump(modelo_info, f)
    print(f"Modelo simulado salvo em {diretorio_aprendizado / 'modelo_ml.joblib'}")

# Salva um vetorizador simulado
vetorizador_info = {
    "tipo": "TfidfVectorizer",
    "versao": "1.0",
    "stop_words": "portuguese",
    "n_features": 100,
    "criado_em": "2023-11-09"
}

with open(diretorio_aprendizado / "vetorizador.joblib", "wb") as f:
    pickle.dump(vetorizador_info, f)
    print(f"Vetorizador simulado salvo em {diretorio_aprendizado / 'vetorizador.joblib'}")

print("Inicialização concluída com sucesso!")
