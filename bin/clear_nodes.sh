#! /bin/bash

echo ssh $1 rm -rf /data/zen*
ssh $1 rm -rf /data/zen*
