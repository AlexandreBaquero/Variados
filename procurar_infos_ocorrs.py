from datetime import datetime
from modulos.funcoes import BancoDados
from modulos.sisbb import Sisbb


log_file = './log.txt'
with open(log_file, 'w') as log:
    log.write('Inicio do processamento: {timestamp}.\n'
              .format(timestamp=datetime.today()))

    # Buscar no Banco de Dados as ocorrências do dia
    banco = BancoDados()
    sql_busca_ocorrs = 'select num_ocorr, cvn, dt_toc, ctr, valor ' \
                       'from ocorrencias_teste ' \
                       'where ver = 1 ' \
                       'order by dt_toc, cvn;'
    lista_tuplas_ocorrs = banco.buscar_dados(sql_busca_ocorrs)
    lista_ocorrs = [[item_tupla for item_tupla in cada_tupla] for cada_tupla in lista_tuplas_ocorrs]
    # print(lista_ocorrs[:5])
    # print(len(lista_ocorrs))

    # Buscar no Banco de Dados as competências do dia para verificar processamento e repasse
    sql_busca_compets = 'select cvn, dt_toc ' \
                        'from ocorrencias_teste ' \
                        'where ver = 1 ' \
                        'group by cvn, dt_toc ' \
                        'order by dt_toc, cvn;'
    lista_tuplas_compets = banco.buscar_dados(sql_busca_compets)
    lista_compets = [[item_tupla for item_tupla in cada_tupla] for cada_tupla in lista_tuplas_compets]
    # print(lista_compets[:5])
    # print(len(lista_compets))

    banco.fechar_conexao()

    log.write('Buscas no BD realizadas, Inicio da busca de informações no SISBB: {timestamp}.\n'
              .format(timestamp=datetime.today()))
    # Entrar no SISBB
    s = Sisbb()
    chave = 'F0431861'
    senha = '82195769'
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
    for item in lista_compets:
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

    log.write('Busca de processamento realizada, Inicio da busca de repasse realizado: {timestamp}.\n'
              .format(timestamp=datetime.today()))

    # Sair do TOC 01 e ir para o TOC 21 buscar o repasse
    s.teclar('f3')
    s.colar(20, 19, '21', 'enter')
    s.aguardar_sem_cursor(1, 3, "TOCM0007")
    s.colar(4, 29, '         ', 'enter')
    s.aguardar_sem_cursor(23, 3, "Informe")

    # Loop das competências a buscar o repasse, apenas as competências que apresentam Falso para processamento
    for item in lista_compets:
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

    log.write('Busca de repasse realizada, buscando infos das competencias para cada ocorrencia: {timestamp}.\n'
              .format(timestamp=datetime.today()))

    # Gravando a informação da lista das competências na lista das ocorrências
    for ocorrencia in lista_ocorrs:
        for competencia in lista_compets:
            if ocorrencia[1] == competencia[0] and ocorrencia[2] == competencia[1]:
                ocorrencia.append(competencia[2])
                ocorrencia.append(competencia[3])

    log.write('Busca das informacoes realizada, Inicio da busca de informacoes das ocorrencias: {timestamp}.\n'
              .format(timestamp=datetime.today()))

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
    for item in lista_ocorrs:
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
        item.append(s.copiar(7, 20, 17))
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

        s.teclar('f3')
        s.aguardar_sem_cursor(3, 24, "Tratamento")
        s.teclar('f3')
        s.aguardar_sem_cursor(3, 23, "Ajustes")
        s.colar(4, 23, "                 ")
        s.colar(5, 23, "    ")
        s.colar(5, 66, "               ", "enter")

    log.write('Busca de informacoes das ocorrencias realizada, Inicio da gravacao do resultado: {timestamp}.\n'
              .format(timestamp=datetime.today()))

    with open('./ocorrencias_teste_2.csv', 'w') as regularizar:
        for item in lista_ocorrs:
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
    banco.load_data('./ocorrencias_teste_2.csv', 'ocorrencias_teste_2')

    log.write('Fim do processamento: {timestamp}.\n'
              .format(timestamp=datetime.today()))

    # Imprimindo informações para verificação simples
    print(lista_compets[:5])
    print(lista_ocorrs[:10])
    print("Fim!")
