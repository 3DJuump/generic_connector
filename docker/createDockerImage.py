#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) createDockerImage.py 2026 AKKODIS INGENIERIE PRODUIT SAS (support@3djuump.com)
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

import os, shutil, sys, re

if __name__ == '__main__':
	lScriptPath = os.path.dirname( os.path.realpath( __file__ ) )
	os.chdir(lScriptPath)
	
	lInfinitePackage = None
	if len(sys.argv) == 2:
		lInfinitePackage = sys.argv[1]
		if not os.path.isabs(lInfinitePackage):
			lInfinitePackage = os.path.realpath(lInfinitePackage)
		assert(os.path.exists(lInfinitePackage))
	while lInfinitePackage is None:
		lInfinitePackage = input('3D Juump Infinite release package (eg : C:/4.0.9.3604-af7956e6cfef0a6a) :')
		if not os.path.exists(os.path.join(lInfinitePackage, 'dist/trixie')):
			print('Invalid folder')
			lInfinitePackage = None
		else:
			break
	# extract infinite version from package name
	lVersion = re.fullmatch('^([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+-[0-9a-z]+).*',os.path.split(lInfinitePackage)[1])
	assert(not lVersion is None)
	lVersion = lVersion.group(1)
	
	sys.path.insert(1, os.path.join(lInfinitePackage,'install form'))

	import infinite # type: ignore

	# copy required files localy
	if os.path.exists('./tmp'):
		shutil.rmtree('./tmp')
	os.makedirs('./tmp')
	for f in os.listdir(os.path.join(lInfinitePackage,'dist/trixie/')):
		if '-cli_' in f or '-migration' in f:
			shutil.copyfile(os.path.join(lInfinitePackage,'dist/trixie',f),'./tmp/'+f)
	shutil.copy(os.path.join(lInfinitePackage,'install form/docker/install_deb_dependencies.sh'),'./tmp/install_deb_dependencies.sh')
	print('Start building docker image, take a break ...')
	os.chdir('..')
	infinite.shellExecExceptOnError(['docker','build','-f', './docker/infinite.generic_connector.Dockerfile','-t', 'infinite.generic_connector:%s' % lVersion, '.'])
