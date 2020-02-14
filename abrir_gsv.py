import csv
from datetime import date, timedelta
from modulos.funcoes import DiaUtilAnterior


compe = open('./competencias.csv', 'r')
competencias = csv.DictReader(compe, delimiter=';')

info_convenios = open("./convenios.csv", "r")
reader = csv.DictReader(info_convenios, delimiter=";")

data_hoje = date.today()
data_hoje_string = data_hoje.strftime("%Y%m%d")
com_extensao = "{data}{ext}".format(data=data_hoje_string, ext=".txt")
arq_atualizacao = "./{ano}{mes}{dia}.txt" \
    .format(ano=data_hoje.year, mes=data_hoje.month, dia=data_hoje.day)

with open(arq_atualizacao, 'w') as arquivo:
    for conv in competencias:
        for registro in reader:
            if int(registro["CD_CVN"]) == int(conv["Convenio"]):

                dt_toc = conv["DataTOC"]
                data_toc = date(year=int(dt_toc[6:]), month=int(dt_toc[3:5]), day=int(dt_toc[:2]))

                calcula_dia = DiaUtilAnterior()

                data_pre = data_toc + timedelta(days=-1)
                if calcula_dia.eh_util(data_pre):
                    dt_pre = data_pre.strftime("%d/%m/%Y")
                else:
                    data_pre = data_toc + timedelta(days=-2)
                    if calcula_dia.eh_util(data_pre):
                        dt_pre = data_pre.strftime("%d/%m/%Y")
                    else:
                        data_pre = data_toc + timedelta(days=-3)
                        dt_pre = data_pre.strftime("%d/%m/%Y")

                arquivo.write("1981;1981;1981;1;"
                              "{CNPJ};"
                              "{NM_CVN};37;3701;"
                              "{CD_CONCI};{CD_CVN};Equipe "
                              "{CD_EQP};"
                              "{DATA_PRE};;11;13;;;"
                              "{DATA_TOC};;N\n".format(CNPJ=registro["CNPJ"],
                                                       NM_CVN=registro["NM_CVN"],
                                                       CD_CONCI=registro["CD_CONCI"],
                                                       CD_CVN=conv["Convenio"],
                                                       CD_EQP=registro["CD_EQP"],
                                                       DATA_TOC=dt_toc,
                                                       DATA_PRE=dt_pre))
                break
