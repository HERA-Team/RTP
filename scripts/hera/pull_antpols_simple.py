#!/usr/bin/env python

import aipy as a
import sys
import optparse
import os
import numpy

o = optparse.OptionParser()
a.scripting.add_standard_options(o, ant=True, pol=True)
opts, args = o.parse_args(sys.argv[1:])


def mfunc(uv, p, d, f):
    i, j = p[2]
    if i in ants and j in ants:
        return p, d, f
    else:
        return p, None, None

ants = map(int, opts.ant.split(','))

for filename in args:
    print filename, '->', filename + 'A'
    uvi = a.miriad.UV(filename)
    if os.path.exists(filename + 'A'):
        print '    File exists... skipping.'
        continue
    uvo = a.miriad.UV(filename + 'A', status='new')
    uvo.init_from_uv(uvi)
    uvo.pipe(uvi, raw=True, mfunc=mfunc,
             append2hist='PULL ANTPOLS:' + ' '.join(sys.argv) + '\n')
