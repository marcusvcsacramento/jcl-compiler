import ftplib
import re
import datetime
import configparser
import sys
import io

config = configparser.ConfigParser()
config.read('arquivos/properties')
"""Carrega configuraÃƒÂ§ÃƒÂµes do arquivo properties"""

sistema='SIAS'
ambiente='PRD'

"""Carrega parÃƒÂ¢metros passados na linha de comando"""
print(sistema+'-'+ambiente)

data_movimento=datetime.datetime.now().strftime("%y%m%d")
dia = int(data_movimento[4:])-1
data_movimento=data_movimento[:4]+'{:02d}'.format(dia)
print(data_movimento)

hostname = config.get('ZOS.'+ambiente,'host')
port = int(config.get('ZOS.'+ambiente,'port'))
ftp_user = config.get('ZOS.FTP.'+ambiente,'user')
ftp_pass = config.get('ZOS.FTP.'+ambiente,'password')


ftp = ftplib.FTP()
ftp.connect(hostname, port)
ftp.set_debuglevel(0)
ftp.login(ftp_user, ftp_pass)
ftp.voidcmd('site filetype=seq')
#ftp.cwd('..')
ftp.pwd()
arquivos=ftp.nlst('..')

with open('arquivos/CPJOB', 'rt') as f:
    for linha in f.read().split('\n'):
        if len(linha)==0:
            continue
        try:
            for arquivo in arquivos.read().split('\n'):
                print(arquivo)
                max_rc = re.search(r'',linha)
                for arquivo in tom_list.split('\n'):
                    if re.search(r''+linha):
                        print(linha)
        except:
            print(sys.exc_info()[1])
ftp.quit()
