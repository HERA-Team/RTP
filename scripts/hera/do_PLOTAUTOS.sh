#! /bin/bash
set -e
plot_uv.py -a autos -t 1 --plot_each=time  -o ${1}.autos.png $1
