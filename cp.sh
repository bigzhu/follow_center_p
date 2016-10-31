#! /bin/bash
rsync -rvz -e "ssh -p 22" ./* bigzhu@follow.center:/home/bigzhu/follow_center/p_src/
