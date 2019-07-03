#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ftplib
import re
import datetime
import configparser
import sys
import io
import codecs

from package.util.util import *
from package.rtc_controller.rtc_controller import *

print("Inicio da Execucao:"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
try:
    config = configparser.ConfigParser()
    config.read('arquivos/properties')
    """Carrega configuracoes do arquivo properties"""
    sistema=sys.argv[1]
    ambiente=sys.argv[2]
    job_name=sys.argv[3]
    demanda=sys.argv[4]
    id_executor=sys.argv[5]
    """Carrega parametros passados na linha de comando"""
    print(sistema+'-'+ambiente)
    diretorio_fonte=config.get('JAZZ','fonte')
    workspace=config.get('JAZZ','workspace')
    load_scm=config.getboolean('JAZZ','load_scm')
    hostname = config.get('ZOS.'+ambiente,'host')
    port = int(config.get('ZOS.'+ambiente,'port'))
    ftp_user = config.get('ZOS.FTP.'+ambiente,'user')
    ftp_pass = config.get('ZOS.FTP.'+ambiente,'password')
    arquivolog = 'arquivos/log/'+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+'.'+sistema+'.'+ambiente+'.log'
    """Determina o arquivo de log geral"""
    lib_batch=config.get(sistema+'.'+ambiente,'lib_batch')
    lib_booklib=config.get(sistema+'.'+ambiente,'lib_booklib')
    lib_cics=config.get(sistema+'.'+ambiente,'lib_cics')
    
except:
    print("\n\n\033[101mParametros invalidos ou nao encontrados no arquivo arquivos/properties\n\n\tFavor ler o README.md do projeto\033[0m \n\n")
    print(sys.exc_info())

arquivo_submeter=open('arquivos/SUBMETER','w')
"""Determina o arquivo onde sera gravado o Programa a que sera submetido apos o upload para o PDS Mainframe"""
arquivo_job=open('arquivos/JOBS','w')
"""Determina o arquivo onde serao gravados os JOB ID's apos a submissao do JCL"""
saida = open(arquivolog,'w')
saida.write('######################  Carregamento de fontes ######################\n')
saida.write('WORKSPACE:'+workspace+'. AMBIENTE:'+sistema+'/'+ambiente+'\n')
if load_scm:
    print('#############################  Login RTC ############################\n')
    saida.write(login_rtc().decode('latin-1')+'\n')
    print('######################  Carregamento de fontes ######################\n')
    saida.write(carrega_workspace(workspace,diretorio_fonte).decode('latin-1')+'\n')

print('######################  Upload de codigo fonte ######################\n')

with open('arquivos/PROGRAMAS', 'rt') as f:
    """Itera o arquivo PROGRAMAS para identificar o PROGRAMA ou BOOKLIB e o formato de compilao"""
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
                fp=None
                try:
                    fp=codecs.open(diretorio_fonte+'/COBOL.GCS/BATCH/'+programa+'.cbl','r',encoding='utf-8')
                except:
                    fp=codecs.open(diretorio_fonte+'/COBOL.GCS/BATCH/'+programa+'.cbl','r')
                arquivo=io.BytesIO(codecs.encode(fp.read(),'iso8859-1','ignore'))
                ftp = ftplib.FTP()
                ftp.connect(hostname, port)
                ftp.set_debuglevel(0)
                ftp.login(ftp_user, ftp_pass)
                ftp.voidcmd('site filetype=seq')
                ftp.pwd()
                ftp.cwd('..')
                ftp.cwd(lib_batch)
                result = ftp.storlines('STOR '+programa, arquivo)
                ftp.close()
                print('{};{};{}\n'.format(programa,classe,tipo))
                arquivo_submeter.write('{};{};{}\n'.format(programa,classe,tipo))
            except:
                print("{};{}\n".format(programa,sys.exc_info()[1]))
                saida.write("{};{}\n".format(programa,sys.exc_info()[1]))
        if(classe=='CICS'):
            tipo = compilacao[2]
            try:
                fp=None
                try:
                    fp=codecs.open(diretorio_fonte+'/COBOL.GCS/CICS/'+programa+'.cics','r',encoding='utf-8')
                except:
                    fp=codecs.open(diretorio_fonte+'/COBOL.GCS/CICS/'+programa+'.cics','r')
                arquivo=io.BytesIO(codecs.encode(fp.read(),'iso8859-1','ignore'))
                ftp = ftplib.FTP()
                ftp.connect(hostname, port)
                ftp.set_debuglevel(0)
                ftp.login(ftp_user, ftp_pass)
                ftp.voidcmd('site filetype=seq')
                ftp.sendcmd("site sbd=(IBM-1047,ISO8859-1)")
                ftp.pwd()
                ftp.cwd('..')
                ftp.cwd(lib_cics)
                result = ftp.storlines('STOR '+programa,arquivo)
                ftp.close()
                print('{};{};{}\n'.format(programa,classe,tipo))
                arquivo_submeter.write('{};{};{}\n'.format(programa,classe,tipo))
            except:
                print("{};{}\n".format(programa,sys.exc_info()[1]))
                saida.write("{};{}\n".format(programa,sys.exc_info()[1]))
        if(classe=='BOOKLIB'):
            try:
                fp=None
                try:
                    fp=codecs.open(diretorio_fonte+'/COBOL.GCS/BOOKLIB/'+programa+'.bkl','r',encoding='utf-8')
                except:
                    fp=codecs.open(diretorio_fonte+'/COBOL.GCS/BOOKLIB/'+programa+'.bkl','r')
                arquivo=io.BytesIO(codecs.encode(fp.read(),'iso8859-1','ignore'))
                ftp = ftplib.FTP()
                ftp.connect(hostname, port)
                ftp.encoding='latin-1'
                ftp.set_debuglevel(0)
                ftp.login(ftp_user, ftp_pass)
                ftp.voidcmd('site filetype=seq')
                ftp.pwd()
                ftp.cwd('..')
                ftp.cwd(lib_booklib)
                result = ftp.storlines('STOR '+programa,arquivo)
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

saida.write('######################     SUBMISSAO DE JOBS   ######################\n')
saida.write('JOBNAME:'+job_name+'\n')
print('######################     SUBMISSAO DE JOBS   ######################\n')
with open('arquivos/SUBMETER', 'rt') as f:
    """ Itera o arquivo com os programas que deram sucesso no Upload para o PDS Maiframe """
    for linha in f.read().split('\n'):
        if len(linha)==0:
            continue
        compilacao = linha.split(';')
        programa = compilacao[0]
        classe  = compilacao[1]
        if(classe=='BATCH' or classe=='CICS'):
            tipo = compilacao[2]
            job_modelo='arquivos/cartao/'+sistema+'/'+ambiente+'/'+tipo+'.model'
            job_final='arquivos/cartao/'+sistema+'/JOB'+sistema+tipo
            model=open(job_modelo,'rt')
            job=sub_string(model,'ID_EXECUTOR',id_executor)
            job=sub_string(job,'DEMANDA_COMPILACAO',demanda)
            job=sub_string(job,'ID_PROGRAMA',programa)
            job=sub_string(job,'JOB_NAME',job_name)
            job=sub_string(job,'DATA_HORA',datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
            job=sub_string(job,'WLM_PROGRAMA','DES_SP'+programa[:4]+'01')
            final=open(job_final,'w+',encoding='latin-1')
            final.write(job.read())
            final.close()
            job_file=open(job_final,'rb')
            result = ftp.storlines('STOR JOB'+sistema,job_file)
            job_number= re.search(r'(JOB[0-9]{5})',result)
            if job_number:
                print("{};{}\n".format(programa,job_number.group(1)))
                saida.write("{};{}\n".format(programa,job_number.group(1)))
                arquivo_job.write("{};{}\n".format(programa,job_number.group(1)))
            else:
                print("{};{}\n".format(programa,'Erro submissão'))
                saida.write("{};{}\n".format(programa,'Erro submissão'))
            saida.flush()
arquivo_job.close()
saida.write('###################### Encerramento compilacao  ######################\n')
print('###################### Encerramento compilacao  ######################\n')
saida.close()
ftp.quit()
print("Fim da Execucao:"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
