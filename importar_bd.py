# import csv
# from datetime import date, datetime
from modulos.funcoes import BancoDados


# def qual_mes(mes):
#     if mes == "JAN":
#         return 1
#     elif mes == "FEB":
#         return 2
#     elif mes == "MAR":
#         return 3
#     elif mes == "APR":
#         return 4
#     elif mes == "MAY":
#         return 5
#     elif mes == "JUN":
#         return 6
#     elif mes == "JUL":
#         return 7
#     elif mes == "AUG":
#         return 8
#     elif mes == "SEP":
#         return 9
#     elif mes == "OCT":
#         return 10
#     elif mes == "NOV":
#         return 11
#     elif mes == "DEC":
#         return 12
#     else:
#         raise Exception
#
#
# ocorrencias = open('./ocorrencias_incluir.csv', 'w')
# itens_ocorr_sas = []
# ocorrencias_sas = open('./ocorrencias.csv', 'r')
# cvns_gerfin = open('./cvns_gerfin.csv', 'r')
# reader_sas = csv.DictReader(ocorrencias_sas, delimiter=';')
# lista_gerfin = []
# for item in cvns_gerfin:
#     lista_gerfin.append(int(item.rstrip("\n")))
# for item in reader_sas:
#     # print(item["DT_CBR_PCL"])
#     # print(item["DT_PRVT_RPSS_CVN"])
#     mes_cobr = qual_mes(item["DT_CBR_PCL"][2:5])
#     mes_toc = qual_mes(item["DT_PRVT_RPSS_CVN"][2:5])
#     dt_cobr = date(int(item["DT_CBR_PCL"][5:]),
#                    mes_cobr,
#                    int(item["DT_CBR_PCL"][:2])).isoformat()
#     dt_toc = date(int(item["DT_PRVT_RPSS_CVN"][5:]),
#                   mes_toc,
#                   int(item["DT_PRVT_RPSS_CVN"][:2])).isoformat()
#     if int(item['NR_CVN']) in lista_gerfin:
#         itens_ocorr_sas.append("{num_ocorrencia};{convenio};{saldo};{dt_cobr};{dt_toc};{contrato};1;\n"
#                                .format(num_ocorrencia=item["NR_SEQL_OCR_CVN"],
#                                        convenio=item["NR_CVN"],
#                                        saldo=item["VL_SDO_CGN"],
#                                        dt_cobr=dt_cobr,
#                                        dt_toc=dt_toc,
#                                        contrato=item["NR_CTR_OPR"]))
#
# for item in itens_ocorr_sas:
#     ocorrencias.write(item)
# ocorrencias_sas.close()
# ocorrencias.close()


banco = BancoDados()
banco.dropar_tabela('ocorrencias_teste')
sql_criar = 'CREATE TABLE `estudo`.`ocorrencias_teste` ' \
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
banco.load_data('./ocorrencias.csv', 'ocorrencias_teste')
