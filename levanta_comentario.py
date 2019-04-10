#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import filecmp
import subprocess
import sys
import datetime

from filecmp import dircmp
from subprocess import check_output


log_date=datetime.datetime.now().strftime("%Y-%m-%d")

with open('PROGRAMA', 'rt') as f:
    for file in f.read().split('\n'):
            if len(file)==0:
                continue
            try:
                with open('programas/'+file,'r') as f:
                    lines = f.readlines()
                    saida=open('programas/resultado/'+file,'w')
                    for i in lines:
                        print(i)
                        if len(i) > 6 and i[6] == '*':
                            saida.write(i)
                        check_environment = re.search(r'(ENVIRONMENT)',i)
                        if check_environment:
                            continue
                    saida.close()
            except:
                print('Error: {} - {}'.format(file,sys.exc_info()))