import copy
import tkinter as tk
from tkinter import ttk
import random
# =============================================================================
# CLASE DEL TABLERO: LÓGICA DEL JUEGO
# =============================================================================

class Tablero:
    def __init__(self, estado=None):
        # Si no se provee estado, crea un tablero vacío de 3x3.
        self.estado = estado if estado else [["" for _ in range(3)] for _ in range(3)]
    
    def __str__(self):
        # Retorna una cadena con la representación visual del tablero.
        s = "\n-------------\n"
        for fila in self.estado:
            s += "| " + " | ".join(celda if celda else " " for celda in fila) + " |\n"
            s += "-------------\n"
        return s

    def hacer_jugada(self, fila, columna, jugador):
        # Coloca la ficha 'jugador' en (fila, columna) si la casilla está vacía.
        if self.estado[fila][columna] == "":
            self.estado[fila][columna] = jugador
            return True
        return False

    def es_terminal(self):
        # Define las líneas ganadoras: filas, columnas y diagonales.
        lineas = [
            self.estado[0], self.estado[1], self.estado[2],
            [self.estado[0][0], self.estado[1][0], self.estado[2][0]],
            [self.estado[0][1], self.estado[1][1], self.estado[2][1]],
            [self.estado[0][2], self.estado[1][2], self.estado[2][2]],
            [self.estado[0][0], self.estado[1][1], self.estado[2][2]],
            [self.estado[0][2], self.estado[1][1], self.estado[2][0]]
        ]
        for linea in lineas:
            if linea[0] == linea[1] == linea[2] != "":
                return linea[0], True  # Hay ganador.
        if all(celda != "" for fila in self.estado for celda in fila):
            return None, True  # Empate.
        return None, False

    def generar_simetrias(self):
        """
        Genera todas las variantes simétricas del tablero aplicando rotaciones y reflejos.
        Esto evita evaluar estados equivalentes repetidos.
        """
        def rotar90(matriz):
            return [list(col)[::-1] for col in zip(*matriz)]
        def reflejar(matriz):
            return [fila[::-1] for fila in matriz]
        
        simetrias = []
        current = copy.deepcopy(self.estado)
        for _ in range(4):
            simetrias.append(current)
            simetrias.append(reflejar(current))
            current = rotar90(current)
        return simetrias

    def evaluar_estado(self):
        """
        Evalúa el estado heurísticamente:
          - Suma 1 por cada línea en la que X (MAX) pueda ganar.
          - Suma 1 por cada línea en la que O (MIN) pueda ganar.
        Retorna la diferencia: (X_score - O_score).
        """
        score_x, score_o = 0, 0
        lineas = [
            self.estado[0], self.estado[1], self.estado[2],
            [self.estado[0][0], self.estado[1][0], self.estado[2][0]],
            [self.estado[0][1], self.estado[1][1], self.estado[2][1]],
            [self.estado[0][2], self.estado[1][2], self.estado[2][2]],
            [self.estado[0][0], self.estado[1][1], self.estado[2][2]],
            [self.estado[0][2], self.estado[1][1], self.estado[2][0]]
        ]
        for linea in lineas:
            if "O" not in linea:
                score_x += 1
            if "X" not in linea:
                score_o += 1
        return score_x - score_o

# =============================================================================
# CLASE RESPONSABLE DE GENERAR LAS JUGADAS VÁLIDAS (CON FILTRO SIMÉTRICO) Y CALCULAR MINIMAX
# =============================================================================

class ManejadorJuego:
    def __init__(self):
        # Almacena la información del árbol de expansión: lista de tuplas (nivel, texto).
        self.tree_lines = []
        self.estado_contador = 0

    def generar_jugadas_validas_simetricas(self, tablero, jugador):
        """
        Genera las jugadas válidas para 'jugador' (colocar ficha en cada casilla vacía)
        y elimina duplicados simétricos utilizando una representación canónica.
        """
        jugadas = []
        seen = set()
        for i in range(3):
            for j in range(3):
                if tablero.estado[i][j] == "":
                    nuevo_tablero = Tablero(copy.deepcopy(tablero.estado))
                    nuevo_tablero.hacer_jugada(i, j, jugador)
                    sim = nuevo_tablero.generar_simetrias()
                    canonical = min(str(s) for s in sim)
                    if canonical not in seen:
                        seen.add(canonical)
                        jugadas.append(nuevo_tablero)
        return jugadas

    def MiniMax(self, tablero):
        """
        Calcula la mejor jugada para MAX (X) evaluando dos niveles:
         - Para cada jugada válida de X, se generan las respuestas válidas para MIN (O).
         - Se toma el valor mínimo de las respuestas de O y se elige la jugada de X cuyo valor mínimo es mayor.
        La información de la expansión se guarda en self.tree_lines para su visualización.
        Retorna el estado (Tablero) correspondiente a la mejor jugada para X.
        """
        self.tree_lines = []  # Reinicia la información del árbol.
        self.tree_lines.append((0, "JUGADA A EVALUAR (Estado actual):"))
        for line in str(tablero).splitlines():
            self.tree_lines.append((0, line))
        best_val = -float("inf")
        best_board = None
        jugadas_X = self.generar_jugadas_validas_simetricas(tablero, "X")
        for idx, jug in enumerate(jugadas_X):
            self.tree_lines.append((1, f"JUGADA A EVALUAR DE MAX #{idx+1}:"))
            self.estado_contador += 1
            for line in str(jug).splitlines():
                self.tree_lines.append((1, line))
            jugadas_O = self.generar_jugadas_validas_simetricas(jug, "O")
            best_val_min = float("inf")
            for jdx, jugO in enumerate(jugadas_O):
                self.tree_lines.append((2, f"JUGADA A EVALUAR DE MIN PARA MAX #{idx+1}, O #{jdx+1}:"))
                self.estado_contador += 1
                for line in str(jugO).splitlines():
                    self.tree_lines.append((2, line))
                eval_val = jugO.evaluar_estado()
                self.tree_lines.append((2, f"Evaluacion = {eval_val}"))
                if eval_val < best_val_min:
                    best_val_min = eval_val
            self.tree_lines.append((1, f"Valor minimo de rama #{idx+1} = {best_val_min}\n"))
            if best_val_min > best_val:
                best_val = best_val_min
                best_board = jug
        self.tree_lines.append((0, f"MEJOR JUGADA DE MAX (Valor = {best_val}):"))
        for line in str(best_board).splitlines():
            self.tree_lines.append((0, line))
        self.tree_lines.append((0, f"Costo Acumulado: {self.estado_contador}"))
            
        # Retorna la mejor jugada para MAX (X)
        return best_board

# =============================================================================
# VISUALIZACIÓN CON TKINTER (ttk.Treeview CON BOTÓN "CONTINUAR")
# =============================================================================

class Visualizer:
    def __init__(self, tree_lines):
        """
        Inicializa el visualizador utilizando una ventana Tkinter con un widget Treeview.
        :param tree_lines: Lista de tuplas (nivel, texto) que contienen la información del árbol.
        """
        self.tree_lines = tree_lines

    def show(self):
        root = tk.Tk()
        root.title("Árbol de Expansión - Minimax")
        root.geometry("800x600")
        tree = ttk.Treeview(root)
        tree.pack(expand=True, fill="both")
        stack = [(-1, "")]
        for depth, text in self.tree_lines:
            cl_text = text.strip()
            if not cl_text:
                continue
            while stack and depth <= stack[-1][0]:
                stack.pop()
            parent_id = stack[-1][1] if stack else ""
            node_id = tree.insert(parent_id, "end", text=cl_text)
            stack.append((depth, node_id))
        btn = tk.Button(root, text="Continuar", command=root.destroy)
        btn.pack(pady=10)
        root.mainloop()

# =============================================================================
# CLASE PRINCIPAL DEL JUEGO
# =============================================================================

class Juego:
    def __init__(self):
        # Inicializa el tablero y el manejador.
        self.tablero = Tablero()
        self.manejador = ManejadorJuego()

    def obtener_jugada_humano(self, turno="O"):
        """
        Solicita la jugada desde consola para el turno indicado.
        :param turno: "X" o "O". En este flujo, sólo al principio el usuario define ambos;
                      luego, el usuario sólo ingresa movimientos para MIN (O).
        :return: (fila, columna) o (-1, -1) si la entrada es inválida.
        """
        print(f"Ingrese la jugada para {turno}:")
        try:
            fila = int(input("Fila (0-2): "))
            col = int(input("Columna (0-2): "))
            if 0 <= fila <= 2 and 0 <= col <= 2:
                if self.tablero.estado[fila][col] == "":
                    return fila, col
                else:
                    print("Casilla ocupada!")
            else:
                print("Casilla inválida!")
        except:
            return -1, -1

    def iniciar(self):
        """
        Flujo del juego:
         1. Fase inicial: El usuario define un movimiento para MAX (X) y para MIN (O) (solo al inicio).
         2. Luego, en cada ciclo:
             a) El algoritmo (minimax) calcula el movimiento para MAX (X) y lo fija.
             b) Se visualiza el árbol de expansión.
             c) Se verifica si el juego ha terminado.
             d) Se solicita al usuario la jugada para MIN (O).
             e) Se actualiza el tablero y se verifica terminalidad.
         3. El ciclo se repite hasta que el juego termine.
        """
        print("¡Tres en Raya!")
        print("Estado inicial del tablero:")
        print(self.tablero)
        
        # --- FASE INICIAL: El usuario define un movimiento para MAX y para MIN ---
        print("\n--- FASE INICIAL ---")
        fila, col = self.obtener_jugada_humano("X")
        if fila == -1:
            print("Entrada inválida para X. Se usará el estado actual.")
        else:
            self.tablero.hacer_jugada(fila, col, "X")
            fila, col = self.obtener_jugada_humano("O")
            if fila == -1:
                print("Entrada inválida para O. Se usará el estado actual.")
            else:
                self.tablero.hacer_jugada(fila, col, "O")
        print("\nTablero después de la fase inicial:")
        print(self.tablero)
        
        # --- CICLO PRINCIPAL ---
        while True:
            # Movimiento de MAX (X) fijado por minimax:
            best_board = self.manejador.MiniMax(self.tablero)
            self.tablero = best_board
            print("\nTablero después de jugada de MAX (según Minimax):")
            print(self.tablero)
            print(f"Costo Ruta: {self.manejador.estado_contador}")
            visualizer = Visualizer(self.manejador.tree_lines)
            visualizer.show()  # El usuario pulsa "Continuar" para cerrar la ventana.
            ganador, terminal = self.tablero.es_terminal()
            if terminal:
                if ganador:
                    print(f"¡Jugador {ganador} gana!")
                else:
                    print("¡Empate!")
                break
            
            # Movimiento de MIN (O): Se le pide al usuario que ingrese la jugada.
            print("\nIngrese la jugada para MIN (O): (Presione enter si desea que Min sea aleatorio)")
            fila, col = self.obtener_jugada_humano("O")
            if fila == -1:
                # Generar jugadas válidas para MIN (O)
                jugadas_validas = self.manejador.generar_jugadas_validas_simetricas(self.tablero, "O")
                if jugadas_validas:
                    # Seleccionar una jugada aleatoria
                    tablero_aleatorio = random.choice(jugadas_validas)
                    # Actualizar el tablero actual con el tablero aleatorio
                    self.tablero.estado = tablero_aleatorio.estado
                    print("Jugada aleatoria generada para MIN (O)")
                else:
                    print("No hay jugadas válidas disponibles para MIN (O)")
            else:
                self.tablero.hacer_jugada(fila, col, "O")
            print("\nTablero después de la jugada de MIN (O):")
            print(self.tablero)
            ganador, terminal = self.tablero.es_terminal()
            if terminal:
                if ganador:
                    print(f"¡Jugador {ganador} gana!")
                else:
                    print("¡Empate!")
                break
            # Nota: En este ciclo, el algoritmo solo fija el movimiento para MAX.
            # Luego se vuelve a comenzar el ciclo y se calcula el próximo movimiento para MAX.
            

if __name__ == "__main__":
    partida = Juego()
    partida.iniciar()
