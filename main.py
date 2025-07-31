import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

class TreeNode:
    """Clase para representar un nodo del árbol sintáctico"""
    def __init__(self, value, node_type="leaf"):
        self.value = value
        self.node_type = node_type  # leaf, unary, binary
        self.left = None
        self.right = None
        self.children = []  # Para operadores con múltiples operandos
    
    def add_child(self, child):
        """Añade un hijo al nodo"""
        self.children.append(child)
    
    def __str__(self):
        return f"{self.node_type}: {self.value}"

def get_precedence(c):
    """
    Calculate precedence for regex operators.
    Precedences for REs:
    '(' -> 1
    '|' -> 2
    '.' -> 3
    '?' -> 4
    '*' -> 4
    '+' -> 4
    '^' -> 5
    """
    precedence_map = {
        '(': 1,
        '|': 2,
        '.': 3,
        '?': 4,
        '*': 4,
        '+': 4,
        '^': 5
    }
    return precedence_map.get(c, 0)

def preprocess_regex(regex):
    """
    Preprocess regex to handle escaped characters and convert extensions.
    Converts '+' to 'aa*' pattern and '?' to '(a|ε)' pattern.
    """
    result = []
    i = 0
    
    while i < len(regex):
        char = regex[i]
        
        if char == '\\' and i + 1 < len(regex):
            result.append(char)
            result.append(regex[i + 1])
            i += 2
            continue
        else:
            result.append(char)
            i += 1
    
    return ''.join(result)

def format_regex(regex):
    """
    Format regex by adding explicit concatenation operators ('.').
    Properly handles character classes, escaped characters, and multi-character tokens.
    """
    all_operators = ['|', '?', '+', '*', '∗', '^']
    binary_operators = ['^', '|']
    result = []
    
    cleaned_regex = regex.replace(' ', '')
    
    i = 0
    while i < len(cleaned_regex):
        char = cleaned_regex[i]
        
        # Handle escaped characters
        if char == '\\' and i + 1 < len(cleaned_regex):
            next_char = cleaned_regex[i + 1]
            if next_char in ['n', 't', 'r', 's', 'd', 'w']:
                token = char + next_char
                result.append(token)
                i += 2
            elif next_char in ['(', ')', '{', '}', '[', ']', '+', '*', '?', '|', '^', '.']:
                result.append(next_char) 
                i += 2
            else:
                token = char + next_char
                result.append(token)
                i += 2
        elif char == '[':
            j = i + 1
            while j < len(cleaned_regex) and cleaned_regex[j] != ']':
                j += 1
            if j < len(cleaned_regex):
                token = cleaned_regex[i:j+1]
                result.append(token)
                i = j + 1
            else:
                result.append(char)
                i += 1
        elif char == '{':
            j = i + 1
            while j < len(cleaned_regex) and cleaned_regex[j] != '}':
                j += 1
            if j < len(cleaned_regex): 
                token = cleaned_regex[i:j+1]
                result.append(token)
                i = j + 1
            else:
                result.append(char)
                i += 1
        else:
            result.append(char)
            i += 1
    
    final_result = []
    for i in range(len(result)):
        token = result[i]
        final_result.append(token)
        
        # Check if we need to add concatenation operator
        if i + 1 < len(result):
            next_token = result[i + 1]
            
            if (token != '(' and 
                token not in binary_operators and
                next_token != ')' and 
                next_token not in all_operators):
                final_result.append('.')
    
    return ''.join(final_result)

def infix_to_postfix(regex):
    """
    Convert infix regex to postfix using Shunting Yard algorithm.
    """
    postfix = []
    stack = []
    formatted_regex = format_regex(regex)
    operators = {'|', '.', '?', '*', '+', '^'}
    
    for c in formatted_regex:
        if c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            if stack:
                stack.pop()
        elif c in operators:
            # Handle operators
            while (stack and 
                   stack[-1] != '(' and
                   get_precedence(stack[-1]) >= get_precedence(c)):
                postfix.append(stack.pop())
            stack.append(c)
        else:
            postfix.append(c)
    
    # Pop remaining operators from stack
    while stack:
        postfix.append(stack.pop())
    
    return ''.join(postfix)

def postfix_to_syntax_tree(postfix):
    """
    Convierte una expresión en notación postfix a un árbol sintáctico
    """
    stack = []
    operators = {'|', '.', '?', '*', '+', '^'}
    
    for char in postfix:
        if char in operators:
            # Operador unario
            if char in {'*', '+', '?'}:
                if stack:
                    operand = stack.pop()
                    node = TreeNode(char, "unary")
                    node.left = operand
                    stack.append(node)
            # Operador binario
            elif char in {'|', '.', '^'}:
                if len(stack) >= 2:
                    right = stack.pop()
                    left = stack.pop()
                    node = TreeNode(char, "binary")
                    node.left = left
                    node.right = right
                    stack.append(node)
        else:
            # Operando (carácter)
            node = TreeNode(char, "leaf")
            stack.append(node)
    
    return stack[0] if stack else None

def simplify_extensions(tree):
    """
    Simplifica las extensiones '+' y '?' en el árbol
    '+' se convierte en 'aa*'
    '?' se convierte en '(a|ε)'
    """
    if tree is None:
        return None
    
    if tree.node_type == "unary":
        if tree.value == '+':
            # Convertir a+ a aa*
            operand = tree.left
            star_node = TreeNode('*', "unary")
            star_node.left = operand
            
            concat_node = TreeNode('.', "binary")
            concat_node.left = operand
            concat_node.right = star_node
            
            return concat_node
        elif tree.value == '?':
            # Convertir a? a (a|ε)
            operand = tree.left
            epsilon_node = TreeNode('ε', "leaf")
            
            or_node = TreeNode('|', "binary")
            or_node.left = operand
            or_node.right = epsilon_node
            
            return or_node
        else:
            tree.left = simplify_extensions(tree.left)
            return tree
    elif tree.node_type == "binary":
        tree.left = simplify_extensions(tree.left)
        tree.right = simplify_extensions(tree.right)
        return tree
    else:
        return tree

def get_tree_height(node):
    """Calcula la altura del árbol"""
    if node is None:
        return 0
    if node.node_type == "leaf":
        return 1
    elif node.node_type == "unary":
        return 1 + get_tree_height(node.left)
    else:  # binary
        return 1 + max(get_tree_height(node.left), get_tree_height(node.right))

def get_tree_width(node):
    """Calcula el ancho del árbol (número de hojas)"""
    if node is None:
        return 0
    if node.node_type == "leaf":
        return 1
    elif node.node_type == "unary":
        return get_tree_width(node.left)
    else:  # binary
        return get_tree_width(node.left) + get_tree_width(node.right)

def visualize_tree(node, ax, x=0, y=0, width=1):
    """
    Visualiza el árbol sintáctico usando matplotlib
    """
    if node is None:
        return
    
    # Dibujar el nodo actual
    if node.node_type == "leaf":
        color = 'lightblue'
    elif node.node_type == "unary":
        color = 'lightgreen'
    else:  # binary
        color = 'lightcoral'
    
    # Crear caja para el nodo
    box = FancyBboxPatch((x-0.1, y-0.05), 0.2, 0.1,
                        boxstyle="round,pad=0.01",
                        facecolor=color,
                        edgecolor='black',
                        linewidth=1)
    ax.add_patch(box)
    
    # Añadir texto del nodo
    ax.text(x, y, node.value, ha='center', va='center', fontsize=10, fontweight='bold')
    
    if node.node_type == "unary":
        # Nodo unario
        child_x = x
        child_y = y - 0.3
        ax.plot([x, child_x], [y-0.05, child_y+0.05], 'k-', linewidth=1)
        visualize_tree(node.left, ax, child_x, child_y, width)
        
    elif node.node_type == "binary":
        # Nodo binario
        left_width = get_tree_width(node.left)
        right_width = get_tree_width(node.right)
        total_width = left_width + right_width
        
        if total_width > 0:
            left_x = x - (right_width / total_width) * width * 0.5
            right_x = x + (left_width / total_width) * width * 0.5
        else:
            left_x = x - 0.2
            right_x = x + 0.2
            
        child_y = y - 0.3
        
        # Conectar con hijos
        ax.plot([x, left_x], [y-0.05, child_y+0.05], 'k-', linewidth=1)
        ax.plot([x, right_x], [y-0.05, child_y+0.05], 'k-', linewidth=1)
        
        visualize_tree(node.left, ax, left_x, child_y, width * 0.5)
        visualize_tree(node.right, ax, right_x, child_y, width * 0.5)

def print_tree(node, prefix="", is_left=True):
    """
    Imprime el árbol en formato texto
    """
    if node is None:
        return
    
    print(prefix + ("└── " if is_left else "┌── ") + str(node))
    
    if node.node_type == "unary":
        print_tree(node.left, prefix + ("    " if is_left else "│   "), True)
    elif node.node_type == "binary":
        print_tree(node.left, prefix + ("    " if is_left else "│   "), True)
        print_tree(node.right, prefix + ("    " if is_left else "│   "), False)

def read_regex_from_file(filename):
    """
    Read regex from a text file.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def process_regex(regex, index):
    """
    Procesa una expresión regular completa: infix -> postfix -> árbol sintáctico
    """
    print(f"\n{'='*60}")
    print(f"EXPRESIÓN REGULAR #{index}: {regex}")
    print(f"{'='*60}")
    
    # Paso 1: Preprocesamiento
    preprocessed = preprocess_regex(regex)
    print(f"1. Después del preprocesamiento: {preprocessed}")
    
    # Paso 2: Conversión infix a postfix
    postfix = infix_to_postfix(preprocessed)
    print(f"2. Notación postfix: {postfix}")
    
    # Paso 3: Crear árbol sintáctico
    tree = postfix_to_syntax_tree(postfix)
    print(f"3. Árbol sintáctico creado")
    
    # Paso 4: Simplificar extensiones
    simplified_tree = simplify_extensions(tree)
    print(f"4. Extensiones simplificadas")
    
    # Paso 5: Mostrar árbol en texto
    print(f"\n5. Árbol sintáctico (formato texto):")
    print_tree(simplified_tree)
    
    # Paso 6: Visualizar árbol
    print(f"\n6. Visualización del árbol:")
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(-2, 2)
    ax.set_ylim(-get_tree_height(simplified_tree) * 0.4, 0.2)
    ax.set_aspect('equal')
    ax.axis('off')
    
    visualize_tree(simplified_tree, ax, 0, 0, 2)
    plt.title(f'Árbol Sintáctico - Expresión #{index}: {regex}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    
    return simplified_tree

def main():
    """
    Función principal que demuestra el algoritmo completo
    """
    print("ALGORITMO DE CONVERSIÓN: INFIX -> POSTFIX -> ÁRBOL SINTÁCTICO")
    print("="*70)
    
    # Leer directamente desde el archivo expresiones_regulares.txt
    filename = "expresiones_regulares.txt"
    regex_list = read_regex_from_file(filename)
    
    if regex_list is None:
        print(f"Error: No se pudo leer el archivo '{filename}'")
        return
    
    print(f"Leyendo expresiones regulares desde: {filename}")
    print("Expresiones encontradas:")
    for i, regex in enumerate(regex_list, 1):
        print(f"  {i}. {regex}")
    
    # Procesar cada expresión regular
    trees = []
    for i, regex in enumerate(regex_list, 1):
        tree = process_regex(regex, i)
        trees.append(tree)
    
    print(f"\n{'='*70}")
    print("PROCESAMIENTO COMPLETADO")
    print(f"Se procesaron {len(regex_list)} expresiones regulares")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
