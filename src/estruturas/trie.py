class NoTrie:
    def __init__(self):
        self.filhos = {}
        self.fim_palavra = False
        self.receitas = []


class ArvoreTrie:
    def __init__(self):
        self.raiz = NoTrie()

    def inserir(self, palavra, receita):
        no_atual = self.raiz
        palavra = palavra.lower().strip()

        for caractere in palavra:
            if caractere not in no_atual.filhos:
                no_atual.filhos[caractere] = NoTrie()
            no_atual = no_atual.filhos[caractere]

        no_atual.fim_palavra = True
        no_atual.receitas.append(receita)

    def buscar_exato(self, palavra):
        no_atual = self.raiz
        palavra = palavra.lower().strip()

        for caractere in palavra:
            if caractere not in no_atual.filhos:
                return []
            no_atual = no_atual.filhos[caractere]

        if no_atual.fim_palavra:
            return no_atual.receitas
        return []

    def buscar_prefixo(self, prefixo):
        no_atual = self.raiz
        prefixo = prefixo.lower().strip()

        for caractere in prefixo:
            if caractere not in no_atual.filhos:
                return []
            no_atual = no_atual.filhos[caractere]

        receitas_encontradas = []
        self._coletar_receitas(no_atual, receitas_encontradas)
        return receitas_encontradas

    def _coletar_receitas(self, no, lista_receitas):
        if no.fim_palavra:
            lista_receitas.extend(no.receitas)

        for filho in no.filhos.values():
            self._coletar_receitas(filho, lista_receitas)

    def listar_todas(self):
        receitas = []
        self._coletar_receitas(self.raiz, receitas)
        return receitas
