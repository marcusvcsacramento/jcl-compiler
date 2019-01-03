import ftplib
import re
import datetime
import configparser

from package.util.util import *

config = configparser.ConfigParser()
config.read('arquivos/properties')

hostname = config.get('zos','host')
port = int(config.get('zos','port'))
ftp_user = config.get('zos.ftp','user')
ftp_pass = config.get('zos.ftp','password')
job_modelo='arquivos/cartao/SMART/dev/JDSZCOMP_I.model'
job_final='arquivos/cartao/SMART/dev/JDSZCOMP'

arquivolog = 'arquivos/log/'+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+'.log'

ftp = ftplib.FTP()
ftp.connect(hostname, port)
ftp.set_debuglevel(0)
ftp.login(ftp_user, ftp_pass)
ftp.voidcmd('site filetype=jes')
ftp.pwd()
saida = open(arquivolog,'w')
with open('arquivos/PROGRAMAS', 'rt') as f:
    for programa in f.read().split('\n'):
        if len(programa)==0:
            continue
        sub_string_file(job_modelo,'arquivos/cartao/SMART/dev/JDSZCOMP_I.tmp','ID_PROGRAMA',programa)
        sub_string_file('arquivos/cartao/SMART/dev/JDSZCOMP_I.tmp',job_final,'WLM_PROGRAMA','DES_SP'+programa[:4]+'01')
        job=open(job_final,'rb')
        result = ftp.storlines('STOR JDSZCOMP',job)
        job_number= re.search(r'(JOB[0-9]{5})',result)
        if job_number:
            saida.write("{};{}\n".format(programa,job_number.group(1)))
        else:
            saida.write("{};{}\n".format(programa,'Erro submissão'))
saida.close()
ftp.quit()