#!/usr/bin/python
# prerequsites:
# 1. root filesystem is in a VG.
# 2. extra unpartitioned block device
import dsstst, os
print "- start: " + os.path.basename(__file__)
# The image used later in fill_pool() is only 10GB in size, so make sure the
# docker pool size is smaller than to avoid running out of the space inside
# the image.
dsstst.check_destroy_and_start_all(vg=dsstst.get_rootvg(),
	conf='DEVS=' + dsstst.extra + '\nDATA_SIZE=5G\n' +
	'POOL_AUTOEXTEND_THRESHOLD=70\nPOOL_AUTOEXTEND_PERCENT=30')
if dsstst.debug != 0 and os.path.isfile(dsstst.profile_extend):
	with open(dsstst.profile_extend) as fd:
		print fd.read()
# Let's dd some file inside a container around 80% to trigger the threashold.
dsstst.fill_pool(percent=0.8, expect=-0.3)
print "- pass: " + os.path.basename(__file__)
