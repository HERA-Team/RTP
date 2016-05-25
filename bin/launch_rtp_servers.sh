#!/bin/bash

SESSION=NODES

tmux new-session -d -s $SESSION

##Window/pane setup
tmux new-window -t $SESSION
tmux split-window -v

#top half
tmux select-pane -t 0
tmux split-window -h
tmux select-pane -t 0
tmux split-window -h
tmux select-pane -t 2
tmux split-window -h
tmux select-pane -t 3
tmux split-window -v

#bottom half
tmux select-pane -t 5
tmux split-window -h
tmux select-pane -t 5
tmux split-window -h
tmux select-pane -t 7
tmux split-window -h
tmux select-window -t 8
tmux split-window -v


##NODE setup
tmux select-pane -t 0
tmux send-keys "ssh still1" C-m
tmux send-keys "source activate HERA" C-m
tmux send-keys "~/src/RTP/bin/still.py --server --config_file=/home/obs/src/RTP/etc/rtp_hera_test1.cfg" C-m

tmux select-pane -t 1
tmux send-keys "ssh still2" C-m
tmux send-keys "source activate HERA" C-m
tmux send-keys "~/src/RTP/bin/still.py --server --config_file=/home/obs/src/RTP/etc/rtp_hera_test1.cfg" C-m

#tmux select-pane -t 2
#tmux send-keys "ssh still3" C-m
#tmux send-keys "source activate HERA" C-m
#tmux send-keys "~/src/RTP/bin/still.py --server --config_file=/home/obs/src/RTP/etc/rtp_hera_test1.cfg" C-m
#
#tmux select-pane -t 3
#tmux send-keys "ssh still4" C-m
#tmux send-keys "source activate HERA" C-m
#tmux send-keys "~/src/RTP/bin/still.py --server --config_file=/home/obs/src/RTP/etc/rtp_hera_test1.cfg" C-m

#tmux select-pane -t 4
#tmux send-keys "ssh node04" C-m
#tmux send-keys "source activate PennStill" C-m
#tmux send-keys "~/githubs/still_workflow/bin/still.py --server --config_file=/home/saulkohn/githubs/still_workflow/etc/still_shredder.cfg" C-m
#
#tmux select-pane -t 5
#tmux send-keys "ssh node05" C-m
#tmux send-keys "source activate PennStill" C-m
#tmux send-keys "~/githubs/still_workflow/bin/still.py --server --config_file=/home/saulkohn/githubs/still_workflow/etc/still_shredder.cfg" C-m
#
#tmux select-pane -t 6
#tmux send-keys "ssh node06" C-m
#tmux send-keys "source activate PennStill" C-m
#tmux send-keys "~/githubs/still_workflow/bin/still.py --server --config_file=/home/saulkohn/githubs/still_workflow/etc/still_shredder.cfg" C-m
#
#tmux select-pane -t 7
#tmux send-keys "ssh node07" C-m
#tmux send-keys "source activate PennStill" C-m
#tmux send-keys "~/githubs/still_workflow/bin/still.py --server --config_file=/home/saulkohn/githubs/still_workflow/etc/still_shredder.cfg" C-m
#
#tmux select-pane -t 8
#tmux send-keys "ssh node08" C-m
#tmux send-keys "source activate PennStill" C-m
#tmux send-keys "~/githubs/still_workflow/bin/still.py --server --config_file=/home/saulkohn/githubs/still_workflow/etc/still_shredder.cfg" C-m
#
#tmux select-pane -t 9
#tmux send-keys "ssh node09" C-m
#tmux send-keys "source activate PennStill" C-m
#tmux send-keys "~/githubs/still_workflow/bin/still.py --server --config_file=/home/saulkohn/githubs/still_workflow/etc/still_shredder.cfg" C-m

tmux attach -t NODES
