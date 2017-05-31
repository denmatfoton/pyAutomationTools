import xml.etree.ElementTree as ET


def parseDevice(element, pathStack):
    path = pathStack[0]
    for i in xrange(1, len(pathStack)):
        path += '/' + pathStack[i]

    codes = {}
    for child in element._children:
        if child.tag == 'code' and child.attrib.get('name') is not None:
            codes.update({child.attrib['name']: child.text.strip(' \t\n\r')})

    return {path: codes}


def readDevicesFromXml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    curElem = root
    pathStack = []
    elemStack = []
    numStack = []
    lastStackNum = -1
    devices = {}

    while True:
        if curElem is None:
            if lastStackNum < 0:
                break

            pathStack.pop()
            numStack[lastStackNum] += 1
            elemNum = numStack[lastStackNum]

            if len(elemStack[lastStackNum]._children) > elemNum:
                curElem = elemStack[lastStackNum]._children[elemNum]
            else:
                elemStack.pop()
                numStack.pop()
                lastStackNum -= 1
                continue

        pathStack.append(curElem.attrib['name'])
        if curElem.attrib.get('type') is None:
            if len(curElem._children) > 0:
                elemStack.append(curElem)
                numStack.append(0)
                lastStackNum += 1
                curElem = curElem._children[0]
            else:
                curElem = None
        elif curElem.attrib['type'] == '433RF':
            devices.update(parseDevice(curElem, pathStack))
            curElem = None

    return devices
