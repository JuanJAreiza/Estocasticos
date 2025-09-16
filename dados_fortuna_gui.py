import random
import tkinter as tk
from tkinter import ttk, messagebox

# -------------------------
# Lógica del juego (idéntica a antes)
# -------------------------
def roll_dice(n):
    return [random.randint(1, 6) for _ in range(n)]

def matches_original(chosen, roll):
    return sum(1 for c, r in zip(chosen, roll) if c == r)

def matches_order_free(chosen, roll):
    return sum(1 for x in set(chosen) if x in set(roll))

def apply_bonus(chosen, roll, match_fn):
    new_roll = roll.copy()
    for i in range(len(chosen)):
        if chosen[i] != roll[i]:
            new_roll[i] = random.randint(1, 6)
    return match_fn(chosen, new_roll), new_roll

def prize_text(mode, matches):
    if mode == 2:
        if matches == 2: return "Primer premio (mayor)"
        elif matches == 1: return "Segundo premio"
        else: return "Perdedor"
    else:
        if matches == 4: return "Premio mayor (4 aciertos)"
        elif matches == 3: return "Segundo premio (3 aciertos)"
        elif matches == 2: return "Tercer premio (2 aciertos)"
        else: return "Perdedor (0-1 aciertos)"

THEORETICAL = {
    "2_Original": {
        "Primer premio (mayor)": 1/36,
        "Segundo premio": 10/36,
        "Perdedor": 25/36
    },
    "2_Orden Libre": {
        "Primer premio (mayor)": 2/36,
        "Segundo premio": 18/36,
        "Perdedor": 16/36
    },
    "2_Dado Bonus": {
        "Primer premio (mayor)": (1/36) + (10/36)*(1/6),
        "Segundo premio": (10/36) - (10/36)*(1/6),
        "Perdedor": 25/36
    },
    "4_Original": {
        "Premio mayor (4 aciertos)": 1/1296,
        "Segundo premio (3 aciertos)": 20/1296,
        "Tercer premio (2 aciertos)": 150/1296,
        "Perdedor (0-1 aciertos)": 1125/1296
    },
    "4_Orden Libre": {
        "Premio mayor (4 aciertos)": 24/1296,
        "Segundo premio (3 aciertos)": 336/1296,
        "Tercer premio (2 aciertos)": 660/1296,
        "Perdedor (0-1 aciertos)": (260+16)/1296
    },
    "4_Dado Bonus": {
        "Premio mayor (4 aciertos)": 0.0087169,
        "Segundo premio (3 aciertos)": 0.079244,
        "Tercer premio (2 aciertos)": 0.270151,
        "Perdedor (0-1 aciertos)": 0.6418889
    }
}

# -------------------------
# GUI
# -------------------------
class DadosFortunaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎲 Los Dados de la Fortuna 🎲")
        self.root.geometry("650x500")
        self.root.config(bg="#f5f5f5")

        # Variables
        self.mode_var = tk.IntVar(value=2)
        # Regla ahora incluye la opción 'bonus' como modo separado para evitar combinaciones simultáneas
        self.rule_var = tk.StringVar(value="Original")
        self.players = []  # Lista de diccionarios: {name_var, dice_vars (list[StringVar]), frame}

        # Frame de configuración
        config_frame = tk.LabelFrame(root, text="Configuración del juego", bg="#f5f5f5", font=("Arial", 12, "bold"))
        config_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(config_frame, text="Modo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        mode_cb = ttk.Combobox(config_frame, textvariable=self.mode_var, values=[2, 4], width=5, state="readonly")
        mode_cb.grid(row=0, column=1, padx=5)
        mode_cb.bind("<<ComboboxSelected>>", lambda e: self.on_mode_change())

        ttk.Label(config_frame, text="Regla:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        rule_cb = ttk.Combobox(config_frame, textvariable=self.rule_var, values=["Original", "Orden Libre", "Dado Bonus"], width=12, state="readonly")
        rule_cb.grid(row=0, column=3, padx=5)
        rule_cb.bind("<<ComboboxSelected>>", lambda e: self.on_rule_change())

        # Frame para jugadores
        self.players_frame = tk.LabelFrame(root, text="Jugadores", bg="#f5f5f5", font=("Arial", 12, "bold"))
        self.players_frame.pack(fill="x", padx=10, pady=10)
        self.add_player()  # Jugador inicial

        # Botones
        btn_frame = tk.Frame(root, bg="#f5f5f5")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Elegir # aleatorios", command=self.auto_numbers).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Agregar jugador", command=self.add_player).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="🎲 Jugar", command=self.play).grid(row=0, column=2, padx=5)

        # Resultados
        self.result_text = tk.Text(root, height=10, font=("Consolas", 11), bg="white")
        self.result_text.pack(fill="both", padx=10, pady=10, expand=True)
        self.show_welcome_text()

    def add_player(self):
        """Agrega un nuevo jugador con nombre y entradas de dados según el modo actual."""
        idx = len(self.players) + 1
        frame = tk.Frame(self.players_frame, bg="#f5f5f5", pady=3)
        frame.pack(fill="x", anchor="w")

        name_var = tk.StringVar(value=f"Jugador {idx}")
        tk.Label(frame, text="Nombre:", bg="#f5f5f5").pack(side="left", padx=(5, 2))
        tk.Entry(frame, textvariable=name_var, width=12).pack(side="left", padx=(0, 10))

        # Botón eliminar jugador
        del_btn = tk.Button(frame, text="✖", fg="red", bg="#f5f5f5", bd=0, command=lambda f=frame: self.delete_player(f))
        del_btn.pack(side="right", padx=5)

        dice_container = tk.Frame(frame, bg="#f5f5f5")
        dice_container.pack(side="left")

        dice_vars = []
        for _ in range(self.mode_var.get()):
            var = tk.StringVar()
            dice_vars.append(var)
            ttk.Entry(dice_container, textvariable=var, width=4).pack(side="left", padx=2)

        self.players.append({
            "name_var": name_var,
            "dice_vars": dice_vars,
            "frame": frame,
            "dice_container": dice_container
        })
        self.renumber_default_names()

    def delete_player(self, frame):
        """Elimina un jugador dado su frame, preservando al menos uno."""
        if len(self.players) <= 1:
            messagebox.showinfo("Aviso", "Debe existir al menos un jugador.")
            return
        self.players = [p for p in self.players if p["frame"] != frame]
        frame.destroy()
        self.renumber_default_names()

    def renumber_default_names(self):
        """Actualiza nombres que aún tienen el formato por defecto 'Jugador X' para mantener correlativo."""
        counter = 1
        for p in self.players:
            current = p["name_var"].get()
            if current.startswith("Jugador "):
                p["name_var"].set(f"Jugador {counter}")
            counter += 1

    def on_mode_change(self):
        """Actualizar cantidad de dados por jugador cuando cambia el modo (2 o 4)."""
        n = self.mode_var.get()
        for p in self.players:
            current = len(p["dice_vars"])
            # Agregar si faltan
            while current < n:
                var = tk.StringVar()
                p["dice_vars"].append(var)
                ttk.Entry(p["dice_container"], textvariable=var, width=4).pack(side="left", padx=2)
                current += 1
            # Eliminar si sobran
            while current > n:
                to_remove = p["dice_vars"].pop()
                # Buscar el widget correspondiente (último hijo)
                children = p["dice_container"].winfo_children()
                if children:
                    children[-1].destroy()
                current -= 1

    def on_rule_change(self):
        """Placeholder por si en un futuro se quiere cambiar algo visual según la regla."""
        pass

    def show_welcome_text(self):
        msg = (
            "Bienvenido a 'Los Dados de la Fortuna'\n"
            "Selecciona modo (2 o 4 dados) y una regla:\n"
            "  - Original: Deben coincidir posición y valor.\n"
            "  - Orden Libre: Solo importa que el valor aparezca.\n"
            "  - Dado Bonus: Después de la primera tirada se relanzan únicamente los dados que no coincidieron.\n"
            "Agrega jugadores, escribe sus elecciones (sin repetir y entre 1-6) y pulsa 'Jugar'.\n"
            "Usa 'Elegir aleatorios' para rellenar rápidamente. ¡Suerte!\n"
        )
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, msg)

    def auto_numbers(self):
        n = self.mode_var.get()
        for p in self.players:
            nums = random.sample(range(1, 7), n)
            for i, var in enumerate(p["dice_vars"]):
                var.set(str(nums[i]))

    def play(self):
        mode = self.mode_var.get()
        rule_selected = self.rule_var.get()  # Puede ser original, order_free, bonus
        bonus = (rule_selected == "Dado Bonus")
        # Si es bonus, la comparación se hace como 'original'
        effective_rule = "Original" if bonus else rule_selected

        # Preparar salida
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Modo: {mode} dados | Regla: {rule_selected}\n")
        self.result_text.insert(tk.END, "="*55 + "\n")

        match_fn = matches_original if effective_rule == "Original" else matches_order_free

        for p in self.players:
            name = p["name_var"].get().strip() or "Jugador"
            # Leer dados elegidos
            try:
                chosen = [int(var.get()) for var in p["dice_vars"]]
                if len(chosen) != mode:
                    raise ValueError("Cantidad incorrecta de números")
                if len(set(chosen)) != len(chosen):
                    raise ValueError("Números repetidos")
                if not all(1 <= x <= 6 for x in chosen):
                    raise ValueError("Fuera de rango")
            except Exception as e:
                messagebox.showerror("Error", f"Entrada inválida para {name}: {e}")
                return

            roll = roll_dice(mode)
            matches_initial = match_fn(chosen, roll)
            if bonus:
                matches_final, roll_final = apply_bonus(chosen, roll, match_fn)
            else:
                matches_final, roll_final = matches_initial, roll

            prize = prize_text(mode, matches_final)
            # Mostrar por jugador
            self.result_text.insert(tk.END, f"{name}\n")
            self.result_text.insert(tk.END, f"  Elección: {chosen}\n")
            self.result_text.insert(tk.END, f"  Tirada inicial: {roll} → {matches_initial} aciertos\n")
            if bonus:
                self.result_text.insert(tk.END, f"  Tirada final (Dado Bonus): {roll_final} → {matches_final} aciertos\n")
            else:
                self.result_text.insert(tk.END, f"  Tirada final: {roll_final} → {matches_final} aciertos\n")
            self.result_text.insert(tk.END, f"  🏆 {prize}\n")
            self.result_text.insert(tk.END, "-"*40 + "\n")

        # Probabilidades teóricas (una sola vez al final)
        key = f"{mode}_{'Orden Libre' if effective_rule=='Orden Libre' else 'Original'}"
        if bonus:
            # Usar la clave bonus si existe para ese número de dados
            key = f"{mode}_Dado Bonus" if f"{mode}_Dado Bonus" in THEORETICAL else key
        self.result_text.insert(tk.END, "\nProbabilidades teóricas:\n")
        theoretical = THEORETICAL.get(key, {})
        if not theoretical:
            self.result_text.insert(tk.END, "  (No disponibles para este modo)\n")
        else:
            for k, v in theoretical.items():
                self.result_text.insert(tk.END, f"  {k:28s}: {v:.4f}\n")

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DadosFortunaApp(root)
    root.mainloop()
