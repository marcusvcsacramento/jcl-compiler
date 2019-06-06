import sys
import io

def sub_string_file(input_file,output_file,original_string,replace_string):
    """Realiza a substituição de uma string em arquivo e tem como output um novo arquivo

    Parâmetros:
    input_file -- Arquivo de Entrada
    output_file -- Arquivo de Saída
    original_string -- String a ser substituída
    replace_string -- Sting para substituição
    """
    result = True
    try:
        with open(input_file, 'rt') as model:
            with open(output_file, 'w+') as final:
                final.write(model.read().replace(original_string,replace_string))
    except:
        result = False
    return result

def sub_string(input_file,original_string,replace_string):
    return io.StringIO(input_file.read().replace(original_string,replace_string))


