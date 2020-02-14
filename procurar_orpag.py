from modulos.funcoes import BancoDados
from modulos.sisbb import Sisbb

banco = BancoDados()
sql_busca = 'select num_ocorr ' \
            'from ocorrencias_teste ' \
            'where gm = 1 ' \
            'and ocorr_701 = 1 ' \
            'and dt_toc < current_date - interval 180 day ' \
            'order by dt_toc;'
lista_ocorr = banco.buscar_dados(sql_busca)
print(lista_ocorr[:20])

s = Sisbb()
chave = 'F0431861'
senha = '82195769'
s.acesso_inicial(chave=chave, senha=senha, cic=True)

