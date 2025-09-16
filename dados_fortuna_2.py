import random
import tkinter as tk
from tkinter import ttk, messagebox

# -------------------------
# Lógica del juego
# -------------------------
def roll_dice(n):
    return [random.randint(1, 6) for _ in range(n)]

def matches_original(chosen, roll):
    return sum(1 for c, r in zip(chosen, roll) if c == r)

def matches_order_free(chosen, roll):
    return sum(1 for x in set(chosen) if x in set(roll))

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
# Diálogo modal simplificado: elegir sólo la cantidad (botones rápidos)
# -------------------------
class QuickRerollDialog:
    """
    Modal que muestra botones 1..max_k para elegir cuántos dados relanzar.
    Retorna k (int) o None si se cancela.
    """
    def __init__(self, parent, player_name, max_k):
        self.parent = parent
        self.player_name = player_name
        self.max_k = max_k
        self.selected_k = None
        self._build()

    def _build(self):
        self.top = tk.Toplevel(self.parent)
        self.top.title(f"Dado Bonus — {self.player_name}")
        self.top.transient(self.parent)
        self.top.grab_set()  # modal
        self.top.resizable(False, False)

        tk.Label(self.top, text=f"{self.player_name}: ¿Cuántos dados quieres relanzar?", font=("Arial", 11, "bold")).pack(padx=12, pady=(10,8))
        tk.Label(self.top, text=f"Máximo permitido: {self.max_k}", font=("Arial", 10)).pack(padx=12, pady=(0,8))

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(padx=12, pady=(0,10))
        for k in range(1, self.max_k + 1):
            def make_cmd(k=k):
                return lambda: self._on_select(k)
            ttk.Button(btn_frame, text=str(k), width=4, command=make_cmd()).pack(side="left", padx=4)

        ctrl_frame = tk.Frame(self.top)
        ctrl_frame.pack(padx=12, pady=(0,12))
        ttk.Button(ctrl_frame, text="Cancelar", command=self._on_cancel).pack()

        # center over parent
        self.parent.update_idletasks()
        x = self.parent.winfo_rootx()
        y = self.parent.winfo_rooty()
        w = self.parent.winfo_width()
        h = self.parent.winfo_height()
        self.top.geometry(f"+{x + w//3}+{y + h//3}")

        self.top.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.top.wait_window()

    def _on_select(self, k):
        self.selected_k = k
        self.top.destroy()

    def _on_cancel(self):
        self.selected_k = None
        self.top.destroy()

# -------------------------
# GUI principal
# -------------------------
class DadosFortunaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎲 Los Dados de la Fortuna 🎲")
        self.root.geometry("760x560")
        self.root.config(bg="#f5f5f5")

        # Variables
        self.mode_var = tk.IntVar(value=2)
        self.rule_var = tk.StringVar(value="Original")
        self.show_theoretical_var = tk.BooleanVar(value=False)  # nuevo: oculto por defecto
        self.players = []  # Lista de diccionarios por jugador

        # Frame de configuración
        config_frame = tk.LabelFrame(root, text="Configuración del juego", bg="#f5f5f5", font=("Arial", 12, "bold"))
        config_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(config_frame, text="Modo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        mode_cb = ttk.Combobox(config_frame, textvariable=self.mode_var, values=[2, 4], width=5, state="readonly")
        mode_cb.grid(row=0, column=1, padx=5)
        mode_cb.bind("<<ComboboxSelected>>", lambda e: self.on_mode_change())

        ttk.Label(config_frame, text="Regla:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        rule_cb = ttk.Combobox(config_frame, textvariable=self.rule_var, values=["Original", "Orden Libre", "Dado Bonus"], width=14, state="readonly")
        rule_cb.grid(row=0, column=3, padx=5)
        rule_cb.bind("<<ComboboxSelected>>", lambda e: self.on_rule_change())

        # Checkbox para mostrar/ocultar probabilidades teóricas
        tk.Checkbutton(config_frame, text="Mostrar probabilidades teóricas", variable=self.show_theoretical_var, bg="#f5f5f5").grid(row=0, column=4, padx=10)

        # Frame para jugadores
        self.players_frame = tk.LabelFrame(root, text="Jugadores", bg="#f5f5f5", font=("Arial", 12, "bold"))
        self.players_frame.pack(fill="x", padx=10, pady=10)
        self.add_player()  # Jugador inicial

        # Botones (sin botón global "Agregar jugador")
        btn_frame = tk.Frame(root, bg="#f5f5f5")
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="Elegir # aleatorios", command=self.auto_numbers).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="🎲 Jugar", command=self.play).grid(row=0, column=1, padx=5)

        # Resultados
        self.result_text = tk.Text(root, height=18, font=("Consolas", 11), bg="white")
        self.result_text.pack(fill="both", padx=10, pady=10, expand=True)
        self.show_welcome_text()

    def add_player(self, index=None):
        """
        Agrega un nuevo jugador.
        Si index is None -> se agrega al final.
        Si index es int -> inserta en esa posición (0-based).
        """
        idx = len(self.players) + 1 if index is None else index + 1
        frame = tk.Frame(self.players_frame, bg="#f5f5f5", pady=3)
        # Si se inserta en medio, empaquetar antes del frame existente
        if index is None or index >= len(self.players):
            frame.pack(fill="x", anchor="w")
        else:
            before_widget = self.players[index]["frame"]
            frame.pack(fill="x", anchor="w", before=before_widget)

        name_var = tk.StringVar(value=f"Jugador {idx}")
        tk.Label(frame, text="Nombre:", bg="#f5f5f5").pack(side="left", padx=(5, 2))
        tk.Entry(frame, textvariable=name_var, width=14).pack(side="left", padx=(0, 10))

        # Contenedor derecho para los botones + y ✖ (pack left para ordenar + then ✖)
        right_controls = tk.Frame(frame, bg="#f5f5f5")
        right_controls.pack(side="right", padx=5)

        # Botón agregar pequeño "+" (a la izquierda de la X)
        add_btn = tk.Button(right_controls, text="+", fg="green", bg="#f5f5f5", bd=0, width=2)
        add_btn.pack(side="left", padx=(0,4))

        # Botón eliminar jugador "✖"
        del_btn = tk.Button(right_controls, text="✖", fg="red", bg="#f5f5f5", bd=0, width=2)
        del_btn.pack(side="left")

        dice_container = tk.Frame(frame, bg="#f5f5f5")
        dice_container.pack(side="left")

        dice_vars = []
        for _ in range(self.mode_var.get()):
            var = tk.StringVar()
            dice_vars.append(var)
            ttk.Entry(dice_container, textvariable=var, width=4).pack(side="left", padx=2)

        # crear el dict del jugador
        player_dict = {
            "name_var": name_var,
            "dice_vars": dice_vars,
            "frame": frame,
            "dice_container": dice_container,
            "add_btn": add_btn,
            "del_btn": del_btn
        }

        # Insertar en la lista en la posición adecuada
        if index is None or index >= len(self.players):
            self.players.append(player_dict)
        else:
            self.players.insert(index, player_dict)

        # enlazar comandos (ahora que player_dict está en self.players)
        add_btn.configure(command=lambda f=frame: self.add_player_after(f))
        del_btn.configure(command=lambda f=frame: self.delete_player(f))

        self.renumber_default_names()

    def add_player_after(self, frame):
        """Inserta un nuevo jugador justo después del frame indicado."""
        # encontrar índice del player con ese frame
        for i, p in enumerate(self.players):
            if p["frame"] == frame:
                insert_index = i + 1
                break
        else:
            insert_index = len(self.players)
        self.add_player(index=insert_index)

    def delete_player(self, frame):
        """Elimina un jugador dado su frame, preservando al menos uno."""
        if len(self.players) <= 1:
            messagebox.showinfo("Aviso", "Debe existir al menos un jugador.")
            return
        # remover de la lista y destruir frame
        for p in list(self.players):
            if p["frame"] == frame:
                self.players.remove(p)
                p["frame"].destroy()
                break
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
                p["dice_vars"].pop()
                children = p["dice_container"].winfo_children()
                if children:
                    children[-1].destroy()
                current -= 1

    def on_rule_change(self):
        """Placeholder si queremos comportamientos visuales al cambiar regla."""
        pass

    def show_welcome_text(self):
        msg = (
            "Bienvenido a 'Los Dados de la Fortuna'\n\n"
            "Reglas disponibles:\n"
            "  - Original: Deben coincidir posición y valor.\n"
            "  - Orden Libre: Solo importa que el valor aparezca.\n"
            "  - Dado Bonus: Después de la primera tirada puedes intentar relanzar dados no acertados (riesgo/recompensa).\n\n"
            
            "Puedes añadir jugadores usando el pequeño botón '+'.\n"
            "Usa 'Elegir # aleatorios' para rellenar rápidamente.\n ¡Suerte!\n"
        )
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, msg)

    def auto_numbers(self):
        n = self.mode_var.get()
        for p in self.players:
            nums = random.sample(range(1, 7), n)
            for i, var in enumerate(p["dice_vars"]):
                var.set(str(nums[i]))

    def _ask_k_via_quick_dialog(self, player_name, max_k):
        """
        Si max_k == 1 devuelve 1 (auto).
        Si max_k > 1 abre QuickRerollDialog que retorna k (1..max_k) o None si cancela.
        """
        if max_k == 0:
            return 0
        if max_k == 1:
            return 1
        dlg = QuickRerollDialog(self.root, player_name, max_k)
        return dlg.selected_k  # int or None

    def play(self):
        mode = self.mode_var.get()
        rule_selected = self.rule_var.get()  # "Original", "Orden Libre", "Dado Bonus"
        is_bonus_rule = (rule_selected == "Dado Bonus")
        effective_rule = "Original" if is_bonus_rule else rule_selected  # comparación se basa en Original/Orden Libre

        # Preparar salida
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Modo: {mode} dados | Regla: {rule_selected}\n")
        self.result_text.insert(tk.END, "="*80 + "\n\n")

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

            # Tirada inicial
            roll = roll_dice(mode)
            matches_initial = match_fn(chosen, roll)

            # Mensaje por jugador: tirada inicial
            self.result_text.insert(tk.END, f"{name}\n")
            self.result_text.insert(tk.END, f"  Elección: {chosen}\n")
            self.result_text.insert(tk.END, f"  Tirada inicial: {roll} → {matches_initial} aciertos\n")

            # Lógica especial para Dado Bonus (preguntar al usuario si quiere intentar)
            if is_bonus_rule:
                non_match_indices = [i for i, (c, r) in enumerate(zip(chosen, roll)) if c != r]
                max_k = len(non_match_indices)
                if max_k == 0:
                    self.result_text.insert(tk.END, "  Todos los dados ya acertaron. No hay Dado Bonus posible.\n")
                    matches_final = matches_initial
                    roll_final = roll
                else:
                    want_bonus = messagebox.askyesno("Dado Bonus", f"{name}: obtuviste {matches_initial} aciertos. ¿Deseas intentar el Dado Bonus? (máx {max_k} dados a relanzar)")
                    if not want_bonus:
                        matches_final = matches_initial
                        roll_final = roll
                    else:
                        # obtener k solo por botones rápidos (o auto si max_k == 1)
                        k = self._ask_k_via_quick_dialog(name, max_k)
                        if k is None or k == 0:
                            # cancelado o no seleccionado
                            matches_final = matches_initial
                            roll_final = roll
                        else:
                            # relanzar las primeras k posiciones no-acertadas
                            indices_to_reroll = non_match_indices[:k]
                            roll_final = roll.copy()
                            successes = 0
                            failures = 0
                            # relanzar y contar por posición
                            for idx in indices_to_reroll:
                                new_val = random.randint(1, 6)
                                roll_final[idx] = new_val
                                if chosen[idx] == new_val:
                                    successes += 1
                                else:
                                    failures += 1

                            # aplicar regla proporcional: +successes - failures
                            matches_final = matches_initial + successes - failures
                            matches_final = max(0, min(matches_final, mode))

                            # mostrar detalles
                            self.result_text.insert(tk.END, f"  Relanzados {k} dados (indices: {indices_to_reroll})\n")
                            for idx in indices_to_reroll:
                                self.result_text.insert(tk.END, f"    - Pos {idx+1}: elegido {chosen[idx]} -> nuevo valor {roll_final[idx]} -> {'ACIERTO' if chosen[idx]==roll_final[idx] else 'FALLÓ'}\n")
                            net = successes - failures
                            if net > 0:
                                self.result_text.insert(tk.END, f"  Resultado Dado Bonus: +{net} aciertos ( {successes} aciertos nuevos, {failures} fallos ).\n")
                            elif net < 0:
                                self.result_text.insert(tk.END, f"  Resultado Dado Bonus: {net} neto ( {successes} aciertos nuevos, {failures} fallos ).\n")
                            else:
                                self.result_text.insert(tk.END, f"  Resultado Dado Bonus: neto 0 ( {successes} aciertos, {failures} fallos ).\n")
            else:
                # regla Original u Orden Libre sin el diálogo extra
                roll_final = roll
                matches_final = matches_initial

            # mostrar tirada final y premio
            if is_bonus_rule and roll_final != roll:
                self.result_text.insert(tk.END, f"  Tirada final (con Dado Bonus): {roll_final} → {matches_final} aciertos\n")
            else:
                self.result_text.insert(tk.END, f"  Tirada final: {roll_final} → {matches_final} aciertos\n")

            prize = prize_text(mode, matches_final)
            self.result_text.insert(tk.END, f"  🏆 {prize}\n")
            self.result_text.insert(tk.END, "-"*70 + "\n")

        # Probabilidades teóricas (una sola vez al final) — se muestran solo si el checkbox está activo
        if self.show_theoretical_var.get():
            key = f"{mode}_{'Orden Libre' if effective_rule=='Orden Libre' else 'Original'}"
            if is_bonus_rule:
                key = f"{mode}_Dado Bonus" if f"{mode}_Dado Bonus" in THEORETICAL else key
            self.result_text.insert(tk.END, "\nProbabilidades teóricas:\n")
            theoretical = THEORETICAL.get(key, {})
            if not theoretical:
                self.result_text.insert(tk.END, "  (No disponibles para este modo)\n")
            else:
                for k, v in theoretical.items():
                    self.result_text.insert(tk.END, f"  {k:28s}: {v:.4f}\n")
        else:
            self.result_text.insert(tk.END, "\n¡Gracias por jugar!\n")

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DadosFortunaApp(root)
    root.mainloop()
