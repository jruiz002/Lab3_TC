# Laboratorio 3 - Teoría de la Computación

## Conversión de Expresiones Regulares: Infix → Postfix → Árbol Sintáctico

Este proyecto implementa un algoritmo completo para convertir expresiones regulares desde notación infix a postfix, y luego construir un árbol sintáctico visual.

### Características

- **Algoritmo Shunting Yard**: Conversión de infix a postfix
- **Árbol Sintáctico**: Construcción de árbol a partir de notación postfix
- **Simplificación de Extensiones**: Conversión de `+` y `?` a operadores básicos
- **Visualización**: Dibujo automático del árbol usando matplotlib
- **Lectura de Archivos**: Procesamiento de múltiples expresiones desde archivo

### Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

### Uso

#### Opción 1: Usar ejemplos predefinidos
```bash
python main.py
# Presionar Enter cuando se solicite el nombre del archivo
```


### Formato del Archivo de Entrada

El archivo debe contener una expresión regular por línea:
```
(a* | b*)+
((ε | a) | b*)*
(a | b)* abb (a | b)*
0? (1?)? 0*
```

### Salida del Programa

Para cada expresión regular, el programa muestra:

1. **Preprocesamiento**: Expresión después del preprocesamiento
2. **Notación Postfix**: Conversión usando Shunting Yard
3. **Árbol Sintáctico**: Estructura del árbol en formato texto
4. **Visualización**: Gráfico del árbol sintáctico

### Estructura del Código

- `TreeNode`: Clase para representar nodos del árbol
- `infix_to_postfix()`: Algoritmo Shunting Yard
- `postfix_to_syntax_tree()`: Construcción del árbol
- `simplify_extensions()`: Simplificación de `+` y `?`
- `visualize_tree()`: Visualización gráfica
- `process_regex()`: Procesamiento completo de una expresión

### Ejemplos Incluidos

1. `(a* | b*)+` - Unión de cerraduras de Kleene con extensión +
2. `((ε | a) | b*)*` - Cerradura de Kleene con unión y epsilon
3. `(a | b)* abb (a | b)*` - Patrón con concatenación
4. `0? (1?)? 0*` - Múltiples extensiones anidadas

### Notas Técnicas

- **Extensiones**: `+` se convierte en `aa*`, `?` se convierte en `(a|ε)`
- **Operadores**: Soporte para `|`, `*`, `+`, `?`, `.` (concatenación)
- **Visualización**: Colores diferentes para hojas (azul), unarios (verde), binarios (rojo)
