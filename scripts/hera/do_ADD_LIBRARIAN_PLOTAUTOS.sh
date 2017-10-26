#! /bin/bash
set -e
#
# example configuration: args = ['onsite', parent_dirs, basename]
#
# first argument is the "connection" -- used to decide how to connect to librarian
# second argument is the store path prefix
# third argument is the base filename
#
# Note that the actual file of interest is present in PWD *without* the
# path prefix.
#
# XXX redundant with the other do_*_LIBRARIAN.sh scripts

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

conn="$1"
store_path="$2"
basename="$3"

# define polarization
pol1="xx"

fn=$(basename ${basename} uv)

# only upload to the librarian from the "main" thread
if is_same_pol $fn $pol1; then
    # get output filenames
    nopol_base=$(remove_pol $fn)
    autos=`echo ${nopol_base}auto_specs.png`
    pos=`echo ${nopol_base}auto_v_pos.png`
    rxr=`echo ${nopol_base}auto_v_rxr.png`
    rmsx=`echo ${nopol_base}xx.auto_rms_values.png`
    rmsy=`echo ${nopol_base}yy.auto_rms_values.png`

    #store_path tells the librarian where the data came within the librarian
    #basename of the store_path is just the filename
    #ie in a librarian path like /data2/stuff/2456789/zen.2456789.34775.uv
    # /data2/stuff is the "store"
    # 2456789/zen.2456789.34775.uv is the store_path
    # zen.2456789.34775.uv is the basename
    echo upload_to_librarian.py ${conn} ${autos} ${store_path}/${autos}
    upload_to_librarian.py ${conn} ${autos} ${store_path}/${autos}
    echo upload_to_librarian.py ${conn} ${pos} ${store_path}/${pos}
    upload_to_librarian.py ${conn} ${pos} ${store_path}/${pos}
    echo upload_to_librarian.py ${conn} ${rxr} ${store_path}/${rxr}
    upload_to_librarian.py ${conn} ${rxr} ${store_path}/${rxr}
    echo upload_to_librarian.py ${conn} ${rmsx} ${store_path}/${rmsx}
    upload_to_librarian.py ${conn} ${rmsx} ${store_path}/${rmsx}
    echo upload_to_librarian.py ${conn} ${rmsy} ${store_path}/${rmsy}
    upload_to_librarian.py ${conn} ${rmsy} ${store_path}/${rmsy}
fi
