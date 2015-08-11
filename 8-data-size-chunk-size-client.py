#!/usr/bin/python
# prerequsites:
# 1. root filesystem is in a VG.
# 2. have free space in root VG to build up a docker pool.
# 3. additional extra disk
import dsstst, os
print "- start: " + os.path.basename(__file__)
dsstst.check_root()
dsstst.destroy_pool_and_extra_disk()
oldpe = dsstst.get_freepe(dsstst.base) + dsstst.oldpe
# Fill into 70% of free space to trigger auto-extension.
size = str(int(32 * oldpe * 0.7)) + 'MB'
vg=dsstst.get_rootvg()
dsstst.conf_and_start_docker(
	conf='DATA_SIZE=' + size + '\nCHUNK_SIZE=1024\nDEVS=' + dsstst.extra)
dsstst.check_chunksize(size=1024, vg=vg)
dsstst.check_percent(
	new = dsstst.get_freepe(dsstst.base) +
		dsstst.get_freepe(dsstst.pextra), old = oldpe, percent=0.7)
print "- pass: " + os.path.basename(__file__)
