import os
import csv
import requests
from tqdm import tqdm
from urllib.parse import urlparse
from openpyxl import Workbook
import pandas as pd

def download_file(url, filename, folder):
    try:
        # Verifica se a pasta 'downloads' existe e cria se não existir
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        # Verifica se a pasta do ambiente existe e cria se não existir
        folder_path = os.path.join('downloads', folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Extrai a extensão do nome do arquivo na URL
        filename_extension = os.path.splitext(urlparse(url).path)[-1]

        # Junta o diretório 'downloads' com o nome do arquivo e sua extensão
        filepath = os.path.join(folder_path, filename + filename_extension)

        # Verifica se o arquivo já existe na pasta 'downloads'
        if os.path.exists(filepath):
            print(f"O arquivo {filename} já existe na pasta 'downloads'. Pulando o download.")
            return 'OK'

        print(f"\nSalvando arquivo como: {filepath}")

        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

        with open(filepath, 'wb') as f:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(data)

        progress_bar.close()

        # Retorna o tamanho do arquivo baixado
        return 'OK', os.path.getsize(filepath)

        if total_size != 0 and progress_bar.n != total_size:
            print("Erro ao fazer o download completo do arquivo.")
            return 'Erro'
        else:
            print(f"Download concluído: {filepath}")
            return 'OK'

    except Exception as e:
        print(f"Erro ao fazer o download de {url}: {e}")
        return 'Erro'

def create_report(downloads):
    # Cria um novo arquivo Excel e adiciona uma planilha
    wb = Workbook()
    ws = wb.active

    # Adiciona cabeçalhos à planilha
    ws.append(['URL', 'Nome do Arquivo', 'Ambiente', 'Status'])

    # Adiciona dados à planilha
    for download in downloads:
        url, filename, ambiente, status = download  # Desempacota a lista
        ws.append([url, filename, ambiente, status])

    # Salva o arquivo Excel
    wb.save('relatorio_downloads.xlsx')

def main():
    # Nome do arquivo CSV
    csv_file = 'links.csv'

    # Abrindo o arquivo CSV e lendo os links, nomes de arquivo e ambientes
    df = pd.read_csv(csv_file, delimiter=';')

    # Atualiza o arquivo links.csv com o tamanho do arquivo
    for index, row in df.iterrows():
        url = row['URL']  # Link de download
        filename = row['Nome do Arquivo']  # Nome do arquivo
        folder = row['Ambiente']  # Pasta onde o arquivo deve ser salvo
        status, size = download_file(url, filename, folder)
        df.at[index, 'Tamanho'] = size if status == 'OK' else 0

    # Salva o arquivo CSV atualizado
    df.to_csv(csv_file, sep=';', index=False)

if __name__ == "__main__":
    main()