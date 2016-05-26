#! /bin/bash
set -e 

for i in 1 2 3 4; do
    echo ssh still${i} "echo rm -rf /data/zen.*.uv{,c} /data/*bad_ants* /data/*png"
    ssh still${i} "rm -rf /data/zen.*.uv{,c} /data/*bad_ants* /data/*png"
done
