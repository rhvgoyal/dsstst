import os, sys, re, string, subprocess, time
# Set to non-zero to enable debug.
debug = 1
extra = 'vdb'
pextra = '/dev/' + extra + '1'
# Pv for root VG
base = '/dev/vda2'
# default free PE size for the extra disk.
oldpe = 2559
conf_storage_setup = "/etc/sysconfig/docker-storage-setup"
conf_storage = "/etc/sysconfig/docker-storage"
profile_extend = '/etc/lvm/profile/atomicos--docker-pool-extend.profile'
newvg = "dss-testing-vg"
pool='docker-pool'
def check_root():
	if os.getuid() != 0:
		sys.exit('- error: root is required.')
def check_extra_disk():
	global extra
	pathname = os.path.join("/dev/", extra)
	try:
		os.stat(pathname)
	except:
		sys.exit('- error: no extra disk.')
def check_vg_add(vg):
	global extra
	if get_devvg(dev='/dev/' + extra + '1', args='pvdisplay') != vg:
		sys.exit('- error: new device is not added to the VG.')
def check_pool():
	out = subprocess.check_output(['lvs'])
	match = re.search('docker-pool', out)
	if not match:
		sys.exit('- error: the docker pool is not created.')
def check_root_and_disk():
	check_root()
	check_extra_disk()
# Always make sure old >= new in this call.
def check_percent(new, old, percent):
	global debug
	actual = round((old - new) / float(old), 2)
	if debug != 0:
		print 'check_percent: actual = ' + str(actual)
	if percent + 0.01 < actual or percent - 0.01 > actual:
		sys.exit('- error: default docker pool size is not ' +
			str(percent) + ' of free.')
def check_chunksize(size, vg):
	global debug
	out = subprocess.check_output(['ls', '-l',
		'/dev/' + vg + '/docker-pool'])
	if debug != 0:
		print 'check_chunksize: out = ' + out
	dm=os.path.basename(string.split(out)[10])
	fd = open('/sys/block/' + dm + '/queue/optimal_io_size')
	if int(fd.read()) != size * 1024:
		sys.exit('- error: chunk size is not ' + str(size) + '.')
	fd.close()
def check_vg_and_pool(vg):
	check_vg_add(vg)
	check_pool()
def get_rootvg():
	global debug
	# This rootfs line sucks!
	# rootfs / rootfs rw 0 0
	with file('/proc/mounts') as f:
		s = f.read()
	matches=re.findall(r'.+ / ', s)
	for line in matches:
		dev=string.split(line)[0]
		if dev == 'rootfs':
			continue
		else:
			break
	assert dev
	if debug != 0:
		print sys._getframe().f_code.co_name + ': dev = ' + dev
	vg=get_devvg(dev=dev, args='lvdisplay')
	if not vg:
		sys.exit('- error: root filesystem is not resided in LVM.')
	return vg
# Returns a list of VGs for the docker pool.
def get_poolvg():
	out = subprocess.check_output(['lvs'])
	matches = re.findall(pool + ' \S+', out)
	vg=[]
	for line in matches:
		vg.append(string.split(line)[1])
	return vg
# Return the VG name of the device.
def get_devvg(dev='', args=''):
	try:
		out = subprocess.check_output([args, dev])
	except:
		sys.exit('- error: running ' + args + '.')
	match = re.search(r'VG Name.+', out)
	return string.split(match.group())[2]
# Return the No. of free PE of the device.
def get_freepe(dev):
	global debug
	out = subprocess.check_output(['pvdisplay', dev])
	match = re.search('Free PE.+', out)
	freepe = int(string.split(match.group())[2])
	if debug != 0:
		print 'get_freepe: ' + str(freepe)
	return freepe
# Return the size in GB of the docker pool.
def get_poolsize():
	global debug
	out = subprocess.check_output('lvs')
	match = re.search('docker-pool.+', out)
	size = float(string.split(match.group())[3][:-1])
	if debug != 0:
		print 'get_poolsize: size = ' + str(size)
	return size
# Return the size of a partition.
def get_partsize(dev):
	global debug
	out = subprocess.check_output(['fdisk', '-l', '/dev/' + dev])
	if debug != 0:
		print out
	match = re.search(dev + '2.+', out)
	size = int(string.split(match.group())[3])
	if debug != 0:
		print 'get_partsize: size = ' + str(size)
	return size
def start_docker():
	if subprocess.call(['systemctl', 'start', 'docker']) != 0:
		sys.exit('- error: starting the docker daemon.')
def start_conf_and_check_vg_and_pool(vg='', conf=''):
	conf_and_start_docker(conf)
	check_vg_and_pool(vg)
def conf_and_start_docker(conf):
	global conf_storage_setup
	fd = open(conf_storage_setup, 'w')
	fd.write(conf)
	fd.close()
	start_docker()
def destroy_pool():
	global debug, pool
	run_poolvg_lvremove()
def destroy_extra_disk():
	global extra, newvg
	vg=get_rootvg()
	vgreduce_missing(vg)
	vgreduce_missing(newvg)
	run_cmd(args=['vgreduce', vg, '/dev/' + extra +'1'], force=1)
	run_cmd(args=['vgreduce', newvg, '/dev/' + extra +'1'], force=1)
	run_cmd(args=['vgremove', newvg], force=1)
	run_cmd(args=['pvremove', '/dev/' + extra + '1'], force=1)
	run_cmd(args=['vgchange', '-s', '4M',  vg], force=1)
	# If don't sleep here, fdisk could race without wiping out the
	# partition promptly. Sleep a bit longer to settle down.
	time.sleep(60)
	pipe = subprocess.Popen(['fdisk', '/dev/' + extra],
		stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	pipe.communicate(input='d\nw\n')
def destroy_pool_and_extra_disk():
	subprocess.call(['systemctl', 'stop', 'docker'])
	destroy_pool()
	destroy_extra_disk()
	subprocess.call(['rm -rf /var/lib/docker/*'], shell=True)
def vgreduce_missing(vg):
	fnull = open(os.devnull, 'w')
	subprocess.call(['vgreduce', '--removemissing', vg], stdout=fnull,
			stderr=subprocess.STDOUT, close_fds=True)
def run_cmd(args=[], force=0):
	global debug
	if debug == 0:
		fnull = open(os.devnull, 'w')
		if force != 0:
			try:
				subprocess.call(args, stdout=fnull,
					stderr=subprocess.STDOUT,
					close_fds=True)
			except:
				pass
		else:
			subprocess.call(args, stdout=fnull,
				stderr=subprocess.STDOUT, close_fds=True)
	else:
		if force != 0:
			print 'run_cmd: args = ' + str(args)
			try:
				subprocess.call(args)
			except:
				pass
		else:
			subprocess.call(args)
def run_poolvg_lvremove():
	global debug, extra
	for vg in get_poolvg():
		run_cmd(args=['lvremove', '-f', vg + '/docker-pool'])
def exit_internal(args=sys._getframe().f_code.co_name):
	sys.exit('internal error: ' + args)
def exit_lo(msg, dev):
	subprocess.call(['losetup', '-d', dev])
	sys.exit('- error: ' + msg)
def exit_lo_umount(msg, dev):
	subprocess.call(['umount', dev])
	exit_lo(msg=msg, dev=dev)
def fill_pool(percent, expect):
	subprocess.call(['docker', 'pull', 'rhel7'])
	old = get_poolsize()
	count = int(old * percent * 1024)
	subprocess.call(['docker', 'run', 'rhel7', 'dd', 'if=/dev/zero',
		'of=/dssfile', 'bs=1M', 'count=' + str(count)])
        # Sleep longer to settle down.
	time.sleep(60)
	new = get_poolsize()
	check_percent(new=new, old=old, percent=expect)
def check_root_and_extra_disk_destroy_rootvg():
	check_root_and_disk()
	destroy_pool_and_extra_disk()
def check_root_and_destroy_pool():
	check_root()
	subprocess.call(['systemctl', 'stop', 'docker'])
	destroy_pool()
	subprocess.call(['rm -rf /var/lib/docker/*'], shell=True)
def check_destroy_and_start_all(vg='', conf=''):
	check_root_and_extra_disk_destroy_rootvg()
	start_conf_and_check_vg_and_pool(vg=vg, conf=conf)
