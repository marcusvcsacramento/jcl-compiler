import ftplib
import re
import datetime
import configparser
import sys
import io

config = configparser.ConfigParser()
config.read('arquivos/properties')
"""Carrega configurações do arquivo properties"""

sistema=sys.argv[1]
ambiente=sys.argv[2]

"""Carrega parâmetros passados na linha de comando"""
print(sistema+'-'+ambiente)

hostname = config.get('ZOS.'+ambiente,'host')
port = int(config.get('ZOS.'+ambiente,'port'))
ftp_user = config.get('ZOS.FTP.'+ambiente,'user')
ftp_pass = config.get('ZOS.FTP.'+ambiente,'password')


ftp = ftplib.FTP()
ftp.connect(hostname, port)
ftp.set_debuglevel(2)
ftp.login(ftp_user, ftp_pass)
ftp.voidcmd('site filetype=seq')
ftp.cwd('..')
ftp.cwd('HOM.ZEK.JCLFONTE')

with open('arquivos/CPJOB', 'rt') as f:
    for linha in f.read().split('\n'):
        if len(linha)==0:
            continue
        submissao = linha.split(';')
        job = submissao[0]
        try:
            with open('arquivos/job_sias/'+job,'w+', errors='ignore',encoding='latin-1') as cartao_job:
                ftp.retrlines('RETR ' + job, lambda s: cartao_job.write(re.sub('[ \t]+$','\n',s )))
            cartao_job.close()
        except:
            print('Job Não encontrado:'+job)
ftp.quit()
