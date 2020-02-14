from modulos.sisbb import Sisbb
import csv


def escrever_log(texto):
    arquivo = open('./logs.csv', 'a')
    arquivo.write(texto)
    arquivo.close()


chave = 'F0431861'
senha = '82195769'


s = Sisbb()
s.acesso_inicial(chave=chave, senha=senha, cic=True)

# Entrar no TOC 01-a para verificar tratamento da competência
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
s.colar(21, 19, '01', 'enter')
s.aguardar_sem_cursor(1, 3, "TOCM0028")
s.teclar('f9')
s.aguardar_sem_cursor(1, 3, "TOCM2816")
s.colar(5, 66, "                 ", 'enter')
s.aguardar_sem_cursor(23, 3, "Informe")


arq_log = open('./logs.csv', 'w')
arq_log.write("NR_OCR;Info_ORPAG\n")
arq_log.close()

with open('./sas_orpag.csv', 'r') as arq_ocorrs:
    reader = csv.DictReader(arq_ocorrs, delimiter=';')
    for linha in reader:
        s.colar(5, 66, linha["NR_SEQL_OCR_CVN"], 'enter')
        if s.copiar(23, 3, 8) == "Registro" or s.copiar(12, 77, 1) == "*":
            # continue
            escrever_log("{ocorr};{info}\n".format(ocorr=linha["NR_SEQL_OCR_CVN"], info="0"))
            # log.write("{ocorr};{info}".format(ocorr=linha["NR_SEQL_OCR_CVN"], info="0"))
        else:
            tela = s.copiar_tela()
            ocorrencia = int(s.copiar(12, 14, 8, tela))
            ocorrencia_orp = int(linha["NR_SEQL_OCR_CVN"])
            if ocorrencia == ocorrencia_orp:
                s.colar(12, 3, "x", "enter")
                if s.copiar(23, 15, 10) == "autorizado" or s.copiar(23, 14, 6) == "encami":
                    escrever_log("{ocorr};{info}\n".format(ocorr=linha["NR_SEQL_OCR_CVN"], info="0"))
                else:
                    s.aguardar_sem_cursor(5, 23, linha["NR_SEQL_OCR_CVN"])
                    s.teclar('f12')
                    s.aguardar_sem_cursor(1, 3, "TOCM0036")
                    for registro in range(12, 22):
                        if s.copiar(registro, 16, 28) == "DEVOLUCAO DE VALOR VIA ORPAG":
                            escrever_log("{ocorr};{info}\n".format(ocorr=linha["NR_SEQL_OCR_CVN"], info="1"))
                            s.teclar('f3')
                            s.aguardar_sem_cursor(1, 3, "TOCM285B")
                            s.colar(17, 3, 'i', 'enter')
                            if s.copiar(23, 49, 9) == "pendentes":
                                escrever_log("{ocorr};{info};{reg}\n"
                                             .format(ocorr=linha["NR_SEQL_OCR_CVN"], info="1", reg="já regularizado"))
                                break
                            else:
                                s.aguardar_sem_cursor(1, 3, "TOCM2801")
                                s.colar(13, 3, 'x', 'enter')
                                s.aguardar_sem_cursor(4, 23, linha["NR_SEQL_OCR_CVN"])
                                s.colar(21, 23, linha['VL_SDO_CGN'], 'enter')
                                if s.copiar(23, 12, 9) == "bloqueado" or s.copiar(23, 13, 7) == "cliente":
                                    s.teclar('f3')
                                    s.aguardar_sem_cursor(1, 3, "TOCM2801")
                                    s.teclar('f3')
                                    s.aguardar_sem_cursor(1, 3, "TOCM285B")
                                    break
                                else:
                                    s.aguardar_sem_cursor(24, 3, "Confirma")
                                    s.colar(24, 74, 's', 'enter')
                                    s.aguardar_sem_cursor(23, 3, "Ajuste gravado")
                                    s.teclar('f3')
                                    s.aguardar_sem_cursor(1, 3, "TOCM2801")
                                    s.teclar('f3')
                                    s.aguardar_sem_cursor(1, 3, "TOCM285B")
                                    break
                        # else:
                        #     escrever_log("{ocorr};{info}\n".format(ocorr=linha["NR_SEQL_OCR_CVN"], info="0"))
                    if s.copiar(1, 3, 8) != "TOCM285B":
                        s.teclar('f3')
                        s.aguardar_sem_cursor(1, 3, "TOCM285B")
                    s.teclar('f3')
                    s.aguardar_sem_cursor(1, 3, "TOCM2816")
                    s.colar(5, 66, "                 ", 'enter')
                    s.aguardar_sem_cursor(23, 3, "Informe")
            else:
                continue
