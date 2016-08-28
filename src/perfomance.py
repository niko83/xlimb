#!/usr/bin/env python
#-*- coding: utf-8 -*-
from datetime import datetime


ran = list(range(1000000))

start = datetime.now()
#  list(map(float, ran))
a = 0
for i in ran:
    a -=  0.002#i < 500000

print(datetime.now() - start)

