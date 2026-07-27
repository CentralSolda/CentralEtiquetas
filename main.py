import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class CentralEtiquetasApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('Central Etiquetas')
        self.root.geometry('720x520')
        self.root.resizable(False, False)

        self.produtos_path = tk.StringVar(value='')
        self.tabela_path = tk.StringVar(value='')
        self.modelo = tk.StringVar(value='75x35')
        self.status = tk.StringVar(value='Aguardando arquivos...')

        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill='both', expand=True)

        title = ttk.Label(container, text='CENTRAL ETIQUETAS', font=('Segoe UI', 20, 'bold'))
        title.pack(pady=(0, 16))

        files_frame = ttk.LabelFrame(container, text='Arquivos', padding=16)
        files_frame.pack(fill='x')

        self._row_file(files_frame, 'Lista de Produtos', self.produtos_path, self._choose_produtos)
        self._row_file(files_frame, 'Tabela 1 (PDF)', self.tabela_path, self._choose_tabela)

        model_frame = ttk.LabelFrame(container, text='Modelo', padding=16)
        model_frame.pack(fill='x', pady=16)

        ttk.Radiobutton(model_frame, text='75 x 35 mm', variable=self.modelo, value='75x35').pack(anchor='w')
        ttk.Radiobutton(model_frame, text='75 x 25 mm', variable=self.modelo, value='75x25').pack(anchor='w')
        ttk.Radiobutton(model_frame, text='50 x 25 mm', variable=self.modelo, value='50x25').pack(anchor='w')

        actions = ttk.Frame(container)
        actions.pack(fill='x', pady=(0, 12))

        ttk.Button(actions, text='GERAR ETIQUETAS', command=self.gerar).pack(fill='x')

        self.progress = ttk.Progressbar(container, orient='horizontal', mode='determinate', maximum=100)
        self.progress.pack(fill='x', pady=(8, 6))

        ttk.Label(container, textvariable=self.status).pack(anchor='w')

    def _row_file(self, parent, label, variable, command):
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=8)
        ttk.Label(row, text=label, width=18).pack(side='left')
        entry = ttk.Entry(row, textvariable=variable)
        entry.pack(side='left', fill='x', expand=True, padx=(0, 8))
        ttk.Button(row, text='Selecionar', command=command).pack(side='left')

    def _choose_produtos(self):
        path = filedialog.askopenfilename(
            title='Selecionar lista de produtos',
            filetypes=[('Planilhas', '*.csv *.xlsx *.xlsm'), ('CSV', '*.csv'), ('Excel', '*.xlsx *.xlsm')],
        )
        if path:
            self.produtos_path.set(path)

    def _choose_tabela(self):
        path = filedialog.askopenfilename(
            title='Selecionar Tabela 1',
            filetypes=[('PDF', '*.pdf')],
        )
        if path:
            self.tabela_path.set(path)

    def gerar(self):
        if not self.produtos_path.get():
            messagebox.showwarning('Central Etiquetas', 'Selecione a lista de produtos.')
            return
        if not self.tabela_path.get():
            messagebox.showwarning('Central Etiquetas', 'Selecione a Tabela 1.')
            return

        self.progress['value'] = 0
        etapas = [
            'Lendo lista de produtos...',
            'Lendo Tabela 1...',
            'Cruzando preços...',
            'Aplicando regras...',
            'Gerando PDF...',
            'Finalizando...',
        ]
        for i, etapa in enumerate(etapas, start=1):
            self.status.set(etapa)
            self.progress['value'] = (i / len(etapas)) * 100
            self.root.update_idletasks()
            self.root.after(150)

        self.status.set('Concluído.')
        messagebox.showinfo('Central Etiquetas', 'Estrutura inicial carregada com sucesso.')


if __name__ == '__main__':
    root = tk.Tk()
    try:
        ttk.Style().theme_use('clam')
    except tk.TclError:
        pass
    app = CentralEtiquetasApp(root)
    root.mainloop()
