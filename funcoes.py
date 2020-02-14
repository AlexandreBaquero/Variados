import sys
import pymysql
import csv
from modulos.sisbb import Sisbb
from datetime import datetime, timedelta


class AcessoSisbb:
    def __init__(self):
        self.chave = ''
        self.senha = ''

    def retorna_chave_senha(self):
        self.chave = 'f0431861'
        self.senha = '82195769'
        dict_acesso = {self.chave: self.senha}
        return dict_acesso


class BancoDados:
    def __init__(self):
        self.conexao = self.conector()

    @staticmethod
    def conector():
        host = "172.20.0.24"
        usuario = "F0431861"
        senha = "1234"
        db = "estudo"

        try:
            con = pymysql.connect(host=host, user=usuario, password=senha, db=db, autocommit=True, local_infile=1)
            return con

        except Exception as exc:
            print("Error: {}".format(str(exc)))
            sys.exit(1)

    def inserir_dados(self, sql_statement):
        try:
            with self.conexao.cursor():
                cursor = self.conexao.cursor()
                cursor.execute(sql_statement)
                self.conexao.commit()

        except Exception as exc:
            print("Error: {}".format(str(exc)))
            sys.exit(1)
        return

    def dropar_tabela(self, tabela):
        try:
            with self.conexao.cursor():
                sql_drop = 'drop table {tabela}'.format(tabela=tabela)
                cursor = self.conexao.cursor()
                cursor.execute(sql_drop)

        except Exception as exc:
            print('Error: {}'.format(str(exc)))
            sys.exit(1)

    def criar_tabela(self, sql_criar):
        try:
            with self.conexao.cursor():
                sql_create = sql_criar
                cursor = self.conexao.cursor()
                cursor.execute(sql_create)

        except Exception as exc:
            print('Error: {}'.format(str(exc)))
            sys.exit(1)

    def buscar_dados(self, sql_select):
        try:
            with self.conexao.cursor():
                cursor = self.conexao.cursor()
                cursor.execute(sql_select)
                resultado = cursor.fetchall()

                lista_competencias = []
                for comp in resultado:
                    lista_competencias.append(comp)

        except Exception as exc:
            print("Error: {}".format(str(exc)))
            sys.exit(1)

        return lista_competencias

    def fechar_conexao(self):
        self.conexao.close()

    def load_data(self, arquivo, tabela):
        load_sql = "load data local infile '{arquivo}' into table estudo.{tabela} fields terminated by ';' " \
                   "lines terminated by '\n' ignore 1 lines;".format(arquivo=arquivo, tabela=tabela)
        self.inserir_dados(load_sql)


class Toc:
    def __init__(self):
        pass

    # Essa função busca as últimas 5 datas TOC dos convênios migrados e grava num arquivo csv 'lista_datas.csv'
    @staticmethod
    def atualiza_datas_toc(chave, senha):
        # Acessar o SISBB usando o módulo Sisbb do arquivo sisbb.py
        s = Sisbb()
        s.acesso_inicial(chave, senha, cic=True)

        lista_datas = []

        # Acessar o TOC
        s.colar(15, 14, "toc")
        s.colar(16, 14, s.senha, "enter")
        s.aguardar_sem_cursor(10, 13, "Responsabilidade")
        s.teclar("f3")
        s.aguardar(1, 3, "TOCM0000")

        # Acessar a opção 01-a
        s.colar(20, 19, "01")
        s.colar(21, 19, "a", "enter")
        s.aguardar_sem_cursor(10, 41, "Produto")
        s.colar(12, 28, "x", "enter")
        s.aguardar(1, 3, "TOCM0040")

        with open('./arquivos/cvns_migrados.csv', 'r') as convenios:
            lista_cvns = convenios.readlines()
            # print(lista_cvns[:10])
            for convenio in lista_cvns:
                cvn = int(convenio)
                s.colar(4, 21, "         ", "enter")
                s.aguardar_sem_cursor(23, 3, "Informe")
                s.colar(4, 21, str(cvn), 'enter')
                s.teclar('f4')
                s.aguardar_sem_cursor(10, 32, "Prevista")
                tela = s.copiar_tela()
                for info in range(12, 17):
                    if s.copiar(info, 32, 10, tela) != "":
                        lista_datas.append((cvn, "{ano}-{mes}-{dia}".format(ano=s.copiar(info, 38, 4, tela),
                                                                            mes=s.copiar(info, 35, 2, tela),
                                                                            dia=s.copiar(info, 32, 2, tela))))
                s.teclar('f3')
                s.aguardar_sem_cursor(7, 37, "CPF")

        with open("./arquivos/cvns_gerfin.csv", "r") as cvns_gerfin:
            gerfin = cvns_gerfin.readlines()
            lista_gerfin = []
            for i in gerfin:
                cvn = int(i)
                lista_gerfin.append(cvn)

        with open("./arquivos/artefatos/lista_datas.csv", "w") as atualizar:
            for reg in lista_datas:
                if reg[0] in lista_gerfin:
                    atualizar.write("{convenio};{data};{timestamp};N/A;{tipo}\n"
                                    .format(convenio=reg[0],
                                            timestamp=datetime.timestamp(datetime.now()),
                                            data=reg[1],
                                            tipo="GERFIN"))
                else:
                    atualizar.write("{convenio};{data};{timestamp};;{tipo}\n"
                                    .format(convenio=reg[0],
                                            timestamp=datetime.timestamp(datetime.now()),
                                            data=reg[1],
                                            tipo="MANUAL"))

        gravando = BancoDados()
        gravando.load_data('./arquivos/artefatos/lista_datas.csv', 'competencias')

        print("Busca de datas TOC realizadas com sucesso")
        return lista_datas


class DiaUtilAnterior:
    def __init__(self):
        pass

    @staticmethod
    def retorna(dia):
        delta = timedelta(days=-1)
        if datetime.weekday(dia + delta) == 6:
            return dia + delta + delta + delta
        else:
            return dia + delta

    @staticmethod
    def eh_util(dia):
        if datetime.weekday(dia) == 5 or datetime.weekday(dia) == 6:
            return False
        else:
            return True


class ConvenioEquipe:
    def __init__(self):
        pass

    @staticmethod
    def retorna_equipe(convenio):
        with open('./arquivos/convenios.csv') as arquivo:
            convenios = csv.DictReader(arquivo, delimiter=';')
            for linha in convenios:
                if int(linha["CD_CVN"]) == int(convenio):
                    return linha["CD_EQP"]
