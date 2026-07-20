from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from estruturas.btree import ArvoreB
from estruturas.hash_table import TabelaHash
from estruturas.trie import ArvoreTrie
from models.receita import Receita
from services.busca_service import BuscaService
from services.integridade_service import IntegridadeService
from services.inovacao_service import InovacaoService
from services.logistica_service import LogisticaService
from services.otimizacao_service import OtimizacaoService
from services.producao_service import ProducaoService
from services.receita_service import ReceitaService
from services.recomendacao_service import RecomendacaoService

CAMINHO_JSON = Path("data/receitas.json")
CAMINHO_BINARIO_BTREE = Path("data/arvore_b.bin")
CAMINHO_DEPENDENCIAS_PREPARO = Path("data/dependencias_preparo.json")
CAMINHO_REDE_ENTREGA = Path("data/rede_entrega.json")


@dataclass
class ContextoSistema:
    receitas: List[Receita]
    tabela_hash: TabelaHash
    arvore_trie: ArvoreTrie
    arvore_b: ArvoreB
    busca_service: BuscaService
    integridade_service: IntegridadeService
    recomendacao_service: RecomendacaoService
    producao_service: ProducaoService
    otimizacao_service: OtimizacaoService
    logistica_service: LogisticaService
    inovacao_service: InovacaoService


def formatar_receita(receita: Receita) -> str:
    return (
        f"ID: {receita.id_receita} | "
        f"Nome: {receita.nome} | "
        f"Categoria: {receita.categoria} | "
        f"Classe: {receita.classe_prato} | "
        f"Ingredientes: {', '.join(receita.ingredientes)} | "
        f"Tempo: {receita.tempo_preparo} min | "
        f"Custo: R$ {receita.custo_estimado:.2f} | "
        f"Venda: R$ {receita.valor_venda:.2f} | "
        f"Avaliação: {receita.avaliacao_clientes:.1f} | "
        f"Dificuldade: {receita.dificuldade_logistica}"
    )


def imprimir_receitas_ou_vazio(resultados: List[Receita]) -> None:
    if resultados:
        for receita in resultados:
            print(formatar_receita(receita))
    else:
        print("Nenhuma receita encontrada.")


def ler_inteiro_opcional(mensagem: str) -> Optional[int]:
    texto = input(mensagem).strip()
    if not texto:
        return None
    try:
        return int(texto)
    except ValueError:
        print("Valor inválido, ignorando limite.")
        return None


def ler_float_opcional(mensagem: str) -> Optional[float]:
    texto = input(mensagem).strip()
    if not texto:
        return None
    try:
        return float(texto)
    except ValueError:
        print("Valor inválido, ignorando limite.")
        return None
    
def ler_ingredientes_disponiveis_opcional(mensagem: str) -> Optional[set]:
    texto = input(mensagem).strip()
    if not texto:
        return None
    return {ingrediente.strip() for ingrediente in texto.split(",") if ingrediente.strip()}    


def carregar_estruturas() -> ContextoSistema:
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
    producao_service = ProducaoService(CAMINHO_DEPENDENCIAS_PREPARO)
    otimizacao_service = OtimizacaoService()
    logistica_service = LogisticaService(CAMINHO_REDE_ENTREGA)
    inovacao_service = InovacaoService(logistica_service)

    return ContextoSistema(
        receitas=receitas,
        tabela_hash=tabela_hash,
        arvore_trie=arvore_trie,
        arvore_b=arvore_b,
        busca_service=busca_service,
        integridade_service=integridade_service,
        recomendacao_service=recomendacao_service,
        producao_service=producao_service,
        otimizacao_service=otimizacao_service,
        logistica_service=logistica_service,
        inovacao_service=inovacao_service,
    )


def listar_pontos_rede(logistica_service: LogisticaService) -> None:
    print("\nEstações:")
    for estacao in logistica_service.estacoes:
        print(f"  {estacao['id']} - {estacao['nome']}")
    print("Regiões:")
    for regiao in logistica_service.regioes:
        print(f"  {regiao['id']} - {regiao['nome']}")

def listar_receitas_com_dependencias(producao_service: ProducaoService) -> None:
    print("\nReceitas com dependência de preparo cadastrada:")
    for id_receita in sorted(producao_service.ids_receitas, key=producao_service.obter_nome):
        print(f"  {id_receita} - {producao_service.obter_nome(id_receita)}")        


def menu_investigacao(contexto: ContextoSistema) -> None:
    while True:
        print("\n--- Modo Investigação ---")
        print("1 - Receitas repetidas e conflitos por nome")
        print("2 - Existe erro de dependência de preparo?")
        print("3 - Quais preparos faltam para uma receita?")
        print("4 - Existe gargalo operacional na rede de entrega?")
        print("5 - Quais são as Regiões isoladas e pontos críticos da rede de entrega?")
        print("0 - Voltar")

        subopcao = input("Escolha uma opção: ").strip()

        if subopcao == "0":
            break

        elif subopcao == "1":
            repetidas = contexto.integridade_service.detectar_repetidas(contexto.receitas)
            conflitos = contexto.integridade_service.detectar_conflitos_por_nome(contexto.receitas)

            print(f"Receitas repetidas encontradas: {len(repetidas)}")
            for item in repetidas:
                print(f"- Original: {item['receita_original'].nome} | Repetida: {item['receita_repetida'].nome}")

            print(f"Conflitos por nome encontrados: {len(conflitos)}")
            for conflito in conflitos:
                print(f"- Nome: {conflito['nome']}")
                for receita in conflito["receitas"]:
                    print(f"  * {formatar_receita(receita)}")

        elif subopcao == "2":
            viavel = contexto.producao_service.existe_sequencia_viavel()
            print(f"Existe sequência viável para todas as preparações cadastradas: {viavel}")

            if not viavel:
                inconsistencias = contexto.producao_service.identificar_inconsistencias()

                if inconsistencias["referencias_invalidas_nomes"]:
                    print("Referências inválidas (dependência para um preparo não cadastrado):")
                    for item in inconsistencias["referencias_invalidas_nomes"]:
                        print(f"  {item['origem']} -> {item['dependencia_inexistente']}")

                if inconsistencias["vertices_em_ciclo_nomes"]:
                    print("Preparações presas em dependência circular:")
                    for nome in inconsistencias["vertices_em_ciclo_nomes"]:
                        print(f"  - {nome}")

        elif subopcao == "3":
            listar_receitas_com_dependencias(contexto.producao_service)
            id_receita = input("Digite o ID da receita: ").strip()
            try:
                resultado = contexto.producao_service.preparos_necessarios_para(id_receita)
                print(f"Preparos necessários para {resultado['nome_receita']}:")
                for nome in resultado["preparos_necessarios_nomes"]:
                    print(f"  - {nome}")
                print(f"Tempo total estimado de preparo: {resultado['tempo_total_estimado_min']} min")
            except ValueError as erro:
                print(erro)

        elif subopcao == "4":
            resultado = contexto.logistica_service.calcular_fluxo_maximo()
            print(f"Capacidade máxima de atendimento: {resultado['fluxo_maximo_pedidos_hora']} pedidos/hora")
            print(f"Produção total das estações: {resultado['capacidade_producao_total']} pedidos/hora")
            print(f"Capacidade da frota: {resultado['capacidade_frota_total']} pedidos/hora")
            print(f"Limite agregado das regiões: {resultado['capacidade_regioes_total']} pedidos/hora")
            print(f"Gargalo identificado: {resultado['recurso_gargalo']}")
            for aresta in resultado["arestas_gargalo"]:
                print(f"  {aresta['origem_nome']} -> {aresta['destino_nome']} (capacidade {aresta['capacidade']})")

        elif subopcao == "5":
            diagnostico = contexto.logistica_service.diagnostico()
            if diagnostico["grafo_conectado"]:
                print("Rede totalmente conectada: nenhuma região isolada no momento.")
            else:
                componentes = contexto.logistica_service.grafo_geografico.componentes_conexos()
                print(f"ATENÇÃO: a rede está fragmentada em {len(componentes)} componentes isolados entre si:")
                for componente in componentes:
                    nomes = [contexto.logistica_service.obter_nome(v) for v in componente]
                    print(f"  - {', '.join(nomes)}")

            criticos = contexto.logistica_service.identificar_pontos_criticos()
            if not criticos:
                print("Nenhum ponto crítico (ponte) encontrado na rede.")
            for item in criticos:
                print(f"Conexão crítica: {item['origem_nome']} -- {item['destino_nome']} ({item['tempo_min']} min)")
                print(f"  Se essa conexão falhar, ficam isolados: {', '.join(item['vertices_isolados_nomes'])}")

        else:
            print("Opção inválida.")


def menu_chef(contexto: ContextoSistema) -> None:
    while True:
        print("\n--- Modo Chef ---")
        print("1 - Menu econômico")
        print("2 - Menu rápido")
        print("3 - Melhores avaliadas")
        print("4 - Sequência de produção do menu do dia")
        print("5 - Menu Degustação VIP")
        print("6 - Menu Especial Dia dos Namorados")
        print("0 - Voltar")

        subopcao = input("Escolha uma opção: ").strip()

        if subopcao == "0":
            break

        elif subopcao == "1":
            limite_custo = float(input("Digite o limite de custo: ").strip())
            resultados = contexto.recomendacao_service.recomendar_menu_economico(contexto.receitas, limite_custo)
            imprimir_receitas_ou_vazio(resultados)

        elif subopcao == "2":
            limite_tempo = int(input("Digite o limite de tempo (min): ").strip())
            resultados = contexto.recomendacao_service.recomendar_menu_rapido(contexto.receitas, limite_tempo)
            imprimir_receitas_ou_vazio(resultados)

        elif subopcao == "3":
            quantidade = int(input("Digite a quantidade máxima: ").strip())
            resultados = contexto.recomendacao_service.recomendar_melhores_avaliadas(contexto.receitas, quantidade)
            imprimir_receitas_ou_vazio(resultados)

        elif subopcao == "4":
            listar_receitas_com_dependencias(contexto.producao_service)
            ids_texto = input("Digite os IDs das receitas do menu, separados por vírgula: ").strip()
            ids_receitas = [id_receita.strip() for id_receita in ids_texto.split(",") if id_receita.strip()]
            try:
                resultado = contexto.producao_service.sequencia_producao_menu(ids_receitas)
                print(f"Sequência de produção (viável: {resultado['viavel']}):")
                for nome in resultado["sequencia_nomes"]:
                    print(f"  - {nome}")
                if resultado["bloqueados_nomes"]:
                    print("Bloqueados por inconsistência de dependência:")
                    for nome in resultado["bloqueados_nomes"]:
                        print(f"  - {nome}")
                print(f"Tempo total estimado: {resultado['tempo_total_estimado_min']} min")
            except ValueError as erro:
                print(erro)

        elif subopcao == "5":
            print("Critério: 1 - Lucro | 2 - Avaliação")
            criterio = "avaliacao" if input("Escolha o critério: ").strip() == "2" else "lucro"

            print("Recurso principal: 1 - Orçamento | 2 - Tempo")
            recurso_principal = "tempo" if input("Escolha o recurso principal: ").strip() == "2" else "orcamento"

            limite_recurso_principal = int(input(f"Digite o limite de {recurso_principal}: ").strip())
            limite_ingredientes_raros = ler_inteiro_opcional("Limite de ingredientes raros (Enter para não limitar): ")
            capacidade_equipe = ler_inteiro_opcional("Capacidade da equipe em unidades (Enter para não limitar): ")
            ingredientes_disponiveis = ler_ingredientes_disponiveis_opcional(
                "Ingredientes disponíveis em estoque, separados por vírgula (Enter para não restringir): "
            )

            resultado = contexto.otimizacao_service.otimizar_menu_vip(
                contexto.receitas,
                criterio=criterio,
                recurso_principal=recurso_principal,
                limite_recurso_principal=limite_recurso_principal,
                limite_ingredientes_raros=limite_ingredientes_raros,
                capacidade_equipe=capacidade_equipe,
                ingredientes_disponiveis=ingredientes_disponiveis,
            )

            print(f"\nMenu VIP otimizado ({len(resultado['receitas'])} receitas):")
            for receita in resultado["receitas"]:
                print(formatar_receita(receita))
            print(f"Valor total ({criterio}): {resultado['valor_total']}")
            print(f"Uso do recurso principal: {resultado['uso_recurso_principal']} / {limite_recurso_principal}")
            print(f"Ajustado por restrições secundárias: {resultado['ajustado_por_restricoes_secundarias']}")

        elif subopcao == "6":
            print("Critério: 1 - Lucro | 2 - Avaliação | 3 - Tempo")
            criterio = {"1": "lucro", "2": "avaliacao", "3": "tempo"}.get(input("Escolha o critério: ").strip(), "lucro")
            tempo_maximo = ler_inteiro_opcional("Tempo máximo de preparo em minutos (Enter para não limitar): ")
            custo_maximo = ler_float_opcional("Custo máximo (Enter para não limitar): ")
            ingredientes_disponiveis = ler_ingredientes_disponiveis_opcional(
                "Ingredientes disponíveis em estoque, separados por vírgula (Enter para não restringir): "
            )

            resultado = contexto.otimizacao_service.sugerir_menu_dia_dos_namorados(
                contexto.receitas, criterio=criterio, tempo_maximo=tempo_maximo, custo_maximo=custo_maximo,
                ingredientes_disponiveis=ingredientes_disponiveis,
            )

            if not resultado["encontrado"]:
                print("Nenhuma combinação viável encontrada com essas restrições.")
            else:
                print("\nMenu Especial Dia dos Namorados:")
                print(f"Entrada: {resultado['entrada']}")
                print(f"Prato principal: {resultado['prato_principal']}")
                print(f"Sobremesa: {resultado['sobremesa']}")
                print(f"Valor total de venda: R$ {resultado['valor_total_venda']:.2f}")
                print(f"Custo estimado: R$ {resultado['custo_estimado']:.2f}")
                print(f"Lucro estimado: R$ {resultado['lucro_estimado']:.2f}")
                print(f"Tempo total de preparo: {resultado['tempo_total_preparo_min']} minutos")
                print(f"Avaliação média: {resultado['avaliacao_media']}")
                print(f"Dificuldade logística: {resultado['dificuldade_logistica']}")
                print(f"Justificativa: {resultado['justificativa']}")

        else:
            print("Opção inválida.")


def menu_logistica(contexto: ContextoSistema) -> None:
    while True:
        print("\n--- Modo Logística ---")
        print("1 - Listar pontos da rede de entrega")
        print("2 - Menor rede de conexões (árvore geradora mínima)")
        print("3 - Consultar rota entre dois pontos")
        print("4 - Consultar caminho alternativo")
        print("5 - Capacidade máxima de atendimento")
        print("6 - Roteirizar entrega com múltiplas paradas")
        print("0 - Voltar")

        subopcao = input("Escolha uma opção: ").strip()

        if subopcao == "0":
            break

        elif subopcao == "1":
            listar_pontos_rede(contexto.logistica_service)

        elif subopcao == "2":
            resultado = contexto.logistica_service.arvore_geradora_minima()
            print(f"Conecta todos os pontos: {resultado['conecta_todos_os_pontos']}")
            print(f"Tempo total da rede mínima: {resultado['peso_total_min']} min")
            print(f"Arestas usadas: {resultado['quantidade_arestas_mst']} de {resultado['quantidade_arestas_originais']} disponíveis")
            for origem, destino, peso in resultado["arestas_nomes"]:
                print(f"  {origem} -- {destino} ({peso} min)")

        elif subopcao == "3":
            listar_pontos_rede(contexto.logistica_service)
            origem = input("ID do ponto de origem: ").strip()
            destino = input("ID do ponto de destino: ").strip()
            try:
                resultado = contexto.logistica_service.menor_caminho(origem, destino)
                if resultado["encontrado"]:
                    print(" -> ".join(resultado["caminho_nomes"]))
                    print(f"Tempo total: {resultado['tempo_total_min']} min")
                else:
                    print("Não existe rota entre esses pontos.")
            except ValueError as erro:
                print(erro)

        elif subopcao == "4":
            listar_pontos_rede(contexto.logistica_service)
            origem = input("ID do ponto de origem: ").strip()
            destino = input("ID do ponto de destino: ").strip()
            try:
                resultado = contexto.logistica_service.caminho_alternativo(origem, destino)
                principal = resultado["caminho_principal"]
                alternativo = resultado["caminho_alternativo"]
                print("Rota principal:", " -> ".join(principal["caminho_nomes"]), f"({principal['tempo_total_min']} min)")
                if alternativo["encontrado"]:
                    print("Rota alternativa:", " -> ".join(alternativo["caminho_nomes"]), f"({alternativo['tempo_total_min']} min)")
                else:
                    print("Não existe rota alternativa — esse trecho depende de um único caminho crítico.")
            except ValueError as erro:
                print(erro)

        elif subopcao == "5":
            quantidade_entregadores = ler_inteiro_opcional(
                "Simular com quantos entregadores? (Enter para usar o valor cadastrado): "
            )
            resultado = contexto.logistica_service.calcular_fluxo_maximo(quantidade_entregadores=quantidade_entregadores)
            print(f"Capacidade máxima de atendimento: {resultado['fluxo_maximo_pedidos_hora']} pedidos/hora")
            print(f"Produção total das estações: {resultado['capacidade_producao_total']} pedidos/hora")
            print(f"Capacidade da frota: {resultado['capacidade_frota_total']} pedidos/hora")
            print(f"Limite agregado das regiões: {resultado['capacidade_regioes_total']} pedidos/hora")
            print(f"Gargalo identificado: {resultado['recurso_gargalo']}")

        elif subopcao == "6":
            listar_pontos_rede(contexto.logistica_service)
            partida = input("ID do ponto de partida: ").strip()
            pontos_texto = input("IDs dos pontos a visitar, separados por vírgula: ").strip()
            pontos_visita = [ponto.strip() for ponto in pontos_texto.split(",") if ponto.strip()]
            retornar_ao_inicio = input("Retornar ao ponto de partida ao final? (s/n): ").strip().lower() == "s"
            try:
                resultado = contexto.inovacao_service.calcular_rota_entrega(partida, pontos_visita, retornar_ao_inicio)
                print("Rota otimizada:", " -> ".join(resultado["rota_nomes"]))
                print(f"Tempo total: {resultado['tempo_total_min']} min")
                print(f"Melhoria do 2-opt sobre a rota inicial: {resultado['melhoria_2opt_min']} min")
            except ValueError as erro:
                print(erro)

        else:
            print("Opção inválida.")


def menu_recuperacao_p1(contexto: ContextoSistema) -> None:
    while True:
        print("\n--- Recuperação P1: Árvore B em Binário ---")
        print("1 - Salvar Árvore B em binário")
        print("2 - Carregar Árvore B do binário")
        print("3 - Diagnóstico da Árvore B")
        print("4 - Buscar na Árvore B carregada")
        print("0 - Voltar")

        subopcao = input("Escolha uma opção: ").strip()

        if subopcao == "0":
            break

        elif subopcao == "1":
            try:
                contexto.arvore_b.salvar_em_binario(CAMINHO_BINARIO_BTREE)
                print(f"Árvore B salva com sucesso em: {CAMINHO_BINARIO_BTREE}")
            except Exception as erro:
                print(f"Erro ao salvar a Árvore B: {erro}")

        elif subopcao == "2":
            try:
                contexto.arvore_b = ArvoreB.carregar_de_binario(CAMINHO_BINARIO_BTREE)
                contexto.busca_service = BuscaService(contexto.tabela_hash, contexto.arvore_trie, contexto.arvore_b)
                print("Árvore B carregada com sucesso do arquivo binário.")
            except Exception as erro:
                print(f"Erro ao carregar a Árvore B: {erro}")

        elif subopcao == "3":
            diagnostico = contexto.arvore_b.diagnostico()
            print("\n--- Diagnóstico da Árvore B ---")
            print(f"Grau mínimo: {diagnostico['grau_minimo']}")
            print(f"Quantidade de nós: {diagnostico['quantidade_nos']}")
            print(f"Quantidade de chaves: {diagnostico['quantidade_chaves']}")
            print(f"Altura: {diagnostico['altura']}")

        elif subopcao == "4":
            try:
                if not CAMINHO_BINARIO_BTREE.exists():
                    print("O arquivo binário da Árvore B ainda não existe. Use a opção 1 primeiro.")
                    continue

                arvore_persistida = ArvoreB.carregar_de_binario(CAMINHO_BINARIO_BTREE)
                busca_persistida = BuscaService(contexto.tabela_hash, contexto.arvore_trie, arvore_persistida)
                print("RAM limpa simulada: Árvore B foi recarregada do binário.")

                chave = int(input("Digite o tempo de preparo para buscar: ").strip())
                resultados = busca_persistida.buscar_por_tempo(chave)
                imprimir_receitas_ou_vazio(resultados)
            except ValueError:
                print("Digite um valor numérico válido.")
            except Exception as erro:
                print(f"Erro na recuperação P1: {erro}")

        else:
            print("Opção inválida.")


def menu() -> None:
    contexto = carregar_estruturas()

    print("\n=== DESAFIO NA COZINHA ===")
    print(f"Receitas carregadas: {len(contexto.receitas)}")

    while True:
        print("\n--- Consulta Rápida ---")
        print("1 - Listar todas as receitas")
        print("2 - Buscar receita por ID")
        print("3 - Buscar receita por nome/prefixo")
        print("4 - Buscar receitas por categoria")
        print("5 - Buscar por ingrediente")
        print("\n--- Modos de Interação ---")
        print("6 - Modo Investigação")
        print("7 - Modo Chef")
        print("8 - Modo Logística")
        print("\n--- Outros ---")
        print("9 - Recuperação P1: Árvore B em binário")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            print("Encerrando o sistema...")
            break

        elif opcao == "1":
            for receita in contexto.receitas:
                print(formatar_receita(receita))

        elif opcao == "2":
            id_receita = input("Digite o ID da receita: ").strip()
            receita = contexto.busca_service.buscar_por_id(id_receita)
            print(formatar_receita(receita) if receita else "Receita não encontrada.")

        elif opcao == "3":
            termo = input("Digite o nome ou prefixo: ").strip()
            imprimir_receitas_ou_vazio(contexto.busca_service.buscar_por_prefixo(termo))

        elif opcao == "4":
            categoria = input("Digite a categoria: ").strip()
            imprimir_receitas_ou_vazio(contexto.busca_service.buscar_por_categoria(categoria, contexto.receitas))

        elif opcao == "5":
            ingrediente = input("Digite o ingrediente: ").strip()
            imprimir_receitas_ou_vazio(contexto.busca_service.buscar_por_ingrediente(ingrediente, contexto.receitas))

        elif opcao == "6":
            menu_investigacao(contexto)

        elif opcao == "7":
            menu_chef(contexto)

        elif opcao == "8":
            menu_logistica(contexto)

        elif opcao == "9":
            menu_recuperacao_p1(contexto)

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()