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
    job_name=sys.argv[4]

    data_execucao = datetime.datetime.now().strftime("%y%m%d")
    #data_execucao = '190604'
    data_load = datetime.datetime.now().strftime("%Y%m%d")
    #data_load = '20190604'

    hostname = config.get('ZOS.'+ambiente_tom,'host')
    port = int(config.get('ZOS.'+ambiente_tom,'port'))
    ftp_user = config.get('ZOS.FTP.'+ambiente_tom,'user')
    ftp_pass = config.get('ZOS.FTP.'+ambiente_tom,'password')

    hostname_load = config.get('ZOS.'+ambiente,'host')
    port_load = int(config.get('ZOS.'+ambiente,'port'))
    ftp_user_load = config.get('ZOS.FTP.'+ambiente,'user')
    ftp_pass_load = config.get('ZOS.FTP.'+ambiente,'password')

    load_lib = config.get(sistema+'.'+ambiente,'lib_load')
    tom = config.get('ZOS.'+ambiente_tom,'tom')
    tom_directory= 'arquivos/tom'
    load_directory= 'arquivos/load'
except:
    print("\n\n\033[101mParâmetros inválidos ou não encontrados no arquivo arquivos/properties\n\n\tFavor ler o README.md do projeto\033[0m \n\n")

arquivolog = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
saida = open('arquivos/log/'+arquivolog+'.'+sistema+'.'+ambiente+'.RESULTADO.log','w')
arquivo_jobs = 'arquivos/JOBS'
ftp = ftplib.FTP()
ftp.connect(hostname, port)
ftp.set_debuglevel(0)
ftp.login(ftp_user, ftp_pass)
ftp.set_pasv(False)
ftp.voidcmd('site filetype=seq')
ftp.sendcmd("site sbd=(IBM-1047,ISO8859-1)")
ftp.cwd('..')
saida.write('######################     VALIDACAO DE JOBS   ######################\n')
saida.write('JOBNAME:'+job_name+'. AMBIENTE:'+sistema+'/'+ambiente+'\n')
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
            print(tom+'.F'+data_execucao+'.'+job_name+'.'+jobnumber)
            with open(tom_directory+'/'+programa+'-'+jobnumber,'w', encoding="latin-1",errors="ignore") as arquivo:
                ftp.retrlines('RETR '+tom+'.F'+data_execucao+'.'+job_name+'.'+jobnumber,arquivo.write)

            arquivo.close()

            with open(tom_directory+'/'+programa+'-'+jobnumber,'r', encoding="latin-1") as arquivo:
                for linha in arquivo.read().split('\n'):
                    if len(linha)==0:
                        continue
                max_rc = re.search(r''+job_name+'[ ]{1,}ENDED.*RC=([0-9]{4})',linha)
                jcl_error = re.search(r'(JCL ERROR)',linha)
                abend = re.search(r'(ABEND=[A-Z0-9]{3,5})',linha)
            try:
                ftp_load = ftplib.FTP()
                ftp_load.connect(hostname_load, port_load)
                ftp_load.set_debuglevel(0)
                ftp_load.login(ftp_user_load, ftp_pass_load)
                ftp_load.set_pasv(False)
                ftp_load.voidcmd('site filetype=seq')
                ftp_load.sendcmd("site sbd=(IBM-1047,ISO8859-1)")
                ftp_load.cwd('..')
                ftp_load.cwd(load_lib)
                with open(load_directory+'/'+programa,'w', encoding="latin-1") as arquivo_load:
                    ftp_load.retrlines('RETR '+programa,arquivo_load.write)
                arquivo_load.close()
                ftp_load.close()

                with open(load_directory+'/'+programa,'r', encoding="latin-1") as arquivo_load:
                    for linha_load in arquivo_load.read().split('\n'):
                        if len(linha_load)==0:
                            continue
                        load_result=re.search(r'('+data_load+'[0-9]{4})',linha_load)
                arquivo_load.close()
                if load_result:
                    load_value = load_result.group(1)
            except:
                load_result=''
            color="\033[42m"
            if max_rc:
                if str(max_rc.group(1))!="0000" and str(max_rc.group(1)) != "0004":
                    color="\033[41m"
                print(color+"{};{};{};{}\033[0m\n".format(programa,jobnumber,max_rc.group(1),load_value))
                saida.write("{};{};{};{}\n".format(programa,jobnumber,max_rc.group(1),load_value))
            if jcl_error:
                print("\033[101m{};{};{};{}\033[0m\n".format(programa,jobnumber,jcl_error.group(1),load_value))
                saida.write("{};{};{};{}\n".format(programa,jobnumber,jcl_error.group(1),load_value))
            if abend:
                print("\033[101m{};{};{};{}\033[0m\n".format(programa,jobnumber,abend.group(1),load_value))
                saida.write("{};{};{};{}\n".format(programa,jobnumber,abend.group(1),load_value))
            saida.flush()
        except:
            error_text = 'Em Processamento'
            if str(sys.exc_info()[1]).find('not found') is not -1:
#                print(sys.exc_info()[1])
                error_text='Sem SYSOUT'

            print("{};{};{};{}\n".format(programa,jobnumber,error_text,load_value))
            saida.write("{};{};{};{}\n".format(programa,jobnumber,error_text,load_value))
saida.close()
ftp.close()
