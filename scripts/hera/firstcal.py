#! /usr/bin/env python
import capo.hex as hx, capo.arp as arp, capo.red as red, capo.omni as omni
import numpy as n, pylab as p, aipy as a
import sys,optparse

o = optparse.OptionParser()
a.scripting.add_standard_options(o,cal=True,pol=True)
o.add_option('--plot', action='store_true', help='Plot things.')
o.add_option('--ubls', default='', help='Unique baselines to use, separated by commas (ex: 1_4,64_49).')
o.add_option('--ex_ants', default='', help='Antennas to exclude, separated by commas (ex: 1,4,64,49).')
opts,args = o.parse_args(sys.argv[1:])
connection_file=opts.cal
PLOT=opts.plot

def flatten_reds(reds):
    freds = []
    for r in reds:
        freds += r
    return freds

def save_gains(s,f,pol,filename=None,ubls=None,ex_ants=None):
    """
    s: solutions
    f: frequencies
    pol: polarization
    filename: if a specific file was used (instead of many), change output name
    ubls: unique baselines used to solve for s'
    ex_ants: antennae excluded to solve for s'
    """
    s2 = {}
    for k,i in s.iteritems():
        s2[str(k)] = omni.get_phase(f,i)
    if not ubls is None: s2['ubls']=ubls
    if not ex_ants is None: s2['ex_ants']=ex_ants
    if not filename is None:
        outname='%s.fc.npz'%filename
    else:
        outname='fcgains.%s.npz'%pol
    print 'Saving fcgains to %s'%outname
    n.savez(outname,**s2)

def normalize_data(datadict):
    d = {}
    for key in datadict.keys():
        d[key] = datadict[key]/n.where(n.abs(datadict[key]) == 0., 1., n.abs(datadict[key]))
    return d 

    
#hera info assuming a hex of 19 and 128 antennas
aa = a.cal.get_aa(opts.cal, n.array([.150]))
ex_ants = []
ubls = []
for a in opts.ex_ants.split(','):
    try: ex_ants.append(int(a))
    except: pass
for bl in opts.ubls.split(','):
    try:
        i,j = bl.split('_')
        ubls.append((int(i),int(j)))
    except: pass
print 'Excluding Antennas:',ex_ants
if len(ubls) != None: print 'Using Unique Baselines:',ubls
info = omni.aa_to_info(aa, fcal=True, ubls=ubls, ex_ants=ex_ants)
reds = flatten_reds(info.get_reds())
#redstest = infotest.get_reds()#for plotting 

print 'Number of redundant baselines:',len(reds)
#Read in data here.
ant_string =','.join(map(str,info.subsetant))
bl_string = ','.join(['_'.join(map(str,k)) for k in reds])
times, data, flags = arp.get_dict_of_uv_data(args, bl_string, opts.pol, verbose=True)
dataxx = {} #not necessarily xx data inside
for (i,j) in data.keys():
    dataxx[(i,j)] = data[(i,j)][opts.pol]
fqs = n.linspace(.1,.2,203) #XXX
dlys = n.fft.fftshift(n.fft.fftfreq(fqs.size, fqs[1]-fqs[0]))

#gets phase solutions per frequency.
fc = omni.FirstCal(dataxx,fqs,info)
sols = fc.run()

#Save solutions
if len(args)==1: save_gains(sols,fqs, opts.pol, filename=args[0], ubls=ubls, ex_ants=ex_ants)
else: save_gains(sols,fqs, opts.pol, ubls=ubls, ex_ants=ex_ants) 

