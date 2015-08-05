#!/usr/bin/python
# prerequsites:
# 1. root filesystem is in a VG.
# 2. have free space in root VG to build up a docker pool.
import dsstst, os
print "- start: " + os.path.basename(__file__)
dsstst.check_root()
dsstst.destroy_pool_and_extra_disk()
oldpe = dsstst.get_freepe()
vg=dsstst.get_rootvg()
dsstst.conf_and_start_docker(conf='DATA_SIZE=80%FREE')
dsstst.check_chunksize(size=512, vg=vg)
dsstst.check_percent(new=dsstst.get_freepe(), old=oldpe, percent=0.8)
print "- pass: " + os.path.basename(__file__)
