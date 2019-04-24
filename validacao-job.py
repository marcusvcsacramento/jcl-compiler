#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import ftplib
import re
import datetime
import codecs
import configparser
import sys

try:
    config = configparser.ConfigParser()
    config.read('arquivos/properties')
    sistema=sys.argv[1]
    ambiente=sys.argv[2]
    ambiente_tom=sys.argv[3]
    data_execucao = datetime.datetime.now().strftime("%y%m%d")
    #data_execucao = '190411'
    data_load = datetime.datetime.now().strftime("%Y%m%d")
    #data_load = '20190411'

    hostname = config.get('ZOS.'+ambiente_tom,'host')
    port = int(config.get('ZOS.'+ambiente_tom,'port'))
    ftp_user = config.get('ZOS.FTP.'+ambiente_tom,'user')
    ftp_pass = config.get('ZOS.FTP.'+ambiente_tom,'password')

    hostname_load = config.get('ZOS.'+ambiente,'host')
    port_load = int(config.get('ZOS.'+ambiente,'port'))
    ftp_user_load = config.get('ZOS.FTP.'+ambiente,'user')
    ftp_pass_load = config.get('ZOS.FTP.'+ambiente,'password')

    load_lib = ''
    tom = config.get('ZOS.'+ambiente_tom,'tom')
    tom_directory= 'arquivos/tom'
    load_directory= 'arquivos/load'
except:
    print("\n\n\033[101mParâmetros inválidos ou não encontrados no arquivo arquivos/properties\n\n\tFavor ler o README.md do projeto\033[0m \n\n")

arquivolog = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
saida = open('arquivos/log/'+arquivolog+'.'+sistema+'.'+ambiente+'.RESULTADO.log','w')
arquivo_jobs = 'arquivos/JOBS_DIARIA'
ftp = ftplib.FTP()
ftp.connect(hostname, port)
ftp.set_debuglevel(0)
ftp.login(ftp_user, ftp_pass)
ftp.set_pasv(False)
ftp.voidcmd('site filetype=seq')
ftp.sendcmd("site sbd=(IBM-1047,ISO8859-1)")
ftp.cwd('..')

with open(arquivo_jobs,'r') as job:
    for linha in job.read().split('\n'):
        if len(linha)==0:
            continue
        compilacao = linha.split(';')
        programa = compilacao[0]
        jobnumber = compilacao[1]
        max_rc=''
        jcl_error=''
        abend=''
        load_result=''
        load_value=''
        try:
            print("######   Realizando GET do JOB de Homologação "+sistema.center(8)+" "+ambiente.center(8)+": "+programa.center(8)+"    ######")
            with open(tom_directory+'/'+programa+'-'+jobnumber,'w', encoding="latin-1") as arquivo:
                ftp.retrlines('RETR '+tom+'.F'+data_execucao+'.'+programa+'.'+jobnumber,lambda s: arquivo.write(re.sub('$','\n',s )))

            arquivo.close()
            with open(tom_directory+'/'+programa+'-'+jobnumber,'r', encoding="latin-1") as arquivo:
                for linha in arquivo.read().split('\n'):
                    #print('linha('+str(len(linha))+'):'+linha)
                    if len(linha)==0:
                        continue
                    teste=''+linha
                    max_rc = re.search(r''+programa+'.*[ ]{1,2}ENDED.*RC=([0-9]{4})',linha)
                    jcl_error = re.search(r'(JCL ERROR)',linha)
                    abend = re.search(r'(ABEND=[A-Z0-9]{3,5})',linha)
                    step = re.search(r'[ ]{2}[-]([A-Z0-9]{3,8})[ |A-Z]{4,}([0-9]{2,3}|[F][L][U][S][H])',linha)
                    data_movimento = re.search(r'[D][A][T][A][:].*([0-9]{6})',linha)
                    periodo_movimento = re.search(r'[P][E][R][I][O][D][O][:].*([0-9A-Z-]{20,20})',linha)
                    ano_mes_movimento = re.search(r'[A][N][O][ ][M][E][S][:].*([0-9]{4})',linha)
                    dia_movimento = re.search(r'[D][I][A][:].*([0-9]{2})',linha)
                    data_anterior_movimento = re.search(r'[D][A][T][A][ ][A][N][T][E][R][I][O][R][:].*([0-9A-Z]{6,})',linha)
                    if step:
                        color="\033[42m"
                        if str(step.group(1))!="STEP":
                            if str(step.group(2))=="999" or str(step.group(2))=="99":
                                color="\033[41m"
                            if str(step.group(2))=="FLUSH" or str(step.group(2))=="JCL ERROR" or str(step.group(2))=="ABEND":
                                color="\033[43m"
                            print(color+"  STEP {}:{}\033[0m".format(step.group(1).ljust(10),step.group(2).rjust(5)))
                    if max_rc:
                        color="\033[42m"
                        if str(max_rc.group(1))!="00" or str(max_rc.group(1))!="02" or str(max_rc.group(1))!="04":
                                color="\033[42m"
                        print("\nResultado da Execução: "+color+"{};{};{}\033[0m\n".format(programa,jobnumber,max_rc.group(1)))
                        saida.write("{};{};{}\n".format(programa,jobnumber,max_rc.group(1)))
                    if jcl_error:
                        print("\nResultado da Execução:\033[42m {};{};{}\033[0m\n".format(programa,jobnumber,jcl_error.group(1)))
                        saida.write("{};{};{}\n".format(programa,jobnumber,jcl_error.group(1)))
                    if abend:
                        print("\nResultado da Execução:\033[42m {};{};{}\033[0m\n".format(programa,jobnumber,abend.group(1)))
                        saida.write("{};{};{}\n".format(programa,jobnumber,abend.group(1)))
                    if data_movimento:
                        print("Data de Movimento:          {}".format(data_movimento.group(1)))
                    if periodo_movimento:
                        print("Período de Movimento:       {}".format(periodo_movimento.group(1)))
                    if ano_mes_movimento:
                        print("Ano Mês de Movimento:       {}".format(ano_mes_movimento.group(1)))
                    if dia_movimento:
                        print("Dia de Movimento:           {}".format(dia_movimento.group(1)))
                    if data_anterior_movimento:
                        print("Data Anterior de Movimento: {}".format(data_anterior_movimento.group(1)))
                    saida.flush()
        except:
            error_text = 'Em Processamento'
            if str(sys.exc_info()[1]).find('not found') is not -1:
                error_text='Sem SYSOUT'
                print(sys.exc_info())
            print("{};{};{}\n".format(programa,jobnumber,error_text))
            saida.write("{};{};{}\n".format(programa,jobnumber,error_text))
        print("###################################################################################")
saida.close()
ftp.close()
