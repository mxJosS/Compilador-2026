import csv
import os

class TriploGenerator:
    def __init__(self):
        self.triplos = []
        self.temp_count = 1

    def new_temp(self):
        temp = f"T{self.temp_count}"
        self.temp_count += 1
        return temp

    def reset_temps(self):
        """Reinicia el contador para reusar T1 en cada nueva instrucción."""
        self.temp_count = 1

    def current_line(self):
        return len(self.triplos) + 1

    def add_triplo(self, objeto, fuente, operador):
        self.triplos.append({
            "ID": len(self.triplos) + 1,  
            "Objeto": objeto,
            "Fuente": fuente,
            "Operador": operador
        })

    def update_jump(self, line_index, target_line):
        """
        Parchea la línea a la que debe saltar.
        El Operador ya se definió como TRUE, FALSE o JMP al crear el espacio pendiente.
        Solo actualizamos la columna Fuente con la línea destino.
        """
        if 0 < line_index <= len(self.triplos):
            self.triplos[line_index - 1]["Objeto"] = "VACÍO"
            self.triplos[line_index - 1]["Fuente"] = target_line

    def clear(self):
        self.triplos = []
        self.temp_count = 1

    def get_all(self):
        return self.triplos

    def export_csv(self, filepath="salida/triplos.csv"):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["#", "Dato Objeto", "Dato Fuente", "Operador"])
            for t in self.triplos:
                writer.writerow([t["ID"], t["Objeto"], t["Fuente"], t["Operador"]])


class Parser:
    def __init__(self, tokens, st, eh, triplos_gen):
        self.tokens = tokens
        self.st = st
        self.eh = eh
        self.triplos = triplos_gen
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.return_jumps = []

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def match_lexema(self, esperado):
        if self.current_token and self.current_token.get("lexema") == esperado:
            self.advance()
            return True
        return False

    def match_tipo(self, tipo_esperado):
        if self.current_token and self.current_token.get("tipo") == tipo_esperado:
            valor = self.current_token.get("lexema")
            self.advance()
            return valor
        return None

    def parse(self):
        while self.current_token is not None:
            self.statement()

    def statement(self):
        if not self.current_token: return
        self.triplos.reset_temps() # CLAVE: Reusa el T1
        
        tipo = self.current_token.get("tipo")

        if tipo == "TIPO":
            self.declaracion()
        elif tipo == "ID":
            self.asignacion_o_llamada()
        elif tipo == "FOR":
            self.ciclo_for()
        elif tipo == "RETURN":
            self.retorno()
        else:
            self.advance()

    def declaracion(self):
        self.advance() # Consume One/Two/Tree
        if self.current_token and self.current_token.get("lexema") == "=":
            self.advance() 

        # Si es función (One funtion() { ... })
        if self.current_token and (self.current_token.get("lexema") == "funtion" or self.current_token.get("tipo") == "FUNC"):
            self.advance()
            if self.match_lexema("("):
                self.match_lexema(")")
                # Salto JMP para brincar la función
                salto_func = self.triplos.current_line()
                self.triplos.add_triplo("VACÍO", "PENDIENTE", "JMP")
                
                if self.match_lexema("{"):
                    while self.current_token and self.current_token.get("lexema") != "}":
                        self.statement()
                    self.match_lexema("}")
                
                # Actualiza el salto al final de la función y los Returns
                fin_func = self.triplos.current_line()
                self.triplos.update_jump(salto_func, fin_func)
                for r_jump in self.return_jumps:
                    self.triplos.update_jump(r_jump, fin_func)
                self.return_jumps = []
            return

        # Si es una lista de variables
        while self.current_token and self.current_token.get("lexema") != ";":
            self.advance()
        self.match_lexema(";")

    def asignacion_o_llamada(self):
        var_name = self.current_token.get("lexema")
        self.advance()

        # Soporte nativo para incrementos como a++
        if self.current_token and self.current_token.get("lexema") == "++":
            self.advance()
            t_inc = self.triplos.new_temp()
            self.triplos.add_triplo(t_inc, var_name, "=")
            self.triplos.add_triplo(t_inc, "1", "+")
            self.triplos.add_triplo(var_name, t_inc, "=")
            if self.current_token and self.current_token.get("lexema") == ";":
                self.advance()
            return

        if self.match_lexema("="):
            temp_result = self.expresion()
            if temp_result:
                # REGLA ESTRICTA: Toda asignación simple (a = 10) debe pasar por T1 primero
                if not str(temp_result).startswith("T"):
                    t_asig = self.triplos.new_temp()
                    self.triplos.add_triplo(t_asig, temp_result, "=")
                    self.triplos.add_triplo(var_name, t_asig, "=")
                else:
                    # Si ya viene de una expresión (T1), se asigna directo
                    self.triplos.add_triplo(var_name, temp_result, "=")
            
            if self.current_token and self.current_token.get("lexema") == ";":
                self.advance()

    def ciclo_for(self):
        self.advance() 
        self.match_lexema("(")
        
        # 1. Inicialización
        if self.current_token.get("tipo") == "ID":
            self.asignacion_o_llamada()
        else:
            while self.current_token and self.current_token.get("lexema") != ";":
                self.advance()
            self.match_lexema(";")
            
        inicio_condicion = self.triplos.current_line()
        saltos_true, saltos_false = [], []
        
        # 2. Condición
        self.procesar_comparacion(saltos_true, saltos_false)
        while self.current_token and self.current_token.get("tipo") == "OP_LOG":
            self.advance()
            self.procesar_comparacion(saltos_true, saltos_false)
        self.match_lexema(";")
        
        # 3. Guardar la posición exacta del incremento
        inc_pos_start = self.pos
        while self.current_token and self.current_token.get("lexema") != ")":
            self.advance()
        inc_pos_end = self.pos
        self.match_lexema(")")
        
        # Backpatch TRUE: El bloque inicia justo aquí
        inicio_bloque = self.triplos.current_line()
        for linea in saltos_true: 
            self.triplos.update_jump(linea, inicio_bloque)
            
        # 4. Parsear el Cuerpo del For
        if self.match_lexema("{"):
            while self.current_token and self.current_token.get("lexema") != "}":
                self.statement()
            self.match_lexema("}")
        else:
            self.statement() 
            
        # 5. Volver al incremento usando las posiciones guardadas (Backtracking)
        if inc_pos_start < inc_pos_end:
            self.triplos.reset_temps() 
            save_pos = self.pos 
            
            self.pos = inc_pos_start
            self.current_token = self.tokens[self.pos]
            
            self.asignacion_o_llamada() 
            
            self.pos = save_pos
            self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
            
        # 6. Salto incondicional (JMP) para evaluar la condición de nuevo
        self.triplos.add_triplo("VACÍO", inicio_condicion, "JMP")
        
        # Backpatch FALSE
        salida = self.triplos.current_line()
        for linea in saltos_false: 
            self.triplos.update_jump(linea, salida)

    def procesar_comparacion(self, saltos_true, saltos_false):
        izq = self.expresion()
        op_rel = self.match_tipo("OP_REL")
        der = self.expresion()
        
        if not str(izq).startswith("T"):
            t_comp = self.triplos.new_temp()
            self.triplos.add_triplo(t_comp, izq, "=")
            izq = t_comp
            
        self.triplos.add_triplo(izq, der, op_rel)
        
        # Agregamos los espacios para los saltos (Operador ya definido como TRUE/FALSE)
        saltos_true.append(self.triplos.current_line())
        self.triplos.add_triplo("VACÍO", "PENDIENTE", "TRUE")
        
        saltos_false.append(self.triplos.current_line())
        self.triplos.add_triplo("VACÍO", "PENDIENTE", "FALSE")

    def expresion(self):
        temp_izq = self.termino()
        
        if self.current_token and self.current_token.get("lexema") in ["+", "-"]:
            if not str(temp_izq).startswith("T"):
                nuevo_t = self.triplos.new_temp()
                self.triplos.add_triplo(nuevo_t, temp_izq, "=")
                temp_izq = nuevo_t

            while self.current_token and self.current_token.get("lexema") in ["+", "-"]:
                op = self.current_token.get("lexema")
                self.advance()
                temp_der = self.termino()
                self.triplos.add_triplo(temp_izq, temp_der, op)
                
        return temp_izq

    def termino(self):
        temp_izq = self.factor()
        
        if self.current_token and self.current_token.get("lexema") in ["*", "/"]:
            if not str(temp_izq).startswith("T"):
                nuevo_t = self.triplos.new_temp()
                self.triplos.add_triplo(nuevo_t, temp_izq, "=")
                temp_izq = nuevo_t

            while self.current_token and self.current_token.get("lexema") in ["*", "/"]:
                op = self.current_token.get("lexema")
                self.advance()
                temp_der = self.factor()
                self.triplos.add_triplo(temp_izq, temp_der, op)
                
        return temp_izq

    def factor(self):
        if not self.current_token: return ""
        tipo = self.current_token.get("tipo")
        lexema = self.current_token.get("lexema")

        if tipo in ["ID", "ENTERO", "REAL", "CADENA"]:
            self.advance()
            if self.current_token and self.current_token.get("lexema") == "(": 
                self.advance()
                self.match_lexema(")")
                t_val = self.triplos.new_temp()
                self.triplos.add_triplo(t_val, lexema, "CALL")
                return t_val
            return lexema 
            
        elif lexema == "(":
            self.advance()
            res = self.expresion()
            self.match_lexema(")")
            return res
        return ""

    def retorno(self):
        self.advance()
        self.expresion()
        self.return_jumps.append(self.triplos.current_line())
        self.triplos.add_triplo("VACÍO", "PENDIENTE", "JMP")