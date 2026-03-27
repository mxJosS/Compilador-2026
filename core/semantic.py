import re

class SemanticAnalyzer:
    def __init__(self, symbol_table, error_handler):
        self.st = symbol_table
        self.eh = error_handler
        # Pila de scopes: cada scope es un set de nombres declarados en ese nivel
        # scope_stack[0] = global, scope_stack[-1] = scope actual
        self.scope_stack = [set()]  # Inicia con el scope global
        self.funciones_declaradas = {} 
        self.funcion_actual = None
        # Para rastrear la apertura de función (entre declaración y '{')
        self._esperando_llave_funcion = False
        # Profundidad de llaves dentro de la función para manejar for/if anidados
        self._brace_depth_funcion = 0

    def _current_scope(self):
        """Retorna el scope actual (el tope de la pila)."""
        return self.scope_stack[-1]

    def _is_declared_in_current_scope(self, nombre):
        """Verifica si un nombre ya fue declarado en el scope actual."""
        return nombre in self.scope_stack[-1]

    def _is_declared_in_any_scope(self, nombre):
        """Verifica si un nombre fue declarado en cualquier scope (para uso de variables)."""
        for scope in self.scope_stack:
            if nombre in scope:
                return True
        return False

    def _declare_in_current_scope(self, nombre):
        """Declara un nombre en el scope actual."""
        self.scope_stack[-1].add(nombre)

    def _push_scope(self):
        """Crea un nuevo scope (al entrar a una función)."""
        self.scope_stack.append(set())

    def _pop_scope(self):
        """Elimina el scope actual (al salir de una función). No elimina el global."""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def analyze(self, codigo):
        lineas = codigo.split('\n')
        patrones = [
            ('CADENA', '[""\u201c\u201d][^""\u201c\u201d]*[""\u201c\u201d]'),
            ('REAL', r'\b\d+\.\d+\b'),
            ('ENTERO', r'\b\d+\b'),
            ('TIPO', r'\b(?:One|Two|Tree)\b'),
            ('FOR', r'\bfor\b'),
            ('RETURN', r'\b[Rr]eturn\b'),
            ('FUNC', r'\$[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()'),
            ('ID', r'\$[A-Za-z0-9]+'),
            ('PALABRA_ERR', r'[a-zA-ZñÑáéíóúÁÉÍÓÚ_][a-zA-ZñÑáéíóúÁÉÍÓÚ0-9_]*'),
            ('ASIGNACION', r'='),
            ('LLAVE_ABRE', r'\{'),
            ('LLAVE_CIERRA', r'\}'),
        ]
        regex_unida = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in patrones)

        for num_linea, linea in enumerate(lineas, 1):
            tokens_linea = []
            for match in re.finditer(regex_unida, linea):
                tipo_token = match.lastgroup
                lexema = match.group(tipo_token)
                tokens_linea.append((tipo_token, lexema))

            tipo_declaracion = None
            hubo_asignacion = False
            id_izquierdo = None
            hubo_return = False

            for tipo_token, lexema in tokens_linea:
                if tipo_token == 'TIPO':
                    tipo_declaracion = lexema
                
                elif tipo_token == 'RETURN':
                    hubo_return = True

                elif tipo_token == 'LLAVE_ABRE':
                    if self._esperando_llave_funcion:
                        # Entramos al cuerpo de la función → nuevo scope local
                        self._push_scope()
                        self._esperando_llave_funcion = False
                        self._brace_depth_funcion = 1
                    elif self.funcion_actual:
                        # Llave de for/if/while DENTRO de la función
                        self._brace_depth_funcion += 1

                elif tipo_token == 'LLAVE_CIERRA':
                    if self.funcion_actual:
                        self._brace_depth_funcion -= 1
                        if self._brace_depth_funcion == 0:
                            # Es la llave que cierra la función → salir del scope
                            self._pop_scope()
                            self.funcion_actual = None
                        # Si depth > 0, solo se cierra un for/if anidado
                    
                elif tipo_token == 'FUNC':
                    if tipo_declaracion:
                        # Declaración de función
                        if self._is_declared_in_current_scope(lexema):
                            self.eh.add(lexema, num_linea, "Variable duplicada")
                        elif lexema in self.funciones_declaradas:
                            self.eh.add(lexema, num_linea, "Variable duplicada")
                        else:
                            self.funciones_declaradas[lexema] = tipo_declaracion
                            self._declare_in_current_scope(lexema)
                            self.funcion_actual = lexema
                            self._esperando_llave_funcion = True
                    else:
                        if lexema not in self.funciones_declaradas:
                            # Función indefinida
                            self.eh.add(lexema, num_linea, "Función indefinida")
                        elif hubo_asignacion or hubo_return:
                            # Función usada en lado derecho de asignación o return
                            self._verificar_tipo(lexema, id_izquierdo, hubo_return, num_linea, tipo_token)
                            
                elif tipo_token == 'ID':
                    tipo_en_tabla = self._obtener_tipo(lexema)
                    if tipo_declaracion:
                        # Declaración de variable → verificar duplicado SOLO en el scope actual
                        if self._is_declared_in_current_scope(lexema):
                            self.eh.add(lexema, num_linea, "Variable duplicada")
                        else:
                            self._declare_in_current_scope(lexema)
                    else:
                        if not self._is_declared_in_any_scope(lexema) and tipo_en_tabla == "":
                            # Variable indefinida (no fue declarada en ningún scope)
                            self.eh.add(lexema, num_linea, "Variable indefinida")
                        elif hubo_asignacion or hubo_return:
                            # Variable usada en lado derecho → verificar tipo
                            self._verificar_tipo(lexema, id_izquierdo, hubo_return, num_linea, tipo_token)
                    # Solo actualizamos id_izquierdo si estamos ANTES de la asignación
                    if not hubo_asignacion and not hubo_return:
                        id_izquierdo = lexema

                elif tipo_token == 'PALABRA_ERR':
                    self.eh.add(lexema, num_linea, "Variable indefinida (sin $)")

                elif tipo_token == 'ASIGNACION':
                    hubo_asignacion = True
                
                elif tipo_token in ('ENTERO', 'REAL', 'CADENA'):
                    # Literales en lado derecho de asignación o return → verificar tipo
                    if hubo_asignacion or hubo_return:
                        self._verificar_tipo(lexema, id_izquierdo, hubo_return, num_linea, tipo_token)

    def _verificar_tipo(self, lexema, id_izquierdo, hubo_return, num_linea, tipo_token):
        """Verifica compatibilidad de tipos entre un valor y la variable/función destino."""
        tipo_del_id = ""
        
        if hubo_return:
            tipo_del_id = self.funciones_declaradas.get(self.funcion_actual, "")
        else:
            tipo_del_id = self._obtener_tipo(id_izquierdo)
            
        tipo_del_valor = ""
        
        if tipo_token == 'ENTERO': tipo_del_valor = "One"
        elif tipo_token == 'REAL': tipo_del_valor = "Two"
        elif tipo_token == 'CADENA': tipo_del_valor = "Tree"
        elif tipo_token == 'ID': tipo_del_valor = self._obtener_tipo(lexema)
        elif tipo_token == 'FUNC': tipo_del_valor = self.funciones_declaradas.get(lexema, "")
        
        if tipo_del_id and tipo_del_valor and tipo_del_id != tipo_del_valor:
            nombres_tipos = {
                "One": "One (entero)", 
                "Two": "Two (real)", 
                "Tree": "Tree (cadena)"
            }
            tipo_desc = nombres_tipos.get(tipo_del_id, tipo_del_id)
            self.eh.add(lexema, num_linea, f"Incompatibilidad de tipos, {tipo_desc}")

    def _obtener_tipo(self, lexema):
        for sim in self.st.get_all():
            if sim["Lexema"] == lexema:
                return sim["Tipo"].replace("-", "") 
        return ""