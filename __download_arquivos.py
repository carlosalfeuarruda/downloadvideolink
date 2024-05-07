import os
import csv
import requests
from tqdm import tqdm
from urllib.parse import urlparse
from openpyxl import Workbook

def download_file(url, filename):
    try:
        # Verifica se a pasta 'downloads' existe e cria se não existir
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        # Extrai a extensão do nome do arquivo na URL
        filename_extension = os.path.splitext(urlparse(url).path)[-1]

        # Junta o diretório 'downloads' com o nome do arquivo e sua extensão
        filepath = os.path.join('downloads', filename + filename_extension)

        # Verifica se o arquivo já existe na pasta 'downloads'
        if os.path.exists(filepath):
            print(f"O arquivo {filename} já existe na pasta 'downloads'. Pulando o download.")
            return 'OK', os.path.getsize(filepath), os.path.getsize(filepath)

        response = requests.head(url)
        total_size = int(response.headers.get('content-length', 0))

        print(f" Salvando arquivo como: {filepath}")

        response = requests.get(url, stream=True)
        with open(filepath, 'wb') as f, tqdm(
                total=total_size, unit='B', unit_scale=True, desc=filename, ascii=True) as pbar:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                pbar.update(len(data))

        downloaded_size = os.path.getsize(filepath)
        if downloaded_size != total_size:
            print("Erro: O tamanho do arquivo baixado não corresponde ao tamanho esperado.")
            return 'Erro', 0, total_size
        else:
            print(f"Download concluído: {filepath}\n")
            return 'OK', downloaded_size, total_size

    except Exception as e:
        print(f"Erro ao fazer o download de {url}: {e}")
        return 'Erro', 0, 0

def create_report(downloads):
    # Cria um novo arquivo Excel e adiciona uma planilha
    wb = Workbook()
    ws = wb.active

    # Adiciona cabeçalhos à planilha
    ws.append(['URL', 'Nome do Arquivo', 'Tamanho Esperado', 'Tamanho Baixado', 'Status'])

    # Adiciona dados à planilha
    for download in downloads:
        url, filename, status = download
        status, downloaded_size, expected_size = status  # Separando o status, tamanho baixado e tamanho esperado

        ws.append([url, filename, expected_size, downloaded_size, status])

    # Salva o arquivo Excel
    wb.save('relatorio_downloads.xlsx')

def main():
    downloads = []

    # Nome do arquivo CSV
    csv_file = 'links.csv'

    # Abrindo o arquivo CSV e lendo os links e nomes de arquivo
    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file, delimiter=';')  # Define o ponto e vírgula como delimitador
        next(reader)  # Pula o cabeçalho, se houver
        for row in reader:
            url = row[0]  # Link de download
            filename = row[1]  # Nome do arquivo
            status = download_file(url, filename)
            downloads.append([url, filename, status])

    # Cria o relatório em Excel
    create_report(downloads)

if __name__ == "__main__":
    main()
