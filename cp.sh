#! /bin/bash
rsync -rvz --exclude '.git' -e "ssh -p 22" ../lib_p_bz bigzhu@follow.center:/home/bigzhu/
rsync -rvz --exclude '.git' -e "ssh -p 22" ./* bigzhu@follow.center:/home/bigzhu/follow_center_p/
