#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import ftplib
import re
import datetime
import codecs
import configparser
import sys

config = configparser.ConfigParser()
config.read('arquivos/properties')
ambiente=sys.argv[1]
data_execucao = datetime.datetime.now().strftime("%y%m%d")
hostname = config.get('ZOS.'+ambiente,'host')
port = int(config.get('ZOS.'+ambiente,'port'))
ftp_user = config.get('ZOS.FTP.'+ambiente,'user')
ftp_pass = config.get('ZOS.FTP.'+ambiente,'password')
tom = config.get('ZOS.'+ambiente,'tom')
tom_directory= 'arquivos/tom'

arquivolog = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
saida = open('arquivos/log/'+arquivolog+'_TOM.log','w')
arquivo_jobs = 'arquivos/JOBS'
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
        try:
            print(tom+'.F'+data_execucao+'.JHDEVOPS.'+jobnumber)
            with open(tom_directory+'/'+programa+'-'+jobnumber,'w', encoding="latin-1") as arquivo:
                ftp.retrlines('RETR '+tom+'.F'+data_execucao+'.JHDEVOPS.'+jobnumber,arquivo.write)
            arquivo.close()
            with open(tom_directory+'/'+programa+'-'+jobnumber,'r', encoding="latin-1") as arquivo:
                for linha in arquivo.read().split('\n'):
                    if len(linha)==0:
                        continue
                max_rc = re.search(r'JHDEVOPS ENDED.*RC=([0-9]{4})',linha)
                jcl_error = re.search(r'(JCL ERROR)',linha)
                abend = re.search(r'(ABEND=[A-Z0-9]{3,5})',linha)
                if max_rc:
                    print("{};{};{}\n".format(programa,jobnumber,max_rc.group(1)))
                    saida.write("{};{};{}\n".format(programa,jobnumber,max_rc.group(1)))
                if jcl_error:
                    print("{};{};{}\n".format(programa,jobnumber,jcl_error.group(1)))
                    saida.write("{};{};{}\n".format(programa,jobnumber,jcl_error.group(1)))
                if abend:
                    print("{};{};{}\n".format(programa,jobnumber,abend.group(1)))
                    saida.write("{};{};{}\n".format(programa,jobnumber,abend.group(1)))
        except:
            print("{};{};{}\n".format(programa,jobnumber,"Não encontrado SYSOUT"))
            saida.write("{};{};{}\n".format(programa,jobnumber,"Não encontrado SYSOUT"))


ftp.quit()
saida.close()
