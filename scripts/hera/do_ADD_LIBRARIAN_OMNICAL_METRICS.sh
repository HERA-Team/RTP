#! /bin/bash
set -e
#
# example configuration: args = ['onsite', parent_dirs, basename]
#
# first argument is the "connection" -- used to decide how to connect to librarian
# second argument is the path prefix to the local file
# third argument is the file name
#
# Note that the actual file of interest is present in PWD *without* the
# path prefix.
#
# XXX redundant with the other do_*_LIBRARIAN.sh scripts

# import common functions
source _common.sh

conn="$1"
store_path="$2"
basename="$3"

# define polarization
pol1="xx"

fn=$(basename ${basename} uv)

# only upload from the "main" polarization thread
if is_same_pol $fn $pol1; then
    # get ant_metrics filename
    nopol_base=$(remove_pol $fn)
    metrics_f=`echo ${nopol_base}HH.uv.omni.calfits.omni_metrics.json`
    total_path=`echo ${store_path}/${metrics_f}`
    #store_path tells the librarian where the data came within the librarian
    #basename of the store_path is just the filename
    #ie in a librarian path like /data2/stuff/2456789/zen.2456789.34775.uv
    # /data2/stuff is the "store"
    # 2456789/zen.2456789.34775.uv is the store_path
    # zen.2456789.34775.uv is the basename
    echo upload_to_librarian.py ${conn} ${metrics_f} ${total_path}
    upload_to_librarian.py ${conn} ${metrics_f} ${total_path}
fi
