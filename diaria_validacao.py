import time
import ftplib
import re
import datetime
import configparser
import sys
import io

from package.zos_util.validacao_job import *
from package.util.util import *
from package.rtc_controller.rtc_controller import *


print("Início da Execução:"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
"""Carrega configurações do arquivo properties"""
config = configparser.ConfigParser()
config.read('arquivos/properties')

try:
    sistema=sys.argv[1]
    ambiente=sys.argv[2]
    data_movimento=sys.argv[3]
    periodo_movimento=sys.argv[4]
    data_anterior=sys.argv[5]
    anomes_movimento=data_movimento[:4]
    dia_movimento=data_movimento[-2:]
except:
    print("\n\n\033[101mParâmetros inválidos ou não encontrados no arquivo arquivos/properties\n\n\tFavor ler o README.md do projeto\033[0m \n\n")


"""Carrega parâmetros passados na linha de comando"""
print(sistema+'-'+ambiente)

hostname = config.get('ZOS.'+ambiente,'host')
port = int(config.get('ZOS.'+ambiente,'port'))
ftp_user = config.get('ZOS.FTP.'+ambiente,'user')
ftp_pass = config.get('ZOS.FTP.'+ambiente,'password')

arquivolog = 'arquivos/log/'+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+'.'+sistema+'.'+ambiente+'.DIARIA.log'
"""Determina o arquivo de log geral"""
id_executor = 'MS'+datetime.datetime.now().strftime("%y%m%d")
"""Determina o arquivo onde será gravado o Programa a que será submetido após o upload para o PDS Mainframe"""
arquivo_job=open('arquivos/JOBS_DIARIA','w')
"""Determina o arquivo onde serão gravados os JOB ID's após a submissão do JCL"""
saida = open(arquivolog,'w')


ftp = ftplib.FTP()
ftp.connect(hostname, port)
ftp.set_debuglevel(0)
ftp.login(ftp_user, ftp_pass)
ftp.sendcmd("site sbd=(IBM-1047,ISO8859-1)")
ftp.voidcmd('site filetype=jes')

saida.write('######################     SUBMISSÃO DE JOBS   ######################\n')
print('######################     SUBMISSÃO DE JOBS   ######################\n')
with open('arquivos/DIARIA', 'rt') as f:
    """ Itera o arquivo com os programas que deram sucesso no Upload para o PDS Maiframe """
    for linha in f.read().split('\n'):
        if len(linha)==0:
            continue
        submissao = linha.split(';')
        job = submissao[0]
        job_modelo='arquivos/cartao/'+sistema+'/'+ambiente+'/'+job+'.model'
        job_final='arquivos/cartao/'+sistema+'/JOB'+sistema+job
        sub_string_file(job_modelo,'arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCL.tmp','ID_EXECUTOR',id_executor)
        sub_string_file('arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCL.tmp','arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCLI.tmp','DATA_MOVIMENTO',data_movimento)
        sub_string_file('arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCLI.tmp','arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCLII.tmp','ANOMES_MOVIMENTO',anomes_movimento)
        sub_string_file('arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCLII.tmp','arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCLIII.tmp','DIA_MOVIMENTO',dia_movimento)
        sub_string_file('arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCLIII.tmp','arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCLIV.tmp','DATA_ANTERIOR',data_anterior)
        sub_string_file('arquivos/cartao/'+sistema+'/'+ambiente+'/JOBJCLIV.tmp',job_final,'PERIODO_MOVIMENTO',periodo_movimento)
        cartao_job=open(job_final,'rb')
        result = ftp.storlines('STOR JOB'+sistema,cartao_job)
        job_number= re.search(r'(JOB[0-9]{5})',result)
        if job_number:
            saida.write("{};{}\n".format(job,job_number.group(1)))
            arquivo_job.write("{};{}\n".format(job,job_number.group(1)))
            time.sleep(1)
            i=1
            check_job = True

            while check_job:
                check_job = verifica_retorno(job,job_number.group(1),sistema,ambiente)
                i=+1
                if check_job:
                    print("Aguardando "+job_number.group(1)+'|'+job+'-'+str(i))
                    time.sleep(1)
                    var = input("Verificar Execução? \n [1]-\033[42mSim\033[0m\n [2]-\033[41mNão\033[0m(Próximo JOB)\n [Ctrl + C]-\033[41mInterrompe toda execução\033[0m:\nDigite Opção: ")
                    if var == '2':
                        check_job=False
            print("###################################################################################")
        else:
            print("{};{}\n".format(job,'Erro submissão'))
            saida.write("{};{}\n".format(job,'Erro submissão'))
        saida.flush()
arquivo_job.close()
saida.write('###################### Encerramento Execução  ######################\n')
print('###################### Encerramento compilação  ######################\n')
saida.close()
ftp.quit()
print("Fim da Execução:"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
