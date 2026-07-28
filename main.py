from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from layouts.etiqueta50x25 import Layout50x25
from layouts.etiqueta75x25 import Layout75x25
from layouts.etiqueta75x35 import Layout75x35
from utils.etiquetas import GeradorEtiquetas
from utils.excel import ler_produtos
from utils.pdf import ler_tabela_precos
from utils.precos import arredondar_preco


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
LOGO_PATH = ASSETS_DIR / "logo.png"


class CentralEtiquetasApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Central Etiquetas")
        self.root.geometry("720x520")
        self.root.resizable(False, False)

        self.produtos_path = tk.StringVar(value="")
        self.tabela_path = tk.StringVar(value="")
        self.modelo = tk.StringVar(value="75x35")
        self.status = tk.StringVar(value="Aguardando arquivos...")

        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        title = ttk.Label(container, text="CENTRAL ETIQUETAS", font=("Segoe UI", 20, "bold"))
        title.pack(pady=(0, 16))

        files_frame = ttk.LabelFrame(container, text="Arquivos", padding=16)
        files_frame.pack(fill="x")

        self._row_file(files_frame, "Lista de Produtos", self.produtos_path, self._choose_produtos)
        self._row_file(files_frame, "Tabela 1 (PDF)", self.tabela_path, self._choose_tabela)

        model_frame = ttk.LabelFrame(container, text="Modelo", padding=16)
        model_frame.pack(fill="x", pady=16)

        ttk.Radiobutton(model_frame, text="75 x 35 mm", variable=self.modelo, value="75x35").pack(anchor="w")
        ttk.Radiobutton(model_frame, text="75 x 25 mm", variable=self.modelo, value="75x25").pack(anchor="w")
        ttk.Radiobutton(model_frame, text="50 x 25 mm", variable=self.modelo, value="50x25").pack(anchor="w")

        actions = ttk.Frame(container)
        actions.pack(fill="x", pady=(0, 12))

        self.btn_gerar = ttk.Button(actions, text="GERAR ETIQUETAS", command=self.gerar)
        self.btn_gerar.pack(fill="x")

        self.progress = ttk.Progressbar(container, orient="horizontal", mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(8, 6))

        ttk.Label(container, textvariable=self.status).pack(anchor="w")

    def _row_file(self, parent, label, variable, command):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=8)
        ttk.Label(row, text=label, width=18).pack(side="left")
        entry = ttk.Entry(row, textvariable=variable)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(row, text="Selecionar", command=command).pack(side="left")

    def _choose_produtos(self):
        path = filedialog.askopenfilename(
            title="Selecionar lista de produtos",
            filetypes=[("Planilhas", "*.csv *.xlsx *.xlsm"), ("CSV", "*.csv"), ("Excel", "*.xlsx *.xlsm")],
        )
        if path:
            self.produtos_path.set(path)

    def _choose_tabela(self):
        path = filedialog.askopenfilename(
            title="Selecionar Tabela 1",
            filetypes=[("PDF", "*.pdf")],
        )
        if path:
            self.tabela_path.set(path)

    def _set_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        self.btn_gerar.config(state=state)

    def _ler_modelo(self):
        modelo = self.modelo.get()
        if modelo == "75x35":
            return Layout75x35()
        if modelo == "75x25":
            return Layout75x25()
        if modelo == "50x25":
            return Layout50x25()
        raise ValueError("Modelo inválido.")

    def gerar(self):
        if not self.produtos_path.get():
            messagebox.showwarning("Central Etiquetas", "Selecione a lista de produtos.")
            return
        if not self.tabela_path.get():
            messagebox.showwarning("Central Etiquetas", "Selecione a Tabela 1.")
            return

        self._set_busy(True)
        self.progress["value"] = 0
        self.status.set("Lendo lista de produtos...")
        self.root.update_idletasks()

        try:
            produtos = ler_produtos(self.produtos_path.get())
            self.progress["value"] = 20
            self.status.set("Lendo Tabela 1...")
            self.root.update_idletasks()

            tabela_precos = ler_tabela_precos(self.tabela_path.get())
            self.progress["value"] = 45
            self.status.set("Cruzando preços...")
            self.root.update_idletasks()

            produtos_para_imprimir = []
            sem_preco = []
            for produto in produtos:
                preco_texto = tabela_precos.get(produto.sku)
                if preco_texto is None:
                    sem_preco.append(produto.sku)
                    continue

                preco = arredondar_preco(preco_texto)
                produtos_para_imprimir.append(
                    {
                        "sku": produto.sku,
                        "descricao": produto.descricao,
                        "preco": preco,
                    }
                )

            self.progress["value"] = 65
            self.status.set("Gerando PDF...")
            self.root.update_idletasks()

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            modelo = self.modelo.get()
            output_file = OUTPUT_DIR / f"etiquetas_central_solda_{modelo}.pdf"

            gerador = GeradorEtiquetas(logo_path=str(LOGO_PATH) if LOGO_PATH.exists() else None)
            resultado = gerador.gerar_pdf(
                produtos=produtos_para_imprimir,
                caminho_saida=str(output_file),
                modelo=modelo,
            )

            self.progress["value"] = 100
            self.status.set("Concluído.")

            resumo = (
                f"PDF gerado com sucesso!\n\n"
                f"Modelo: {modelo}\n"
                f"Produtos lidos: {len(produtos)}\n"
                f"Etiquetas geradas: {resultado.total_etiquetas}\n"
                f"Produtos sem preço: {len(sem_preco)}\n"
                f"Arquivo: {resultado.arquivo_pdf}"
            )
            if sem_preco:
                resumo += "\n\nSKUs sem preço: " + ", ".join(sem_preco[:20])
            messagebox.showinfo("Central Etiquetas", resumo)

        except Exception as exc:
            self.status.set("Erro na geração.")
            messagebox.showerror("Central Etiquetas", f"Não foi possível gerar as etiquetas.\n\n{exc}")
        finally:
            self._set_busy(False)


if __name__ == "__main__":
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    CentralEtiquetasApp(root)
    root.mainloop()
