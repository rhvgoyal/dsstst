#!/usr/bin/python
# Prerequistes:
# 1. root disk is in a VG.
# 2. extra unpartitioned block device
import dsstst, os
print "- start: " + os.path.basename(__file__)
dsstst.check_destroy_and_start_all(vg=dsstst.get_rootvg(),
	conf='DEVS=' + dsstst.extra)
print "- pass: " + os.path.basename(__file__)
