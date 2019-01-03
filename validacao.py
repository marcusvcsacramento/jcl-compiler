
import os
import ftplib
import re
import datetime
import codecs

hostname = "zosdev"
port = 21
arquivolog = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
count_programa=0
response = os.system("ping -n 1 " + hostname)
if response == 0:
    saida = open(arquivolog+'_LOAD.log','w')
    print(hostname +' esta acessivel!')
    ftp = ftplib.FTP()
    ftp.connect(hostname, port)
    ftp.set_debuglevel(0)
    ftp.login("TE89323", "1983mv")
    ftp.set_pasv(False)
    ftp.voidcmd('site filetype=seq')
    ftp.cwd('..')
    ftp.cwd('DES.V01.LOAD')
    with open('PROGRAMAS', 'rt') as f:
        for programa in f.read().split('\n'):
            if len(programa)==0:
                continue
            with open('load/'+programa,'w') as arquivo:
                try:
                    ftp.retrlines('RETR ' + programa,arquivo.write)
                    arquivo.close()
                    texto_arquivo =  codecs.open('load/'+programa, "r", "latin-1")
                    texto = texto_arquivo.read()
                    texto_arquivo.close
                    load = re.search(r'(20181224[0-9]{4})',texto)
                    if load:
                        saida.write("{};{}\n".format(programa,load.group(1)))
                except:
                    saida.write("{};{}\n".format(programa,'Nao encontrada LOAD'))
    ftp.quit()
print("executou")
