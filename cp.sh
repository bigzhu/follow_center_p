#! /bin/bash
rsync -rvz -e "ssh -p 22" ../lib_p_bz bigzhu@follow.center:/home/bigzhu/
rsync -rvz -e "ssh -p 22" ./* bigzhu@follow.center:/home/bigzhu/follow_center_p/
