import ftplib
import re
import datetime
import configparser
import sys
import io

from package.util.util import *
from package.rtc_controller.rtc_controller import *

diretorio_fonte = 'arquivos/fonte_gcs_hom'
#carrega_workspace('SCRIPT.HOM.COBOL',diretorio_fonte).decode('latin-1')

ftp = ftplib.FTP()
ftp.connect('zosprd', 21)
ftp.encoding='latin-1'
ftp.set_debuglevel(1)
ftp.login('elton', '1111bbb')
ftp.voidcmd('site filetype=seq')
ftp.pwd()
ftp.cwd('..')
#ftp.cwd('PRD.GE.A.PGMLIB.COB2P')
ftp.cwd('PRD.V01.RDZ')

var = input("Manda ver?")


with open('arquivos/PROGRAMAS', 'rt') as f:
    result=''
    for linha in f.read().split('\n'):
        if len(linha)==0:
            continue
        compilacao = linha.split(';')
        programa = compilacao[0]
        classe  = compilacao[1]
        fp=open(diretorio_fonte+'/COBOL.GCS/BATCH/'+programa+'','r',encoding='utf-8')
        job=io.BytesIO(fp.read().encode('latin-1'))
        result = ftp.storlines('STOR '+programa, job)
#        result= ftp.delete(programa)

ftp.close()
