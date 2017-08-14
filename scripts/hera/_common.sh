#! /bin/bash
# define commonly used functions

function get_pol ()
# function for extracting polarization string
# assumes the typical file format, and keys in on pattern "zen.xxxxxxx.xxxxx.pp.*",
# returns "pp"
{
    local pol=$(echo $1 | sed -E 's/zen\.[0-9]{7}\.[0-9]{5}\.(..)\.*$/\1/')
    echo "$pol"
}

function remove_pol ()
# function for getting the filename with the polarization string removed
{
    local pol=$(get_pol $1)
    local fn=$(echo $1 | sed -E "s/\.${pol}\././")
    echo $fn
}

function join_by ()
# function for concatenating strings
# from https://stackoverflow.com/questions/1527049/join-elements-of-an-array
# example syntax: (join_by , a b c) -> a,b,c
{
    local IFS="$1"; shift; echo "$*";
}

function is_lin_pol ()
# takes in a file name, and returns 0 if a linear polarization
# (e.g., 'xx'), and 1 if not
{
    local pol=$(get_pol $1)
    if [ ${pol:0:1} == ${pol:1:1} ]; then
        return 0
    else
        return 1
    fi
}

function is_same_pol ()
# takes in a file name, and returns 0 if it matches 2nd argument
# designed to be used to single out particular polarization
{
    local pol=$(get_pol $1)
    if [ ${pol} == $2 ]; then
        return 0
    else
        return 1
    fi
}
function replace_pol ()
# feed in a file name and a polarization, and replace the
# polarization with the provided one
{
    local pol=$(get_pol $1)
    local new_fn=$(echo $1 | sed -E "s/$pol/$2/")
    echo "$new_fn"
}