"""
dados_fortuna.py
Simulación interactiva del juego "Los dados de la fortuna" (Entregable 2).
Versión simplificada: **SIN** Monte Carlo.
Implementa:
 - Modo 2 dados y 4 dados
 - Reglas: Original (posición importa), Orden libre
 - Regla opcional "Dado bonus" (relanzar no-coincidentes una vez)
 - Interfaz de consola interactiva

Autores originales del diseño: Juan José Areiza Orrego & Andres Felipe Martinez Taborda
Versión: Monte Carlo removido por petición del usuario.
"""

import random

# -------------------------
# Utilidades básicas
# -------------------------
def roll_dice(n):
    """Lanza n dados (1..6) y devuelve lista de resultados."""
    return [random.randint(1,6) for _ in range(n)]

def unique_choice(values, k):
    """Genera elección aleatoria de k números únicos (1..6)."""
    return random.sample(values, k)

# -------------------------
# Conteo de aciertos
# -------------------------
def matches_original(chosen, roll):
    """
    Cuenta coincidencias en el modo 'original' (la posición importa).
    Retorna número de aciertos por posición exacta (0..len(chosen)).
    """
    return sum(1 for c, r in zip(chosen, roll) if c == r)

def matches_order_free(chosen, roll):
    """
    Cuenta cuántos de los números elegidos aparecen al menos una vez en el lanzamiento.
    (Ej: elegido {1,2,3,4}, tirada [1,1,2,3] -> 3 aciertos).
    """
    chosen_set = set(chosen)
    roll_set = set(roll)
    return sum(1 for x in chosen_set if x in roll_set)

# -------------------------
# Aplicar regla 'bonus' (reroll non-matches once)
# -------------------------
def apply_bonus(chosen, roll, mode, match_fn):
    """
    Aplica la regla 'dado bonus' que permite relanzar los dados que no coincidieron
    (según la función match_fn que cuenta coincidencias) y devuelve la nueva cantidad
    de coincidencias tras el relanzamiento junto con la nueva tirada.
    """
    n = len(chosen)
    new_roll = roll.copy()
    for i in range(n):
        # para original y para la simplificación aplicada a order_free relanzamos por posición
        if chosen[i] != roll[i]:
            new_roll[i] = random.randint(1,6)
    return match_fn(chosen, new_roll), new_roll

# -------------------------
# Texto de premio según modo
# -------------------------
def prize_text_mode_2(matches):
    """Etiqueta de premio para modo 2 (original/order-free/bonus)."""
    if matches == 2:
        return "Primer premio (mayor)"
    elif matches == 1:
        return "Segundo premio"
    else:
        return "Perdedor"

def prize_text_mode_4(matches):
    """Etiqueta de premio para modo 4 (original/order-free/bonus)."""
    if matches == 4:
        return "Premio mayor (4 aciertos)"
    elif matches == 3:
        return "Segundo premio (3 aciertos)"
    elif matches == 2:
        return "Tercer premio (2 aciertos)"
    else:
        return "Perdedor (0-1 aciertos)"

# -------------------------
# Simulación de un solo ensayo (incluye elección del jugador y reglas)
# -------------------------
def single_game(chosen, mode=2, rule="original", apply_bonus_flag=False):
    """
    Ejecuta un solo juego:
      - chosen: lista de números (len 2 or 4), sin repetidos.
      - mode: 2 o 4
      - rule: "original" o "order_free"
      - apply_bonus_flag: si True se aplica el bonus (se relanzan no-coincidentes)
    Devuelve dict con roll inicial, matches inicial, (si hubo relanzamiento) nuevo roll y matches, y etiqueta de premio final.
    """
    n = mode
    roll = roll_dice(n)
    match_fn = matches_original if rule == "original" else matches_order_free
    matches_initial = match_fn(chosen, roll)

    if apply_bonus_flag:
        matches_after, new_roll = apply_bonus(chosen, roll, mode, match_fn)
        final_matches = matches_after
        final_roll = new_roll
    else:
        final_matches = matches_initial
        final_roll = roll

    prize = prize_text_mode_2(final_matches) if mode == 2 else prize_text_mode_4(final_matches)

    return {
        "chosen": chosen,
        "roll_initial": roll,
        "matches_initial": matches_initial,
        "applied_bonus": apply_bonus_flag,
        "roll_final": final_roll,
        "matches_final": final_matches,
        "prize": prize
    }

# -------------------------
# Probabilidades teóricas (valores tomados del entregable 1)
# (Se conservan aquí para referencia y mostrar al usuario)
# -------------------------
THEORETICAL = {
    "2_original": {
        "Primer premio (mayor)": 1/36,
        "Segundo premio": 10/36,
        "Perdedor": 25/36
    },
    "2_order_free": {
        "Primer premio (mayor)": 2/36,
        "Segundo premio": 18/36,
        "Perdedor": 16/36
    },
    "2_bonus": {
        "Primer premio (mayor)": (1/36) + (10/36)*(1/6),
        "Segundo premio": (10/36) - (10/36)*(1/6),
        "Perdedor": 25/36
    },
    "4_original": {
        "Premio mayor (4 aciertos)": 1/1296,
        "Segundo premio (3 aciertos)": 20/1296,
        "Tercer premio (2 aciertos)": 150/1296,
        "Perdedor (0-1 aciertos)": 1125/1296
    },
    "4_order_free": {
        "Premio mayor (4 aciertos)": 24/1296,
        "Segundo premio (3 aciertos)": 336/1296,
        "Tercer premio (2 aciertos)": 660/1296,
        "Perdedor (0-1 aciertos)": (260+16)/1296
    },
    "4_bonus": {
        # Valores aproximados según el entregable
        "Premio mayor (4 aciertos)": 0.0087169,
        "Segundo premio (3 aciertos)": 0.079244,
        "Tercer premio (2 aciertos)": 0.270151,
        "Perdedor (0-1 aciertos)": 0.6418889  # aproximación
    }
}

# -------------------------
# Interfaz de consola (simple, sin Monte Carlo)
# -------------------------
def interactive_mode():
    print("=== Los Dados de la Fortuna (Simulación interactiva) ===")
    # Selección de modo
    while True:
        mode_in = input("Elige modo (2 para 2 dados, 4 para 4 dados) [default 2]: ").strip()
        if mode_in == "" or mode_in == "2":
            mode = 2
            break
        elif mode_in == "4":
            mode = 4
            break
        else:
            print("Entrada no válida. Intenta 2 o 4.")

    # Reglas
    while True:
        print("\nReglas disponibles:")
        print("  1) original (posición importa)")
        print("  2) order_free (orden libre)")
        rule_in = input("Elige regla (1 o 2) [default 1]: ").strip()
        if rule_in == "" or rule_in == "1":
            rule = "original"
            break
        elif rule_in == "2":
            rule = "order_free"
            break
        else:
            print("Entrada no válida.")

    # Preguntar si desea aplicar bonus
    bonus_in = input("¿Deseas aplicar la regla 'Dado bonus' (relanzar no-coincidentes)? (s/n) [n]: ").strip().lower()
    apply_bonus_flag = bonus_in == "s"

    # Elección de números por parte del usuario
    n = mode
    print(f"\nIntroduce tus {n} números (entre 1 y 6) sin repetir, separados por espacios.")
    print("Ejemplo para 2 dados: 3 5")
    while True:
        line = input("Tus números (o escribe 'auto' para auto-elegir): ").strip()
        if line.lower() == "auto" or line == "":
            chosen = unique_choice(list(range(1,7)), n)
            print("Elección automática:", chosen)
            break
        else:
            parts = line.split()
            try:
                nums = [int(p) for p in parts]
                if len(nums) != n:
                    print(f"Debes ingresar exactamente {n} números.")
                    continue
                if any(x < 1 or x > 6 for x in nums):
                    print("Los números deben estar entre 1 y 6.")
                    continue
                if len(set(nums)) != n:
                    print("No se permiten repetidos; selecciona números únicos.")
                    continue
                chosen = nums
                break
            except ValueError:
                print("Entrada inválida. Ingresa números separados por espacios o 'auto'.")

    # Ejecutar un juego único
    print("\n--- Ejecutando un lanzamiento ---")
    result = single_game(chosen, mode=mode, rule=rule, apply_bonus_flag=apply_bonus_flag)
    print("Elección del jugador:", result["chosen"])
    print("Tirada inicial:", result["roll_initial"], "-> coincidencias iniciales:", result["matches_initial"])
    if result["applied_bonus"]:
        print("Se aplicó Dado bonus. Tirada final:", result["roll_final"], "-> coincidencias finales:", result["matches_final"])
    else:
        print("Tirada final (sin bonus):", result["roll_final"], "-> coincidencias finales:", result["matches_final"])
    print("Resultado:", result["prize"])

    # Mostrar probabilidades teóricas del entregable para referencia
    print("\nProbabilidades teóricas (referencia del Entregable 1):")
    key = f"{mode}_{'order_free' if rule == 'order_free' else 'original'}"
    if apply_bonus_flag:
        key = f"{mode}_bonus" if f"{mode}_bonus" in THEORETICAL else key + "_bonus"
    # Ajustar claves para acceso seguro
    if mode == 2:
        if apply_bonus_flag:
            for k, v in THEORETICAL["2_bonus"].items():
                print(f"  {k:25s}: {v:.6f}")
        elif rule == "original":
            for k, v in THEORETICAL["2_original"].items():
                print(f"  {k:25s}: {v:.6f}")
        else:
            for k, v in THEORETICAL["2_order_free"].items():
                print(f"  {k:25s}: {v:.6f}")
    else:  # mode 4
        if apply_bonus_flag:
            for k, v in THEORETICAL["4_bonus"].items():
                print(f"  {k:25s}: {v:.6f}")
        elif rule == "original":
            for k, v in THEORETICAL["4_original"].items():
                print(f"  {k:25s}: {v:.6f}")
        else:
            for k, v in THEORETICAL["4_order_free"].items():
                print(f"  {k:25s}: {v:.6f}")

    print("\nGracias por jugar")

# -------------------------
# Si se ejecuta como script
# -------------------------
if __name__ == "__main__":
    interactive_mode()
