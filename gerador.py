import ftplib
import re
import datetime
import configparser
import sys
import io

from package.util.util import *
from package.rtc_controller.rtc_controller import *

print("Início da Execução:"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
try:
    config = configparser.ConfigParser()
    config.read('arquivos/properties')
    """Carrega configurações do arquivo properties"""

    sistema=sys.argv[1]
    ambiente=sys.argv[2]
    job_name=sys.argv[3]
    """Carrega parâmetros passados na linha de comando"""
    print(sistema+'-'+ambiente)

    diretorio_fonte=config.get('JAZZ','fonte')
    workspace=config.get('JAZZ','workspace')
    hostname = config.get('ZOS.'+ambiente,'host')
    port = int(config.get('ZOS.'+ambiente,'port'))
    ftp_user = config.get('ZOS.FTP.'+ambiente,'user')
    ftp_pass = config.get('ZOS.FTP.'+ambiente,'password')

    arquivolog = 'arquivos/log/'+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+'.'+sistema+'.'+ambiente+'.log'
    """Determina o arquivo de log geral"""
    id_executor = 'MS'+datetime.datetime.now().strftime("%y%m%d")
    lib_batch=config.get(sistema+'.'+ambiente,'lib_batch')
    lib_booklib=config.get(sistema+'.'+ambiente,'lib_booklib')
    lib_cics=config.get(sistema+'.'+ambiente,'lib_cics')

except:
    print("\n\n\033[101mParâmetros inválidos ou não encontrados no arquivo arquivos/properties\n\n\tFavor ler o README.md do projeto\033[0m \n\n")
    print(sys.exc_info()[1])

arquivo_submeter=open('arquivos/SUBMETER','w')
"""Determina o arquivo onde será gravado o Programa a que será submetido após o upload para o PDS Mainframe"""
arquivo_job=open('arquivos/JOBS','w')
"""Determina o arquivo onde serão gravados os JOB ID's após a submissão do JCL"""
saida = open(arquivolog,'w')
saida.write('######################  Carregamento de fontes ######################\n')
print('######################  Carregamento de fontes ######################\n')
#saida.write(carrega_workspace(workspace,diretorio_fonte).decode('latin-1')+'\n')
job_final='arquivos/cartao/GERADO/JOB'+sistema+tipo
saida.write('######################     SUBMISSÃO DE JOBS   ######################\n')
print('######################     SUBMISSÃO DE JOBS   ######################\n')
with open('arquivos/PROGRAMAS', 'rt') as f:
    """ Itera o arquivo com os programas que deram sucesso no Upload para o PDS Maiframe """
    for linha in f.read().split('\n'):
        if len(linha)==0:
            continue
        compilacao = linha.split(';')
        programa = compilacao[0]
        classe  = compilacao[1]
        try:
            if(classe=='BATCH' or classe=='CICS'):
                tipo = compilacao[2]
                model=open(job_modelo,'rt')
                job=sub_string(model,'ID_EXECUTOR',id_executor)
                job=sub_string(job,'ID_PROGRAMA',programa)
                job=sub_string(job,'JOB_NAME',job_name)
                job=sub_string(job,'DATA_HORA',datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
                job=sub_string(job,'WLM_PROGRAMA','DES_SP'+programa[:4]+'01')
                final=open(job_final,'w+',encoding='latin-1')
                final.write(job.read())
        except:
            print("Erro ao Gerar cartão:"+programa)



            saida.flush()
arquivo_job.close()
saida.write('###################### Encerramento compilação  ######################\n')
print('###################### Encerramento compilação  ######################\n')
saida.close()
print("Fim da Execução:"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
