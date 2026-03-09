#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) init.py 2026 AKKODIS INGENIERIE PRODUIT SAS (support@3djuump.com)
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

import os, shutil

if __name__ == '__main__':
	
	for (d,dl,fl) in os.walk('/generic_connector'):
		for f in fl:
			lSrcPath = os.path.join(d,f)
			lRelPath = os.path.relpath(lSrcPath,'/generic_connector')
			lDstPath = os.path.join('/connector/_scripts',lRelPath)
			os.makedirs(os.path.split(lDstPath)[0],exist_ok=True)
			# i have to round mtime some times it contains ms for src path but not for dst path
			if not os.path.exists(lDstPath) or (int(os.path.getmtime(lSrcPath)) > int(os.path.getmtime(lDstPath))):
				print('Copy %s' % (lRelPath))
				shutil.copy2(lSrcPath,lDstPath)
	shutil.copy2('/connector/_scripts/README.md','/connector/README.md')
	