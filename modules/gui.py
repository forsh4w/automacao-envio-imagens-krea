import tkinter as tk
from winotify import Notification
import sys
from tkinter import messagebox


def mostrar_notificacao(mensagem):
    try:
        toast = Notification(
            app_id="PJe Automação",
            title="Aviso",
            msg=f"⚠️ {mensagem}",
            duration="short",  # ou "long"
        )
        toast.show()
    except Exception as e:
        print(f"[⚠️ Aviso] Falha ao exibir notificação: {e}")

def mostrar_janela_mensagem(mensagem):
    root = tk.Tk()
    root.title("Mensagem")
    root.resizable(False, False)

    root.attributes("-topmost", True)  # Fica sempre acima das outras janelas

    label = tk.Label(
        root,
        text=f"{mensagem}",
        font=("Verdana", 12),
        justify="center",
        padx=10,
        pady=10,
    )
    label.pack(pady=(10, 5))

    ok_button = tk.Button(
        root,
        text="✅ OK",
        font=("Verdana", 10, "bold"),
        width=10,
        command=root.destroy,  # Fecha a janela ao clicar
    )
    ok_button.pack(pady=(0, 15))

    # Centraliza a janela depois que todos os widgets foram montados
    root.update_idletasks()  # força cálculo do tamanho ideal
    largura = root.winfo_width()
    altura = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (largura // 2)
    y = (root.winfo_screenheight() // 2) - (altura // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()

def mostrar_janela_dados():
    """
    Abre uma janela Tkinter que solicita:
    - nome da pessoa
    - texto sugerido pela cliente
    - variações desejadas (opcional)
    
    Retorna um dicionário com os dados quando o usuário clicar em OK.
    """

    def enviar_dados():
        nome = entry_nome.get().strip()
        texto = text_sugerido.get("1.0", tk.END).strip()
        variacoes_str = entry_variacoes.get().strip()

        if not nome or not texto:
            messagebox.showwarning("Aviso", "Por favor, preencha o nome e o texto sugerido.")
            return
        
        # Converte a string de variações em lista (removendo espaços extras)
        variacoes = [v.strip() for v in variacoes_str.split(",") if v.strip()]

        # Guarda os resultados e fecha a janela
        dados["nome"] = nome
        dados["texto"] = texto
        dados["variacoes"] = variacoes
        janela.destroy()

    dados = {}

    # Criação da janela
    janela = tk.Tk()
    janela.title("Sugestão de Texto")
    janela.geometry("400x350")
    janela.resizable(False, False)

    # Componentes da interface
    tk.Label(janela, text="Nome da pessoa:").pack(anchor="w", padx=10, pady=(10, 0))
    entry_nome = tk.Entry(janela, width=50)
    entry_nome.pack(padx=10, pady=5)

    tk.Label(janela, text="Texto sugerido pela cliente:").pack(anchor="w", padx=10, pady=(10, 0))
    text_sugerido = tk.Text(janela, height=6, width=50)
    text_sugerido.pack(padx=10, pady=5)

    tk.Label(janela, text="Três variações desejadas separadas por vírgula:").pack(anchor="w", padx=10, pady=(10, 0))
    entry_variacoes = tk.Entry(janela, width=50)
    entry_variacoes.pack(padx=10, pady=5)

    tk.Button(janela, text="OK", command=enviar_dados, width=10).pack(pady=15)

    # Mantém a janela aberta até o usuário clicar em OK
    janela.mainloop()

    return dados
