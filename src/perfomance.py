#!/usr/bin/env python
#-*- coding: utf-8 -*-

from vector import Vector2D
from datetime import datetime
from bitarray import bitarray
import random
import math
from math import floor
import copy
import numpy
import itertools

import struct

ran = list(range(1000000))

start = datetime.now()
#  list(map(float, ran))
for i in ran:
    float(i)

print(datetime.now() - start)



import datetime
import math
import hashlib
for i in range(100):

    s = datetime.datetime.now()
    for i in range(100000):
        m = hashlib.sha1()
        m.update(b"Nobody inspects%s")
        m.digest()
    print (datetime.datetime.now() - s)
