#!/usr/bin/python
import dsstst, subprocess, os, sys
print "- start: " + os.path.basename(__file__)
# Storage is already configured with devicemapper driver. Can't configure it
# with overlay driver. To override, remove /etc/sysconfig/docker-storage and
# retry.
dsstst.check_root()
dsstst.destroy_pool_and_extra_disk()
if os.path.isfile(dsstst.conf_storage):
	os.remove(dsstst.conf_storage)
dsstst.conf_and_start_docker(conf='STORAGE_DRIVER=overlay')
subprocess.call(['docker', 'pull', 'rhel7'])
if subprocess.call(['docker', 'run', '--rm', 'rhel7', 'grep',
	'^overlay / overlay rw,', '/etc/mtab']) != 0:
	sys.exit("- error: unable to utilize overlayfs.")
print "- pass: " + os.path.basename(__file__)
