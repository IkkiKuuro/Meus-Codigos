import os
import shutil
from pathlib import Path

def organizar_arquivos(diretorio):
    # Mapeamento de extensões para pastas
    categorias = {
        # Imagens
        'imagens': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
        # Documentos
        'documentos': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx'],
        # Vídeos
        'videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'],
        # Áudios
        'audios': ['.mp3', '.wav', '.ogg', '.flac', '.aac'],
        # Compactados
        'compactados': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        # Executáveis
        'executaveis': ['.exe', '.msi', '.deb', '.rpm'],
        # Outros
        'outros': []
    }
    
    # Converte o diretório para um objeto Path
    diretorio_path = Path(diretorio)
    
    # Cria as pastas se não existirem
    for categoria in categorias:
        pasta = diretorio_path / categoria
        if not pasta.exists():
            pasta.mkdir()
            print(f"Pasta '{categoria}' criada.")
    
    # Conta quantos arquivos foram movidos
    total_movidos = 0
    
    # Percorre os arquivos no diretório
    for item in diretorio_path.iterdir():
        # Se for um arquivo (não uma pasta)
        if item.is_file():
            # Obtém a extensão do arquivo
            extensao = item.suffix.lower()
            destino = None
            
            # Encontra a categoria para este arquivo
            for categoria, extensoes in categorias.items():
                if extensao in extensoes:
                    destino = diretorio_path / categoria / item.name
                    break
            
            # Se não encontrou categoria específica, vai para 'outros'
            if destino is None:
                destino = diretorio_path / 'outros' / item.name
            
            # Move o arquivo se o destino não existir
            if not destino.exists():
                try:
                    shutil.move(str(item), str(destino))
                    print(f"Movido: {item.name} → {destino.parent.name}")
                    total_movidos += 1
                except Exception as e:
                    print(f"Erro ao mover {item.name}: {e}")
    
    print(f"\nTotal de {total_movidos} arquivos organizados.")

if __name__ == "__main__":
    # Pergunta ao usuário qual diretório organizar
    diretorio = input("Digite o caminho do diretório para organizar (Enter para usar Downloads): ")
    
    # Se não forneceu diretório, usa a pasta Downloads
    if not diretorio:
        diretorio = str(Path.home() / "Downloads")
    
    if os.path.isdir(diretorio):
        print(f"Organizando arquivos em: {diretorio}")
        organizar_arquivos(diretorio)
    else:
        print(f"O diretório '{diretorio}' não existe.")