from modulos.sisbb import Sisbb

s = Sisbb()
s.acesso_inicial(chave="F0431861", senha="82195764", cic=True)
s.colar(15, 14, "clientes")
s.colar(16, 14, "82195764", "enter")
s.aguardar(1, 2, "SBBP6130")
s.colar(21, 20, "01", "enter")
s.aguardar(1, 3, "MCIM0000")
s.colar(19, 18, "01", "enter")
s.aguardar(1, 3, "MCIM001A")

with open("./convenios.txt", "r") as mcis:
    reader = mcis.readlines()
    infos = []
    for linha in reader:
        mci = linha.rstrip("\n")
        s.colar(20, 57, "         ", "enter")
        s.aguardar_sem_cursor(23, 3, "Informe")
        s.colar(20, 57, mci, "enter")

        s.aguardar_sem_cursor(3, 15, "Consulta")
        cnpj = s.copiar(4, 12, 45)
        infos.append("{mci};{cnpj}\n".format(mci=mci, cnpj=cnpj))
        s.teclar("f3")
        s.aguardar(1, 3, "MCIM001A")

    with open('./mcis_cnpjs_4.csv', 'w') as resultado:
        for info in infos:
            resultado.write(info)

    # s.teclar("f5")
    # s.colar(15, 14, "clientes")
    # s.colar(16, 14, "82195764", "enter")
    # s.aguardar(1, 2, "SBBP6130")
    # s.colar(21, 20, "01", "enter")
    # s.aguardar(1, 3, "MCIM0000")
    # s.colar(19, 18, "01", "enter")
    # s.aguardar(1, 3, "MCIM001A")
    #
    # infos = []
    # for mci in mcis:
    #     s.colar(20, 57, "         ", "enter")
    #     s.aguardar_sem_cursor(23, 3, "Informe")
    #     s.colar(20, 57, mci, "enter")
    #
        # s.aguardar(1, 3, "MCIM100J")
        # cnpj = s.copiar(5, 12, 18)
        # infos.append("{mci};{cnpj}\n".format(mci=mci, cnpj=cnpj))
        # s.teclar("f3")
        # s.aguardar(1, 3, "MCIM001A")
    #
    # with open('./mcis_cnpjs_2.csv', 'w') as resultado:
    #     for info in mcis:
    #         resultado.write(info)


# with open("./convenos.txt", "r") as mcis:
#     reader = mcis.readlines()
#     infos = []
#     for linha in reader:
#         mci = linha.rstrip("\n")
#         s.colar(20, 57, "         ", "enter")
#         s.aguardar_sem_cursor(23, 3, "Informe")
#         s.colar(20, 57, mci, "enter")
#
#         s.aguardar(1, 3, "MCIM100J")
#         cnpj = s.copiar(5, 12, 18)
#         infos.append("{mci};{cnpj}\n".format(mci=mci, cnpj=cnpj))
#         s.teclar("f3")
#         s.aguardar(1, 3, "MCIM001A")
#
# with open('./mcis_cnpjs.csv', 'w') as resultado:
#     for info in infos:
#         resultado.write(info)

