import re


def regular_expression(cell_value):
    expression = str(cell_value)
    print("Output Value: ", expression)
    res_str = re.findall("\d+\.?\d*", expression)  # 正则表达式
    # print("Values in Output Value: ", res_str)
    read_value = res_str[0]
    tolerance_mode = res_str[1]
    if len(res_str) == 3:
        tolerance_value = res_str[2]
    elif len(res_str) == 2:
        tolerance_value = 0
    print("Read Value: ", read_value)
    print("Tolerance Mode: ", tolerance_mode)
    print("Tolerance Value: ", tolerance_value)
    return read_value, tolerance_mode, tolerance_value


def tolerance_num_2_string(tol_mode):
    if tol_mode == '0':
        mode = 'Null'
    elif tol_mode == '1':
        mode = 'Absolute'
    elif tol_mode == '2':
        mode = 'Percentage'
    elif tol_mode == '3':
        mode = 'Fractional'
    return mode


def text_2_script():
    txt = """import api,time
from asyncore import write

#current_value = api.read(local_signal)

objectValue = local_value #跳变阈值
objectSignal = local_signal #跳变信号名
triggerValue = trigger_value #触发信号值
triggerSignal = trigger_signal

cp = api.Capture()

cp.startCapture([objectSignal],'100')
api.write(triggerSignal,triggerValue) #触发条件
time.sleep(10)
cp.stopCapture()
cp.drawChart([objectSignal],'title','plot')

print(cp.time())
print(cp.value(objectSignal))

changelist = []

for i in range(len(cp.value(objectSignal))) and cp.time<3000:
    if cp.value(objectSignal)[i+1]!=cp.value(objectSignal)[i]:
        changelist.append(cp.value(objectSignal)[i+1])
        
outputvalue = changelist[0]
outputsignal = objectSignal"""
    return txt
