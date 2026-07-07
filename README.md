# 🧮 Calculadora-Cientifica-Casio-fx-82ES

Calculadora científica desktop desenvolvida em Python com Tkinter, inspirada no visual da Casio fx-82ES PLUS. Interface escura, formatação numérica no padrão PT-BR e suporte a funções trigonométricas, logarítmicas e constantes matemáticas.

---

## ✨ Funcionalidades

- **Operações básicas** — adição, subtração, multiplicação, divisão e porcentagem
- **Funções científicas** — `sen`, `cos`, `tan` e suas inversas (`sen⁻¹`, `cos⁻¹`, `tan⁻¹`)
- **Logaritmos** — `log` (base 10) e `ln` (natural)
- **Raiz quadrada e potenciação** — `√`, `x²` e `xʸ`
- **Constantes** — `π` e `e`
- **Parenteses automáticos** — inserção inteligente de `(` e `)`
- **Notação científica** estilo Casio — exibição com superescritos Unicode (ex: `1,5×10⁸`)
- **Formatação PT-BR** — separador decimal com vírgula e milhar com ponto
- **Inversão de sinal** — alterna o sinal do último número ou do resultado
- **Colar da área de transferência** — `Ctrl+V` com normalização automática do texto colado
- **Atalhos de teclado** — operação completa via teclado
- **Interface responsiva** — redimensionamento proporcional da fonte e dos botões

---

## 🖥️ Interface

Layout dividido em duas seções:

| Região | Conteúdo |
|---|---|
| Esquerda (cols 0–2) | Funções científicas: `sen`, `cos`, `tan`, inversas, `log`, `ln`, `√`, `π`, `e`, `x²`, `( )`, `xʸ` |
| Direita (cols 3–6) | Numérica clássica: `AC/C`, `DELETE`, dígitos 0–9, `.`, `%`, operadores e `=` |

**Paleta de cores:**

| Tipo de botão | Cor de fundo |
|---|---|
| Número | Cinza escuro `#333333` |
| Científico / Função | Cinza claro `#A5A5A5` |
| Operador | Laranja `#FF9F0A` |

---

## ⌨️ Atalhos de Teclado

| Tecla | Ação |
|---|---|
| `0`–`9` | Inserir dígito |
| `.` ou `,` | Inserir ponto decimal |
| `+` `-` `*` `/` `%` | Operadores |
| `(` `)` | Parênteses |
| `p` | Inserir `π` |
| `r` | Inserir `√(` |
| `s` | Inserir `sen(` |
| `c` | Inserir `cos(` |
| `t` | Inserir `tan(` |
| `l` | Inserir `log(` |
| `Enter` | Calcular |
| `Backspace` | Apagar último caractere/função |
| `Esc` | Limpar tudo (AC) |
| `Ctrl+V` | Colar expressão |

---

## 🚀 Como executar

### Executável (recomendado)

Baixe o arquivo `.exe` na aba [Releases](../../releases) do repositório e execute diretamente — nenhuma instalação necessária.

### A partir do código-fonte

Requer Python 3.8 ou superior com Tkinter (incluso na instalação padrão).

```bash
python main.py
```

---

## 📁 Estrutura do projeto

```
calculadora-cientifica/
└── main.py      # Código-fonte completo
```

---

## 🔧 Detalhes técnicos

- **Avaliação de expressões** via `eval` com namespace restrito (sem `__builtins__`), limitando o escopo a funções matemáticas seguras
- **Multiplicação implícita** — `2π`, `2(` e `)2` são convertidos automaticamente para Python
- **Fechamento automático de parênteses** ao pressionar `=`
- **Superescritos Unicode** para exibição de expoentes (`⁰¹²³⁴⁵⁶⁷⁸⁹⁻`) e conversão reversa para avaliação
- **Normalização de texto colado** — converte operadores ASCII, separadores PT-BR e filtra caracteres inválidos

---

## 📄 Licença

Este projeto está disponível sob a licença MIT.
