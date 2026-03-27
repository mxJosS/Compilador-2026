import customtkinter as ctk
from tkinter import ttk
from core import lexer
from core import semantic
from core.lexer import Lexer
from models.symbol_table import SymbolTable
from models.error_handler import ErrorHandler
from core.semantic import SemanticAnalyzer

class CompiladorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Proyecto Compilador 7SB Equipo 12")
        self.geometry("1100x700")

        self.st = SymbolTable()
        self.eh = ErrorHandler()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_izq = ctk.CTkFrame(self)
        self.frame_izq.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.label_input = ctk.CTkLabel(self.frame_izq, text="Entrada de Código: ")
        self.label_input.pack(pady=(10, 0))

        self.frame_texto = ctk.CTkFrame(self.frame_izq)
        self.frame_texto.pack(pady=10, padx=10, expand=True, fill="both")

        self.txt_lineas = ctk.CTkTextbox(self.frame_texto, width=40, state="disabled", fg_color="transparent", text_color="gray")
        self.txt_lineas.pack(side="left", fill="y")

        self.txt_input = ctk.CTkTextbox(self.frame_texto)
        self.txt_input.pack(side="right", expand=True, fill="both")

        self.txt_input.bind("<KeyRelease>", self.actualizar_lineas)
        self.txt_input.bind("<MouseWheel>", self.sincronizar_scroll)
        self.txt_input._textbox.bind("<Configure>", self.actualizar_lineas)

        self.btn_analizar = ctk.CTkButton(self.frame_izq, text="Analizar", command=self.ejecutar)
        self.btn_analizar.pack(pady=10)

        self.frame_der = ctk.CTkFrame(self)
        self.frame_der.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.tabview = ctk.CTkTabview(self.frame_der)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab_simbolos = self.tabview.add("Tabla de Símbolos")
        self.tab_errores = self.tabview.add("Tabla de Errores")
        self.tab_opt = self.tabview.add("Código Optimizado")
        self.tab_asm = self.tabview.add("Código Ensamblador")

        self.setup_tablas()
        self.actualizar_lineas()

    def actualizar_lineas(self, event=None):
        lineas = str(self.txt_input.get("1.0", "end-1c").count("\n") + 1)
        numeros = "\n".join(str(i) for i in range(1, int(lineas) + 1))
        self.txt_lineas.configure(state="normal")
        self.txt_lineas.delete("1.0", "end")
        self.txt_lineas.insert("1.0", numeros)
        self.txt_lineas.configure(state="disabled")

    def sincronizar_scroll(self, event):
        # Agregamos [0] al final para tomar solo el primer valor de la tupla
        self.txt_lineas._textbox.yview_moveto(self.txt_input._textbox.yview()[0])   

    def setup_tablas(self):
        self.tree_st = ttk.Treeview(self.tab_simbolos, columns=("Lexema", "Tipo"), show='headings')
        self.tree_st.heading("Lexema", text="Lexema")
        self.tree_st.heading("Tipo", text="Tipo de dato")
        self.tree_st.pack(expand=True, fill="both", padx=5, pady=5)

        self.tree_eh = ttk.Treeview(self.tab_errores, columns=("Token", "Lexema", "Renglon", "Desc"), show='headings')
        self.tree_eh.heading("Token", text="Token")
        self.tree_eh.heading("Lexema", text="Lexema")
        self.tree_eh.heading("Renglon", text="Renglón")
        self.tree_eh.heading("Desc", text="Descripción")
        self.tree_eh.pack(expand=True, fill="both", padx=5, pady=5)

        ctk.CTkLabel(self.tab_opt, text="").pack()
        ctk.CTkLabel(self.tab_asm, text="").pack()

    def ejecutar(self):
        codigo = self.txt_input.get("1.0", "end-1c")
        self.st.clear()
        self.eh.clear()
        lexer = Lexer(self.st, self.eh)
        lexer.tokenize(codigo)
        semantic = SemanticAnalyzer(self.st, self.eh)
        semantic.analyze(codigo)
        self.eh.sort_errors()
        self.actualizar_tablas()
        self.st.export_csv()
        self.eh.export_csv()

    def actualizar_tablas(self):
        for item in self.tree_st.get_children():
            self.tree_st.delete(item)

        for item in self.tree_eh.get_children():
            self.tree_eh.delete(item)
            
        for simbolo in self.st.get_all():
            self.tree_st.insert("", "end", values=(simbolo["Lexema"], simbolo["Tipo"]))
            
        for error in self.eh.get_all():
            self.tree_eh.insert("", "end", values=(error["Token"], error["Lexema"], error["Renglón"], error["Descripción"]))        
            
if __name__ == "__main__":
    app = CompiladorApp()
    app.mainloop()