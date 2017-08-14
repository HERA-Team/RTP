#! /bin/bash
set -e 

for i in 1 2 3 4; do
    echo ssh -t still${i} "sudo rm -rf /data/zen.*.uv{,c,cO,cOR} /data/*bad_ants* /data/*png /data/*ant_metrics* /data/*first.calfits /data/*omni.calfits /data/*stdout_stderr /data/*.uvfits"
    ssh -t still${i} "sudo rm -rf /data/zen.*.uv{,c,cO,cOR} /data/*bad_ants* /data/*png /data/*ant_metrics* /data/*first.calfits /data/*omni.calfits /data/*stdout_stderr /data/*.uvfits"
done
