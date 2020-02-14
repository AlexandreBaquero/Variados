"""
Autores: F6769008 e F4352714
Modulo desenvolvido em Pyhton3.7.4 baseada nas funcoes da biblioteca Term3270.java
Como base eh utilizado o modulo py3270 (disponivel via pip) e o executavel x3270 (disponivel em:http://x3270.bgp.nu/)
"""

from py3270 import *


class Sisbb:
    """
    Classe que representa uma sessao do Sisbb com conexao ativa. Consiste de uma invocacao do emulador e do controle
    sobre ele para enviar e receber informacoes e comandos.
    OBS: Todos os comandos, por depender de uma conexao, podem levantar excecoes. Para garantir a integridade do
    processamento de todos os comandos, as excecoes sao levantadas para a camada que chamou a funcao.

    Nota sobre threading:
    O metodo utilizado para distribuir os sockets pode apresentar inconsistencia se os emuladores forem iniciados com
    menos de 500ms de diferenca de um para o outro. Caso decida que eh necessario o uso de threading, leve em considera-
    cao esse tempo.
    Em python, na maioria dos casos, dividir o processamento em threads nao significa melhora de performance, pois por
    padrao o interpretador ALTERNA entre cada thread para processamento, fazendo com que as concorrencias sejam mera
    ilusao. Existem metodos mais avancados que fazem o real destravamento do interpretador, que nao vamos abordar aqui.
    """
    def __init__(self):
        """
        Invoca o emulador x3270 correspondente ao sistema operacional, esteja ele no PATH ou na pasta onde o .py esta
        sendo executado.
        Realiza a conexao informando os argumentos mais semelhantes ao padrao do Sisbb utilizado na plataforma PW3270.
        """
        try:
            argumentos = [
                "-xrm", "wc3270.verifyHostCert:False",
                "-xrm", "wc3270.noPrompt:True",
                "-xrm", "wc3270.hostColorForDefault:green",
                "-xrm", "wc3270.hostColorForIntensified:red",
                "-xrm", "wc3270.hostColorForProtected:turquoise",
                "-xrm", "wc3270.hostColorForProtectedIntensified:white",
                "-xrm", "wc3270.unlockDelay:False",
                "-xrm", "wc3270.menuBar: False",
                "-set", "altCursor",
                "-set", "blankFill",
                "-set", "underscore",
                "-set", "showTiming",
                "-model", "3279-2"
            ]

            self.em = Emulator(
                visible=True,
                timeout=30,
                app=None,
                args=argumentos
            )
            self.em.app.script_port = self.__verifica_porta_disponivel()
            self.em.connect("L:3270.df.bb:9023")
            self.em.wait_for_field()
            self.__chave = ''
            self.__senha = ''

        except Exception as e:
            print(f"Erro Inicializacao Terminal tn3270, Erro: {e.args}")
            raise e

    @staticmethod
    def __verifica_porta_disponivel():
        try:
            netstat = subprocess.check_output("netstat -nao".split(), universal_newlines=True).splitlines()
        except Exception:
            raise ValueError('Falha na verificação de portas.')

        for porta in range(17938, 18939):
            ocupado = False

            for linha in netstat:
                if '127.0.0.1:' + str(porta) in linha:
                    ocupado = True
                    break
                else:
                    ocupado = False

            if not ocupado:
                return porta

    def copiar(self, linha: int, coluna: int, tamanho: int, tela=None):
        """
        Funcao que retorna o texto procurado na tela do Sisbb. Caso a tela nao seja informada, sera capturada a string
        da tela ao vivo do sisbb. Se ela for informada, a string capturada vira do "print" informado.
        :param linha: int que representa a coordenada LINHA.
        :param coluna: int que representa a coordenada COLUNA.
        :param tamanho: quantidade de caracteres horizontais a serem capturados.
        :param tela: "print" do sisbb que pode nao representar a tela atual exibida em execucao.
        :return: retorna uma String de acordo com os parametros especificados.
        """
        try:
            if 0 < linha <= 24 and 0 < coluna <= 80:
                if tela is None:
                    return self.em.string_get(linha, coluna, tamanho).strip()
                else:
                    info_linha = tela[linha-1]
                    return info_linha[coluna-1:(coluna-1)+tamanho].strip()
            else:
                raise ValueError("Por favor utilize uma linha entre 1 e 24 e uma coluna entre 1 e 80.")

        except Exception as e:
            print(f"Erro Comando Copiar SISBB: {e.args}")
            raise e

    def comparar(self, linha: int, coluna: int, string_a_comparar, tela=None):
        """
        Compara o texto informado com o conteudo da coordenada especificada.
        :param linha: coordenada da LINHA.
        :param coluna: coordenada da COLUNA.
        :param string_a_comparar: texto a ser comparado.
        :param tela: "print" do sisbb que pode nao representar a tela atual exibida em execucao.
        :return: retorna True se o texto comparado é igual ao que esta no sisbb.
        """
        if string_a_comparar == self.copiar(linha, coluna, len(string_a_comparar), tela):
            return True
        return False

    def colar(self, linha: int, coluna: int, texto: str, comando=None):
        """
        Funcao que cola uma string em uma execucao do Sisbb. Funciona em metodo de sobrescrita. Pode dar um comando
        conhecido ao final da colagem ou nao.
        :param linha: int que representa a coordenada LINHA.
        :param coluna: int que representa a coordenada COLUNA.
        :param texto: string que sera escrita no Sisbb ativo a partir das coordenadas especificadas.
        :param comando: comando opcional que será dado apos a colagem do texto informado.
        """
        try:
            self.em.wait_for_field()
            if 0 < linha <= 24 and 0 < coluna <= 80:
                self.em.fill_field(linha, coluna, texto, len(str(texto)))
                if comando is not None:
                    self.teclar(comando)
            else:
                raise ValueError("Por favor utilize uma linha entre 1 e 24 e uma coluna entre 1 e 80.")
        except Exception as e:
            print(f"Erro comando Colar SISBB: {e.args}")
            raise e

    def copiar_tela(self):
        """
        Funcao que copia uma tela inteira do Sisbb e retorna uma 'list'.
        :return: lista de strings que compoem a tela do sisbb registrada.
        """
        try:
            tela = self.em.exec_command(
                "Ascii()".encode("latin-1")
            )
            lista_tela = [x.decode('latin-1') for x in tela.data]

            return lista_tela

        except Exception as e:
            print(f"Erro comando Copiar Tela SISBB: {e.args}")
            raise e

    def teclar(self, comando: str):
        """
        Envia um comando para a sessao ativa do Sisbb. Reconhece diversos modelos de comando com o padrao ENTER, E e
        F ou PF, com ou sem [, ( e {.
        exemplos: Enter, enter, E, e, [enter], f8, f10, pf8, [pf8], (f10), {pf5}
        Nao libera a execucao enquanto a tela continuar a mesma, garantindo que o comando foi processado pelo terminal.
        :param comando: string que representa o comando a ser enviado ao sisbb.
        """
        try:
            # Snap da tela antes do teclar.
            tela_anterior = self.em.exec_command("Snap(Save)".format(self.em.timeout).encode("ascii"))

            acao = self.__trata_comandos(comando)

            if acao == "ENTER" or acao == "E":
                self.em.send_enter()
            else:
                self.em.send_pf(acao)

            # Loop que usa o snap da tela antes de teclar, para garantir que algo mudou.
            while True:
                if tela_anterior != self.em.exec_command("Snap(Wait, Output)".format(self.em.timeout).encode("ascii")):
                    break

        except Exception as e:
            print(f"Erro comando Teclar SISBB: {e.args}")
            raise e

    def aguardar(self, linha: int, coluna: int, texto: str):
        """
        Aguarda um texto aparecer na tela atual do Sisbb.
        ATENCAO: Essa funcao utiliza o movimento do cursor como seguranca adicional que a tela esta pronta. Caso a tela
        que ira utilizar nao desbloqueie o cursor, utilize a funcao aguardar_sem_cursor.
        :param linha: coordenada de LINHA onde ira comecar a comparacao do texto
        :param coluna: coordenada de COLUNA onde ira comecar a comparacao do texto
        :param texto: texto procurado na tela
        """
        self.em.wait_for_field()
        try:
            if 0 < linha <= 24 and 0 < coluna <= 80:
                while True:
                    textodatela = self.copiar(linha, coluna, len(texto))
                    if texto == textodatela:
                        break
            else:
                raise ValueError("Por favor utilize uma linha entre 1 e 24 e uma coluna entre 1 e 80.")

        except Exception as e:
            print(f"Erro comando aguardar SISBB: {e.args}")
            raise e

    def aguardar_sem_cursor(self, linha: int, coluna: int, texto: str):
        """
        Aguarda um texto aparecer na tela atual do Sisbb. Diferentemente da funcao aguardar, essa funcao ignora a
        posicao do cursor, verificando se a tela esta pronta somente pelo destravamento do teclado. Util para telas
        que devem ser aguardadas e que so aceitam teclas de enter ou pfs.

        RECOMENDA-SE O USO DESSA FUNCAO SOMENTE EM CASOS QUE A FUNCAO aguardar NAO ATENDA.
        :param linha: coordenada de LINHA onde ira comecar a comparacao do texto
        :param coluna: coordenada de COLUNA onde ira comecar a comparacao do texto
        :param texto: texto procurado na tela
        """
        while self.em.status.keyboard != b"U":
            print("Aguardando o desbloqueio do teclado...")

        try:
            if 0 < linha <= 24 and 0 < coluna <= 80:
                while True:
                    textodatela = self.copiar(linha, coluna, len(texto))
                    if texto == textodatela:
                        break
            else:
                raise ValueError("Por favor utilize uma linha entre 1 e 24 e uma coluna entre 1 e 80.")

        except Exception as e:
            print(f"Erro comando aguardar SISBB: {e.args}")
            raise e

    def atualizar(self):
        """
        Aguarda a liberacao do teclado, o que GERALMENTE quer dizer que a tela esta pronta.
        OBS: De preferencia a utilizacao da funcao aguardar. Essa funcao foi desenhada para telas que podem ou nao
        aparecer durante a execucao de uma rotina e para ler rodapes apos uma execucao de comando.
        """
        while self.em.status.keyboard != b"U":
            print("Aguardando o desbloqueio do teclado...")

    def posicionar(self, linha: int, coluna: int):
        """
        Posiciona o cursor na coordenada informada.
        :param linha: coordenada LINHA.
        :param coluna: coordenada COLUNA.
        """
        try:
            if 0 < linha <= 24 and 0 < coluna <= 80:
                self.em.move_to(linha, coluna)
            else:
                raise ValueError("Por favor utilize uma linha entre 1 e 24 e uma coluna entre 1 e 80.")

        except Exception as e:
            print(f"Erro comando Posicionar: linha:{linha}, coluna:{coluna}, Erro: {e.args}")
            raise e

    def fechar(self):
        """
        Encerra o emulador do Sisbb.
        """
        self.em.terminate()

    @staticmethod
    def __trata_comandos(comando):
        """
        Faz a limpeza de caracteres para melhorar a identificacao do comando solicitado ao teclar.
        :param comando: comando informado pelo usuario.
        :return: retorna o comando limpo.
        """
        comando_tratado = str(comando).upper().replace("F", "").replace("P", "").replace("[", "").replace("]", "")\
            .replace("(", "").replace(")", "").replace("{", "").replace("}", "")
        return comando_tratado

    def acesso_inicial(self, chave, senha, cic=True):
        """
        Com um sisbb na primeira tela, acessa o cic 50 e deixa o sisbb pronto para acessar qualquer aplicativo.
        :param chave: matricula do funcionario.
        :param senha: senha do funcionario.
        :param cic: opcao de realizar o acesso via cic (processos automatizados) ou nao. O padrao eh sim.
        """
        self.__chave = chave
        self.__senha = senha
        self.aguardar(20, 39, "SISBB")
        self.teclar("enter")
        self.aguardar(14, 2, "Senha")
        self.colar(13, 21, self.__chave)
        self.colar(14, 21, self.__senha, "enter")
        self.atualizar()

        if self.copiar(9, 2, 22) == "Codigo/Senha invalidos":
            raise ValueError("Codigo/Senha invalidos")

        self.aguardar(15, 2, "Aplicativo")

        if cic:
            self.__acesso_cic()

    def __acesso_cic(self):
        self.aguardar(15, 2, "Aplicativo")
        self.colar(15, 14, "CIC")
        self.colar(16, 14, self.__senha, "enter")
        self.aguardar(1, 2, "CIC")
        self.colar(21, 19, "50", "enter")

        if self.comparar(23, 2, "Acesso não autorizado"):
            raise PermissionError("Acesso não autorizado ao CIC 50")

        self.aguardar(15, 2, "Aplicativo")

    @property
    def chave(self):
        return self.__chave

    @property
    def senha(self):
        return self.__senha
