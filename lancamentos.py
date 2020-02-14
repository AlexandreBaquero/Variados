from datetime import datetime
from modulos.sisbb import Sisbb
from modulos.funcoes import BancoDados


def buscar_rescisoes():
    # Buscar as ocorrencias que tem informacao de rescisao
    banco = BancoDados()
    sql_select = "select num_ocorr, valor, cvn, dt_toc " \
                 "from ocorrencias_novo_final " \
                 "where rescisao = 1 " \
                 "order by dt_toc, cvn, num_ocorr;"
    tupla_rescisoes = banco.buscar_dados(sql_select=sql_select)
    lista_rescisoes = [[item_tupla for item_tupla in cada_tupla] for cada_tupla in tupla_rescisoes]
    return lista_rescisoes


# def fazer_rescisao(chave, senha, lista_rescisoes):
#     # Gravar o lancamento de ajuste de rescisao
#     return 0


def buscar_debitar():
    # Buscar as ocorrencias que precisam ser debitadas
    banco = BancoDados()
    sql_select = "select num_ocorr, valor, cvn, dt_toc " \
                 "from ocorrencias_novo_final " \
                 "where valor < 0 and " \
                 "(processado = True or rpss_realizado = True) " \
                 "order by dt_toc, cvn, num_ocorr;"
    tupla_debitos = banco.buscar_dados(sql_select=sql_select)
    lista_debitos = [[item_tupla for item_tupla in cada_tupla] for cada_tupla in tupla_debitos]
    return lista_debitos


def debitar(chave, senha, lista_debitos):
    # Gravar o lancamento de ajuste de debito em conta
    s = Sisbb()
    s.acesso_inicial(chave=chave, senha=senha, cic=True)

    # Entrar no TOC 11-a-01-F9
    s.colar(15, 14, "toc")
    s.colar(16, 14, senha, 'enter')
    s.aguardar_sem_cursor(10, 13, "Responsabilidade")
    s.teclar('f3')
    s.aguardar_sem_cursor(1, 3, "TOCM0000")
    s.colar(20, 19, '11')
    s.colar(21, 19, 'a', 'enter')
    s.aguardar_sem_cursor(8, 30, "partir")
    s.colar(12, 28, 'x', 'enter')
    s.aguardar_sem_cursor(1, 3, "TOCMN010")
    s.colar(21, 19, "01", "enter")
    s.aguardar_sem_cursor(1, 3, "TOCM0028")
    s.teclar("f9")
    s.aguardar_sem_cursor(1, 3, "TOCM2816")
    s.colar(5, 66, '               ', 'enter')
    s.aguardar_sem_cursor(23, 3, "Informe")

    # Loop das ocorrências para realizar os lançamentos
    for item in lista_debitos:
        s.colar(5, 66, str(item[0]), 'enter')
        s.aguardar_sem_cursor(12, 14, str(item[0]))
        tela = s.copiar_tela()
        # valor = s.copiar(12, 45, 14, tela=tela)
        # print(valor)
        if s.copiar(12, 45, 14, tela=tela) == "0,00" or s.copiar(12, 77, 1, tela=tela) == "*":
            item.append('0')
            item.append('Ocorrência já tratada')
        else:
            s.colar(12, 3, "x", "enter")
            s.aguardar_sem_cursor(5, 23, str(item[0]))
            s.colar(17, 3, 'i', 'enter')
            if s.copiar(23, 3, 5) == "Grava":
                item.append('0')
                item.append('Gravação de Ajuste indisponível')
            else:
                s.aguardar_sem_cursor(12, 8, '906')
                s.colar(12, 3, 'x', 'enter')
                s.aguardar_sem_cursor(4, 23, str(item[0]))
                s.aguardar_sem_cursor(7, 23, str(item[2]))
                valor = str(item[1] * -1)
                # print(type(valor))
                s.colar(21, 23, valor, "enter")
                if s.copiar(23, 3, 5) == "Conta":
                    item.append('0')
                    item.append('Conta Corrente invalida para o tipo de ajuste.')
                else:
                    s.aguardar_sem_cursor(24, 3, "Confirma")
                    s.colar(24, 74, 's', 'enter')
                    s.aguardar_sem_cursor(23, 3, "Ajuste")
                    item.append('1')
                    item.append('Valor debitado')
                s.teclar('f3')
                s.aguardar_sem_cursor(1, 3, "TOCM2801")
                s.teclar('f3')
                s.aguardar_sem_cursor(1, 3, "TOCM285B")
            s.teclar('f3')
        s.colar(5, 66, '               ', 'enter')
        s.aguardar_sem_cursor(23, 3, 'Informe')
    return lista_debitos


def buscar_devolucoes():
    # Buscar as ocorrencias que precisam ser devolvidas
    banco = BancoDados()
    sql_select = "select num_ocorr, valor, cvn, dt_toc " \
                 "from ocorrencias_novo_final " \
                 "where valor > 0 and " \
                 "(processado = True or rpss_realizado = True) and " \
                 "rescisao = False and " \
                 "(situacao_ctr in ('Contrato renovado', 'CONTRATO LIQUIDADO') OR " \
                 "(deb_susp = True and situacao_ctr not in ('RENOV/RENEG')));"
    tupla_devolucoes = banco.buscar_dados(sql_select=sql_select)
    lista_devolucoes = [[item_tupla for item_tupla in cada_tupla] for cada_tupla in tupla_devolucoes]
    return lista_devolucoes


def devolver(chave, senha, lista_devolver):
    # Gravar o lancamento de ajuste de devolucao
    s = Sisbb()
    s.acesso_inicial(chave=chave, senha=senha, cic=True)

    # Entrar no TOC 11-a-01-F9
    s.colar(15, 14, "toc")
    s.colar(16, 14, senha, 'enter')
    s.aguardar_sem_cursor(10, 13, "Responsabilidade")
    s.teclar('f3')
    s.aguardar_sem_cursor(1, 3, "TOCM0000")
    s.colar(20, 19, '11')
    s.colar(21, 19, 'a', 'enter')
    s.aguardar_sem_cursor(8, 30, "partir")
    s.colar(12, 28, 'x', 'enter')
    s.aguardar_sem_cursor(1, 3, "TOCMN010")
    s.colar(21, 19, "01", "enter")
    s.aguardar_sem_cursor(1, 3, "TOCM0028")
    s.teclar("f9")
    s.aguardar_sem_cursor(1, 3, "TOCM2816")
    s.colar(5, 66, '               ', 'enter')
    s.aguardar_sem_cursor(23, 3, "Informe")

    # Loop das ocorrências para realizar os lançamentos
    for item in lista_devolver:
        # print(item)
        s.colar(5, 66, str(item[0]), 'enter')
        s.aguardar_sem_cursor(12, 14, str(item[0]))
        tela = s.copiar_tela()
        # valor = s.copiar(12, 45, 14, tela=tela)
        # print(valor)
        if s.copiar(12, 45, 14, tela=tela) == "0,00" or s.copiar(12, 77, 1, tela=tela) == "*":
            item.append('0')
            item.append('Ocorrência já tratada')
        else:
            s.colar(12, 3, "x", "enter")
            s.aguardar_sem_cursor(5, 23, str(item[0]))
            s.colar(17, 3, 'i', 'enter')
            if s.copiar(23, 3, 5) == "Grava":
                item.append('0')
                item.append('Gravação de Ajuste indisponível')
            else:
                s.aguardar_sem_cursor(12, 8, '401')
                s.colar(12, 3, 'x', 'enter')
                s.aguardar_sem_cursor(4, 23, str(item[0]))
                s.aguardar_sem_cursor(7, 23, str(item[2]))
                s.colar(21, 23, str(item[1]), "enter")
                if s.copiar(23, 3, 5) == "Conta" or s.copiar(23, 3, 5) == "Infor":
                    item.append('0')
                    item.append('Conta corrente indisponível')
                else:
                    s.aguardar_sem_cursor(24, 3, "Confirma")
                    s.colar(24, 74, 's', 'enter')
                    s.aguardar_sem_cursor(23, 3, "Ajuste")
                    item.append('1')
                    item.append('Valor devolvido')
                s.teclar('f3')
                s.aguardar_sem_cursor(1, 3, "TOCM2801")
                s.teclar('f3')
                s.aguardar_sem_cursor(1, 3, "TOCM285B")
            s.teclar('f3')
        s.colar(5, 66, '               ', 'enter')
        s.aguardar_sem_cursor(23, 3, 'Informe')
    return lista_devolver


def buscar_amortizacoes():
    # Buscar as ocorrencias que precisam ser amortizadas
    banco = BancoDados()
    sql_select = "select num_ocorr, valor, cvn, dt_toc " \
                 "from ocorrencias_novo_final " \
                 "where valor > 0 and " \
                 "(processado = True or rpss_realizado = True) and " \
                 "deb_susp = False and " \
                 "rescisao = False and " \
                 "situacao_ctr = 'Contrato Normal - em cobranca';"
    tupla_amortizar = banco.buscar_dados(sql_select=sql_select)
    lista_amortizar = [[item_tupla for item_tupla in cada_tupla] for cada_tupla in tupla_amortizar]
    return lista_amortizar


# def amortizar(chave, senha, lista_amortizar):
#     # Gravar o lancamento de ajuste de devolucao
#     return 0
#
#
# def estornar(lista_estornar):
#     pass


def gravar_csv_ocorrencias(arquivo, lista):
    with open(arquivo, 'w') as itens:
        cabecalho_arq = 'NUM_OCORR;VALOR;CONVENIO;DATA_TOC\n'
        itens.write(cabecalho_arq)
        for cada in lista:
            itens.write('{ocorr};{valor};{cvn};{dt_toc}\n'.format(ocorr=str(cada[0]),
                                                                  valor=str(cada[1]),
                                                                  cvn=str(cada[2]),
                                                                  dt_toc=cada[3]))


def lancar():
    resc = buscar_rescisoes()
    debi = buscar_debitar()
    dev = buscar_devolucoes()
    amort = buscar_amortizacoes()

    # data = date.isoformat(date.today())
    ano = str(datetime.today().year)
    mes = str(datetime.today().month)
    dia = str(datetime.today().day)

    arq_rescisoes_fazer = './arquivos/{ano}/{mes}/{dia}/rescisoes_fazer.csv'.format(ano=ano, mes=mes, dia=dia)
    arq_debitar = './arquivos/{ano}/{mes}/{dia}/debitar.csv'.format(ano=ano, mes=mes, dia=dia)
    arq_devolver = './arquivos/{ano}/{mes}/{dia}/devolver.csv'.format(ano=ano, mes=mes, dia=dia)
    arq_amortizar = './arquivos/{ano}/{mes}/{dia}/amortizar.csv'.format(ano=ano, mes=mes, dia=dia)

    gravar_csv_ocorrencias(arq_amortizar, amort)
    gravar_csv_ocorrencias(arq_debitar, debi)
    gravar_csv_ocorrencias(arq_devolver, dev)
    gravar_csv_ocorrencias(arq_rescisoes_fazer, resc)

    chave = 'F0431861'
    senha = '82195769'

    # print(len(dev))
    continua = input("Quer continuar? ")

    if continua.upper() == "S":
        resultado_devolver = devolver(chave=chave, senha=senha, lista_devolver=dev)
        # resultado_amortizar = amortizar(chave=chave, senha=senha, lista_amortizar=amort)
        resultado_debitar = debitar(chave=chave, senha=senha, lista_debitos=debi)
        # resultado_rescisoes = fazer_rescisao(chave=chave, senha=senha, lista_rescisoes=resc)

        # Escrever arquivo com os lançamentos realizados

        arq_devolucoes = './arquivos/{ano}/{mes}/{dia}/devolucoes_realizadas.csv'.format(ano=ano, mes=mes, dia=dia)
        with open(arq_devolucoes, 'w') as devolucoes:
            cabecalho = 'NUM_OCORR;VALOR;CONVENIO;DATA_TOC;DEVOLVIDO;MOTIVO\n'
            devolucoes.write(cabecalho)
            for i in resultado_devolver:
                devolucoes.write('{ocorr};{valor};{cvn};{dt_toc};{devolvido};{motivo}\n'.format(ocorr=str(i[0]),
                                                                                                valor=str(i[1]),
                                                                                                cvn=str(i[2]),
                                                                                                dt_toc=i[3],
                                                                                                devolvido=i[4],
                                                                                                motivo=i[5]))

        arq_debitos = './arquivos/{ano}/{mes}/{dia}/debitos_realizados.csv'.format(ano=ano, mes=mes, dia=dia)
        with open(arq_debitos, 'w') as debitos:
            cabecalho = 'NUM_OCORR;VALOR;CONVENIO;DATA_TOC;DEVOLVIDO;MOTIVO\n'
            debitos.write(cabecalho)
            for i in resultado_debitar:
                debitos.write('{ocorr};{valor};{cvn};{dt_toc};{debitado};{motivo}\n'.format(ocorr=str(i[0]),
                                                                                            valor=str(i[1]),
                                                                                            cvn=str(i[2]),
                                                                                            dt_toc=i[3],
                                                                                            debitado=i[4],
                                                                                            motivo=i[5]))


lancar()
