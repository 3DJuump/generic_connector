#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# Copyright (C) converter3dji 2022 AKKA INGENIERIE PRODUIT (support@realfusio.com)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#         http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from converter3dji import *
import sys
import csv
import re
import logging, logging.handlers

class GenericPsCustomizer (PsCustomizer):
	def __init__(self, pLogger, pRemoveInstanciationAndBakeXForms):
		PsCustomizer.__init__(self,pLogger)
		self.__mRemoveInstanciationAndBakeXForms = pRemoveInstanciationAndBakeXForms

	def computeExtractSettings(self, pFileName):
		lRes = PsCustomizer.computeExtractSettings(self,pFileName)
		lRes['removeinstanciationandbakexforms'] = self.__mRemoveInstanciationAndBakeXForms

		return lRes
		
	def processConvResult(self, pDocsMap, pRootId, pSourceFilePath):
		PsCustomizer.processConvResult(self, pDocsMap, pRootId, pSourceFilePath)
	
## MAIN
if __name__ == '__main__':
	# Retrieve arguments
	# Command line: converter.py commandfile.json
	os.chdir(os.path.dirname( os.path.realpath( __file__ ) ))
	sys.path.append(os.path.abspath("."))

	if len(sys.argv) != 2:
		raise Exception('usage generic_connector.py generic_connector.json')
	lJson = None
	with open(sys.argv[1],'r',encoding='utf-8') as f:
		lJson = json.load(f)

	# instanciate logger
	lLogger = logging.getLogger()
	lLogger.setLevel(logging.INFO)
	# install a console handler
	lConsoleHandler = logging.StreamHandler()
	lConsoleHandler.setFormatter(logging.Formatter('%(levelname)-8s | %(message)s'))
	lLogger.addHandler(lConsoleHandler)
	
	# load Converter3dji settings
	lConverterSettings = Converter3djiSettings()
	lConverterSettings.loadFromJson(lJson['converter3dji'])
	lConverterSettings.echo(lLogger)
	if not os.path.isdir(lConverterSettings.cacheFolder):
		os.makedirs(lConverterSettings.cacheFolder)
	
	# install a file handler
	lLogFile = os.path.join(lConverterSettings.cacheFolder, 'conversion.log')
	if os.path.isfile(lLogFile):
		os.unlink(lLogFile)
	lFileHandler = logging.handlers.RotatingFileHandler(lLogFile,maxBytes=128*1024*1024,backupCount=10)
	lFileHandler.setFormatter( logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s'))
	lLogger.addHandler(lFileHandler)
	
	# load PsConverter settings
	lPsConverterSettings = PsConverterSettings()
	lPsConverterSettings.loadFromJson(lJson['psconverter'])
	lPsConverterSettings.echo(lLogger)
	
	# customization
	lPsCustomizer = GenericPsCustomizer(lLogger,lJson['removeinstanciationandbakexforms'])
	lXRefResolver = FileSystemXRefResolver(lJson['rootfolder'],os.path.join(lConverterSettings.cacheFolder,'xrefs.json'),lLogger)
	
	with Converter3dji(lConverterSettings,lPsCustomizer,lXRefResolver,[PsConverter(lPsConverterSettings,lConverterSettings,lLogger)],lLogger) as lConverter:
		
		lDefaultBuildParameters = lConverter.getDefaultBuildParameters(lJson['scalefactortomillimeters'])
		


		# upload confs, annot and attached documents
		lConverter.addDocument('./docs')
		
		# process CatProducts/CatPart
		lRootIds = lConverter.convert([v for v in lXRefResolver ],True)
		
		lDefaultBuildParameters['buildparameters']['rootstructuredocid'] = lRootIds[0]
		lDefaultBuildParameters['buildparameters']['tags'] = lJson['tags']
		lDefaultBuildParameters['buildparameters']['defaultgeometrysettings']['backfaceculling'] = 'none'
		lDefaultBuildParameters['buildparameters']['buildcomment'] = os.path.split(lJson['rootfolder'])[1]
		lConverter.addDocument(lDefaultBuildParameters)

		lConverter.triggerBuild(lDefaultBuildParameters['id'],False)
