class Parser:
    def __init__(self, tokens, st, eh, triplos_gen):
        self.tokens = tokens
        self.st = st
        self.eh = eh
        self.triplos = triplos_gen
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.return_jumps = []
        # Diccionario para guardar parámetros de funciones: {nombre_func: [lista_parametros]}
        self.func_params = {}

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
        self.triplos.reset_temps()

        tipo = self.current_token.get("tipo")

        if tipo == "TIPO":
            self.declaracion()
        elif tipo == "ID":
            self.asignacion_o_llamada()
        elif tipo == "FOR":
            self.ciclo_for()
        elif tipo == "DO":
            self.ciclo_dowhile()
        elif tipo == "WHILE" or tipo == "WHILE_ES":
            self.ciclo_while()
        elif tipo == "IF":
            self.condicional_if()
        elif tipo == "RETURN":
            self.retorno()
        else:
            self.advance()

    def declaracion(self):
        self.advance()  # Consume el tipo (One/Two/Tree)

        # Si es función (ej. One $AAA(...) { ... })
        if self.current_token and self.current_token.get("tipo") == "FUNC":
            func_name = self.current_token.get("lexema")
            self.advance()
            if self.match_lexema("("):
                # Extraer parámetros de la función
                params = []
                while self.current_token and self.current_token.get("lexema") != ")":
                    if self.current_token.get("tipo") in ["TIPO", "ID"]:
                        if self.current_token.get("tipo") == "ID":
                            params.append(self.current_token.get("lexema"))
                        self.advance()
                    else:
                        self.advance()
                self.match_lexema(")")

                # Guardar parámetros de la función
                self.func_params[func_name] = params

                # Salto JMP para brincar la función
                salto_func = self.triplos.current_line()
                self.triplos.add_triplo("VACÍO", "PENDIENTE", "JMP")

                if self.match_lexema("{"):
                    while self.current_token and self.current_token.get("lexema") != "}":
                        self.statement()
                    self.match_lexema("}")

                fin_func = self.triplos.current_line()
                self.triplos.update_jump(salto_func, fin_func)
                for r_jump in self.return_jumps:
                    self.triplos.update_jump(r_jump, fin_func)
                self.return_jumps = []
            return

        # Declaración múltiple: One $a, $b, $c = 3;
        while self.current_token and self.current_token.get("lexema") != ";":
            if self.current_token.get("tipo") == "ID":
                var_name = self.current_token.get("lexema")
                self.advance()

                # Verificar si hay asignación
                if self.match_lexema("="):
                    self.triplos.reset_temps()
                    temp_result = self.expresion()
                    if temp_result:
                        if not str(temp_result).startswith("T"):
                            t_asig = self.triplos.new_temp()
                            self.triplos.add_triplo(t_asig, temp_result, "=")
                            self.triplos.add_triplo(var_name, t_asig, "=")
                        else:
                            self.triplos.add_triplo(var_name, temp_result, "=")

                # Si hay coma, continuar con la siguiente variable
                if self.match_lexema(","):
                    continue
            else:
                self.advance()

        self.match_lexema(";")

    def asignacion_o_llamada(self):
        var_name = self.current_token.get("lexema")
        self.advance()

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
                if not str(temp_result).startswith("T"):
                    t_asig = self.triplos.new_temp()
                    self.triplos.add_triplo(t_asig, temp_result, "=")
                    self.triplos.add_triplo(var_name, t_asig, "=")
                else:
                    self.triplos.add_triplo(var_name, temp_result, "=")
            
            if self.current_token and self.current_token.get("lexema") == ";":
                self.advance()

    def ciclo_for(self):
        self.advance() 
        self.match_lexema("(")
        
        if self.current_token.get("tipo") == "ID":
            self.asignacion_o_llamada()
        else:
            while self.current_token and self.current_token.get("lexema") != ";":
                self.advance()
            self.match_lexema(";")
            
        self.triplos.reset_temps()
        
        inicio_condicion = self.triplos.current_line()
        saltos_true, saltos_false = [], []
        
        self.procesar_comparacion(saltos_true, saltos_false)
        while self.current_token and self.current_token.get("tipo") == "OP_LOG":
            self.advance()
            self.procesar_comparacion(saltos_true, saltos_false)
        self.match_lexema(";")
        
        inc_pos_start = self.pos
        while self.current_token and self.current_token.get("lexema") != ")":
            self.advance()
        inc_pos_end = self.pos
        self.match_lexema(")")
        
        inicio_bloque = self.triplos.current_line()
        for linea in saltos_true: 
            self.triplos.update_jump(linea, inicio_bloque)
            
        if self.match_lexema("{"):
            while self.current_token and self.current_token.get("lexema") != "}":
                self.statement()
            self.match_lexema("}")
        else:
            self.statement() 
            
        if inc_pos_start < inc_pos_end:
            self.triplos.reset_temps() 
            save_pos = self.pos 
            
            self.pos = inc_pos_start
            self.current_token = self.tokens[self.pos]
            
            self.asignacion_o_llamada() 
            
            self.pos = save_pos
            self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
            
        self.triplos.add_triplo("VACÍO", inicio_condicion, "JMP")
        
        salida = self.triplos.current_line()
        for linea in saltos_false:
            self.triplos.update_jump(linea, salida)

    def ciclo_while(self):
        """Procesa ciclos WHILE: MIENTRAS (cond) { cuerpo }"""
        self.advance()  # Consume WHILE/WHILE_ES
        self.match_lexema("(")

        inicio_condicion = self.triplos.current_line()
        saltos_true, saltos_false = [], []

        # Evaluar condición
        self.procesar_comparacion(saltos_true, saltos_false)
        while self.current_token and self.current_token.get("tipo") == "OP_LOG":
            self.advance()
            self.procesar_comparacion(saltos_true, saltos_false)

        self.match_lexema(")")

        # Backpatch TRUE: el bloque inicia aquí
        inicio_bloque = self.triplos.current_line()
        for linea in saltos_true:
            self.triplos.update_jump(linea, inicio_bloque)

        # Procesar cuerpo
        if self.match_lexema("{"):
            while self.current_token and self.current_token.get("lexema") != "}":
                self.statement()
            self.match_lexema("}")
        else:
            self.statement()

        # Salto incondicional al inicio de la condición
        self.triplos.add_triplo("VACÍO", inicio_condicion, "JMP")

        # Backpatch FALSE: salida del while
        salida = self.triplos.current_line()
        for linea in saltos_false:
            self.triplos.update_jump(linea, salida)

    def ciclo_dowhile(self):
        """Procesa ciclos DO-WHILE: HACER { cuerpo } MIENTRAS (cond)"""
        self.advance()  # Consume DO

        # Guardar posición del inicio del cuerpo (para el salto del WHILE)
        inicio_cuerpo = self.triplos.current_line()

        # Procesar cuerpo del DO
        if self.match_lexema("{"):
            while self.current_token and self.current_token.get("lexema") != "}":
                self.statement()
            self.match_lexema("}")
        else:
            self.statement()

        # Ahora viene el WHILE (cond)
        if self.current_token and self.current_token.get("tipo") in ["WHILE", "WHILE_ES"]:
            self.advance()  # Consume WHILE

        self.match_lexema("(")

        saltos_true, saltos_false = [], []

        # Evaluar condición
        self.procesar_comparacion(saltos_true, saltos_false)
        while self.current_token and self.current_token.get("tipo") == "OP_LOG":
            self.advance()
            self.procesar_comparacion(saltos_true, saltos_false)

        self.match_lexema(")")
        self.match_lexema(";")  # Opcional al final

        # Backpatch TRUE: volver al inicio del cuerpo
        for linea in saltos_true:
            self.triplos.update_jump(linea, inicio_cuerpo)

        # FALSE: continuar después del do-while
        salida = self.triplos.current_line()
        for linea in saltos_false:
            self.triplos.update_jump(linea, salida)

    def condicional_if(self):
        """Procesa condicionales IF: SI (cond) ENTONCES { cuerpo }"""
        self.advance()  # Consume IF
        self.match_lexema("(")

        saltos_true, saltos_false = [], []

        # Evaluar condición
        self.procesar_comparacion(saltos_true, saltos_false)
        while self.current_token and self.current_token.get("tipo") == "OP_LOG":
            self.advance()
            self.procesar_comparacion(saltos_true, saltos_false)

        self.match_lexema(")")

        # Consumir ENTONCES (opcional)
        if self.current_token and self.current_token.get("tipo") == "THEN":
            self.advance()

        # Backpatch TRUE: el bloque inicia aquí
        inicio_bloque = self.triplos.current_line()
        for linea in saltos_true:
            self.triplos.update_jump(linea, inicio_bloque)

        # Procesar cuerpo del IF
        if self.match_lexema("{"):
            while self.current_token and self.current_token.get("lexema") != "}":
                self.statement()
            self.match_lexema("}")
        else:
            self.statement()

        # Backpatch FALSE: salida del if (después del bloque)
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

        if tipo in ["ID", "FUNC", "ENTERO", "REAL", "CADENA"]:
            self.advance()
            # Verificar si es llamada a función: ID seguido de (
            if self.current_token and self.current_token.get("lexema") == "(":
                self.advance()

                # Extraer argumentos para llamadas a función
                args = []
                if self.current_token and self.current_token.get("lexema") != ")":
                    args.append(self.expresion())
                    while self.current_token and self.current_token.get("lexema") == ",":
                        self.advance()
                        args.append(self.expresion())
                self.match_lexema(")")

                # Obtener parámetros formales de la función
                params = self.func_params.get(lexema, [])

                # Generar asignaciones directas a los parámetros formales
                for i, arg in enumerate(args):
                    if i < len(params):
                        param_name = params[i]
                        if arg and not str(arg).startswith("T"):
                            t_asig = self.triplos.new_temp()
                            self.triplos.add_triplo(t_asig, arg, "=")
                            self.triplos.add_triplo(param_name, t_asig, "=")
                        elif arg:
                            self.triplos.add_triplo(param_name, arg, "=")

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
        res = self.expresion()
        
        if res:
            if not str(res).startswith("T"):
                t_ret = self.triplos.new_temp()
                self.triplos.add_triplo(t_ret, res, "=")
                self.triplos.add_triplo("RET", t_ret, "=")
            else:
                self.triplos.add_triplo("RET", res, "=")
                
        if self.current_token and self.current_token.get("lexema") == ";":
            self.advance()
            
        self.return_jumps.append(self.triplos.current_line())
        self.triplos.add_triplo("VACÍO", "PENDIENTE", "JMP")