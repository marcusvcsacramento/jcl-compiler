import ftplib
import re
import datetime
import configparser
import sys

from package.util.util import *
from package.rtc_controller.rtc_controller import *


config = configparser.ConfigParser()
config.read('arquivos/properties')

sistema=sys.argv[0]
ambiente=sys.argv[1]
diretorio_fonte=config.get('JAZZ','fonte')
workspace=config.get('JAZZ','workspace')


hostname = config.get('ZOS.'+ambiente,'host')
port = int(config.get('ZOS.'+ambiente,'port'))
ftp_user = config.get('ZOS.FTP.'+ambiente,'user')
ftp_pass = config.get('ZOS.FTP.'+ambiente,'password')

arquivolog = 'arquivos/log/'+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+'.log'
id_executor = 'MS'+datetime.datetime.now().strftime("%y%m%d")
lib_batch=config.get(sistema+'.'+ambiente,'lib_batch')
lib_booklib=config.get(sistema+'.'+ambiente,'lib_booklib')
lib_cics=config.get(sistema+'.'+ambiente,'lib_cics')

saida = open(arquivolog,'w')
saida.write('######################  Carregamento de fontes ######################\n')
saida.write(carrega_workspace(workspace,diretorio_fonte).decode('latin-1')+'\n')

saida.write('######################  Upload de código fonte ######################\n')
with open('arquivos/PROGRAMAS', 'rt') as f:
    result=''
    for linha in f.read().split('\n'):
        if len(linha)==0:
            continue
        compilacao = linha.split(';')
        programa = compilacao[0]
        classe  = compilacao[1]
        try:
            if(classe=='BATCH'):
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
            if(classe=='CICS'):
                job=open(diretorio_fonte+'/COBOL.GCS/BATCH/'+programa+'.cbl','rb')
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
            if(classe=='BOOKLIB'):
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
            saida.write("{};{}\n".format(programa,result))
        except:
            saida.write("{};{}\n".format(programa,sys.exc_info()[1]))
        f.close()

ftp = ftplib.FTP()
ftp.connect(hostname, port)
ftp.set_debuglevel(0)
ftp.login(ftp_user, ftp_pass)
ftp.voidcmd('site filetype=jes')

saida.write('######################     SUBMISSÃO DE JOBS   ######################\n')
with open('arquivos/PROGRAMAS', 'rt') as f:
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
                saida.write("{};{}\n".format(programa,job_number.group(1)))
            else:
                saida.write("{};{}\n".format(programa,'Erro submissão'))
saida.write('###################### Encerramento compilação  ######################\n')
saida.close()
ftp.quit()