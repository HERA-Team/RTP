#! /bin/bash
set -e
plot_uv.py -a autos -t 1 --plot_each=time  --pretty -o ${1}.autos.png $1
