from modulos.sisbb import Sisbb
import csv


def escrever_log(texto):
    arquivo = open('./logs_canc.csv', 'a')
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


arq_log = open('./logs_canc.csv', 'w')
arq_log.write("NR_OCR;Info_ORPAG\n")
arq_log.close()

with open('./sas_orpag_canc.csv', 'r') as arq_ocorrs:
    reader = csv.DictReader(arq_ocorrs, delimiter=';')
    for linha in reader:
        s.colar(5, 66, linha["NR_SEQL_OCR_CVN"], 'enter')
        if s.copiar(12, 45, 14) == "0,00" and s.copiar(12, 77, 1) == "*":
            s.colar(12, 3, "x", "enter")
            s.aguardar_sem_cursor(5, 23, linha["NR_SEQL_OCR_CVN"])
            s.colar(17, 3, "c", "enter")
            s.aguardar_sem_cursor(12, 28, "404")
            s.colar(12, 3, "x", "enter")
            s.aguardar_sem_cursor(23, 10, "ENTER")
            s.teclar("enter")
            s.aguardar_sem_cursor(24, 3, "Confirma")
            s.colar(24, 59, "s", "enter")
            s.aguardar_sem_cursor(23, 3, "Ajuste")
            s.teclar("f3")
            s.aguardar_sem_cursor(1, 3, "TOCM2808")
            s.teclar("f3")
            s.aguardar_sem_cursor(1, 3, "TOCM285B")
            s.teclar("f3")
            s.aguardar_sem_cursor(1, 3, "TOCM2816")
            escrever_log("{ocorr};{reg}".format(ocorr=linha["NR_SEQL_OCR_CVN"], reg="1"))
        else:
            s.colar(5, 66, "                 ", 'enter')
            s.aguardar_sem_cursor(23, 3, "Informe")
            escrever_log("{ocorr};{reg}".format(ocorr=linha["NR_SEQL_OCR_CVN"], reg="0"))
