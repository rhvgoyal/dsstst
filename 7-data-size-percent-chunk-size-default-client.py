#!/usr/bin/python
# prerequsites:
# 1. root filesystem is in a VG.
# 2. have free space in root VG to build up a docker pool.
# 3. additional extra disk
import dsstst, os
print "- start: " + os.path.basename(__file__)
dsstst.check_root()
dsstst.destroy_pool_and_extra_disk()
vg=dsstst.get_rootvg()
oldpe = dsstst.oldpe + dsstst.get_freepe(dev = dsstst.base)
dsstst.conf_and_start_docker(conf='DATA_SIZE=80%FREE\nDEVS=' + dsstst.extra)
dsstst.check_chunksize(size=512, vg=vg)
dsstst.check_percent(
	new = dsstst.get_freepe(dsstst.base) + dsstst.get_freepe(dsstst.pextra),
		old = oldpe , percent = 0.8)
print "- pass: " + os.path.basename(__file__)
