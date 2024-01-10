import re


def regular_expression(cell_value):
    expression = str(cell_value)
    print("Output Value: ", expression)
    res_str = re.findall("\d+\.?\d*", expression)  # 正则表达式
    # print("Values in Output Value: ", res_str)
    read_value = res_str[0]
    tolerance_mode = res_str[1]
    tolerance_value = res_str[2]
    print("Read Value: ", read_value)
    print("Tolerance Mode: ", tolerance_mode)
    print("Tolerance Value: ", tolerance_value)
    return read_value, tolerance_mode, tolerance_value


def tolerance_mode_string(tol_mode):
    if tol_mode == '0':
        mode = 'Null'
    elif tol_mode == '1':
        mode = 'Absolute'
    elif tol_mode == '2':
        mode = 'Percentage'
    elif tol_mode == '3':
        mode = 'Fractional'
    return mode


