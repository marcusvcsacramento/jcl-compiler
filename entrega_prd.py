import ftplib
import re
import datetime
import configparser
import sys
import io
import codecs

from package.util.util import *
from package.rtc_controller.rtc_controller import *

diretorio_fonte = 'arquivos/fonte_gcs_hom'
carrega_workspace('SCRIPT.HOM.COBOL',diretorio_fonte).decode('latin-1')

ftp = ftplib.FTP()
ftp.connect('zosprd', 21)
ftp.encoding='latin-1'
ftp.set_debuglevel(0)
ftp.login('', '')
ftp.voidcmd('site filetype=seq')
ftp.pwd()
ftp.cwd('..')
ftp.cwd('PRD.GE.A.PGMLIB.COB2P')

var = input("Manda ver?")

log=open('arquivos/log/ENTREGA_PRD_JOB.log','w+')

log.write('Realizando entreas em Produção:\n- Origem:FLUXO-HOM(SCRIPT.HOM.COBOL)\n- Destino:PRD.GE.A.PGMLIB.COB2P\n')
with open('arquivos/PROGRAMAS', 'rt') as f:
    result=''
    for linha in f.read().split('\n'):
        if len(linha)==0:
            continue
        compilacao = linha.split(';')
        programa = compilacao[0]
        classe  = compilacao[1]
        fp=None
        try:
            fp=codecs.open(diretorio_fonte+'/COBOL.GCS/BATCH/'+programa+'.cbl','r',encoding='utf-8')
        except:
            fp=codecs.open(diretorio_fonte+'/COBOL.GCS/BATCH/'+programa+'.cbl','r')
        arquivo=io.BytesIO(codecs.encode(fp.read(),'iso8859-1','ignore'))
        result = ftp.storlines('STOR '+programa, arquivo)
        log.write('Programa '+programa+'. '+result+'\n')

try:
    fj=codecs.open('arquivos/cartao/SIAS/GERADO/JSIASJV1','r',encoding='utf-8')
except:
    fj=codecs.open('arquivos/cartao/SIAS/GERADO/JSIASJV1','r')
arquivo=io.BytesIO(codecs.encode(fj.read(),'iso8859-1','ignore'))

ftp.cwd('PRD.V01.RDZ')
ftp.cwd('..')
result = ftp.storlines('STOR JPIASJV', arquivo)
log.write('Arquivo JPIASJV1 disponibilizado em:PRD.V01.RDZ')
#        result= ftp.delete(programa)
log.close()
ftp.close()
