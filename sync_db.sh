#! /bin/bash
rsync -rvz -e "ssh -p 22"  bigzhu@192.241.201.94:/home/bigzhu/follow_center/p_src/db_bak/* db_bak
