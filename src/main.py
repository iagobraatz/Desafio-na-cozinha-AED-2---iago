from pathlib import Path

from estruturas.btree import ArvoreB
from estruturas.hash_table import TabelaHash
from estruturas.trie import ArvoreTrie
from models.receita import Receita
from services.busca_service import BuscaService
from services.integridade_service import IntegridadeService
from services.recomendacao_service import RecomendacaoService
from services.receita_service import ReceitaService
from utils.hash_util import HashUtil


CAMINHO_JSON = Path("data/receitas.json")


def formatar_receita(receita: Receita) -> str:
    return (
        f"ID: {receita.id_receita} | "
        f"Nome: {receita.nome} | "
        f"Categoria: {receita.categoria} | "
        f"Ingredientes: {', '.join(receita.ingredientes)} | "
        f"Tempo: {receita.tempo_preparo} min | "
        f"Custo: R$ {receita.custo_estimado:.2f} | "
        f"Avaliação: {receita.avaliacao_clientes:.1f}"
    )


def carregar_estruturas():
    servico_receitas = ReceitaService(CAMINHO_JSON)
    receitas = servico_receitas.carregar_receitas()

    tabela_hash = TabelaHash()
    arvore_trie = ArvoreTrie()
    arvore_b = ArvoreB(grau_minimo=2)

    for receita in receitas:
        tabela_hash.inserir(receita.id_receita, receita)
        arvore_trie.inserir(receita.nome, receita)
        arvore_b.inserir(receita.tempo_preparo, receita)

    busca_service = BuscaService(tabela_hash, arvore_trie, arvore_b)
    integridade_service = IntegridadeService()
    recomendacao_service = RecomendacaoService()

    return receitas, tabela_hash, arvore_trie, arvore_b, busca_service, integridade_service, recomendacao_service


def menu() -> None:
    receitas, tabela_hash, arvore_trie, arvore_b, busca_service, integridade_service, recomendacao_service = carregar_estruturas()

    print("\n=== DESAFIO NA COZINHA ===")
    print(f"Receitas carregadas: {len(receitas)}")

    while True:
        print("\n1 - Listar todas as receitas")
        print("2 - Buscar receita por ID")
        print("3 - Buscar receita por nome/prefixo")
        print("4 - Buscar receitas por categoria")
        print("5 - Modo Investigação")
        print("6 - Modo Chef")
        print("7 - Buscar por ingrediente")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            print("Encerrando o sistema...")
            break

        elif opcao == "1":
            for receita in receitas:
                print(formatar_receita(receita))

        elif opcao == "2":
            id_receita = input("Digite o ID da receita: ").strip()
            receita = busca_service.buscar_por_id(id_receita)
            if receita:
                print(formatar_receita(receita))
            else:
                print("Receita não encontrada.")

        elif opcao == "3":
            termo = input("Digite o nome ou prefixo: ").strip()
            resultados = busca_service.buscar_por_prefixo(termo)
            if resultados:
                for receita in resultados:
                    print(formatar_receita(receita))
            else:
                print("Nenhuma receita encontrada.")

        elif opcao == "4":
            categoria = input("Digite a categoria: ").strip()
            resultados = busca_service.buscar_por_categoria(categoria, receitas)
            if resultados:
                for receita in resultados:
                    print(formatar_receita(receita))
            else:
                print("Nenhuma receita encontrada nessa categoria.")

        elif opcao == "5":
            print("\n--- Modo Investigação ---")
            repetidas = integridade_service.detectar_repetidas(receitas)
            conflitos = integridade_service.detectar_conflitos_por_nome(receitas)

            print(f"Receitas repetidas encontradas: {len(repetidas)}")
            for item in repetidas:
                print(f"- Original: {item['receita_original'].nome} | Repetida: {item['receita_repetida'].nome}")

            print(f"Conflitos por nome encontrados: {len(conflitos)}")
            for conflito in conflitos:
                print(f"- Nome: {conflito['nome']}")
                for receita in conflito["receitas"]:
                    print(f"  * {formatar_receita(receita)}")

        elif opcao == "6":
            print("\n--- Modo Chef ---")
            print("1 - Menu econômico")
            print("2 - Menu rápido")
            print("3 - Melhores avaliadas")
            subopcao = input("Escolha uma opção: ").strip()

            if subopcao == "1":
                limite_custo = float(input("Digite o limite de custo: ").strip())
                resultados = recomendacao_service.recomendar_menu_economico(receitas, limite_custo)
                for receita in resultados:
                    print(formatar_receita(receita))

            elif subopcao == "2":
                limite_tempo = int(input("Digite o limite de tempo (min): ").strip())
                resultados = recomendacao_service.recomendar_menu_rapido(receitas, limite_tempo)
                for receita in resultados:
                    print(formatar_receita(receita))

            elif subopcao == "3":
                quantidade = int(input("Digite a quantidade máxima: ").strip())
                resultados = recomendacao_service.recomendar_melhores_avaliadas(receitas, quantidade)
                for receita in resultados:
                    print(formatar_receita(receita))
            else:
                print("Opção inválida.")
        elif opcao == "7":
            ingrediente = input("Digite o ingrediente: ").strip()
            resultados = busca_service.buscar_por_ingrediente(ingrediente, receitas)
            
            if resultados:
                for receita in resultados:
                    print(formatar_receita(receita))
            else:
                print("Nenhuma receita encontrada.")        
# IAGO KAINAN BUBOLZ BRAATZ
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
