import ftplib
import re
import datetime
import configparser
import sys

from package.util.util import *
from package.rtc_controller.rtc_controller import *


config = configparser.ConfigParser()
config.read('arquivos/properties')
"""Carrega configurações do arquivo properties"""

sistema=sys.argv[1]
ambiente=sys.argv[2]
"""Carrega parâmetros passados na linha de comando"""
print(sistema+'-'+ambiente)

diretorio_fonte=config.get('JAZZ','fonte')
workspace=config.get('JAZZ','workspace')
hostname = config.get('ZOS.'+ambiente,'host')
port = int(config.get('ZOS.'+ambiente,'port'))
ftp_user = config.get('ZOS.FTP.'+ambiente,'user')
ftp_pass = config.get('ZOS.FTP.'+ambiente,'password')

arquivolog = 'arquivos/log/'+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+'.log'
"""Determina o arquivo de log geral"""
id_executor = 'MS'+datetime.datetime.now().strftime("%y%m%d")
lib_batch=config.get(sistema+'.'+ambiente,'lib_batch')
lib_booklib=config.get(sistema+'.'+ambiente,'lib_booklib')
lib_cics=config.get(sistema+'.'+ambiente,'lib_cics')

arquivo_submeter=open('arquivos/SUBMETER','w')
"""Determina o arquivo onde será gravado o Programa a que será submetido após o upload para o PDS Mainframe"""
arquivo_job=open('arquivos/JOBS','w')
"""Determina o arquivo onde serão gravados os JOB ID's após a submissão do JCL"""
saida = open(arquivolog,'w')
saida.write('######################  Carregamento de fontes ######################\n')
print('######################  Carregamento de fontes ######################\n')
saida.write(carrega_workspace(workspace,diretorio_fonte).decode('latin-1')+'\n')
saida.write('######################  Upload de código fonte ######################\n')
print('######################  Upload de código fonte ######################\n')

with open('arquivos/PROGRAMAS', 'rt') as f:
    """Itera o arquivo PROGRAMAS para identificar o PROGRAMA ou BOOKLIB e o formato de compilação"""
    result=''
    for linha in f.read().split('\n'):
        if len(linha)==0:
            continue
        compilacao = linha.split(';')
        programa = compilacao[0]
        classe  = compilacao[1]
        if(classe=='BATCH'):
            tipo = compilacao[2]
            try:
                job=open(diretorio_fonte+'/COBOL.GCS/BATCH/'+programa+'.cbl','rb')
                ftp = ftplib.FTP()
                ftp.connect(hostname, port)
                ftp.set_debuglevel(0)
                ftp.login(ftp_user, ftp_pass)
                ftp.voidcmd('site filetype=seq')
                ftp.pwd()
                ftp.cwd('..')
                ftp.cwd(lib_batch)
                result = ftp.storlines('STOR '+programa,job)
                ftp.close()
                print('{};{};{}\n'.format(programa,classe,tipo))
                arquivo_submeter.write('{};{};{}\n'.format(programa,classe,tipo))
            except:
                print("{};{}\n".format(programa,sys.exc_info()[1]))
                saida.write("{};{}\n".format(programa,sys.exc_info()[1]))
        if(classe=='CICS'):
            tipo = compilacao[2]
            try:
                job=open(diretorio_fonte+'/COBOL.GCS/CICS/'+programa+'.cbl','rb')
                ftp = ftplib.FTP()
                ftp.connect(hostname, port)
                ftp.set_debuglevel(0)
                ftp.login(ftp_user, ftp_pass)
                ftp.voidcmd('site filetype=seq')
                ftp.pwd()
                ftp.cwd('..')
                ftp.cwd(lib_cics)
                result = ftp.storlines('STOR '+programa,job)
                ftp.close()
                print('{};{};{}\n'.format(programa,classe,tipo))
                arquivo_submeter.write('{};{};{}\n'.format(programa,classe,tipo))
            except:
                print("{};{}\n".format(programa,sys.exc_info()[1]))
                saida.write("{};{}\n".format(programa,sys.exc_info()[1]))
        if(classe=='BOOKLIB'):
            try:
                job=open(diretorio_fonte+'/COBOL.GCS/BOOKLIB/'+programa+'.bkl','rb')
                ftp = ftplib.FTP()
                ftp.connect(hostname, port)
                ftp.set_debuglevel(0)
                ftp.login(ftp_user, ftp_pass)
                ftp.voidcmd('site filetype=seq')
                ftp.pwd()
                ftp.cwd('..')
                ftp.cwd(lib_booklib)
                result = ftp.storlines('STOR '+programa,job)
                ftp.close()
                print('{};{}\n'.format(programa,classe))
            except:
                print("{};{}\n".format(programa,sys.exc_info()[1]))
                saida.write("{};{}\n".format(programa,result))
    arquivo_submeter.close()
    f.close()

ftp = ftplib.FTP()
ftp.connect(hostname, port)
ftp.set_debuglevel(0)
ftp.login(ftp_user, ftp_pass)
ftp.voidcmd('site filetype=jes')

saida.write('######################     SUBMISSÃO DE JOBS   ######################\n')
print('######################     SUBMISSÃO DE JOBS   ######################\n')
with open('arquivos/SUBMETER', 'rt') as f:
    """ Itera o arquivo com os programas que deram sucesso no Upload para o PDS Maiframe """
    for linha in f.read().split('\n'):
        if len(linha)==0:
            continue
        compilacao = linha.split(';')
        programa = compilacao[0]
        classe  = compilacao[1]
        if(classe=='BATCH'):
            tipo = compilacao[2]
            job_modelo='arquivos/cartao/'+sistema+'/'+ambiente+'/'+tipo+'.model'
            job_final='arquivos/cartao/'+sistema+'/JOB'+sistema+tipo
            sub_string_file(job_modelo,'arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCL.tmp','ID_PROGRAMA',programa)
            sub_string_file('arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCL.tmp','arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCLI.tmp','ID_EXECUTOR',id_executor)
            sub_string_file('arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCLI.tmp',job_final,'WLM_PROGRAMA','DES_SP'+programa[:4]+'01')
            job=open(job_final,'rb')
            result = ftp.storlines('STOR JOB'+sistema,job)
            job_number= re.search(r'(JOB[0-9]{5})',result)
            if job_number:
                print("{};{}\n".format(programa,job_number.group(1)))
                saida.write("{};{}\n".format(programa,job_number.group(1)))
                arquivo_job.write("{};{}\n".format(programa,job_number.group(1)))
            else:
                print("{};{}\n".format(programa,'Erro submissão'))
                saida.write("{};{}\n".format(programa,'Erro submissão'))
arquivo_job.close()
saida.write('###################### Encerramento compilação  ######################\n')
print('###################### Encerramento compilação  ######################\n')
saida.close()
ftp.quit()
