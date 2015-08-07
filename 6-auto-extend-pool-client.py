#!/usr/bin/python
# prerequsites:
# 1. root filesystem is in a VG.
# 2. have free space in root VG to build up a docker pool.
import dsstst, os
print "- start: " + os.path.basename(__file__)
dsstst.check_root_and_destroy_pool()
# The image used later in fill_pool() is only 10GB in size, so make sure the
# docker pool size is smaller than to avoid running out of the space inside
# the image.
dsstst.conf_and_start_docker(
	conf='POOL_AUTOEXTEND_THRESHOLD=70\nPOOL_AUTOEXTEND_PERCENT=30\n' +
		'DATA_SIZE=5G')
if dsstst.debug != 0:
	with open(dsstst.profile_extend) as fd:
		print fd.read()
# Let's dd some file inside a container around 80% to trigger the threashold.
dsstst.fill_pool(percent=0.8, expect=-0.3)
print "- pass: " + os.path.basename(__file__)
