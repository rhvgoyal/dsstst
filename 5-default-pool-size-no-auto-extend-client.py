#!/usr/bin/python
# prerequsites:
# 1. root filesystem is in a VG.
# 2. have free space in root VG to build up a docker pool.
# 3. only one pv
import dsstst, os, sys
print "- start: " + os.path.basename(__file__)
dsstst.check_root_and_destroy_pool()
# The image used later in fill_pool() is only 10GB in size, so make sure the
# docker pool size is smaller than to avoid running out of the space inside
# the image. 
dsstst.conf_and_start_docker('AUTO_EXTEND_POOL=no\nDATA_SIZE=5GB')
if os.path.isfile(dsstst.profile_extend):
	print >> sys.stderr, '- warn: docker pool extend profile exists.'
# Use 90% for now due to xfs behaviours badly when the pool is full.
dsstst.fill_pool(percent=0.9, expect=0)
print "- pass: " + os.path.basename(__file__)
