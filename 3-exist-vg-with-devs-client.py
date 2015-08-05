#!/usr/bin/python
# Prerequistes:
# 1. root disk is in a VG
# 2. extra unpartitioned block device
import dsstst, os
print "- start: " + os.path.basename(__file__)
vg=dsstst.get_rootvg()
dsstst.check_destroy_and_start_all(vg=vg,
	conf='DEVS=' + dsstst.extra + '\nVG=' + vg)
print "- pass: " + os.path.basename(__file__)
