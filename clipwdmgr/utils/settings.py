# -*- coding: utf-8 -*-

#The MIT License (MIT)
#
#Copyright (c) 2015,2018 Sami Salkosuo
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#

#program settings 

import json
import os

from ..globals import *
from .utils import *


class Settings:

    def getSettingsFile(self):
        return "%s/%s" % (GlobalVariables.CLIPWDMGR_DATA_DIR,CLIPWDMGR_SETTINGS_FILE_NAME)

    def readSettingsFile(self):

        #read JSON file and return dictionary
        settingsFile=self.getSettingsFile()
        if os.path.isfile(settingsFile):
            jsonDict=json.load(open(settingsFile,'r'))
        else:
            jsonDict={}
            #file does not exist
            #get defaults and save
            settingNames=list(SETTING_DEFAULT_VALUES.keys())
            for name in settingNames:
                jsonDict[name]=SETTING_DEFAULT_VALUES[name]
            self.saveSettingsFile(jsonDict)
        
        return jsonDict

    def resetSettings(self):
        jsonDict={}
        #set settings to defaults
        settingNames=list(SETTING_DEFAULT_VALUES.keys())
        for name in settingNames:
            jsonDict[name]=SETTING_DEFAULT_VALUES[name]
        self.saveSettingsFile(jsonDict)

    def saveSettingsFile(self,jsonDict):

        #save json to settings file
        settingsFile="%s/%s" % (GlobalVariables.CLIPWDMGR_DATA_DIR,CLIPWDMGR_SETTINGS_FILE_NAME)
        jsonDict=json.dump(jsonDict,open(settingsFile,'w'), sort_keys=True, indent=4)
        
    def getInt(self,settingName):
        return int(self.get(settingName))

    def getBoolean(self,settingName):
        stringValue=str(self.get(settingName))
        return stringValue.lower() in ("yes","y","true", "on", "t", "1")

    def get(self,settingName):
        settingsDict=self.readSettingsFile()

        #TODO: if seting is columnwidth and another setting autowidth then calculate column
        #width from terminal size

        return settingsDict[settingName]

    def set(self,settingName,settingValue):
        settingsDict=self.readSettingsFile()
        settingsDict[settingName]=settingValue
        self.saveSettingsFile(settingsDict)



