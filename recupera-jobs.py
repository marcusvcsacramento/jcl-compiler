import ftplib
import re
import datetime
import configparser
import sys
import io

config = configparser.ConfigParser()
config.read('arquivos/properties')
"""Carrega configuraç;oeses do arquivo properties"""

sistema=sys.argv[1]
ambiente=sys.argv[2]

"""Carrega parÃ¢metros passados na linha de comando"""
print(sistema+'-'+ambiente)

hostname = config.get('ZOS.'+ambiente,'host')
port = int(config.get('ZOS.'+ambiente,'port'))
ftp_user = config.get('ZOS.FTP.'+ambiente,'user')
ftp_pass = config.get('ZOS.FTP.'+ambiente,'password')


ftp = ftplib.FTP()
ftp.connect(hostname, port)
ftp.set_debuglevel(0)
ftp.login(ftp_user, ftp_pass)
ftp.voidcmd('site filetype=seq')
ftp.cwd('..')
ftp.cwd('PRD.ZEK.JCLFONTE')

with open('arquivos/CPJOB', 'rt') as f:
    for linha in f.read().split('\n'):
        if len(linha)==0:
            continue
        submissao = linha.split(';')
        job = submissao[0]
        try:
            with open('arquivos/job_smart/'+job+'.jcl','w+', errors='ignore',encoding='utf-8') as cartao_job:
                ftp.retrlines('RETR ' + job, lambda s: cartao_job.write(re.sub('[ \t]+$','\n',s )))
            cartao_job.close()
        except:
            print('Job Não encontrado:'+job)
            print(sys.exc_info()[1])
ftp.quit()
