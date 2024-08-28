from matrix import get_matrix
from heapq import heappush, heappop
import time

#  A classe das configurações representa qualquer geração
class Configuration:
    def __init__(self, points, cost=0, is_solution=False):
        self.points = points  # Os pontos onde estão estações
        self.cost = cost  # O custo da configuração
        self.is_solution = is_solution  # Boolean que determina se é ou não solução

    # Sobrecarga do operador < para comparar configurações pelo custo
    def __lt__(self, other):
        return self.cost < other.cost


evaluation_count = 0  # Counter do número de avaliações

# Função que calcula o valor de B e, por acréscimo, o custo de cada configuração
def calculate_cost_and_B(matrix, configuration):
    global evaluation_count
    evaluation_count += 1  # Incrementa-se o counter das avaliações

    A = len(configuration.points)  # A é igual ao número de estações (número de pontos)
    total_families = sum(sum(row) for row in matrix)  # Soma do total de famílias na matriz
    total_distance_cost = 0  # Declaração da variável do custo total da distância

    # Percorre cada parcela da matriz para calcular o custo total da distância (de todos os pontos somados)
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            # Calcula a distância mínima de Manhattan entre o ponto (i, j) e a estação mais próxima
            min_distance = min([max(abs(i - x), abs(j - y)) for x, y in configuration.points], default=float('inf'))
            if min_distance > 6:
                min_distance = 6
            distance_cost = [0, 0, 1, 2, 4, 8, 10][min_distance]
            family_count = matrix[i][j]  # Número de famílias no ponto (i, j)
            cell_distance_cost = family_count * distance_cost  # Custo da distância para o ponto (i, j)
            total_distance_cost += cell_distance_cost  # Incrementa o custo total

    # Aplicação da fórmula de B
    B = total_distance_cost / total_families if total_families != 0 else 0
    cost = 1000 * A + 100 * B  # Aplicação da fórmula do custo
    configuration.cost = cost  # Atribuição do custo à configuração avaliada
    configuration.is_solution = (B <= 3)  # Valida ou não a solução
    return configuration


# Verifica se a estação não está demasiado próxima de outra estação (+ eficiência)
def is_valid_new_point(points, new_point):
    for x, y in points:
        if max(abs(x - new_point[0]), abs(y - new_point[1])) <= 2:  # Tem de estar a mais de 2 de distância
            return False
    return True


def expand_configuration(matrix, config, min_cost_solution):
    n, m = len(matrix), len(matrix[0]) # Dimensões da matriz
    new_configs = []  # Guarda as novas configurações geradas
    for i in range(1, n - 1):  # Para poupar tempo de execução
        for j in range(1, m - 1):  # Salta a extremidade do tabuleiro (+ eficiência)
            # Verifica se a parcela é válida (não tem já estação e está suficientemente longe de outra)
            if (i, j) not in config.points and is_valid_new_point(config.points, (i, j)):
                new_points = config.points + [(i, j)]  # Adiciona o novo ponto à lista de pontos
                new_config = Configuration(new_points)  # Cria configuração com os pontos
                new_config = calculate_cost_and_B(matrix, new_config)  # Chama a função que atribui custo e valor de B
                # Só considera as que estão abaixo do upper-bound
                if new_config.cost < min_cost_solution:
                    new_configs.append(new_config)
    return new_configs


def branch_and_bound(matrix_id, max_queue_size):
    global evaluation_count
    evaluation_count = 0

    matrix = get_matrix(matrix_id)  # Obtem a matriz com base no ID fornecido pelo utilizador
    min_cost_solution = float('inf')  # Valor da melhor solução (menor custo) serve como upper bound, inicia com +inf.
    best_config = None  # Incializa melhor configuração como nula
    pq = []  # Fila de prioridade começa vazia
    initial_config = Configuration([], 0, False)  # Configuração Inicial (sem estação)
    heappush(pq, initial_config)  # Adiciona a configuração inicial à priority queue

    start_time = time.time()  # Começa a contagem
    time_limit = 60  # 60 segundos de limite de tempo
    eval_limit = 100000  # Limite de 100 000 avaliações

    while pq:
        current_time = time.time()  # Controla o tempo
        if current_time - start_time > time_limit:
            print("Tempo limite excedido.")
            break
        if evaluation_count >= eval_limit:
            print("Limite de avaliações excedido.")
            break  # Limita o número de avaliações
        current_config = heappop(pq)  # Faz pop da primeira configuração na fila
        new_configs = expand_configuration(matrix, current_config, min_cost_solution)  # Expande essa configuração
        # Faz update da melhor solução e guarda a configuração (caso a haja)
        for config in new_configs:
            if config.is_solution and config.cost < min_cost_solution:
                min_cost_solution = config.cost
                best_config = config
            # Se ainda não for solução vai para a fila
            if not config.is_solution:
                heappush(pq, config)
        # Chamada do método de prune da árvore
        pq = prune_priority_queue(pq, min_cost_solution, max_queue_size)

    return min_cost_solution, best_config.points if best_config else None, evaluation_count


# Função que vai fazer prune ou "podar" as configurações que não vale a pena explorar
def prune_priority_queue(pq, min_cost_solution, max_queue_size):
    # Filtra as configurações com um custo menor ou igual ao custo mínimo encontrado
    pruned_pq = [config for config in pq if config.cost <= min_cost_solution]
    # Verifica se o tamanho máximo da fila não deve ter restirções (instâncias 1-16)
    if max_queue_size == float('inf'):
        return pruned_pq  # Não limita o tamanho da fila
    return sorted(pruned_pq, key=lambda x: x.cost)[:max_queue_size] # Limita a fila (instâncias 17-20)

