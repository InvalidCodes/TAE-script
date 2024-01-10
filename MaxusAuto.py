import xlrd
import warnings
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from pathlib import Path
from src.build_seq import Sequence_Handler, controller
from src.function import *
from src.function_gui import *

warnings.filterwarnings('ignore')

seq = controller()


def get_path_mapping():
    path1 = tk.filedialog.askopenfile(mode='r', title='选择Mapping文件')
    gui_mapping().delete(0, 'end')
    gui_mapping().insert(0, path1.name)


def get_path_test():
    path2 = tk.filedialog.askopenfile(mode='r', title='选择测试用例')
    gui_test_case().delete(0, 'end')
    gui_test_case().insert(0, path2.name)


def get_path_save():
    path3 = tk.filedialog.askdirectory(title='选择保存路径')
    gui_save().delete(0, 'end')
    gui_save().insert(0, path3)
    return


def get_path_lib():
    path4 = tk.filedialog.askdirectory(title='选择库文件路径')
    gui_library().delete(0, 'end')
    gui_library().insert(0, path4)


def clear_mapping():
    gui_mapping().delete(0, 'end')


def clear_test():
    gui_test_case().delete(0, 'end')


def clear_save():
    gui_save().delete(0, 'end')


def clear_lib():
    gui_library().delete(0, 'end')


def generate():
    # --- 自定义表格内容列数 ---#
    functionality1 = 1  # 一级功能
    functionality2 = 2  # 二级功能
    case_default = 4  # 测试用例名
    test_type_default = 6  # 测试环境s
    command_default = 8  # 输入命令
    input_val_default = 9  # 输入值
    output_var_default = 11  # 变量名称
    operator_default = 12  # 运算符
    output_val_default = 13  # 期望输出值
    output_des_default = 14  # 容差
    result_default = 15  # 输出结果

    cap_var = 'CapVars'
    for_var = 'ForVar'
    capture_name = 'Capture Variable'
    capture_name_mc = 'McCapture Name'

    # --- 参数列表 ---#
    for_mode = 0  # for模式
    flag = False
    count_out_var = 0
    case_len = 1
    hil_cap_list = []  # HIL变量列表
    inca_cap_list = []  # INCA变量列表

    sheet_name = gui_sheet().get()  # 获取测试用例的sheet名
    map_path = gui_mapping().get()
    save_path = gui_save().get()
    case_path = gui_test_case().get()
    clib_path = gui_mapping().get()
    ptr = int(gui_start().get()) - 1
    print("Pointer Initial Position：", ptr)

    rdf = xlrd.open_workbook(case_path).sheet_by_name(sheet_name)
    rows = rdf.nrows

    # 循环遍历工作表中行
    while ptr < rows:
        test_environment = rdf.cell_value(ptr, test_type_default)  # 当前工作表类型，如HIL（从0开始）
        print("当前测试环境：", test_environment)

        # 计算每个测试用例长度
        while rdf.cell_value(ptr + case_len, case_default) == '':  # 测试用例名称为空
            case_len = case_len + 1
        print("当前测试用例长度：", case_len)

        # 环境是HIL且有测试用例名称的每个用例
        if 'HIL' in test_environment and rdf.cell_value(ptr + case_len, case_default) != '':
            seq_name = rdf.cell_value(ptr, case_default)  # 定义序列名
            my_seq = Sequence_Handler(map_path)  # 由mapping生成新的测试用例

            # 从文件读入
            for i in range(ptr + 1, ptr + case_len):
                input_command = rdf.cell_value(i, command_default)  # 写入变量名
                input_val = rdf.cell_value(i, input_val_default)  # 输出变量值
                output_var = rdf.cell_value(i, output_var_default)  # 读出变量名
                operator = rdf.cell_value(i, operator_default)  # 运算符
                output_val = rdf.cell_value(i, output_val_default)  # 检测值
                output_des = rdf.cell_value(i, output_des_default)

                test_result = rdf.cell_value(i, result_default)  # waituntiltrue
                func_lv1 = rdf.cell_value(i, functionality1)  # 一级功能
                func_lv2 = rdf.cell_value(i, functionality2)  # 二级功能

                # 略过功能ID
                if (func_lv1 != '' and seq_name == '') or (func_lv2 != '' and seq_name == ''):
                    pass

                # 开始正文
                else:
                    # Wait功能
                    if input_command == 'wait' and for_mode == 0:
                        my_seq.wait(int(input_val))

                    # Clib功能
                    elif input_command != '' and input_val == 'clib':
                        path1 = clib_path
                        A = path1.find('library')
                        path2 = Path(input_command + '.clib')  # 创建一个路径对象指向clib
                        path3 = path1[A - 1:]
                        path4 = os.path.join(path3, path2)  # 创造完整路径
                        path5 = os.path.join(path1, path2)
                        my_seq.callLibrary(path5, path2, path4)  # 加载clib文件

                    # For功能
                    elif input_command != '' and input_val == 'FOR':
                        for_mode = 1  # 进入循环模式
                        start = str(int(rdf.cell_value(i + 1, 9)))  # FOR循环信息
                        stop = str(int(rdf.cell_value(i + 2, 9)))
                        step = str(int(rdf.cell_value(i + 3, 9)))  # for循环步长
                        my_seq.newvar(cap_var, 0)  # 创建变量
                        my_seq.newvar(for_var, 0)  # 设置变量
                        add_for = my_seq.addFor(start, stop, step, True, for_var)  # 添加FOR模块
                        write, isMC = my_seq.writeseq(input_command, for_var, 1, text)  # isMC检测是否是INCA变量，变量添加到相应列表
                        add_for.children.append(write)  # 写入操作添加到循环
                        if isMC and input_command not in inca_cap_list:  # 放入对应列表
                            inca_cap_list.append(input_command)
                        elif not isMC and input_command not in hil_cap_list:
                            hil_cap_list.append(input_command)

                    # 循环状态
                    elif input_command == '' and output_var != '' and for_mode == 1:
                        if output_des == '' and test_result != '':  # read,延时
                            read = my_seq.readseq(output_var, '', 'Equal', 1, True, for_var, 'WaitUntilTrue',
                                                  test_result,
                                                  text)
                        elif output_des == '' and test_result == '':  # read,非延时
                            read = my_seq.readseq(output_var, '', 'Equal', 1, True, for_var, None, '', text)
                        elif output_des != '' and test_result != '':  # Tol.延时
                            read = my_seq.read_tolerance(True, for_var, output_var, '', 'Percentage', output_des, 1,
                                                         'WaitUntilTrue', test_result, text)
                        else:
                            read = my_seq.read_tolerance(True, for_var, output_var, '', 'Percentage', output_des, 1,
                                                         None,
                                                         '',
                                                         text)
                        add_for.children.append(read)  # 添加Read模块
                        if rdf.cell_value(i + 1, output_var_default) == '':
                            for_mode = 0  # For模式结束(检测列下一行为空白)

                    # 跳过空行
                    elif input_command == '' and output_val == '':
                        continue

                    # 读值
                    elif output_var != '' and for_mode == 0:
                        var_box = ['Equal', 'LessThan', 'LessThanOrEqual', 'GreaterThan', 'GreaterThanOrEqual',
                                   'NotEqual']
                        if operator in var_box:
                            if output_val != '':  # 有读取值
                                read_val, tol_mod, tol_val = regular_expression(output_val)
                                tol_mod_name = tolerance_mode_string(tol_mod)
                                print("Tolerance Mode Name: ", tol_mod_name)
                            else:  # 无读取值
                                tol_mod_name = 'Null'
                        my_seq.read_tolerance(False, '', output_var, read_val, tol_mod_name,
                                              tol_val, 1,
                                              'WaitUntilTrue', test_result, text)

                    # for0
                    elif output_val == '' and '.clib' not in input_command and for_mode == 0:
                        write, isMC3 = my_seq.writeseq(input_command, int(input_val), 1, text)
                        if isMC3 and input_command not in inca_cap_list:  # 添加监测量
                            inca_cap_list.append(input_command)
                        elif not isMC3 and input_command not in hil_cap_list:
                            hil_cap_list.append(input_command)

                    # command=wait，for1
                    elif input_command == 'wait' and for_mode == 1:
                        add_for.children.append(my_seq.wait(int(input_val)))
                    if output_var != '':
                        isMC1 = my_seq.finditem(output_var).values[0, 1] == 'Measurement'  # 添加INCA变量
                        if isMC1 and output_var not in inca_cap_list:
                            inca_cap_list.append(output_var)
                        elif not isMC1 and output_var not in hil_cap_list:
                            hil_cap_list.append(output_var)

            my_seq.startcapture(hil_cap_list, inca_cap_list, capture_name)
            if not inca_cap_list:
                pass
            else:
                my_seq.startcapture(hil_cap_list, inca_cap_list, capture_name_mc)
                my_seq.addcapturetoreport(seq_name, inca_cap_list, capture_name_mc)  # INCA变量绘制
                my_seq.stopcapture(capture_name_mc)
            my_seq.stopcapture(capture_name)
            my_seq.addcapturetoreport(seq_name, hil_cap_list, capture_name)  # HIL变量绘制

            hil_cap_list = []
            inca_cap_list = []
            my_seq.save(seq_name, save_path)  # 保存
            ptr = ptr + case_len  # 下个用例

            if seq_name != '':
                print('用例名称:', seq_name)
                op = '用例名称' + seq_name + '\n'
                text.insert('1.0', op)
                window.update()
            if ptr > rows - 2:
                print('用例生成完毕！')
                text.insert('1.0', '用例生成完毕！\n')
                break
            case_len = 1
        else:
            ptr = ptr + case_len
            if ptr > rows - 2:
                print('用例生成完毕！')
                text.insert('1.0', '用例生成完毕！\n')
                text.insert('1.0', '用例生成完毕！\n')
                break


def gui_mapping():
    label = tk.Label(window, text='Mapping路径:', font=('Consolas', 15))
    label.place(x=20, y=20)
    entry_mapping = tk.Entry(window, bg='black', fg='white', font=('Consolas', 12), width=35)
    entry_mapping.place(x=170, y=25)
    button = tk.Button(window, text='选取Mapping文件', command=get_path_mapping)
    button.place(x=20, y=60)
    button_clear = tk.Button(window, text='清除', command=clear_mapping)
    button_clear.place(x=150, y=60)
    entry_mapping.insert(0, r'C:\Users\zk\Desktop\Mapping文件\Mapping.xlsx')
    return entry_mapping


def gui_test_case():
    label = tk.Label(window, text='TestCase路径:', font=('Consolas', 15))
    label.place(x=20, y=120)
    entry_test_case = tk.Entry(window, bg='black', fg='white', font=('Consolas', 12), width=35)
    entry_test_case.place(x=170, y=125)
    button = tk.Button(window, text='选取TestCase文件', command=get_path_test)
    button.place(x=20, y=160)
    button_clear = tk.Button(window, text='清除', command=clear_test)
    button_clear.place(x=150, y=160)
    entry_test_case.insert(0, r'C:\Users\zk\Desktop\测试用例\LIN.xls')
    return entry_test_case


def gui_sheet():
    label_sheet = tk.Label(window, text='Sheet:', font=('Consolas', 15))
    label_sheet.place(x=200, y=160)
    entry_sheet = tk.Entry(window, bg='grey', fg='white', font=('Consolas', 15), width=10)
    entry_sheet.place(x=270, y=160)
    # entry_sheet.insert(0, 'CTD')
    entry_sheet.insert(0, 'Sheet1')
    return entry_sheet


def gui_library():
    label = tk.Label(window, text='Library路径:', font=('Consolas', 15))
    label.place(x=20, y=220)
    entry_library = tk.Entry(window, bg='black', fg='white', font=('Consolas', 12), width=35)
    entry_library.place(x=170, y=223)
    button = tk.Button(window, text='选取库文件路径', command=get_path_lib)
    button.place(x=20, y=260)
    # print(GetPath3)
    button_clear = tk.Button(window, text='清除', command=clear_lib)
    button_clear.place(x=150, y=260)
    entry_library.insert(0, r'D:\ZCU_HIL_TAE\library')
    return entry_library


def gui_save():
    label = tk.Label(window, text='保存路径:', font=('Consolas', 15))
    label.place(x=20, y=320)
    entry_save = tk.Entry(window, bg='black', fg='white', font=('Consolas', 12), width=35)
    entry_save.place(x=170, y=323)
    button = tk.Button(window, text='选取Seq保存路径', command=get_path_save)
    button.place(x=20, y=360)
    button_clear = tk.Button(window, text='清除', command=clear_save)
    button_clear.place(x=150, y=360)
    entry_save.insert(0, r'C:\Users\zk\Desktop\测试用例\output')
    return entry_save


def gui_start():
    label_start = tk.Label(window, text='Start:', font=('Consolas', 15))
    label_start.place(x=200, y=360)
    entry_start = tk.Entry(window, bg='grey', fg='white', font=('Consolas', 15), width=10)
    entry_start.place(x=270, y=360)
    entry_start.insert(0, 5)
    return entry_start


def gui_generate():
    label = tk.Label(window, text='转换结果:', font=('Consolas', 16))
    label.place(x=20, y=420)
    text_generate = tk.Text(window, font=('Consolas', 10), width=80, height=7)
    text_generate.place(x=20, y=460)
    button = tk.Button(window, text='生成', font=('Consolas', 14), command=generate)
    button.place(x=350, y=410)
    button = tk.Button(window, text='打开生成目录', font=('Consolas', 14), command=open_directory)
    button.place(x=450, y=410)
    return text_generate


def gui():
    gui_mapping()
    gui_test_case()
    gui_sheet()
    gui_library()
    gui_save()
    gui_start()


# --GUI--
window = tk.Tk()
window.title('MAXUS TAE')
window.geometry('640x600')

text = gui_generate()

gui()

logo = ImageTk.PhotoImage(Image.open('./asset/img/logo.png').resize((125, 40)))
tk.Label(window, image=logo).place(x=500, y=5)
window.iconbitmap('./asset/img/icon.ico')
window.mainloop()
