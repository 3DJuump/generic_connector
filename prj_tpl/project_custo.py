#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) project_custo.py 2026 AKKODIS INGENIERIE PRODUIT SAS (support@3djuump.com)
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

from converter3dji import PsCustomizerBase, Converter3dji, FileSystemXRefResolver, XRefResolverInteface
import os, logging
sPrjFolder = os.path.realpath(os.path.dirname( os.path.realpath( __file__ ) ))
sPrjName = os.path.split(sPrjFolder)[1]
sDataFolder = sPrjFolder

class GenericPsCustomizer (PsCustomizerBase):
	def __init__(self, pLogger : logging.Logger):
		PsCustomizerBase.__init__(self,pLogger)

	def computeExtractSettings(self, pFileName):
		lRes = PsCustomizerBase.computeExtractSettings(self,pFileName)
		lRes['fixinvalidxforms'] = 'auto'
		if pFileName.endswith('.fbx'):
			lRes['geometrylevel'] = ['geometryparent']
		elif pFileName.endswith('.model'):
			lRes['geometrylevel'] = ['body']
		return lRes
		
	def processConvResult(self, pDocsMap, pRootId, pSourceFilePath, pAABB):
		PsCustomizerBase.processConvResult(self, pDocsMap, pRootId, pSourceFilePath, pAABB)


def createPsCustomizer(pLogger: logging.Logger, pCacheFolder: str):
	return GenericPsCustomizer(pLogger)


def createXRefSolver(pLogger: logging.Logger, pCacheFolder: str):
	return FileSystemXRefResolver(sDataFolder,os.path.join(pCacheFolder,'xrefs.json'),pLogger)

def convertAndBuild(pLogger: logging.Logger, pConverter:Converter3dji, pCustomizer: PsCustomizerBase, pXRefSolver: XRefResolverInteface ):
	lRootIds = pConverter.convertFiles([v for v in pXRefSolver ],True)
	
	# upload confs, annot and attached documents
	pConverter.addDocument(os.path.join(sPrjFolder,'docs'))

	lDefaultBuildParameters = pConverter.getDefaultBuildParameters()
	lDefaultBuildParameters['rootstructuredocid'] = next(iter(lRootIds.values()))
	lDefaultBuildParameters['tags'] = [sPrjName]
	lDefaultBuildParameters['buildcomment'] = sPrjName
	
	pConverter.triggerBuild(lDefaultBuildParameters,'generic_connector.py')
