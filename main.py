import customtkinter as ctk
from tkinter import ttk
from core.lexer import Lexer
from core.parser import Parser
from core.semantic import SemanticAnalyzer
from core.intermediate import TriploGenerator
from models.symbol_table import SymbolTable
from models.error_handler import ErrorHandler

class CompiladorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Proyecto Compilador 7SB Equipo 12")
        self.geometry("1100x700")

        self.st = SymbolTable()
        self.eh = ErrorHandler()
        self.triplos_gen = TriploGenerator()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # UI - Lado Izquierdo
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

        self.btn_analizar = ctk.CTkButton(self.frame_izq, text="Analizar", command=self.ejecutar)
        self.btn_analizar.pack(pady=10)

        # UI - Lado Derecho
        self.frame_der = ctk.CTkFrame(self)
        self.frame_der.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.tabview = ctk.CTkTabview(self.frame_der)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab_simbolos = self.tabview.add("Tabla de Símbolos")
        self.tab_errores = self.tabview.add("Tabla de Errores")
        self.tab_triplos = self.tabview.add("Triplos")
        self.tab_opt = self.tabview.add("Código Optimizado")
        self.tab_asm = self.tabview.add("Código Ensamblador")

        self.setup_tablas()
        self.actualizar_lineas()

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

        # --- AQUÍ SE AGREGÓ LA COLUMNA "ID" PARA QUE COINCIDA CON LA IMAGEN ---
        self.tree_triplos = ttk.Treeview(self.tab_triplos, columns=("ID", "Dato Objeto", "Dato Fuente", "Operador"), show='headings')
        self.tree_triplos.heading("ID", text="#")
        self.tree_triplos.heading("Dato Objeto", text="Data Objeto")
        self.tree_triplos.heading("Dato Fuente", text="Data Fuente")
        self.tree_triplos.heading("Operador", text="Operador")
        
        # Ajustamos los anchos para que el número "#" no ocupe tanto espacio
        self.tree_triplos.column("ID", width=40, anchor="center")
        self.tree_triplos.column("Dato Objeto", width=100, anchor="center")
        self.tree_triplos.column("Dato Fuente", width=100, anchor="center")
        self.tree_triplos.column("Operador", width=100, anchor="center")
        
        self.tree_triplos.pack(expand=True, fill="both", padx=5, pady=5)

    def actualizar_lineas(self, event=None):
        lineas = str(self.txt_input.get("1.0", "end-1c").count("\n") + 1)
        numeros = "\n".join(str(i) for i in range(1, int(lineas) + 1))
        self.txt_lineas.configure(state="normal")
        self.txt_lineas.delete("1.0", "end")
        self.txt_lineas.insert("1.0", numeros)
        self.txt_lineas.configure(state="disabled")

    def sincronizar_scroll(self, event):
        self.txt_lineas._textbox.yview_moveto(self.txt_input._textbox.yview()[0]) 

    def ejecutar(self):
        codigo = self.txt_input.get("1.0", "end-1c")
        
        self.st.clear()
        self.eh.clear()
        self.triplos_gen.clear()

   
        lexer_obj = Lexer(self.st, self.eh)
        lexer_obj.tokenize(codigo)

    
        tokens = lexer_obj.tokens
        if tokens:
            parser_obj = Parser(tokens, self.st, self.eh, self.triplos_gen)
            parser_obj.parse()

    
        semantic_obj = SemanticAnalyzer(self.st, self.eh)
        semantic_obj.analyze(codigo)

        self.eh.sort_errors()
        self.actualizar_tablas()
        
        self.st.export_csv()
        self.eh.export_csv()
        self.triplos_gen.export_csv() 

    def actualizar_tablas(self):
        for tree in [self.tree_st, self.tree_eh, self.tree_triplos]:
            for item in tree.get_children():
                tree.delete(item)
            
        for s in self.st.get_all():
            self.tree_st.insert("", "end", values=(s["Lexema"], s["Tipo"]))
        for e in self.eh.get_all():
            self.tree_eh.insert("", "end", values=(e["Token"], e["Lexema"], e["Renglón"], e["Descripción"]))        
        
        for t in self.triplos_gen.get_all():
            self.tree_triplos.insert("", "end", values=(t["ID"], t["Objeto"], t["Fuente"], t["Operador"]))

if __name__ == "__main__":
    app = CompiladorApp()
    app.mainloop()