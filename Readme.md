# JCL Compiler


Aplicação para compilação e deploy de código fonte Mainframe


### Requisitos

**RTC-scmTools-Linux64-6.0.4** ou **RTC-scmTools-Win64-6.0.4** adicionados ao **PATH** do SO:
* Windows: `set PATH=%PATH%;«Diretóio para o RTC»`
* Linux: `export PATH=$PATH:«Diretóio para o RTC»`
* Python **3.2.5**
* Workspace JAZZ para manipulação dos arquivos

### Configuração

1. Criar o Workspace Jazz do projeto e configurá-lo no arquivo _arquivos/properties_
2. Configurar Usuários e senhas no arquivo _arquivos/properties_
3. As Libs(PDS's) onde os programas serão submetidos devem ser informadas no arquivo _arquivos/properties_
4. As configurações de usuário e senha devem ser informados no arquivo _arquivos/properties_
5. Os Cartões de JOB utilizados se encontram em no arquivo _arquivos/cartao_

### SYSOUT na saída TIVOLI

Para que o acompanhamento seja realizado na validação dos JOB's via TIVOLI(TOM WEB) é necesário configurá-lo com as seguintes variáveis:
```
//JHHELLO JOB (00,EV),'ID_EXECUTOR',TIME=1440,REGION=0M,
//         CLASS=A,MSGCLASS=T,MSGLEVEL=(1,1)
//* Necessário o ROUTE PRINT para JES2PRD1 e MSGCLASS T. Além dos cartões SYSOUT e SYSPRINT
/*ROUTE PRINT JES2PRD1
//*DIARIA JV1. DATA:DATA_MOVIMENTO
//*DIARIA JV1. PERIODO:PERIODO_MOVIMENTO
//*DIARIA JV1. ANO MES:ANOMES_MOVIMENTO
//*DIARIA JV1. DIA:DIA_MOVIMENTO
//*DIARIA JV1. DATA ANTERIOR:DATA_ANTERIOR
//STEP0001 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSOUT   DD SYSOUT=*
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
//SYSUT2   DD SYSOUT=*
STEP COM SAIDA NO TOM WEB
//STEP0002 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSOUT   DD SYSOUT=*
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
//SYSUT2   DD SYSOUT=*
STEP COM SAIDA NO TOM WEB
//STEP0003 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSOUT   DD SYSOUT=*
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
//SYSUT2   DD SYSOUT=*
STEP COM SAIDA NO TOM WEB
//
```





### Uso

#### Compilação

1. No arquivo **PROGRAMAS** deve ser informado o programa seguindo o padrão:
  1. «PROGRAMA»**;**«CLASSE»**;**«TIPO COMPILACAO»
    * CLASSE pode ser **BATCH** ou **BOOKLIB**
    * TIPO COMPILACAO deve correspondere ao nome do arquivo model no diretório _arquivos/cartao_: se houver _**VA4002B;BATCH;SUB_ONLINE**_ deve haver um cartão de nome **SUB_ONLINE.model**

Executar em linha de comando: `python submissao.py «SISTEMA» «AMBIENTE» «JOBNAME»`

#### Validação

Após a execução dos Jobs basta executar em linha de comando:`python validacao.py «SISTEMA» «AMBIENTE» PRD «JOBNAME»`

#### Cartões de diária ou testes

#### Submissão

1. No arquivo **DIARIA** deve ser informado o programa seguindo o padrão:
  1. «NOME_JOB»
    * Deve correspondere ao nome do arquivo model no diretório _arquivos/cartao_

Executar em linha de comando: `python submissao.py «SISTEMA» «DIARIA_AMBIENTE» «DATA_MOVIMENTO» «PERIODO_MOVIMENTO» «DIA_ANTERIOR»`

#### Validação

Após a execução dos Jobs basta executar em linha de comando:`python validacao-job.py «SISTEMA» «DIARIA_AMBIENTE» PRD`
