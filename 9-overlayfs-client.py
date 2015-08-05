#!/usr/bin/python
import dsstst, subprocess, os, sys, re
overdir='/var/lib/docker/'
print "- start: " + os.path.basename(__file__)
subprocess.call(['modprobe', 'overlay'])
if not os.path.isfile(dsstst.conf_storage):
	sys.exit('- error: ' + dsstst.conf_storage + ' is not found.')
dsstst.check_root()
dsstst.destroy_pool_and_extra_disk()
# Use loopback for testing. The trailing newline sucks!
dev = subprocess.check_output(['losetup', '-f'])[:-1]
if dsstst.debug != 0:
	print 'dev = ' + dev
subprocess.call(['dd', 'if=/dev/zero', 'of=/tmp/dssdisk', 'bs=1M',
	'count=100'])
if subprocess.call(['losetup', '-f', '/tmp/dssdisk']) != 0:
	sys.exit('- error: losetup')
if subprocess.call(['mkfs.xfs', dev]) != 0:
	if dsstst.debug != 0:
		print 'dev = ' + dev
	dsstst.exit_lo(msg='mkfs.xfs', dev=dev)
if subprocess.call(['mount', dev, overdir]) != 0:
	dsstst.exit_lo(msg='mount',dev=dev)
try:
	os.remove(dsstst.conf_storage_setup)
except:
	pass
dsstst.start_docker()
fd = open(dsstst.conf_storage)
lines = fd.readlines()
fd.close()
fd = open(dsstst.conf_storage, 'w')
for line in lines:
	if re.search('DOCKER_STORAGE_OPTIONS.+', line) == None:
		fd.write(line)
	else:
		fd.write('DOCKER_STORAGE_OPTIONS=-s overlay -g ' + overdir)
fd.close()
if subprocess.call(['systemctl', 'restart', 'docker']):
	dsstst.exit_lo_umount(msg='restarting docker.', dev=dev)
out = subprocess.check_output(['docker', 'info'])
if re.search('Storage Driver: overlay', out) == None:
	dsstst.exit_lo_umount(msg='unable to utilize overlayfs.', dev=dev)
subprocess.call(['losetup', '-d', dev])
print "- pass: " + os.path.basename(__file__)
