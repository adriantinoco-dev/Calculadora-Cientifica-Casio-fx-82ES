import tkinter as tk
import math
import re

# ── Superescritos Unicode ──────────────────────────────────────────────────────
_SUP  = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
_RSUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")

# ── Formatação de resultado ────────────────────────────────────────────────────
def formatar_resultado(valor: float) -> str:
    if not isinstance(valor, (int, float)) or math.isnan(valor) or math.isinf(valor):
        return "Erro"
    if valor == 0:
        return "0"

    abs_v = abs(valor)
    k = math.floor(math.log10(abs_v)) + 1  # ordem de magnitude

    # Notação científica estilo Casio (≥ 10^10 ou < 10^-8)
    if k >= 11 or k <= -8:
        mantissa, exp_str = f"{valor:.9e}".split("e")
        mantissa = mantissa.rstrip("0").rstrip(".").replace(".", ",")
        exp_sup  = str(int(exp_str)).translate(_SUP)
        return f"{mantissa}×10{exp_sup}"

    # Notação decimal com 10 dígitos significativos
    dec = max(0, 10 - k)
    s   = f"{valor:,.{dec}f}"

    # Checa se arredondamento cruzou a fronteira
    if abs(float(s.replace(",", ""))) >= 1e10:
        return formatar_resultado(valor)  # re-entra na branch científica

    # Remove zeros à direita
    if "." in s:
        inteira, frac = s.split(".")
        frac = frac.rstrip("0")
        s = f"{inteira}.{frac}" if frac else inteira

    # EN → PT-BR  (,→. e .→,)
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


# ── Limpeza de expressão formatada → Python ────────────────────────────────────
def limpar_expr(expr: str) -> str:
    # Desfaz notação Casio (ex: 1,445×10¹⁷ → 1.445e17)
    expr = expr.translate(_RSUP).replace("×10", "e")

    # Normaliza números PT-BR (1.234,56 → 1234.56)
    def norm_num(m):
        t = m.group(0)
        if "," in t or t.count(".") > 1:
            t = t.replace(".", "").replace(",", ".")
        return t

    return re.sub(r"[\d.,]+", norm_num, expr)


# ── Tradução da expressão exibida → Python ─────────────────────────────────────
def para_python(expr: str) -> str:
    # Funções inversas ANTES de limpar superescritos (⁻¹ ainda intacto)
    expr = expr.replace("sen⁻¹(", "sen_inv(")
    expr = expr.replace("cos⁻¹(", "cos_inv(")
    expr = expr.replace("tan⁻¹(", "tan_inv(")

    # ² deve ser substituído ANTES de limpar_expr, pois _RSUP converte ² → 2
    expr = expr.replace("²", "**2")

    expr = limpar_expr(expr)

    # Multiplicação implícita: 2π → 2*π, 2( → 2*(, )2 → )*2
    expr = re.sub(r"(\d)\s*(π|e|sen|cos|tan|log|ln|√|\()", r"\1*\2", expr)
    expr = re.sub(r"\)\s*(\d|π|e|sen|cos|tan|log|ln|√|\()",  r")*\1", expr)

    # √x sem parênteses
    expr = re.sub(r"√(\d+\.?\d*|π|e)", r"math.sqrt(\1)", expr)

    for antigo, novo in [
    ("log(",   "math.log10("), ("ln(",    "math.log("), ("√(",  "math.sqrt("),
    ("π",      "math.pi"),    ("^",       "**"),
    ("÷",      "/"),          ("×",       "*"),           ("−", "-"),
    ]:
        expr = expr.replace(antigo, novo)

    # % contextual: X+Y% → X+X*Y/100 | X-Y% → X-X*Y/100 | X*%N → X*N/100 | N% → N/100
    if "%" in expr:
        pct = expr.index("%")
        antes = expr[:pct]
        depois = expr[pct + 1:]
        # Padrão %× (ex: 50%*200): número antes do %, operador depois
        if depois and depois[0] in "*/":
            expr = antes + "/100" + depois
        # Padrão ×% (ex: 200*%50): operador antes do %, número depois
        elif antes and antes[-1] in "*/" and depois:
            expr = antes + depois + "/100"
        else:
            depth, op_idx, op_ch = 0, -1, ""
            for i in range(len(antes) - 1, -1, -1):
                ch = antes[i]
                if ch == ")": depth += 1
                elif ch == "(": depth -= 1
                elif ch in "+-" and depth == 0 and i > 0:
                    op_idx, op_ch = i, ch
                    break
            if op_idx > 0:
                base = antes[:op_idx]
                num  = antes[op_idx + 1:]
                expr = f"{base}{op_ch}({base})*{num}/100{depois}"
            else:
                expr = f"{antes}/100{depois}"

    # `e` e `pi` soltos que não sejam math.e / math.pi
    expr = re.sub(r"(?<!math\.)\bpi\b", "math.pi", expr)
    expr = re.sub(r"(?<!math\.)\be\b",  "math.e",  expr)
    return expr



# ── Normalização de texto colado ───────────────────────────────────────────────
def limpar_colado(texto: str) -> str:
    texto = texto.strip()
    # Vírgula decimal PT-BR entre dígitos → ponto
    texto = re.sub(r"(\d),(\d)", r"\1.\2", texto)
    # Operadores ASCII → símbolos da calculadora
    texto = texto.translate(str.maketrans({"*": "×", "/": "÷", "-": "−"}))
    # Remove espaços
    texto = texto.replace(" ", "")
    # Percorre token a token: funções conhecidas têm prioridade
    FUNCOES = ["sen⁻¹(", "cos⁻¹(", "tan⁻¹(", "sen(", "cos(", "tan(", "log(", "ln(", "√("]
    VALIDOS = set("0123456789.+−×÷%^()π²√e")
    resultado, i = [], 0
    while i < len(texto):
        consumido = False
        for fn in FUNCOES:
            if texto[i:].startswith(fn):
                resultado.append(fn)
                i += len(fn)
                consumido = True
                break
        if not consumido:
            if texto[i] in VALIDOS:
                resultado.append(texto[i])
            i += 1
    return "".join(resultado)

# ── Calculadora ────────────────────────────────────────────────────────────────
class Calculadora:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.expr      = ""          # expressão visível
        self.val_real  = None        # resultado numérico completo
        self.mostrando = False       # se está exibindo resultado

        self._build_ui()
        self.root.bind("<Key>",       self._tecla)
        self.root.bind("<Configure>", self._resize)
        self.root.bind("<Control-v>",  self._colar)

    # ── Display ───────────────────────────────────────────────────────────────
    def _atualizar(self):
        self.lbl_resultado.config(text=self.expr or "0")
        self.btn_ac.config(text="C" if self.expr else "AC")

    # ── Entrada ───────────────────────────────────────────────────────────────
    def inserir(self, val: str):
        operadores = set("+-−×÷%^²")
        if self.mostrando:
            if val in operadores and self.expr != "Erro":
                # Continua com o valor numérico completo
                base = self.val_real
                if isinstance(base, float) and base.is_integer():
                    base = int(base)
                self.expr = str(base) + val
            else:
                self.expr = val
            self.mostrando = False
        else:
            self.expr = val if self.expr == "Erro" else self.expr + val
        self._atualizar()

    def inserir_func(self, func: str):
        if self.mostrando or self.expr == "Erro":
            self.expr      = func
            self.mostrando = False
        else:
            self.expr += func
        self._atualizar()

    def elevar_quadrado(self):
        """Insere ² e calcula imediatamente."""
        self.inserir("²")
        self.calcular()

    def inserir_percentual(self):
        """Insere %× se o display termina com dígito ou ), caso contrário apenas %."""
        ultimo = self.expr[-1] if self.expr and not self.mostrando else ""
        if ultimo.isdigit() or ultimo == ")":
            self.expr += "%×"
            self._atualizar()
        else:
            self.inserir("%")

    # ── Ações especiais ───────────────────────────────────────────────────────
    def limpar(self):
        self.expr      = ""
        self.val_real  = None
        self.mostrando = False
        self.lbl_formula.config(text="")
        self._atualizar()

    def apagar(self, _=None):
        if self.mostrando:
            self.limpar()
            return
        for tok in ("sen⁻¹(","cos⁻¹(","tan⁻¹(","sen(","cos(","tan(","log(","ln(","√("):
            if self.expr.endswith(tok):
                self.expr = self.expr[:-len(tok)]
                self._atualizar()
                return
        self.expr = self.expr[:-1]
        self._atualizar()

    def parentese(self):
        if self.mostrando or self.expr == "Erro":
            self.expr = "("
            self.mostrando = False
        else:
            abre  = self.expr.count("(")
            fecha = self.expr.count(")")
            ultimo = self.expr[-1] if self.expr else ""
            if abre > fecha and ultimo not in ("+","−","×","÷","(","^","²",""):
                self.expr += ")"
            else:
                self.expr += "("
        self._atualizar()

    def inverter_sinal(self):
        if self.mostrando and self.val_real is not None and self.expr != "Erro":
            self.val_real = -self.val_real
            base = int(self.val_real) if isinstance(self.val_real, float) and self.val_real.is_integer() else self.val_real
            self.expr = str(base)
            self.lbl_resultado.config(text=formatar_resultado(self.val_real))
            return

        # Inverte o último número digitado
        m = re.search(r"([-−]?)(?:\d+\.?\d*(?:[eE][+−-]?\d+)?|π|e)$", self.expr)
        if m:
            ini = m.start()
            self.expr = (self.expr[:ini] + self.expr[ini+1:]) if m.group(1) else (self.expr[:ini] + "−" + self.expr[ini:])
        elif not self.expr or self.expr[-1] in ("+","−","×","÷","("):
            self.expr += "−"
        self._atualizar()

    def calcular(self, _=None):
        if not self.expr:
            return

        expr_vis = self.expr.strip()
        # Fecha parênteses abertos automaticamente
        diff = expr_vis.count("(") - expr_vis.count(")")
        if diff > 0:
            expr_vis += ")" * diff

        self.lbl_formula.config(text=expr_vis)
        py = para_python(expr_vis)

        try:
            def sen(g):     return math.sin(math.radians(g))
            def cos(g):     return math.cos(math.radians(g))
            def tan(g):     return math.tan(math.radians(g))
            def sen_inv(v): return math.degrees(math.asin(v))
            def cos_inv(v): return math.degrees(math.acos(v))
            def tan_inv(v): return math.degrees(math.atan(v))

            resultado = eval(py, {
                "math": math, "__builtins__": None,
                "sen": sen, "cos": cos, "tan": tan,
                "sen_inv": sen_inv, "cos_inv": cos_inv, "tan_inv": tan_inv,
            })
            self.val_real = resultado
            self.lbl_resultado.config(text=formatar_resultado(resultado))
            base = int(resultado) if isinstance(resultado, float) and resultado.is_integer() else resultado
            self.expr      = str(base)
            self.mostrando = True
        except Exception:
            self.lbl_resultado.config(text="Erro")
            self.expr      = "Erro"
            self.val_real  = None
            self.mostrando = True

    def _colar(self, _=None):
        try:
            texto = self.root.clipboard_get()
        except tk.TclError:
            return
        limpo = limpar_colado(texto)
        if not limpo:
            return
        if self.mostrando or self.expr == "Erro":
            self.expr = limpo
            self.mostrando = False
        else:
            self.expr += limpo
        self._atualizar()

    # ── Teclado ───────────────────────────────────────────────────────────────
    def _tecla(self, ev):
        c, k = ev.char, ev.keysym
        if c.isdigit():           self.inserir(c)
        elif c in (".", ","):     self.inserir(".")
        elif c == "+":            self.inserir("+")
        elif c == "-":            self.inserir("−")
        elif c == "*":            self.inserir("×")
        elif c == "/":            self.inserir("÷")
        elif c == "%":            self.inserir("%")
        elif c in ("(", ")"):     self.inserir(c)
        elif c.lower() == "p":    self.inserir("π")
        elif c.lower() == "r":    self.inserir_func("√(")
        elif c.lower() == "s":    self.inserir_func("sen(")
        elif c.lower() == "c":    self.inserir_func("cos(")
        elif c.lower() == "t":    self.inserir_func("tan(")
        elif c.lower() == "l":    self.inserir_func("log(")
        elif k == "Return":       self.calcular()
        elif k == "v" and (ev.state & 0x4): self._colar()
        elif k == "BackSpace":    self.apagar()
        elif k == "Escape":       self.limpar()

    # ── Resize responsivo ─────────────────────────────────────────────────────
    def _resize(self, ev):
        if ev.widget != self.root:
            return
        s = max(0.65, min(min(ev.width / 640, ev.height / 450), 2.5))
        self.lbl_formula.config(  font=("Segoe UI", int(14 * s)))
        self.lbl_resultado.config(font=("Segoe UI", int(36 * s), "bold"))
        for btn, btype in self._btns:
            sz = {"operator": 22, "number": 18, "function": 14}.get(btype, 12)
            btn.config(font=("Segoe UI", int(sz * s), "bold"))

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.root.configure(bg="#000000")
        self.root.geometry("640x450")
        self.root.minsize(480, 320)

        # Display
        frm = tk.Frame(self.root, bg="#000000")
        frm.pack(fill="x", padx=20, pady=(15, 5))

        self.lbl_formula = tk.Label(frm, text="", font=("Segoe UI", 14),
            bg="#000000", fg="#888888", anchor="e", justify="right")
        self.lbl_formula.pack(fill="x", pady=(5, 2))

        self.lbl_resultado = tk.Label(frm, text="0", font=("Segoe UI", 36, "bold"),
            bg="#000000", fg="#FFFFFF", anchor="e", justify="right")
        self.lbl_resultado.pack(fill="x", pady=(2, 5))

        # Botões
        grid = tk.Frame(self.root, bg="#000000")
        grid.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        for i in range(5): grid.rowconfigure(i, weight=1)
        for i in range(7): grid.columnconfigure(i, weight=1)

        self._btns = []   # (btn, type) para resize

        layout = [
            # Científicos — col 0-2
            ("sen",    0,0,1,"scientific", lambda: self.inserir_func("sen(")),
            ("cos",    0,1,1,"scientific", lambda: self.inserir_func("cos(")),
            ("tan",    0,2,1,"scientific", lambda: self.inserir_func("tan(")),
            ("sen⁻¹",  1,0,1,"scientific", lambda: self.inserir_func("sen⁻¹(")),
            ("cos⁻¹",  1,1,1,"scientific", lambda: self.inserir_func("cos⁻¹(")),
            ("tan⁻¹",  1,2,1,"scientific", lambda: self.inserir_func("tan⁻¹(")),
            ("log",    2,0,1,"scientific", lambda: self.inserir_func("log(")),
            ("ln",     2,1,1,"scientific", lambda: self.inserir_func("ln(")),
            ("√",      2,2,1,"scientific", lambda: self.inserir_func("√(")),
            ("π",      3,0,1,"scientific", lambda: self.inserir("π")),
            ("e",      3,1,1,"scientific", lambda: self.inserir("e")),
            ("x²",     3,2,1,"scientific", self.elevar_quadrado),
            ("( )",    4,0,2,"scientific", self.parentese),
            ("xʸ",     4,2,1,"scientific", lambda: self.inserir("^")),
            # Função — col 3-6, linha 0
            ("AC",     0,3,1,"function",   self.limpar),
            ("DELETE", 0,4,2,"function",   self.apagar),
            ("÷",      0,6,1,"operator",   lambda: self.inserir("÷")),
            # Números e operadores
            ("7",      1,3,1,"number",     lambda: self.inserir("7")),
            ("8",      1,4,1,"number",     lambda: self.inserir("8")),
            ("9",      1,5,1,"number",     lambda: self.inserir("9")),
            ("×",      1,6,1,"operator",   lambda: self.inserir("×")),
            ("4",      2,3,1,"number",     lambda: self.inserir("4")),
            ("5",      2,4,1,"number",     lambda: self.inserir("5")),
            ("6",      2,5,1,"number",     lambda: self.inserir("6")),
            ("−",      2,6,1,"operator",   lambda: self.inserir("−")),
            ("1",      3,3,1,"number",     lambda: self.inserir("1")),
            ("2",      3,4,1,"number",     lambda: self.inserir("2")),
            ("3",      3,5,1,"number",     lambda: self.inserir("3")),
            ("+",      3,6,1,"operator",   lambda: self.inserir("+")),
            ("0",      4,3,1,"number",     lambda: self.inserir("0")),
            (".",      4,4,1,"number",     lambda: self.inserir(".")),
            ("%",      4,5,1,"number",     self.inserir_percentual),
            ("=",      4,6,1,"operator",   self.calcular),
        ]

        CORES = {
            "number":    ("#333333","#FFFFFF","#4F4F4F","#FFFFFF"),
            "scientific":("#A5A5A5","#000000","#D4D4D2","#000000"),
            "function":  ("#A5A5A5","#000000","#D4D4D2","#000000"),
            "operator":  ("#FF9F0A","#FFFFFF","#FCA34D","#FFFFFF"),
        }

        for texto, row, col, span, btype, cmd in layout:
            bg, fg, abg, afg = CORES[btype]
            fonte = ("Segoe UI", 12, "bold") if len(texto) > 3 else ("Segoe UI", 14, "bold")
            btn = tk.Button(grid, text=texto, font=fonte,
                bg=bg, fg=fg, activebackground=abg, activeforeground=afg,
                bd=0, relief="flat", command=cmd)
            btn.grid(row=row, column=col, columnspan=span, sticky="nsew", padx=3, pady=3)
            btn.bind("<Enter>", lambda e, b=btn, c=abg: b.config(bg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=bg:  b.config(bg=c))
            self._btns.append((btn, btype))
            if texto == "AC":
                self.btn_ac = btn


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Calculadora Científica")
    Calculadora(root)
    root.mainloop()
