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

### Uso

#### Compilação

1. No arquivo **PROGRAMAS** deve ser informado o programa seguindo o padrão:
  1. «PROGRAMA»**;**«CLASSE»**;**«TIPO COMPILACAO»
    * CLASSE pode ser **BATCH** ou **BOOKLIB**
    * TIPO COMPILACAO deve correspondere ao nome do arquivo model no diretório _arquivos/cartao_: se houver _**VA4002B;BATCH;SUB_ONLINE**_ deve haver um cartão de nome **SUB_ONLINE.model**

Executar em linha de comando: `python submissao.py «SISTEMA» «AMBIENTE»`

#### Validação

Após a execução dos Jobs basta executar em linha de comando:`python validacao.py TOM PRD`
