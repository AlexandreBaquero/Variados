from modulos.funcoes import BancoDados
from modulos.sisbb import Sisbb

banco = BancoDados()
sql_busca = 'select cvn, dt_toc ' \
            'from ocorrencias_teste ' \
            'where ver = 1 ' \
            'group by cvn, dt_toc ' \
            'order by dt_toc;'
lista_compets = banco.buscar_dados(sql_busca)
print(lista_compets[:20])
print(len(lista_compets))

s = Sisbb()
chave = 'F0431861'
senha = '82195769'
s.acesso_inicial(chave=chave, senha=senha, cic=True)

print("parar!")
print("Fim!")