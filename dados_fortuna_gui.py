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
        self.rule_var = tk.StringVar(value="original")
        self.bonus_var = tk.BooleanVar(value=False)
        self.entry_vars = []

        # Frame de configuración
        config_frame = tk.LabelFrame(root, text="Configuración del juego", bg="#f5f5f5", font=("Arial", 12, "bold"))
        config_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(config_frame, text="Modo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Combobox(config_frame, textvariable=self.mode_var, values=[2, 4], width=5, state="readonly").grid(row=0, column=1, padx=5)

        ttk.Label(config_frame, text="Regla:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Combobox(config_frame, textvariable=self.rule_var, values=["original", "order_free"], width=10, state="readonly").grid(row=0, column=3, padx=5)

        tk.Checkbutton(config_frame, text="Dado bonus", variable=self.bonus_var, bg="#f5f5f5").grid(row=0, column=4, padx=10)

        # Frame para números
        self.numbers_frame = tk.LabelFrame(root, text="Tus números", bg="#f5f5f5", font=("Arial", 12, "bold"))
        self.numbers_frame.pack(fill="x", padx=10, pady=10)
        self.update_number_entries()

        # Botones
        btn_frame = tk.Frame(root, bg="#f5f5f5")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Elegir aleatorios", command=self.auto_numbers).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="🎲 Jugar", command=self.play).grid(row=0, column=1, padx=5)

        # Resultados
        self.result_text = tk.Text(root, height=10, font=("Consolas", 11), bg="white")
        self.result_text.pack(fill="both", padx=10, pady=10, expand=True)

    def update_number_entries(self):
        for widget in self.numbers_frame.winfo_children():
            widget.destroy()
        self.entry_vars = []
        n = self.mode_var.get()
        for i in range(n):
            var = tk.StringVar()
            self.entry_vars.append(var)
            ttk.Entry(self.numbers_frame, textvariable=var, width=5).grid(row=0, column=i, padx=5, pady=5)

    def auto_numbers(self):
        n = self.mode_var.get()
        nums = random.sample(range(1, 7), n)
        for i, var in enumerate(self.entry_vars):
            var.set(str(nums[i]))

    def play(self):
        try:
            chosen = [int(var.get()) for var in self.entry_vars]
            if len(set(chosen)) != len(chosen):
                raise ValueError("Números repetidos.")
            if not all(1 <= x <= 6 for x in chosen):
                raise ValueError("Números fuera de rango (1-6).")
        except Exception as e:
            messagebox.showerror("Error", f"Entrada inválida: {e}")
            return

        mode = self.mode_var.get()
        rule = self.rule_var.get()
        bonus = self.bonus_var.get()

        # Tirada inicial
        roll = roll_dice(mode)
        match_fn = matches_original if rule == "original" else matches_order_free
        matches_initial = match_fn(chosen, roll)

        if bonus:
            matches_final, roll_final = apply_bonus(chosen, roll, match_fn)
        else:
            matches_final, roll_final = matches_initial, roll

        prize = prize_text(mode, matches_final)

        # Mostrar resultados
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Elección del jugador: {chosen}\n")
        self.result_text.insert(tk.END, f"Tirada inicial: {roll} → {matches_initial} aciertos\n")
        if bonus:
            self.result_text.insert(tk.END, f"Tirada final (con bonus): {roll_final} → {matches_final} aciertos\n")
        else:
            self.result_text.insert(tk.END, f"Tirada final: {roll_final} → {matches_final} aciertos\n")
        self.result_text.insert(tk.END, f"\n🏆 Resultado: {prize}\n")

        # Probabilidades teóricas
        key = f"{mode}_{'order_free' if rule=='order_free' else 'original'}"
        if bonus:
            key = f"{mode}_bonus" if f"{mode}_bonus" in THEORETICAL else key
        self.result_text.insert(tk.END, "\nProbabilidades teóricas:\n")
        for k, v in THEORETICAL.get(key, {}).items():
            self.result_text.insert(tk.END, f"  {k:25s}: {v:.4f}\n")

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DadosFortunaApp(root)
    root.mainloop()
