
def sub_string_file(input_file,output_file,original_string,replace_string):
    result = True
    try:
        with open(input_file, 'rt') as model:
            with open(output_file, 'w+') as final:
                final.write(model.read().replace(original_string,replace_string))
    except:
        result = False
    return result
