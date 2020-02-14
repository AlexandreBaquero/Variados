import sys
from modulos.sisbb import Sisbb
from modulos.funcoes import AcessoSisbb


class Ocorrencias:
    def __init__(self):
        self.ocorrencias = []

    def busca_ocorrencias(self, convenio, data):
        try:
            acesso = AcessoSisbb()
            acesso.retorna_chave_senha()

            data_strip = data.replace('/', '')
            mes = data_strip[2:4]
            ano = data_strip[4:]

            s = Sisbb()
            s.acesso_inicial(chave=acesso.chave, senha=acesso.senha, cic=True)

            # Entrar no TOC 11-a para buscar as ocorrências do convênio e da data
            s.colar(15, 14, "toc")
            s.colar(16, 14, acesso.senha, 'enter')
            s.aguardar_sem_cursor(10, 13, "Responsabilidade")
            s.teclar('f3')
            s.aguardar_sem_cursor(1, 3, "TOCM0000")
            s.colar(20, 19, '11')
            s.colar(21, 19, 'a', 'enter')
            s.aguardar_sem_cursor(8, 30, "partir")
            s.colar(12, 28, 'x', 'enter')
            s.aguardar_sem_cursor(1, 3, "TOCMN010")
            s.colar(21, 19, '01', 'enter')
            s.aguardar_sem_cursor(1, 3, "TOCM0028")
            s.colar(6, 24, "         ")
            s.colar(6, 24, convenio)
            s.colar(8, 24, mes)
            s.colar(8, 29, ano)
            s.colar(8, 36, mes)
            s.colar(8, 41, ano, 'enter')
            tela = s.copiar_tela()
            convenio_tela = str(s.copiar(12, 10, 9, tela)).strip(' ')
            if convenio != convenio_tela:
                raise Exception('Convênio não encontrado')
            s.colar(12, 3, 'x', 'enter')
            s.aguardar_sem_cursor(1, 3, "TOCM2814")

            paginas = True
            while paginas:
                tela_ocorrs = s.copiar_tela()
                for linha in range(12, 22):
                    ocorr = str(s.copiar(linha, 9, 8, tela_ocorrs))
                    if ocorr.rstrip() == '':
                        paginas = False
                        break
                    else:
                        self.ocorrencias.append(ocorr)
                s.teclar('f8')
                if s.copiar(23, 3, 6) == "Ultima":
                    paginas = False
            return self.ocorrencias

        except Exception as exc:
            print("Erro: {exc}".format(exc=exc))
            sys.exit(1)


class Tratamento:
    def __init__(self):
        self.listaDevolver = []
        self.listaDebitar = []
        self.listaVerificarCredora = []
        self.listaAmortizar = []
        self.listaRenovReneg = []
        self.listaVerificarDevedora = []

    def distribuir_ocorrencias(self, lista_ocorrencias):
        try:
            acesso = AcessoSisbb()
            acesso.retorna_chave_senha()

            # Acesar o SISBB
            s = Sisbb()
            s.acesso_inicial(chave=acesso.chave, senha=acesso.senha, cic=True)

            # Entrar no TOC 11-a para buscar as ocorrências do convênio e da data
            s.colar(15, 14, "toc")
            s.colar(16, 14, acesso.senha, 'enter')
            s.aguardar_sem_cursor(10, 13, "Responsabilidade")
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

            # Entrar em cada ocorrencia
            for ocorr in lista_ocorrencias:
                s.colar(5, 66, '               ', 'enter')
                s.aguardar_sem_cursor(23, 3, "Informe")
                s.colar(5, 66, ocorr, 'enter')
                tela = s.copiar_tela()
                ocorr_tela = s.copiar(12, 14, 8, tela)
                if ocorr != ocorr_tela:
                    raise ValueError("Ocorrencia nao encontrada")
                elif s.copiar(12, 26, 3) == "701":
                    s.colar(12, 3, 'x', 'enter')
                    s.aguardar_sem_cursor(5, 23, ocorr)
                    s.teclar('f2')
                    if s.copiar(6, 16, 6) == "Existe":
                        s.teclar('enter')
                    s.aguardar_sem_cursor(1, 3, 'CDCM1510')
                    tela_situacao = s.copiar_tela()
                    situacao = str(s.copiar(7, 20, 30, tela_situacao)).rstrip(' ')
                    parcela_em_ser = str(s.copiar(16, 65, 10, tela_situacao))
                    if s.copiar(7, 66, 15, tela_situacao) == "DEBITO SUSPENSO":
                        deb_susp = True
                    else:
                        deb_susp = False
                    if situacao in ('Contrato renovado',
                                    'CONTRATO LIQUIDADO',
                                    'Contrato Cancelado',
                                    'OPERACAO PREJUIZO CEDIDA',
                                    'PREJ. REC.C/RESTRIÇÃO',
                                    'COM ACORDO NO SISTEMA RAO',
                                    'PREJ.RECUPERADO S/RESTRIÇÃO',
                                    'Proposta Cancelada'):
                        self.listaDevolver.append((ocorr, situacao, deb_susp, parcela_em_ser))
                    elif situacao in ('Contrato Normal',
                                      'Contrato Atraso acima 60 dias',
                                      'Contrato Normal - em cobranca',
                                      'Contrato em Prejuizo',
                                      'Contrato Atraso ate 60 dias') \
                            and deb_susp is True:
                        self.listaDevolver.append((ocorr, situacao, deb_susp, parcela_em_ser))
                    elif situacao in ('Contrato Normal - em cobranca',
                                      'Contrato em Prejuizo',
                                      'Contrato Atraso acima 60 dias') \
                            and deb_susp is False:
                        self.listaAmortizar.append((ocorr, situacao, deb_susp, parcela_em_ser))
                    elif situacao == "RENOV/RENEG":
                        self.listaRenovReneg.append((ocorr, situacao, deb_susp, parcela_em_ser))
                    else:
                        self.listaVerificarCredora.append((ocorr, situacao, deb_susp, parcela_em_ser))
                    s.teclar('f3')
                    s.aguardar_sem_cursor(5, 23, ocorr)
                    s.teclar('f3')
                elif s.copiar(12, 26, 3) == "201":
                    s.colar(12, 3, 'x', 'enter')
                    s.aguardar_sem_cursor(5, 23, ocorr)
                    if s.copiar(17, 80, 1) != '0':
                        self.listaVerificarDevedora.append(ocorr)
                    else:
                        self.listaDebitar.append(ocorr)
                    s.teclar('f3')
                    s.aguardar_sem_cursor(1, 3, "TOCM2816")
                else:
                    raise ValueError("Ocorrencia nao encontrada")

        except ValueError as exc:
            print("Erro: {exc}".format(exc=exc))
            sys.exit(1)

    def listar_ocorrencias(self):
        print("Ocorrencias a devolver: ")
        for ocorr in self.listaDevolver:
            print("{ocorrencia}".format(ocorrencia=ocorr))
        print("Ocorrencias credoras a verificar: ")
        for ocorr in self.listaVerificarCredora:
            print("{ocorrencia}".format(ocorrencia=ocorr))
        print("Ocorrencias a debitar: ")
        for ocorr in self.listaDebitar:
            print("{ocorrencia}".format(ocorrencia=ocorr))
        print("Ocorrencias renov/reneg: ")
        for ocorr in self.listaRenovReneg:
            print("{ocorrencia}".format(ocorrencia=ocorr))
        print("Ocorrencias a amortizar: ")
        for ocorr in self.listaAmortizar:
            print("{ocorrencia}".format(ocorrencia=ocorr))
        print("Ocorrencias devedoras a verificar:")
        for ocorr in self.listaVerificarDevedora:
            print("{ocorrencia}".format(ocorrencia=ocorr))

    def devolver(self):
        # Gravar o lancamento de ajuste de devolucao
        acesso = AcessoSisbb()
        acesso.retorna_chave_senha()

        # Acesar o SISBB
        s = Sisbb()
        s.acesso_inicial(chave=acesso.chave, senha=acesso.senha, cic=True)

        # Entrar no TOC 11-a-01-F9
        s.colar(15, 14, "toc")
        s.colar(16, 14, acesso.senha, 'enter')
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
        for item in self.listaDevolver:
            # print(item)
            s.colar(5, 66, str(item[0]), 'enter')
            s.aguardar_sem_cursor(12, 14, str(item[0]))
            tela = s.copiar_tela()
            valor_tela = s.copiar(12, 45, 14, tela=tela)
            valor = str(valor_tela).replace('.', '')
            # print(valor)
            if s.copiar(12, 45, 14, tela=tela) == "0,00" or s.copiar(12, 77, 1, tela=tela) == "*":
                continue
                # item.append('0')
                # item.append('Ocorrência já tratada')
            else:
                s.colar(12, 3, "x", "enter")
                s.aguardar_sem_cursor(5, 23, str(item[0]))
                s.colar(17, 3, 'i', 'enter')
                if s.copiar(23, 3, 5) == "Grava":
                    # item.append('0')
                    # item.append('Gravação de Ajuste indisponível')
                    continue
                else:
                    s.aguardar_sem_cursor(12, 8, '401')
                    s.colar(12, 3, 'x', 'enter')
                    s.aguardar_sem_cursor(4, 23, str(item[0]))
                    # s.aguardar_sem_cursor(7, 23, str(item[2]))
                    s.colar(21, 23, valor, "enter")
                    if s.copiar(23, 3, 5) == "Conta" or s.copiar(23, 3, 5) == "Infor":
                        continue
                        # item.append('0')
                        # item.append('Conta corrente indisponível')
                    else:
                        s.aguardar_sem_cursor(24, 3, "Confirma")
                        s.colar(24, 74, 's', 'enter')
                        s.aguardar_sem_cursor(23, 3, "Ajuste")
                        # item.append('1')
                        # item.append('Valor devolvido')
                    s.teclar('f3')
                    s.aguardar_sem_cursor(1, 3, "TOCM2801")
                    s.teclar('f3')
                    s.aguardar_sem_cursor(1, 3, "TOCM285B")
                s.teclar('f3')
            s.colar(5, 66, '               ', 'enter')
            s.aguardar_sem_cursor(23, 3, 'Informe')

    def debitar(self):
        # Gravar o lancamento de ajuste de debito
        acesso = AcessoSisbb()
        acesso.retorna_chave_senha()

        # Acesar o SISBB
        s = Sisbb()
        s.acesso_inicial(chave=acesso.chave, senha=acesso.senha, cic=True)

        # Entrar no TOC 11-a-01-F9
        s.colar(15, 14, "toc")
        s.colar(16, 14, acesso.senha, 'enter')
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
        for item in self.listaDebitar:
            s.colar(5, 66, str(item), 'enter')
            s.aguardar_sem_cursor(12, 14, str(item))
            tela = s.copiar_tela()
            valor_tela = s.copiar(12, 45, 14, tela=tela)
            valor = str(valor_tela).replace('.', '')
            if s.copiar(12, 45, 14, tela=tela) == "0,00" or s.copiar(12, 77, 1, tela=tela) == "*":
                continue
                # item.append('0')
                # item.append('Ocorrência já tratada')
            else:
                s.colar(12, 3, "x", "enter")
                s.aguardar_sem_cursor(5, 23, str(item))
                s.colar(17, 3, 'i', 'enter')
                if s.copiar(23, 3, 5) == "Grava":
                    continue
                    # item.append('0')
                    # item.append('Gravação de Ajuste indisponível')
                else:
                    s.aguardar_sem_cursor(12, 8, '906')
                    s.colar(12, 3, 'x', 'enter')
                    s.aguardar_sem_cursor(4, 23, str(item))
                    # s.aguardar_sem_cursor(7, 23, str(item[2]))
                    # valor = str(item[1] * -1)
                    # print(type(valor))
                    s.colar(21, 23, valor, "enter")
                    if s.copiar(23, 3, 5) == "Conta":
                        continue
                        # item.append('0')
                        # item.append('Conta Corrente invalida para o tipo de ajuste.')
                    else:
                        s.aguardar_sem_cursor(24, 3, "Confirma")
                        s.colar(24, 74, 's', 'enter')
                        s.aguardar_sem_cursor(23, 3, "Ajuste")
                        # item.append('1')
                        # item.append('Valor debitado')
                    s.teclar('f3')
                    s.aguardar_sem_cursor(1, 3, "TOCM2801")
                    s.teclar('f3')
                    s.aguardar_sem_cursor(1, 3, "TOCM285B")
                s.teclar('f3')
            s.colar(5, 66, '               ', 'enter')
            s.aguardar_sem_cursor(23, 3, 'Informe')


cvn = input('Convenio: ')
dt = input('Data TOC: ')
processamento = Ocorrencias()
lista_ocorrs = processamento.busca_ocorrencias(cvn, dt)
print(lista_ocorrs)
print("\nA quantidade de ocorrencias a processar eh de {lenght}.\n".format(lenght=len(lista_ocorrs)))
lancar = Tratamento()
lancar.distribuir_ocorrencias(lista_ocorrs)
lancar.listar_ocorrencias()
devolver = input("Deseja devolver os valores acima: ")
debitar = input("Deseja debitar os valores acima: ")
if devolver.upper() == "S":
    lancar.devolver()
if debitar.upper() == "S":
    lancar.debitar()
