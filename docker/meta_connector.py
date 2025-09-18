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

import os, shutil, sys, time, logging, subprocess, json, multiprocessing, psutil,uuid,datetime

sLogger = None

def raiseException(pMsg):
	sLogger.exception(pMsg)
	raise Exception(pMsg)

def checkEnv(pName, pIsSecret):
	global sLogger
	if (not pName in os.environ) or (os.environ[pName] == ''):
		raiseException('%s env is not set or empty' % pName)
	sLogger.info('%s=%s' % (pName, '***' if pIsSecret else os.environ[pName]))

def cmdToString(pCmd):
	return '"' + str('" "'.join(pCmd)) + '"'
	

def shellExecExceptOnError (cmd, disableException = False):
	stdout = ''
	stderr = ''
	errorCode = 1
	lMsg = ''
	# make sure we have a list
	if type(cmd) is str :
		import shlex
		cmd = shlex.split(cmd)
	
	try :
		proc = subprocess.Popen(cmd, 0, None, None, subprocess.PIPE, subprocess.PIPE)
		out = proc.communicate()
		stdout = out[0].decode('utf-8', errors="ignore")
		stderr = out[1].decode('utf-8', errors="ignore")
		errorCode = proc.returncode
		if proc.returncode != 0:
			lMsg = 'Error executing %s, return %d %s %s' % (cmdToString(cmd),proc.returncode,stdout,stderr)
	except Exception as e:
		lMsg = 'Error executing %s %s' % (cmdToString(cmd),str(e))
		stdout = ''
		stderr = ''
		errorCode = 1
	except :
		lMsg = 'Error executing %s ' % (cmdToString(cmd))
		stdout = ''
		stderr = ''
		errorCode = 1
	if len(lMsg) > 0 and not disableException:
		raiseException(lMsg)
	return (stdout, stderr, errorCode)

def init():
	# ensure that env is properly set
	checkEnv('CONNECTOR_MODE',False)
	
	sLogger.debug('Init cli conf file')
	shellExecExceptOnError(['3dJuumpInfiniteCli','cli','conf','init','--location','.'])
	
	# init/update connector conf
	sLogger.debug('Init/update connector conf')
	lCurrentContent = {}
	if os.path.exists('/connector/_scripts/connector_conf.json'):
		with open('/connector/_scripts/connector_conf.json','r',encoding='utf-8') as fd:
			lCurrentContent = json.load(fd)
	lDefaultValues = {
		'$schema': './connector_conf.schema.json',
		'directoryNickName': 'thedirectory',
		'cacheFolder': '/connector/_cache',
		'infiniteCliExe': '/usr/bin/3dJuumpInfiniteCli',
		'indexer': {
			'serveforever':False,
			'enabledocumentvalidation': True,
			'httpport': 8888
		},
		'maxWorkerCount': multiprocessing.cpu_count(),
		'maxRamMB': round(psutil.virtual_memory().total / (1024*1024))
	}
	
	lNewContent = lDefaultValues | lCurrentContent
	

	with open('/connector/_scripts/connector_conf.json','w',encoding='utf-8') as fd:
		json.dump(lNewContent,fd,indent='\t')

	with open('/connector/_scripts/conf_4_1.json','r',encoding='utf-8') as fd:
		lIsDirectoryRegistered = 'thedirectory' in json.load(fd)['directory_collection']
	
	return (lIsDirectoryRegistered)

def initFolder(pFolderPath : str):
	os.chdir(pFolderPath)
	if not os.path.exists('project_custo.py'):
		sLogger.info('Found a new folder %s, init it' % os.path.split(pFolderPath)[1])
		shutil.copy('/connector/_scripts/prj_tpl/project_custo.py','project_custo.py')

		with open('/connector/_scripts/prj_tpl/project_conf.json.tpl','r',encoding='utf-8') as fd:
			lConf = json.load(fd)
			lConf['$schema'] = '/connector/_scripts/prj_tpl/project_conf.schema.json'
			lConf['projectId'] = 'prj_' + str(uuid.uuid4()).replace('-','')
		with open('project_conf.json','w',encoding='utf-8') as fd:
			json.dump(lConf,fd,indent='\t')

		shutil.copytree('/connector/_scripts/prj_tpl/docs','docs')



sSkipped = set()

def processFolder(pFolderPath : str, pIsDaemon: bool):
	os.chdir(pFolderPath)

	lSuccessMarkerFilePath = os.path.join(pFolderPath,'remove_me_to_trigger_a_processing.txt')
	if os.path.exists(lSuccessMarkerFilePath):
		if not pFolderPath in sSkipped:
			sLogger.debug('"%s" : skip it, remove_me_to_trigger_a_processing.txt is present' % pFolderPath)
		sSkipped.add(pFolderPath)
		return
	if pFolderPath in sSkipped:
		sSkipped.remove(pFolderPath)
	with open(lSuccessMarkerFilePath,'w',encoding='utf-8') as fd:
		fd.write('Remove this file to force reprocessing')

	with open('project_conf.json','r',encoding='utf-8') as fd:
		lProjectId = json.load(fd)['projectId']

	# ensures that projects is created on the directory
	try:
		shellExecExceptOnError(['3dJuumpInfiniteCli','generator','canbuild',lProjectId, 'thedirectory','--ifmissingcreatewithname',os.path.split(pFolderPath)[1]])
	except Exception as e:
		sLogger.warning('Error while calling "generator canbuild" on %s' % pFolderPath)
		sLogger.debug(e)
		return
	
	# call generic connector
	try:
		shellExecExceptOnError(['/connector/_scripts/generic_connector.py','/connector/_scripts/connector_conf.json',pFolderPath])
	except Exception as e:
		sLogger.warning('Got an error while calling generic_connector on %s' % pFolderPath)
		sLogger.debug(e)
		return

if __name__ == '__main__':
	
	lRootFolder = os.path.dirname( os.path.realpath( __file__ ) )
	os.chdir(lRootFolder)

	sLogger = logging.getLogger()
	sLogger.setLevel(logging.INFO)
	sLogger.setLevel(logging.DEBUG)
	
	# install a console handler
	lConsoleHandler = logging.StreamHandler()
	lConsoleHandler.setFormatter(logging.Formatter('%(levelname)-8s | %(message)s'))
	sLogger.addHandler(lConsoleHandler)
	
	# get lock
	(lIsDirectoryRegistered) = init()
	lMode = os.environ['CONNECTOR_MODE']
	if lMode != 'sleep' and not lIsDirectoryRegistered:
		sLogger.warning('"thedirectory" is not registered fallback to sleep mode')
		lMode = 'sleep'
	if lMode == 'sleep' or not lIsDirectoryRegistered:
		sLogger.info('Sleep for ever')
		while True:
			time.sleep(10)
	elif lMode in ['oneshot','daemon']:

		lIsDaemon = lMode == 'daemon'
		sLogger.debug('Check for folder to process ...')
		while True:
			# sLogger.debug('Check for folder to process ...')

			for d in os.listdir('/connector'):
				if d.startswith('_') or not os.path.isdir(os.path.join('/connector',d)):
					continue
				lCurrentWd = os.getcwd()
				lFolderPath = os.path.join('/connector',d)
				initFolder(lFolderPath)
				processFolder(lFolderPath,lIsDaemon)
				os.chdir(lCurrentWd)
			if lIsDaemon:
				time.sleep(2)
			else:
				break
	else:
		raiseException('set CONNECTOR_MODE env with oneOf [sleep, oneshot, daemon ]')
