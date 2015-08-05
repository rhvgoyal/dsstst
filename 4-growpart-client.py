#!/usr/bin/python
# prerequsites:
# 1. root filesystem is on the second partion of a disk.
# 2. virtual disk has been enlarged to $offset (5G by default)
# 3. no GROWPART is set at start.
import dsstst, os, sys
offset = 5000000
dev = 'vda'
print "- start: " + os.path.basename(__file__)
dsstst.check_root_and_destroy_pool()
old = dsstst.get_partsize(dev=dev)
dsstst.conf_and_start_docker('GROWPART=true')
if dsstst.get_partsize(dev=dev) - old <= offset:
	sys.exit('- error: partition growing size is unexpected.')
print "- pass: " + os.path.basename(__file__)
