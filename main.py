import time
from bnb import branch_and_bound, get_matrix

# Definição de códigos de cor ANSI para os diferentes custos de distância
# Para facilitar a verificação manual
COLORS = {
    0: "\033[92m",  # Verde para distância de 0
    1: "\033[92m",  # Verde para distância de 1
    2: "\033[94m",  # Azul para distância de 2
    3: "\033[93m",  # Amarelo para distância de 3
    4: "\033[91m",  # Vermelho para distância de 4
    5: "\033[95m",  # Roxo para distância de 5
    6: "\033[96m",  # Azul Ciano para distância de >= 6
    "reset": "\033[0m"  # Reset na cor
}


# Função que faz print dos resultados
def print_matrix_with_stations(matrix, stations):
    n, m = len(matrix), len(matrix[0])  # Dimensões da matriz
    distances = [[float('inf')] * m for _ in range(n)]  # Inicialização da matriz de distâncias

    # Distância mínima entre cada parcela e uma qualquer estação
    #  Pontos da estação são (x, y)
    for x, y in stations:
        #  As parcelas são representadas pelos pontos (i, j)
        for i in range(n):
            for j in range(m):
                #  Distância de Manhattan é definida por max(abs(i - x), abs(j - y))
                distances[i][j] = min(distances[i][j], max(abs(i - x), abs(j - y)))

    #  Itera pela matriz original para preparar a impressão
    for i, row in enumerate(matrix):
        row_str = ""
        for j, cell in enumerate(row):
            distance = distances[i][j]
            if distance > 6:
                distance = 6  # As distâncias superiores a 6 também são pintadas de azul ciano
            color_code = COLORS[distance]  # Obtem o código de cor correspondente à distância
            if (i, j) in stations:
                cell_str = f"{cell}#"  # Marca a posição da estação
            else:
                cell_str = str(cell)  # Mostra o valor da parcela
            row_str += f"{color_code}{cell_str:<3}{COLORS['reset']}"  # Adiciona a célula colorida à linha
        print(row_str)  # Print da matriz

def main():
    matrix_id = input("Escolha uma instância para resolver (ex. 'id1', 'id2'): ")
    matrix = get_matrix(matrix_id)

    # As instâncias mais complexas têm uma fila de prioridade limitada
    # Para que se consiga resolver no tempo e número de avaliações pretendidos
    if matrix_id in ['id17', 'id18', 'id19', 'id20']:
        max_queue_size = 140
    else:
        max_queue_size = float('inf') # Caso contrário não há limitações na fila

    start_time = time.time()  # Contabilização de tempo
    best_cost, stations, evaluation_count = branch_and_bound(matrix_id, max_queue_size)  # Chamada do algoritmo
    end_time = time.time()  # Para o tempo
    elapsed_time = (end_time - start_time) * 1000  # Passa para msec

    #  Tratamento de erro para solução nula
    #  Display da melhor solução, caso exista, e alguns dados extra
    if stations is not None:
        print("\nMelhor solução:")
        print_matrix_with_stations(matrix, stations)
        print(f"\nCusto: {round(best_cost)}")  # Custo arredondado
    else:
        print("Sem solução.")
    print(f"Número de Avaliações: {evaluation_count}")
    print(f"Tempo: {elapsed_time:.3f} msec")

if __name__ == "__main__":
    main()
