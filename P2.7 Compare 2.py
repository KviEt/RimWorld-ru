# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET
import re
import codecs

pathOriginal = r".\Defs"
pathRus = r".\DefInjected"

tagText = ["label", "rulesStrings", "description", "gerund", "verb", "deathMessage", "pawnsPlural", "fixedName", "gerundLabel", "pawnLabel", "labelShort",
    "labelSocial", "stuffAdjective", "labelMale", "labelFemale", "quotation", "formatString", "skillLabel", "customLabel",
      "text", "name", "summary", "jobString", "letterLabelFriendly", "arrivalTextFriendly", "successfullyRemovedHediffMessage",
      "arrivalTextEnemy", "letterLabelEnemy", "labelMechanoids", "recoveryMessage", "baseInspectLine", "beginLetter", "beginLetterLabel",
      "endMessage", "adjective", "reportString", "letterLabel", "letterText", "graphLabelY", "letter", "oldLabel", "labelSolidTended",
      "labelSolidTendedWell", "labelTendedInner", "labelTendedWellInner", "destroyedLabel", "labelTended", "labelTendedWell",
      "destroyedOutLabel", "destroyedLabel", "discoverLetterText", "discoverLetterLabel", "leaderTitle", "helpTexts", "rulesStrings",
           "instantlyOldLabel", "useLabel", "ingestCommandString", "ingestReportString", "Description", "helpText", "rejectInputMessage", "onMapInstruction" 
          ]
allText = {}
allTextValue = {}
allTextExcess = {}

def addElement(fileXML, elementText, text, nameDef):
    if("subSounds" not in elementText):
        if(nameDef not in allText):
            allText[nameDef] = []
        elementsList = allText[nameDef]
        if(elementText not in elementsList):
            elementsList.append(elementText[:])
            allTextValue[elementText] = (text, fileXML)

def findText(element, tagPath, li, fileXML, nameDef, necessary):
    for subElement in element:
        if(subElement.tag in tagText):
            countSubElement = list(subElement)
            if(countSubElement):
                i = 0
                tagPathSub = tagPath + "." + subElement.tag
                for sub2Element in subElement:
                    text = sub2Element.text
                    if(text and necessary):
                        addElement(fileXML, tagPathSub + u"." + str(i), text, nameDef)
                    i = i + 1
            else:
                text = subElement.text
                if(text and necessary):            
                    addElement(fileXML, tagPath + u"." + subElement.tag, text, nameDef)
        else:
            listElement = list(subElement)
            isli = subElement.tag == "li"
            if(listElement):
                if(isli):
                    findText(subElement, (tagPath + u"." + str(li))[:], 0, fileXML, nameDef, necessary)
                else:
                    findText(subElement, (tagPath + u"." + subElement.tag)[:], 0, fileXML, nameDef, necessary)
            if(isli):
                li = li + 1
            text = subElement.text
            if(text):
                expectSTR = re.compile(u"[aA-zZ]+[ \t]+[aA-zZ]")
                result = expectSTR.match(text)
                if(result and text != u"false" and text != u"true"):
                    print tagPath + u"." + subElement.tag + u" значение:"
                    print text

def findDef(root, fileXML):
    for element in root:
        name = element.tag
        if(name[-3:] == u"Def" and name != u"SongDef"):
            abstract = element.get("Abstract")
            if(abstract):
                classAbs = element.get("Name")
                print u"Внимание! Абстрактный класс %s\n"%classAbs
                if(classAbs):
                    tagPath = classAbs
                else:
                    tagPath = "None"
                findText(element, tagPath, 0, fileXML, name, False)
            else:
                defName = element.find("defName")
                if(defName is None):
                    defName = element.find("DefName")
                if(defName is not None):
                    tagPath = defName.text
                    parent = element.get("ParentName")
                    if(parent):
                        findText(element, tagPath, 0, fileXML, name, False)
                    else:
                        findText(element, tagPath, 0, fileXML, name, True)
                else:
                    print u"Внимание! Неожидаемый элемент %s в файле %s"%(element.tag, fileXML)
        else:
            findDef(element, fileXML)
        

def gather(path, fileXML):
    tree = ET.parse(path)
    root = tree.getroot()
    findDef(root, fileXML)
    
def compare(path, nameDef, fileXML):
    tree = ET.parse(path)
    root = tree.getroot()
    for element in root:
        nameElement = element.tag
        if(nameElement in allText[nameDef]):
            allText[nameDef].remove(nameElement)
        else:
            if(fileXML not in allTextExcess):
                allTextExcess[fileXML] = []
            allTextExcess[fileXML].append(nameElement)
    
def findXMLORG(path):
    listOfDir = os.listdir(path)
    for fileXML in listOfDir:
        if ".xml" in fileXML:
            (head, tail) = os.path.split(path)
            gather(os.path.join(path, fileXML), fileXML)
        else:
            subDir = os.path.join(path, fileXML)
            if os.path.isdir(subDir):
                findXMLORG(subDir)

def findXMLRUS(path, nameDef):
    listOfDir = os.listdir(path)
    for fileXML in listOfDir:
        if ".xml" in fileXML:
            compare(os.path.join(path, fileXML), nameDef, fileXML)          

def proofFile(path):
    tree = ET.parse(path)
    root = tree.getroot()
    element = root.find("ThoughtDef/stages")
    i = 0
    for sub in element:
        label = sub.find("label")
        print sub.tag == "li"
        print sub.tag
        if(label is not None):
            print label.text
        print i
        i = i + 1
        

listOfDir = os.listdir(pathOriginal)
for element in listOfDir:
    sub = os.path.join(pathOriginal, element)
    if os.path.isdir(sub): 
        findXMLORG(sub)


listOfDir = os.listdir(pathRus)
for nameDef in listOfDir:
    if(nameDef in allText):
        sub = os.path.join(pathRus, nameDef)
        if os.path.isdir(sub): 
            findXMLRUS(sub, nameDef)
    else:
        print u"Ошибка! Неожидаемый класс %s в переводе"%nameDef

for key in allText.keys():
    allElement = allText[key]
    if(allElement):
        for element in allElement:
            nameFile = allTextValue[element][1]
            print u"\nВ папке %s у файла %s, отсутствует:"%(key, nameFile),
            print u"%s значение: %s"%(element, allTextValue[element][0])

"""Эта проверка не актуальна до тех пор пока скрипт не будет определять абстрактные переменные
for key in allTextExcess.keys():
    print u"\nВ файле %s, не существующие переменные:"%key
    allElement = allTextExcess[key]
    for element in allElement:
        print u"%s"%element"""

txt = codecs.open("Result.txt", "w", "utf-8")
txt.write(u'\ufeff')
for defName in allText:
    if(allText[defName]):
        txt.write(u"В папке %s:\n"%defName)
    for var in allText[defName]:
        txt.write(u"\tТребуется перевести: %s\n"%allTextValue[var][0])
txt.close()
