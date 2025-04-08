import random
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import os
from matplotlib.gridspec import GridSpec
import time

class ChessBoardGame:
    def __init__(self):
        """Inicializa el juego con el tablero y configuraciones iniciales"""
        self.board_size = 4
        self.positions = {
            'P1': {'current': 1, 'start': 1, 'end': 16},
            'P2': {'current': 4, 'start': 4, 'end': 13}
        }
        self.turn = None
        self.moves_history = {'P1': [], 'P2': []}
        self.all_possible_moves = {'P1': set(), 'P2': set()}
        self.winning_moves = {'P1': set(), 'P2': set()}
        self.move_symbols = ['U', 'D', 'L', 'R', 'UL', 'UR', 'DL', 'DR']
        self.max_moves = 0
        self.current_move_count = 0
        self.game_over = False
        self.winner = None
        self.mode = None
        self.move_sequence = {'P1': [], 'P2': []}
        
        # Configurar figura unificada
        self.fig = plt.figure(figsize=(14, 7))
        self.gs = GridSpec(1, 2, width_ratios=[1, 1.5])
        
        # Añadir texto para el temporizador
        self.timer_text = None
        
        if not os.path.exists('output'):
            os.makedirs('output')

    def initialize_game(self, mode='auto', max_moves=10, move_sequence=None):
        """Inicializa el juego con los parámetros dados"""
        self.mode = mode
        self.max_moves = max(max_moves, 3)
        self.max_moves = min(self.max_moves, 100)
        
        self.turn = 'P1' if random.randint(0, 1) == 0 else 'P2'
        print(f"El jugador {self.turn} comienza primero.")
        
        if mode == 'manual' and move_sequence:
            seq_len = len(move_sequence)
            self.move_sequence['P1'] = list(move_sequence[:seq_len//2])
            self.move_sequence['P2'] = list(move_sequence[seq_len//2:])
        elif mode == 'manual':
            self.move_sequence['P1'] = [random.choice(self.move_symbols) for _ in range(self.max_moves//2)]
            self.move_sequence['P2'] = [random.choice(self.move_symbols) for _ in range(self.max_moves//2)]

    def update_timer_display(self, seconds_left):
        """Actualiza el display del temporizador"""
        if self.timer_text is not None:
            self.timer_text.remove()
        
        self.timer_text = self.fig.text(
            0.5, 0.95, 
            f"Tiempo para próximo movimiento: {seconds_left} segundos", 
            ha='center', va='top', fontsize=12, color='red'
        )
        plt.draw()

    def countdown(self, duration=10):
        """Muestra una cuenta regresiva"""
        for i in range(duration, 0, -1):
            self.update_timer_display(i)
            plt.pause(1)
        
        self.update_timer_display(0)
        plt.pause(0.5)

    def position_to_coords(self, position):
        """Convierte número de posición (1-16) a coordenadas del tablero (fila, columna)"""
        row = (position - 1) // self.board_size
        col = (position - 1) % self.board_size
        return row, col
    
    def coords_to_position(self, row, col):
        """Convierte coordenadas del tablero a número de posición"""
        return row * self.board_size + col + 1
    
    def is_valid_move(self, player, move):
        """Verifica si un movimiento es válido para la posición actual del jugador"""
        current_pos = self.positions[player]['current']
        row, col = self.position_to_coords(current_pos)
        
        if move == 'U':
            new_row, new_col = row - 1, col
        elif move == 'D':
            new_row, new_col = row + 1, col
        elif move == 'L':
            new_row, new_col = row, col - 1
        elif move == 'R':
            new_row, new_col = row, col + 1
        elif move == 'UL':
            new_row, new_col = row - 1, col - 1
        elif move == 'UR':
            new_row, new_col = row - 1, col + 1
        elif move == 'DL':
            new_row, new_col = row + 1, col - 1
        elif move == 'DR':
            new_row, new_col = row + 1, col + 1
        else:
            return False
        
        if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size:
            new_pos = self.coords_to_position(new_row, new_col)
            other_player = 'P2' if player == 'P1' else 'P1'
            if new_pos != self.positions[other_player]['current']:
                return True
        return False
    
    def get_possible_moves(self, player):
        """Obtiene todos los movimientos válidos para un jugador"""
        possible_moves = []
        for move in self.move_symbols:
            if self.is_valid_move(player, move):
                possible_moves.append(move)
        return possible_moves
    
    def make_move(self, player, move):
        """Ejecuta un movimiento para un jugador"""
        if self.game_over:
            return False
            
        current_pos = self.positions[player]['current']
        row, col = self.position_to_coords(current_pos)
        
        if move == 'U':
            new_row, new_col = row - 1, col
        elif move == 'D':
            new_row, new_col = row + 1, col
        elif move == 'L':
            new_row, new_col = row, col - 1
        elif move == 'R':
            new_row, new_col = row, col + 1
        elif move == 'UL':
            new_row, new_col = row - 1, col - 1
        elif move == 'UR':
            new_row, new_col = row - 1, col + 1
        elif move == 'DL':
            new_row, new_col = row + 1, col - 1
        elif move == 'DR':
            new_row, new_col = row + 1, col + 1
        
        new_pos = self.coords_to_position(new_row, new_col)
        self.positions[player]['current'] = new_pos
        self.moves_history[player].append((current_pos, new_pos, move))
        
        for possible_move in self.get_possible_moves(player):
            self.all_possible_moves[player].add((current_pos, possible_move))
            if new_pos == self.positions[player]['end']:
                self.winning_moves[player].add((current_pos, possible_move))
        
        if new_pos == self.positions[player]['end']:
            self.game_over = True
            self.winner = player
            print(f"¡El jugador {player} ha ganado!")
            return True
        
        self.current_move_count += 1
        if self.current_move_count >= self.max_moves:
            self.game_over = True
            print("Juego terminado sin ganador (límite de movimientos alcanzado).")
            return False
        
        self.turn = 'P2' if player == 'P1' else 'P1'
        return True

    def draw_board(self, ax):
        """Dibuja el tablero en el eje proporcionado"""
        ax.clear()
        ax.set_xlim(0, self.board_size)
        ax.set_ylim(0, self.board_size)
        ax.set_xticks(range(self.board_size + 1))
        ax.set_yticks(range(self.board_size + 1))
        ax.grid(True)
        ax.set_title(f"Tablero - Movimiento {self.current_move_count}")
        
        rectangles = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                color = 'white' if (i + j) % 2 == 0 else 'gray'
                rect = Rectangle((j, self.board_size - 1 - i), 1, 1, color=color)
                rectangles.append(rect)
        
        pc = PatchCollection(rectangles, match_original=True)
        ax.add_collection(pc)
        
        for player in ['P1', 'P2']:
            start_pos = self.positions[player]['start']
            end_pos = self.positions[player]['end']
            
            start_row, start_col = self.position_to_coords(start_pos)
            end_row, end_col = self.position_to_coords(end_pos)
            
            start_row_plt = self.board_size - 1 - start_row
            end_row_plt = self.board_size - 1 - end_row
            
            ax.text(start_col + 0.5, start_row_plt + 0.3, f"Inicio {player}", 
                   ha='center', va='center', fontsize=8)
            ax.text(end_col + 0.5, end_row_plt + 0.7, f"Fin {player}", 
                   ha='center', va='center', fontsize=8)
        
        for player in ['P1', 'P2']:
            pos = self.positions[player]['current']
            row, col = self.position_to_coords(pos)
            row_plt = self.board_size - 1 - row
            
            color = 'red' if player == 'P1' else 'blue'
            ax.plot(col + 0.5, row_plt + 0.5, 'o', markersize=20, 
                   color=color, alpha=0.5, label=f'Jugador {player}')
            
            ax.text(col + 0.5, row_plt + 0.5, player, 
                   ha='center', va='center', color='white', fontweight='bold')
        
        for player, history in self.moves_history.items():
            color = 'red' if player == 'P1' else 'blue'
            for move in history:
                from_pos, to_pos, _ = move
                from_row, from_col = self.position_to_coords(from_pos)
                to_row, to_col = self.position_to_coords(to_pos)
                
                from_row_plt = self.board_size - 1 - from_row
                to_row_plt = self.board_size - 1 - to_row
                
                ax.arrow(from_col + 0.5, from_row_plt + 0.5, 
                         (to_col - from_col) * 0.8, (to_row_plt - from_row_plt) * 0.8, 
                         head_width=0.1, head_length=0.1, fc=color, ec=color, alpha=0.3)
        
        ax.legend(loc='upper right')

    def draw_full_nfa(self, ax):
        """Dibuja el NFA en el eje proporcionado"""
        ax.clear()
        G = nx.DiGraph()
        
        for pos in range(1, 17):
            G.add_node(pos)
        
        edge_labels = {}
        for player in ['P1', 'P2']:
            color = 'red' if player == 'P1' else 'blue'
            for (from_pos, move) in self.all_possible_moves[player]:
                if self.is_valid_move_from_position(player, from_pos, move):
                    to_pos = self.calculate_new_position(from_pos, move)
                    if to_pos:
                        G.add_edge(from_pos, to_pos, color=color, move=move)
                        edge_labels[(from_pos, to_pos)] = move
        
        pos_layout = {}
        for node in G.nodes():
            row, col = self.position_to_coords(node)
            pos_layout[node] = (col, self.board_size - 1 - row)
        
        edge_colors = [G[u][v]['color'] for u, v in G.edges()]
        node_colors = ['lightgray' for _ in G.nodes()]
        
        for i, node in enumerate(G.nodes()):
            if node == self.positions['P1']['start']:
                node_colors[i] = 'pink'
            elif node == self.positions['P1']['end']:
                node_colors[i] = 'lightcoral'
            elif node == self.positions['P2']['start']:
                node_colors[i] = 'lightblue'
            elif node == self.positions['P2']['end']:
                node_colors[i] = 'deepskyblue'
        
        nx.draw(G, pos_layout, ax=ax, with_labels=True, node_color=node_colors, 
               edge_color=edge_colors, node_size=800, font_weight='bold')
        
        nx.draw_networkx_edge_labels(G, pos_layout, edge_labels=edge_labels, 
                                    font_color='green', ax=ax)
        
        ax.set_title("Red NFA de Movimientos")

    def update_display(self):
        """Actualiza toda la visualización en una sola ventana"""
        if not hasattr(self, 'ax_board'):
            self.ax_board = self.fig.add_subplot(self.gs[0])
        if not hasattr(self, 'ax_nfa'):
            self.ax_nfa = self.fig.add_subplot(self.gs[1])
        
        self.draw_board(self.ax_board)
        self.draw_full_nfa(self.ax_nfa)
        
        if not self.game_over:
            turn_text = f"Turno actual: Jugador {self.turn}"
            self.fig.text(0.5, 0.02, turn_text, ha='center', va='bottom', fontsize=12)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.draw()
        
        if not self.game_over:
            self.countdown()

    def is_valid_move_from_position(self, player, from_pos, move):
        """Verifica si un movimiento es válido desde una posición dada"""
        row, col = self.position_to_coords(from_pos)
        
        if move == 'U':
            new_row, new_col = row - 1, col
        elif move == 'D':
            new_row, new_col = row + 1, col
        elif move == 'L':
            new_row, new_col = row, col - 1
        elif move == 'R':
            new_row, new_col = row, col + 1
        elif move == 'UL':
            new_row, new_col = row - 1, col - 1
        elif move == 'UR':
            new_row, new_col = row - 1, col + 1
        elif move == 'DL':
            new_row, new_col = row + 1, col - 1
        elif move == 'DR':
            new_row, new_col = row + 1, col + 1
        
        if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size:
            return True
        return False
    
    def calculate_new_position(self, from_pos, move):
        """Calcula la nueva posición desde una posición y movimiento dados"""
        row, col = self.position_to_coords(from_pos)
        
        if move == 'U':
            new_row, new_col = row - 1, col
        elif move == 'D':
            new_row, new_col = row + 1, col
        elif move == 'L':
            new_row, new_col = row, col - 1
        elif move == 'R':
            new_row, new_col = row, col + 1
        elif move == 'UL':
            new_row, new_col = row - 1, col - 1
        elif move == 'UR':
            new_row, new_col = row - 1, col + 1
        elif move == 'DL':
            new_row, new_col = row + 1, col - 1
        elif move == 'DR':
            new_row, new_col = row + 1, col + 1
        
        if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size:
            return self.coords_to_position(new_row, new_col)
        return None

    def auto_play(self):
        """Juega automáticamente el juego con temporizador"""
        if self.mode != 'auto':
            print("El modo no es automático.")
            return
        
        print("Iniciando juego en modo automático...")
        self.update_display()
        
        while not self.game_over and self.current_move_count < self.max_moves:
            player = self.turn
            possible_moves = self.get_possible_moves(player)
            
            if not possible_moves:
                print(f"El jugador {player} no tiene movimientos válidos. Pasando turno.")
                self.turn = 'P2' if player == 'P1' else 'P1'
                self.current_move_count += 1
                self.update_display()
                continue
                
            move = random.choice(possible_moves)
            print(f"Jugador {player} mueve desde {self.positions[player]['current']} con {move}")
            self.make_move(player, move)
            self.update_display()
        
        if self.winner:
            result_text = f"¡Jugador {self.winner} ha ganado!"
        else:
            result_text = "Juego terminado sin ganador (límite de movimientos alcanzado)."
        
        self.fig.text(0.5, 0.02, result_text, ha='center', va='bottom', fontsize=12, color='green')
        plt.draw()
        
        self.generate_output_files()
        plt.pause(5)

    def manual_play(self):
        """Juega manualmente con secuencias predefinidas y temporizador"""
        if self.mode != 'manual':
            print("El modo no es manual.")
            return
        
        print("Iniciando juego en modo manual...")
        print(f"Secuencia P1: {self.move_sequence['P1']}")
        print(f"Secuencia P2: {self.move_sequence['P2']}")
        self.update_display()
        
        p1_idx = p2_idx = 0
        
        while not self.game_over and self.current_move_count < self.max_moves:
            player = self.turn
            move_sequence = self.move_sequence[player]
            current_idx = p1_idx if player == 'P1' else p2_idx
            
            if current_idx >= len(move_sequence):
                print(f"Secuencia de movimientos agotada para {player}. Pasando turno.")
                self.turn = 'P2' if player == 'P1' else 'P1'
                self.current_move_count += 1
                self.update_display()
                continue
                
            move = move_sequence[current_idx]
            
            if player == 'P1':
                p1_idx += 1
            else:
                p2_idx += 1
                
            if self.is_valid_move(player, move):
                print(f"Jugador {player} mueve desde {self.positions[player]['current']} con {move}")
                self.make_move(player, move)
                self.update_display()
            else:
                print(f"Movimiento {move} no válido para {player} en posición {self.positions[player]['current']}. Intentando reconfigurar...")
                possible_moves = self.get_possible_moves(player)
                if possible_moves:
                    move = random.choice(possible_moves)
                    print(f"Reconfigurado: {player} mueve con {move} en lugar")
                    self.make_move(player, move)
                    self.update_display()
                else:
                    print(f"No hay movimientos válidos para {player}. Pasando turno.")
                    self.turn = 'P2' if player == 'P1' else 'P1'
                    self.current_move_count += 1
                    self.update_display()
        
        if self.winner:
            result_text = f"¡Jugador {self.winner} ha ganado!"
        else:
            result_text = "Juego terminado sin ganador (límite de movimientos alcanzado)."
        
        self.fig.text(0.5, 0.02, result_text, ha='center', va='bottom', fontsize=12, color='green')
        plt.draw()
        
        self.generate_output_files()
        plt.pause(5)

    def generate_output_files(self):
        """Genera archivos de salida con todos los movimientos y movimientos ganadores"""
        with open('output/all_possible_moves.txt', 'w') as f:
            f.write("Todos los movimientos posibles:\n")
            for player in ['P1', 'P2']:
                f.write(f"\nJugador {player}:\n")
                for from_pos, move in sorted(self.all_possible_moves[player]):
                    to_pos = self.calculate_new_position(from_pos, move)
                    f.write(f"Desde {from_pos} con {move} -> {to_pos}\n")
        
        with open('output/winning_moves.txt', 'w') as f:
            f.write("Movimientos ganadores:\n")
            for player in ['P1', 'P2']:
                f.write(f"\nJugador {player}:\n")
                if self.winning_moves[player]:
                    for from_pos, move in sorted(self.winning_moves[player]):
                        to_pos = self.calculate_new_position(from_pos, move)
                        f.write(f"Desde {from_pos} con {move} -> {to_pos} (GANA)\n")
                else:
                    f.write("No se encontraron movimientos ganadores.\n")
        
        with open('output/move_history.txt', 'w') as f:
            f.write("Historial de movimientos:\n")
            for player in ['P1', 'P2']:
                f.write(f"\nJugador {player}:\n")
                for i, (from_pos, to_pos, move) in enumerate(self.moves_history[player], 1):
                    f.write(f"Movimiento {i}: Desde {from_pos} con {move} -> {to_pos}\n")
        
        print("Archivos de salida generados en la carpeta 'output'.")

def main():
    """Función principal con menú de opciones"""
    print("Juego de Movimientos en Tablero de Ajedrez 4x4")
    print("---------------------------------------------")
    print("NOTA: Cada movimiento tendrá un tiempo de 10 segundos de visualización")
    
    game = ChessBoardGame()
    
    while True:
        print("\nOpciones:")
        print("1. Modo automático")
        print("2. Modo manual (introducir cadena de movimientos)")
        print("3. Modo manual (generar cadena aleatoria)")
        print("4. Salir")
        
        choice = input("Seleccione una opción: ")
        
        if choice == '1':
            max_moves = int(input("Ingrese el número máximo de movimientos (3-100): "))
            game.initialize_game(mode='auto', max_moves=max_moves)
            game.auto_play()
            plt.show()
        elif choice == '2':
            move_sequence = input("Ingrese la cadena de movimientos (ej. U,D,L,R,UL,DR): ").upper().split(',')
            max_moves = len(move_sequence)
            game.initialize_game(mode='manual', max_moves=max_moves, move_sequence=move_sequence)
            game.manual_play()
            plt.show()
        elif choice == '3':
            max_moves = int(input("Ingrese el número máximo de movimientos (3-100): "))
            game.initialize_game(mode='manual', max_moves=max_moves)
            game.manual_play()
            plt.show()
        elif choice == '4':
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()
