#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) generic_connector.py 2024 AKKODIS INGENIERIE PRODUIT SAS (support@3djuump.com)
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
#

import sys, os
os.chdir(os.path.dirname( os.path.realpath( __file__ ) ))
sys.path.append(os.path.abspath("."))

from converter3dji import *
import logging, logging.handlers, jsonschema, json

def resolveRelativePath(pPath, pRefPath):
	if os.path.isabs(pPath):
		return os.path.realpath(pPath)
	return os.path.realpath(os.path.join(pRefPath,pPath))

def loadConfiguration(pConnectorConf, pPrjConf):

	with open('./connector_conf.schema.json','r',encoding='utf-8') as fd:
		lConnectorConfSchema = json.load(fd)
		jsonschema.Draft7Validator.check_schema(lConnectorConfSchema)

	with open('./prj_tpl/project_conf.schema.json','r',encoding='utf-8') as fd:
		lPrjConfSchema = json.load(fd)
		jsonschema.Draft7Validator.check_schema(lPrjConfSchema)

	with open(pConnectorConf,'r',encoding='utf-8') as fd:
		lConnectorConf = json.load(fd)
		jsonschema.validate(instance=lConnectorConf, schema=lConnectorConfSchema)
		
	with open(pPrjConf,'r',encoding='utf-8') as fd:
		lPrjConf = json.load(fd)
		jsonschema.validate(instance=lPrjConf, schema=lPrjConfSchema)

	lConverterSettings = Converter3djiSettings()

	lConverterSettings.directoryNickName = lConnectorConf['directoryNickName']
	lConverterSettings.infiniteCliExe = resolveRelativePath(lConnectorConf['infiniteCliExe'],os.path.split(pConnectorConf)[0])

	if 'elasticsearchurl' in lConnectorConf['indexer']:
		lConverterSettings.elasticsearchurl = lConnectorConf['indexer']['elasticsearchurl']
		lConverterSettings.inmemoryindexerserveforever = None
		lConverterSettings.inmemoryindexerenabledocumentvalidation = None
		lConverterSettings.docindexhttpport=None
	else:
		lConverterSettings.elasticsearchurl=None
		lConverterSettings.inmemoryindexerserveforever = lConnectorConf['indexer']['serveforever']
		lConverterSettings.inmemoryindexerenabledocumentvalidation = lConnectorConf['indexer']['enabledocumentvalidation']
		lConverterSettings.docindexhttpport=lConnectorConf['indexer']['httpport']

	lConverterSettings.cacheFolder = os.path.join(
		resolveRelativePath(lConnectorConf['cacheFolder'],os.path.split(pConnectorConf)[0])
		, os.path.splitext(os.path.split(pConnectorConf)[1])[0]
		, os.path.split(os.path.split(pPrjConf)[0])[1])
	
	lConverterSettings.projectId = lPrjConf['projectId']
	lConverterSettings.geometryPoolId = lPrjConf['geometryPoolId'] if not lPrjConf['geometryPoolId']  is None else lConverterSettings.projectId.replace('prj_','geom_')
	lConverterSettings.reprocessCacheErrors = lPrjConf['reprocessCacheErrors']
	lConverterSettings.copyBeforeLoad = lPrjConf['copyBeforeLoad']
	lConverterSettings.reprocessDocFromCache = lPrjConf['reprocessDocFromCache']
	lConverterSettings.forceFileProcessing = lPrjConf['forceFileProcessing']
	lConverterSettings.outputunit=lPrjConf['outputunit']
	lConverterSettings.checkValidity()
	lConverterSettings.echo(lLogger)

	lPsConverterSettings = PsConverterSettings()
	lPsConverterSettings.workerCount = min(lConnectorConf['maxWorkerCount'],multiprocessing.cpu_count())
	if lPrjConf['maxWorkerCount'] > 0:
		lPsConverterSettings.workerCount = min(lPsConverterSettings.workerCount,lPrjConf['maxWorkerCount'])
	lPsConverterSettings.maxRamMB = lConnectorConf['maxRamMB']
	lPsConverterSettings.maxTimePerWorkerSec = lPrjConf['maxTimePerWorkerSec']
	lPsConverterSettings.checkValidity()
	lPsConverterSettings.echo(lLogger)

	return (lConverterSettings,lPsConverterSettings)

## MAIN
if __name__ == '__main__':
	
	if sys.platform == 'win32':
		os.system('chcp 65001')  # Change code page to utf-8 on Windows console
	sys.stdout.reconfigure(encoding='utf-8')
	sys.stderr.reconfigure(encoding='utf-8')

	if len(sys.argv) != 3:
		raise Exception('usage generic_connector.py connector_conf.json prj_folder1 [prj_folder2 ...]')

	lConnectorConfPath = os.path.realpath(os.path.abspath(sys.argv[1]))
	lPrjFolder = os.path.realpath(os.path.abspath(sys.argv[2]))
	
	
	# instanciate logger
	lLogger = logging.getLogger()
	lLogger.setLevel(logging.INFO)
	lLogger.setLevel(logging.DEBUG)
	# install a console handler
	lConsoleHandler = logging.StreamHandler()
	lConsoleHandler.setFormatter(logging.Formatter('%(levelname)-8s | %(message)s'))
	lLogger.addHandler(lConsoleHandler)
	
	lLogger.info('Start processing %s' % lPrjFolder)
	# load configurations
	(lConverterSettings,lPsConverterSettings) = loadConfiguration(lConnectorConfPath, os.path.join(lPrjFolder,'project_conf.json'))

	if not os.path.isdir(lConverterSettings.cacheFolder):
		os.makedirs(lConverterSettings.cacheFolder)

	# install a file handler
	lLogFile = os.path.join(lConverterSettings.cacheFolder, 'conversion.log')
	if os.path.isfile(lLogFile):
		os.unlink(lLogFile)
	lFileHandler = logging.handlers.RotatingFileHandler(lLogFile,maxBytes=128*1024*1024,backupCount=10, encoding = 'UTF-8')
	lFileHandler.setFormatter( logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s'))
	lLogger.addHandler(lFileHandler)

	# load project customization
	sys.path.insert(1,lPrjFolder)
	import project_custo # type: ignore
	lLogger.debug('Create PsCustomizer')
	lPsCustomizer = project_custo.createPsCustomizer(lLogger, lConverterSettings.cacheFolder)
	lLogger.debug('Create XRefSolver')
	lXRefResolver = project_custo.createXRefSolver(lLogger, lConverterSettings.cacheFolder)

	lLogger.debug('Create Converter')
	with Converter3dji(lConverterSettings,lPsCustomizer,lXRefResolver,lPsConverterSettings,[],lLogger) as lConverter:
		lLogger.debug('Start conversion/generation')
		project_custo.convertAndBuild(lLogger,lConverter,lPsCustomizer,lXRefResolver)
		
		