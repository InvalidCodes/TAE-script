from pyecore.resources.xmi import XMIResource
from pyecore.utils import DynamicEPackage
import uuid
from pyecore.resources import *
import pandas as pd

root_path = str(__file__)[:str(__file__).rfind("/") + 1]


# print(list1)
class Creat_Sequence_Framework:
    def __init__(self):
        self.rset = ResourceSet()
        resource = self.rset.get_resource(URI(root_path + 'testcase.ecore'))
        # print(resource)
        map = self.rset.get_resource(URI(root_path + 'mapping.ecore'))
        # print(map)
        diag = self.rset.get_resource(URI(root_path + 'generator.ecore'))
        self.map_root = map.contents[0]
        # print(self.map_root)
        self.mm_root = resource.contents[0]
        self.diag_root = diag.contents[0]
        self.MyMetamodel = DynamicEPackage(self.mm_root)
        self.map_node = DynamicEPackage(self.map_root)
        self.diag_node = DynamicEPackage(self.diag_root)
        # print(dir(self.MyMetamodel.Variable()))
        # print(dir(self.MyMetamodel))
        # 获取根节点
        self.root = self.map_node.MappingFolder()
        # print(dir(self.map_node.MappingFolder()))
        self.process = self.MyMetamodel.Process()
        self.activitySequence = self.MyMetamodel.ActivitySequence()
        # print(dir(self.activitySequence))
        # print(dir(self.MyMetamodel.EESMappingChannel()))
        self.activitySequence.name = "activitySequence"
        self.startNode = self.MyMetamodel.StartNode()
        self.endNode = self.MyMetamodel.EndNode()
        # 创建子节点，构建序列框架
        self.process.activitySequence = self.activitySequence
        self.process.startNode = self.startNode
        self.process.endNode = self.endNode
        self.group_init = self.MyMetamodel.Group()
        self.group_init.name = 'Initialization'
        self.group_test_step = self.MyMetamodel.Group()
        self.group_test_step.name = 'TestStep ' + '&' + ' Expected Result'
        self.group_clean_up = self.MyMetamodel.Group()
        self.group_clean_up.name = 'Clean Up'
        self.activitySequence.children.append(self.group_init)
        self.activitySequence.children.append(self.group_test_step)
        self.activitySequence.children.append(self.group_clean_up)
        self.list1 = []  # type list

    def save_seq(self, seq_name, save_path):
        res = XMIResource(URI(save_path + '\\{0}.seq'.format(seq_name)), use_uuid=True)
        res.append(self.process)
        res.save()

    def seq_group(self, tc_module, controller):
        if tc_module == 0:
            self.group_init.children.append(controller)
        elif tc_module == 1:
            self.group_test_step.children.append(controller)
        else:
            self.group_clean_up.children.append(controller)

    def map_type(self, variable_type='', variable_name='', path='', deviceName=''):
        # print(sourceMapping)
        # if variable_name in self.list1:
        #     pass
        # else:
        #     self.list1.append(variable_name)
        #     print(self.list1)
        if variable_type == 'Model':
            variable = self.map_node.ModelMapping()
            variable.name = variable_name
            variable.path = path
            variable.dataType = 'VALUE'
            variable.deviceName = deviceName
            variable.enumeration = self.map_node.Enumeration()
            # return variable
        elif variable_type == 'EES':
            variable = self.map_node.EesMapping()
            variable.name = variable_name
            variable.path = str(path)
            variable.deviceName = deviceName
            # return variable
        elif variable_type == 'Measurement':
            variable = self.map_node.MeasurementMapping()
            variable.name = variable_name
            variable.path = str(path)
            variable.deviceName = deviceName
            variable.dataType = 'Scalar'
        return variable


class controller(Creat_Sequence_Framework):
    def __init__(self):
        super().__init__()
        self.list2 = []

    def write(self, sourceMapping='', value='', tc_module='', variable_type='', device='', path=''):
        # print(value)
        write = self.MyMetamodel.Write()
        # print(self.MyMetamodel.Write())
        write.name = 'Write'
        write.sourceMapping = sourceMapping
        # print(sourceMapping)
        write.value = value
        write.accessMode = self.MyMetamodel.AccessMode()
        # print(self.map_type(variable_type, sourceMapping, path, device))
        self.seq_group(tc_module, write)
        # print(self.list2)
        # print(sourceMapping)
        if sourceMapping in self.list2:
            # print(str(self.list2)+'111')
            pass
        else:
            # print(self.list2)
            self.list2.append(sourceMapping)
            self.activitySequence.mappingItems.append(self.map_type(variable_type, sourceMapping, path, device))
            return write

    def creatVariable(self, name, input, output, initial_value):
        var = self.MyMetamodel.Variable()
        var.input = input
        var.output = output
        var.name = name
        var.save = True
        Inv = self.MyMetamodel.NumberVariableValue()
        Inv.value = str(initial_value)
        var.initialValue = Inv
        # self.activitySequence.variables.append(var)
        self.group_test_step.variables.append(var)  # 在testgroup添加变量
        return var

    def read_Compare(self, isfor, tc_module='', save=False, savedvar='', signal='', raster='', operator='',
                     value='', typeOfTolerance='', valueOfTolerance='', Varname='', timeoptions='', timeout='',
                     variable_type='', device='', path=''):
        read = self.MyMetamodel.Read()
        read.name = 'Read'
        if save is True:
            read.save = True
            read.savedvar = savedvar
            variable = self.MyMetamodel.Variable()
            # print(self.MyMetamodel.Variable())
            variable.input = True
            variable.output = True
            variable.name = savedvar
            initial_value = self.MyMetamodel.StringVariableValue()
            initial_value.value = '0'
            variable.initialValue = initial_value
            self.activitySequence.variables.append(variable)
        SignalItem = self.MyMetamodel.SignalItem()
        SignalItem.raster = raster
        SignalItem.signal = signal
        read.sourceSignalItem = SignalItem
        read.accessMode = self.MyMetamodel.AccessMode()
        taeAssert = self.MyMetamodel.IsAssert()
        expectation = self.MyMetamodel.Expectation()
        taeAssert.timeoption = self.MyMetamodel.ExpectationTimeOption()
        if operator is not None:
            expectation.expectationType = self.MyMetamodel.TYPEEXPECTATIONINTERFACE.Number
            expectationModeNumeric = self.MyMetamodel.ExpectationModeNumeric()
            expectationModeNumeric.operator = operator
            expectationModeNumeric.value = value
            if typeOfTolerance is not None and operator == 'Equal':
                expectationModeNumeric.typeOfTolerance = typeOfTolerance
                expectationModeNumeric.valueOfTolerance = valueOfTolerance
            expectation.expectationInterface = expectationModeNumeric
        else:
            expectation.expectationType = self.MyMetamodel.TYPEEXPECTATIONINTERFACE.Null
        if isfor == True:
            read.accessMode.mode = 'TextValue'
            expectation.expectationType = self.MyMetamodel.TYPEEXPECTATIONINTERFACE.PythonExpression
            expectationModePythonExpression = self.MyMetamodel.ExpectationModePythonExpression()
            expectationModePythonExpression.value = '_value_==' + Varname
            expectation.expectationInterface = expectationModePythonExpression
        if timeoptions is not None:
            taeAssert.timeoption.mode = timeoptions
            taeAssert.timeoption.timeout = timeout
        taeAssert.expectation = expectation
        read.taeAssert = taeAssert
        if signal in self.list2:
            # print(str(self.list2)+'111')
            pass
        else:
            # print(self.list2)
            self.list2.append(signal)
            self.activitySequence.mappingItems.append(self.map_type(variable_type, signal, path, device))
        self.seq_group(tc_module, read)
        return read

    def wait(self, tc_module='', time='', unit=''):
        wait = self.MyMetamodel.Wait()
        wait.name = 'Wait'
        wait.time = time
        # wait.unit = self.MyMetamodel.TYPETIMEUNIT.ms
        if unit == 'h':
            wait.unit = self.MyMetamodel.TYPETIMEUNIT.h
        elif unit == 's':
            wait.unit = self.MyMetamodel.TYPETIMEUNIT.s
        elif unit == 'min':
            wait.unit = self.MyMetamodel.TYPETIMEUNIT.min
        else:
            wait.unit = self.MyMetamodel.TYPETIMEUNIT.ms
        self.seq_group(tc_module, wait)
        return wait

    def scriptblock(self, tc_module='', name='', script=''):
        scriptblock = self.MyMetamodel.ScriptBlock()
        scriptblock.name = name
        scriptblock.script = script
        self.seq_group(tc_module, scriptblock)

    def EESConnect(self, tc_module):
        eesConnect = self.MyMetamodel.EESConnect()
        eesConnect.name = 'EES Connect'
        self.seq_group(tc_module, eesConnect)

    def EESConfig(self, tc_module='', variable='', temp='', withload='', variable_type='', path='', deviceName=''):
        eESConfig = self.MyMetamodel.EESConfig()
        eESConfig.name = "EES Config"
        if temp == "OC":
            eESConfig.potential = self.MyMetamodel.POTENTIAL.OC  # 'Normal', 'OC', 'ToVBAT', 'ToGND', 'ToCOM', 'Other'
        elif temp == "ToVBAT":
            eESConfig.porential = self.MyMetamodel.POTENTIAL.ToVBAT
        elif temp == "Normal":
            eESConfig.porential = self.MyMetamodel.POTENTIAL.Normal
        elif temp == "ToGND":
            eESConfig.porential = self.MyMetamodel.POTENTIAL.ToGND
        elif temp == "ToCOM":
            eESConfig.porential = self.MyMetamodel.POTENTIAL.ToCOM
        else:
            eESConfig.porential = self.MyMetamodel.POTENTIAL.Other
        channel = self.MyMetamodel.EESMappingChannel()
        channel.items = variable
        eESConfig.channel.append(channel)
        self.seq_group(tc_module, eESConfig)
        self.map_type(variable_type, variable, path, deviceName)

    def AllActive(self, tc_module):
        eESActivateAll = self.MyMetamodel.EESActivateAll()
        self.seq_group(tc_module, eESActivateAll)

    def AllDeActive(self, tc_module):
        eESDeActivateAll = self.MyMetamodel.EESDeActivateAll()
        self.seq_group(tc_module, eESDeActivateAll)

    def EESDisconnect(self, tc_module):
        eesDisconnect = self.MyMetamodel.EESDeConnect()
        eesDisconnect.name = 'EES DisConnect'
        self.seq_group(tc_module, eesDisconnect)

    def WaitCondition(self, signal='', operator='', value='', timeout=''):
        read = self.MyMetamodel.Read()
        read.name = 'WaitCondition'
        signalItem = self.MyMetamodel.SignalItem()
        signalItem.raster = '100'
        signalItem.signal = signal
        read.sourceSignalItem = signalItem
        accessMode = self.MyMetamodel.AccessMode()
        accessMode.mode = self.MyMetamodel.TYPEACCESSMODE.PhysicalValue
        read.accessMode = accessMode
        isAssert = self.MyMetamodel.IsAssert()
        expectation = self.MyMetamodel.Expectation()
        expectation.expectationType = self.MyMetamodel.TYPEEXPECTATIONINTERFACE.Number
        expectationModeNumeric = self.MyMetamodel.ExpectationModeNumeric()
        expectationModeNumeric.operator = operator
        expectationModeNumeric.value = value
        expectation.expectationInterface = expectationModeNumeric
        isAssert.expectation = expectation
        isAssert.timeoption = self.MyMetamodel.ExpectationTimeOption()
        isAssert.timeoption.mode = "WaitUntilTrue"
        isAssert.timeoption.timeout = str(timeout)
        read.taeAssert = isAssert

    def callLibrary(self, tc_module='', lib_path='', name='', seq_path='', value=''):
        libPath = lib_path
        callSequence = self.MyMetamodel.CallSequence()
        callSequence.name = str(name)
        callSequence.seqPath = str(seq_path)
        self.rset.metamodel_registry[self.mm_root.nsURI] = self.mm_root
        self.rset.metamodel_registry[self.map_root.nsURI] = self.map_root
        res = self.rset.get_resource(URI(libPath))
        lib_root = res.contents[0]
        for b in lib_root.activitySequence.mappingItems:
            callSequence.mappingItems.append(b)
            # print(tc_module)
        for b, val in zip(lib_root.activitySequence.variables, value):
            b.initialValue = self.MyMetamodel.PythonObjectVariableValue()
            b.initialValue.value = val
            callSequence.variables.append(b)
        self.seq_group(tc_module, callSequence)

    def startCapture(self, tc_module, variable_type, variable_name, path, deviceName, Mcvar_name, Mc_path,
                     Mc_deviceName, capture_name):
        startCapture = self.MyMetamodel.StartCapture()
        startCapture.name = 'Start Capture'
        startCapture.captureName = capture_name
        McCapture = self.MyMetamodel.McCapture()
        captureGroup = self.MyMetamodel.CaptureGroup()
        # print(captureGroup)
        modelCapture = self.MyMetamodel.ModelCapture()
        McCapture.captureName = 'McCapture Name'
        McCapture.raster = '10msRStr'
        McCapture.captureId = uuid.uuid1().hex
        modelCapture.captureName = 'Capture Variable'
        modelCapture.captureId = uuid.uuid1().hex
        for var, type1, path1, device in zip(variable_name, variable_type, path, deviceName):
            signal = self.MyMetamodel.SignalItem()
            signal.signal = var
            modelCapture.signals.append(signal)
            # print(var)
            if var in self.list2:
                pass
            else:
                self.activitySequence.mappingItems.append(self.map_type(type1, var, path1, device))
        for var, type1, path1, device in zip(Mcvar_name, variable_type, Mc_path, Mc_deviceName):
            signal = self.MyMetamodel.SignalItem()
            signal.signal = var
            signal.raster = '10msRStr'
            McCapture.signals.append(signal)
            if var in self.list2:
                pass
            else:
                self.activitySequence.mappingItems.append(self.map_type('Measurement', var, path1, device))
        captureGroup.captures.append(modelCapture)
        captureGroup.captures.append(McCapture)
        chartGroup = self.MyMetamodel.ChartGroup()
        chartGroup.refId = modelCapture.captureId
        chartGroupMC = self.MyMetamodel.ChartGroup()
        chartGroupMC.refId = McCapture.captureId
        captureGroup.chartGroup.append(chartGroupMC)
        captureGroup.chartGroup.append(chartGroup)
        self.activitySequence.captureGroup = captureGroup
        self.seq_group(tc_module, startCapture)
        return startCapture

    def stopCapture(self, tc_module, capture_name):
        stopCapture = self.MyMetamodel.StopCapture()
        stopCapture.name = 'Stop Capture'
        stopCapture.captureName = capture_name
        self.seq_group(tc_module, stopCapture)
        return stopCapture

    def addCaptureToReport(self, tc_module, name, var_name, capture_name):
        addCaptureToReport = self.MyMetamodel.AddCaptureToReport()
        addCaptureToReport.name = 'Add Capture To Report'
        addCaptureToReport.captureName = capture_name
        addCaptureToReport.title = 'title'
        plots = self.MyMetamodel.Chart()
        plots.name = f'plot{name}'
        plots.xLabel = 'time(s)'
        for vars in var_name:
            plots.items.append('{0}'.format(vars))
        addCaptureToReport.plots.append(plots)
        self.seq_group(tc_module, addCaptureToReport)
        return addCaptureToReport

    def sendHexService(self, tc_module='', tester_id='', ecu_id='', p_value='', r_value=''):
        sendHexService = self.diag_node.DynamicValueActivity()
        sendHexService.name = 'sendHexService'
        sendHexService.toolType = 'J2534Fake'
        sendHexService.functionName = 'sendHexService'
        input_field1 = self.diag_node.FieldModel()
        input_field1.attrName = 'txId'
        input_field1.attrValue = tester_id
        input_field2 = self.diag_node.FieldModel()
        input_field2.attrName = 'rxId'
        input_field2.attrValue = ecu_id
        input_field3 = self.diag_node.FieldModel()
        input_field3.attrName = 'command'
        input_field3.attrValue = p_value
        output_field = self.diag_node.SaveAndAssertFieldModel()
        output_field.attrName = "result"
        issave = self.MyMetamodel.IsSave()
        output_field.save = issave
        issave.save = True
        issave.savedvar = 'diag_response_variable'
        taeAssert = self.MyMetamodel.IsAssert()
        output_field.taeAssert = taeAssert
        taeAssert.expectation = self.MyMetamodel.Expectation()
        taeAssert.expectation.expectationType = self.MyMetamodel.TYPEEXPECTATIONINTERFACE.PythonExpression
        taeAssert.expectation.expectationInterface = self.MyMetamodel.ExpectationModePythonExpression()
        taeAssert.expectation.expectationInterface.value = r_value
        sendHexService.inputField.append(input_field1)
        sendHexService.inputField.append(input_field2)
        sendHexService.inputField.append(input_field3)
        sendHexService.outputField.append(output_field)
        variable = self.MyMetamodel.Variable()
        variable.input = True
        variable.output = True
        variable.name = 'diag_response_variable'
        initial_value = self.MyMetamodel.PythonObjectVariableValue()
        variable.initialValue = initial_value
        self.activitySequence.variables.append(variable)
        self.seq_group(tc_module, sendHexService)

    def addfor(self, start, stop, step, save, savedvar):
        addfor = self.MyMetamodel.For()
        addfor.name = 'For'
        addfor.start = str(start)
        addfor.stop = str(stop)
        addfor.step = str(step)
        if save:
            addfor.save = True
            addfor.savedvar = savedvar
        self.seq_group(1, addfor)
        return addfor

    def addGroup(self, name, gpitems):
        addGroup = self.MyMetamodel.Group()
        addGroup.name = name
        if type(gpitems) is list:
            for items in gpitems:
                addGroup.children.append(items)
        else:
            addGroup.children.append(gpitems)
        self.seq_group(1, addGroup)
        return addGroup

    def addchart(self, name):
        chart = self.MyMetamodel.Chart()
        chart.name = name
        chart.items.append()


class Sequence_Handler:
    def __init__(self, filepath):
        self.mapfile = pd.read_excel(filepath)
        self.data = self.mapfile.loc[:, ['Name', 'Type', 'Device', 'Target path']]  # 提取特定列
        self.ctrl = controller()

    def finditem(self, name):
        return self.data[self.data['Name'] == name]  # 根据名称查找

    def newvar(self, name, initial_value):
        item = self.ctrl.creatVariable(name, False, True, initial_value)
        return item

    def writeseq(self, name, value, tc_module, txt):
        data = self.finditem(name)
        if data.empty:
            print("'{0}'变量不存在，请检查Mapping文件".format(name))
            text = name + '变量不存在，请检查Mapping文件\n'
            txt.insert('1.0', text)
        item = self.ctrl.write(name, str(value), tc_module, data.values[0, 1], data.values[0, 2], data.values[0, 3])
        return item, data.values[0, 1] == 'Measurement'  # 检测变量类型是否为标定量

    def readseq(self, name, value, operator, tc_module, isfor, varname, timeoptions, timeout, txt):
        data = self.finditem(name)
        # print(data)
        # print(name)
        if data.empty:
            print("'{0}'变量不存在，请检查Mapping文件".format(name))
            text = name + '变量不存在，请检查Mapping文件\n'
            txt.insert('1.0', text)
        item = self.ctrl.read_Compare(isfor, tc_module, False, '', name, '100', operator, str(value), None, '', varname,
                                      timeoptions, str(timeout), data.values[0, 1], data.values[0, 2],
                                      data.values[0, 3])
        return item

    def read_tolerance(self, isfor, varname, name, value, typeofTolerance, percentage, tc_module, timeoptions, timeout,
                       txt):
        data = self.finditem(name)
        if data.empty:
            print("'{0}'变量不存在，请检查Mapping文件".format(name))
            text = name + '变量不存在，请检查Mapping文件\n'
            txt.insert('1.0', text)
        item = self.ctrl.read_Compare(isfor, tc_module, False, '', name, '100', 'Equal', str(value), typeofTolerance,
                                      str(percentage), varname, timeoptions, str(timeout), data.values[0, 1],
                                      data.values[0, 2], data.values[0, 3])
        return item

    def startcapture(self, name, nameMC, capture_name):  # capture_name
        pathlist = []
        pathlistMC = []
        devicelist = []
        devicelistMC = []
        vartypelist = []
        vartypelistMC = []
        for vars in name:
            data = self.finditem(vars)
            pathlist.append(data.values[0, 3])
            devicelist.append(data.values[0, 2])
            vartypelist.append(data.values[0, 1])
        for vars in nameMC:
            data = self.finditem(vars)
            pathlistMC.append(data.values[0, 3])
            devicelistMC.append(data.values[0, 2])
            vartypelistMC.append(data.values[0, 1])
        item = self.ctrl.startCapture(0, vartypelist, name, pathlist, devicelist, nameMC, pathlistMC, devicelistMC,
                                      capture_name)  # capture_name
        return item

    def stopcapture(self, capture_name):
        item = self.ctrl.stopCapture(2, capture_name)
        return item

    def addcapturetoreport(self, name, varset, MCvarset):
        item = self.ctrl.addCaptureToReport(2, name, varset, MCvarset)
        return item

    def callLibrary(self, lib_path, name, seq_path):
        item = self.ctrl.callLibrary(1, lib_path, name, seq_path)  # 0 1 2代表放的位置
        return item

    def group(self, name, gpitems):
        self.ctrl.addGroup(name, gpitems)

    def addFor(self, start, stop, step, save, savedavr):
        item = self.ctrl.addfor(start, stop, step, save, savedavr)
        return item

    def wait(self, time):
        item = self.ctrl.wait(1, str(time), 'ms')
        return item

    def save(self, name, path):
        self.ctrl.save_seq(name, path)


if __name__ == '__main__':
    seq = Creat_Sequence_Framework()
    seq_name = "test"
    save_path = r"D:\replace_file\test"
    seq.save_seq(seq_name, save_path)
