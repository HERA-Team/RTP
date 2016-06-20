#! /bin/bash

SESSION=RTP

# Refuse to run if the named session already exists. I'm not
# aware of a better way to do this.

if screen -ls |grep .$SESSION >/dev/null ; then
    echo >&2 "error: a screen session named $SESSION already exists"
    exit 1
fi

cd ~/src/RTP

screen -d -m -S $SESSION
screen -S $SESSION -X hardstatus alwayslastline '%c %H%=%h%=%-Lw%{= BW}%n%f %t%{-}%+Lw'
screen -S $SESSION -X caption splitonly
screen -S $SESSION -p 0 -X title "RTP Client"
screen -S $SESSION -X screen
screen -S $SESSION -p 1 -X title "RTP Servers"
screen -S $SESSION -X screen
screen -S $SESSION -p 2 -X title "Deployment"
screen -S $SESSION -X screen
screen -S $SESSION -p 3 -X title "Monitoring"

newline='
'
screen -S $SESSION -p "RTP Client" -X stuff "source activate HERA$newline"
screen -S $SESSION -p "RTP Client" -X stuff "bin/still.py --config_file=etc/rtp_hera_test1.cfg --client" #$newline"
screen -S $SESSION -p "RTP Servers" -X stuff "source activate HERA$newline"
screen -S $SESSION -p "RTP Servers" -X stuff "bin/launch_rtp_servers.sh" #$newline"
screen -S $SESSION -p "Deployment" -X stuff "source activate HERA$newline"
screen -S $SESSION -p "Monitoring" -X stuff "source activate HERA$newline"

# The "select" command doesn't seem to work in -X mode so we can't magically
# switch back to the Client window. Oh well.
#screen -S $SESSION -X select "RTP Client"
echo "Services launched on screen session $SESSION; attach with \"screen -r $SESSION\"."
