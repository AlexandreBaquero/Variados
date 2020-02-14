from datetime import datetime
from modulos.funcoes import BancoDados
from modulos.sisbb import Sisbb


def inicializar_bd_ocorrencias(arquivo_sas):
    banco = BancoDados()
    tabela_nova = 'ocorrencias_novo'
    banco.dropar_tabela(tabela=tabela_nova)
    sql_criar = 'CREATE TABLE `estudo`.`ocorrencias_novo` ' \
                '(`num_ocorr` INT NOT NULL,  ' \
                '`cvn` INT NULL,  ' \
                '`valor` FLOAT NOT NULL,  ' \
                '`dt_cobr` VARCHAR(45) NULL,  ' \
                '`dt_toc` VARCHAR(45) NULL,  ' \
                '`ctr` INT NULL,  ' \
                '`gm` TINYINT NULL,  ' \
                '`ocorr_201` TINYINT NULL,  ' \
                '`ocorr_701` TINYINT NULL,  ' \
                '`ver` TINYINT NULL,  ' \
                '`ts_inclusao` TIMESTAMP default current_timestamp,  ' \
                '`processado` TINYINT NULL default NULL, ' \
                '`rpss_realizado` TINYINT NULL default NULL, ' \
                'PRIMARY KEY (`num_ocorr`, `valor`));'
    banco.criar_tabela(sql_criar=sql_criar)
    banco.load_data(arquivo=arquivo_sas, tabela=tabela_nova)
    banco.fechar_conexao()


def buscar_competencias():
    banco = BancoDados()
    sql_busca = 'select cvn, dt_toc ' \
                'from ocorrencias_novo ' \
                'where cvn in (select * from cvns_gerfin) and ' \
                'dt_toc <= current_date() ' \
                'group by cvn, dt_toc ' \
                'order by dt_toc, cvn;'
    tuplas_competencias = banco.buscar_dados(sql_select=sql_busca)
    banco.fechar_conexao()
    lista_competencias = [[item_tupla for item_tupla in cada_tupla] for cada_tupla in tuplas_competencias]
    return lista_competencias


def buscar_ocorrencias():
    banco = BancoDados()
    sql_busca = 'select num_ocorr, cvn, dt_toc, ctr, valor ' \
                'from ocorrencias_novo ' \
                'where cvn in (select * from cvns_gerfin) and ' \
                'dt_toc <= current_date() ' \
                'order by dt_toc, cvn;'
    tuplas_ocorrencias = banco.buscar_dados(sql_select=sql_busca)
    banco.fechar_conexao()
    lista_ocorrencias = [[item_tupla for item_tupla in cada_tupla] for cada_tupla in tuplas_ocorrencias]
    return lista_ocorrencias


def buscar_processamentos(chave, senha, lista_ocorrencias, lista_competencias):
    s = Sisbb()
    s.acesso_inicial(chave=chave, senha=senha, cic=True)

    # Entrar no TOC 01-a para verificar tratamento da competência
    s.colar(15, 14, "toc")
    s.colar(16, 14, senha, 'enter')
    s.aguardar_sem_cursor(10, 13, "Responsabilidade")
    s.teclar('f3')
    s.aguardar_sem_cursor(1, 3, "TOCM0000")
    s.colar(20, 19, '01')
    s.colar(21, 19, 'a', 'enter')
    s.aguardar_sem_cursor(8, 30, "partir")
    s.colar(12, 28, 'x', 'enter')
    s.aguardar_sem_cursor(1, 3, "TOCM0040")
    s.colar(4, 21, '         ', 'enter')
    s.aguardar_sem_cursor(23, 3, "Informe")

    # Loop nas competências buscadas
    for item in lista_competencias:
        cvn = str(item[0])
        dia = str(item[1][8:])
        mes = str(item[1][5:7])
        ano = str(item[1][:4])
        s.colar(4, 21, cvn)
        s.colar(5, 21, dia)
        s.colar(5, 26, mes)
        s.colar(5, 31, ano, 'enter')
        s.aguardar_sem_cursor(6, 54, "Tratamento")
        if s.copiar(6, 80, 1) == "S":
            item.append('1')
        else:
            item.append('0')
        # print(item)
        s.colar(4, 21, '         ')
        s.colar(5, 21, '  ')
        s.colar(5, 26, '  ')
        s.colar(5, 31, '    ')

    # Sair do TOC 01 e ir para o TOC 21 buscar o repasse
    s.teclar('f3')
    s.colar(20, 19, '21', 'enter')
    s.aguardar_sem_cursor(1, 3, "TOCM0007")
    s.colar(4, 29, '         ', 'enter')
    s.aguardar_sem_cursor(23, 3, "Informe")

    # Loop das competências a buscar o repasse, apenas as competências que apresentam Falso para processamento
    for item in lista_competencias:
        if item[2] == '1':
            # Indicando verdadeiro para as competências que já apresentam verdadeiro para processamento, por economia
            item.append('1')
        else:
            cvn = str(item[0])
            dia = str(item[1][8:])
            mes = str(item[1][5:7])
            ano = str(item[1][:4])
            s.colar(4, 29, cvn)
            s.colar(6, 29, dia)
            s.colar(6, 34, mes)
            s.colar(6, 39, ano, 'enter')
            s.teclar('enter')
            s.aguardar_sem_cursor(23, 3, 'Selecione')
            if s.copiar(13, 27, 27) == ":                    0,00 D":
                item.append('1')
            else:
                item.append('0')
            # print(item)
            s.colar(4, 29, '         ', 'enter')
            s.aguardar_sem_cursor(23, 3, "Informe")

    # Gravando a informação da lista das competências na lista das ocorrências
    for ocorrencia in lista_ocorrencias:
        for competencia in lista_competencias:
            if ocorrencia[1] == competencia[0] and ocorrencia[2] == competencia[1]:
                ocorrencia.append(competencia[2])
                ocorrencia.append(competencia[3])

    # Buscar as informações de rescisão e situação do contrato no aplicativo CDC através do TOC 11-a, 01, F9, ocorr, F2
    s.teclar('f3')
    s.aguardar_sem_cursor(1, 3, "TOCM0000")
    s.colar(20, 19, '11')
    s.colar(21, 19, 'a', 'enter')
    s.aguardar_sem_cursor(8, 30, "partir")
    s.colar(12, 28, 'x', 'enter')
    s.aguardar_sem_cursor(1, 3, "TOCMN010")
    s.colar(21, 19, '01', 'enter')
    s.aguardar_sem_cursor(1, 3, "TOCM0028")
    s.teclar('f9')
    s.aguardar_sem_cursor(1, 3, "TOCM2816")
    s.colar(5, 66, '               ', 'enter')

    # Loop das ocorrências para buscar informações no aplicativo CDC via TOC
    for item in lista_ocorrencias:
        s.colar(5, 66, str(item[0]), 'enter')
        s.aguardar_sem_cursor(12, 14, str(item[0]))
        # print(item[0])
        # print(item[1])
        s.colar(12, 3, "x", "enter")
        s.aguardar_sem_cursor(5, 23, str(item[0]))
        s.teclar('f2')
        if s.copiar(6, 16, 6) == "Existe":
            s.teclar('enter')
        s.aguardar_sem_cursor(4, 20, str(item[3]))
        tela = s.copiar_tela()
        item.append(s.copiar(7, 20, 30, tela=tela))
        if s.copiar(7, 66, 15) == "DEBITO SUSPENSO":
            item.append("1")
        else:
            item.append("0")

        # Se foi processado e é 701, verificar se é rescisão
        if item[5] == "0" or item[4] < 0:
            item.append("0")
        else:
            s.teclar('f2')
            s.aguardar_sem_cursor(3, 43, "Outros")
            s.colar(20, 54, "08", "enter")

            paginas = True
            rescisao = []
            while paginas:
                for linha in range(7, 19):
                    rescisao.append(s.copiar(linha, 42, 3))
                s.teclar('f8')
                if s.copiar(23, 4, 5) == "ltima":
                    paginas = False
            set_rescisao = set(rescisao)
            if "191" in set_rescisao:
                item.append("1")
            else:
                item.append("0")
            set_rescisao.clear()
            s.teclar('f3')
            s.aguardar_sem_cursor(3, 43, "Outros")
            s.teclar('f3')
            s.aguardar_sem_cursor(3, 44, "Consulta")

        # Voltar pra tela inicial
        s.teclar('f3')
        s.aguardar_sem_cursor(3, 24, "Tratamento")
        s.teclar('f3')
        s.aguardar_sem_cursor(3, 23, "Ajustes")
        s.colar(4, 23, "                 ")
        s.colar(5, 23, "    ")
        s.colar(5, 66, "               ", "enter")
    return lista_ocorrencias


def atualizar_bd_ocorrencias(nova_lista_ocorrencias):
    ano = str(datetime.today().year)
    mes = str(datetime.today().month)
    dia = str(datetime.today().day)

    arquivo_atualizado = './arquivos/{ano}/{mes}/{dia}/ocorrencias_atualizadas.csv'.format(ano=ano, mes=mes, dia=dia)
    tabela_nova = 'ocorrencias_novo_final'
    sql_nova_tabela = 'CREATE TABLE `estudo`.`ocorrencias_novo_final` ' \
                      '(`num_ocorr` INT NOT NULL, ' \
                      '`cvn` INT NOT NULL, ' \
                      '`dt_toc` VARCHAR(45) NOT NULL, ' \
                      '`ctr` INT NOT NULL, ' \
                      '`valor` FLOAT NOT NULL, ' \
                      '`processado` TINYINT NOT NULL, ' \
                      '`rpss_realizado` TINYINT NOT NULL, ' \
                      '`situacao_ctr` VARCHAR(45) NOT NULL, ' \
                      '`deb_susp` TINYINT NOT NULL, ' \
                      '`rescisao` TINYINT NOT NULL, ' \
                      'PRIMARY KEY (`num_ocorr`));'

    # Gravando as informacoes em um arquivo
    with open(arquivo_atualizado, 'w') as regularizar:
        for item in nova_lista_ocorrencias:
            regularizar.write('{num};{cvn};{data};{ctr};{valor};{process};{rpss_realizado};{sit};{deb_susp};{resc}\n'
                              .format(num=item[0],
                                      cvn=item[1],
                                      data=item[2],
                                      ctr=item[3],
                                      valor=item[4],
                                      process=item[5],
                                      rpss_realizado=item[6],
                                      sit=item[7],
                                      deb_susp=item[8],
                                      resc=item[9]))

    # Gravando as informações das ocorrências no Banco de Dados
    banco = BancoDados()
    banco.dropar_tabela(tabela_nova)
    banco.criar_tabela(sql_nova_tabela)
    banco.load_data(arquivo_atualizado, tabela_nova)
    banco.fechar_conexao()


def processamento():
    # Inputs necessarios para o processamento
    arquivo_sas = './arquivos/ocorrencias_sas.csv'
    arq_log = './logs/{ano}/{mes}/{dia}/log_processamento.txt'.format(ano=datetime.today().year,
                                                                      mes=datetime.today().month,
                                                                      dia=datetime.today().day)

    # Processamento em si - Escrita do LOG
    with open(arq_log, 'w') as log:
        chave = input("Digite sua chave: ")
        senha = input("Digite sua senha: ")
        log.write('Realizado por {chave}.\n'
                  'Arquivo utilizado: {arquivo}\n'
                  '\n'
                  'Inicio do processamento                        : {data_hora}\n'
                  .format(chave=chave,
                          arquivo=arquivo_sas,
                          data_hora=datetime.today()))
        inicializar_bd_ocorrencias(arquivo_sas=arquivo_sas)
        lista_competencias = buscar_competencias()
        lista_ocorrencias = buscar_ocorrencias()
        log.write('Banco de dados atualizado                      : {data_hora}\n'.format(data_hora=datetime.today()))
        nova_lista_ocorrencias = buscar_processamentos(chave=chave,
                                                       senha=senha,
                                                       lista_ocorrencias=lista_ocorrencias,
                                                       lista_competencias=lista_competencias)
        log.write('Busca de processamentos concluída              : {data_hora}\n'.format(data_hora=datetime.today()))
        atualizar_bd_ocorrencias(nova_lista_ocorrencias=nova_lista_ocorrencias)
        log.write('Banco de Dados atualizado com os processamentos: {data_hora}\n'.format(data_hora=datetime.today()))


processamento()
