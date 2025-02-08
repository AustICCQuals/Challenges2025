mkdir -p /sys/fs/cgroup/init
xargs -rn1 </sys/fs/cgroup/cgroup.procs >/sys/fs/cgroup/init/cgroup.procs || :
# enable controllers
sed -e 's/ / +/g' -e 's/^/+/' </sys/fs/cgroup/cgroup.controllers \
    >/sys/fs/cgroup/cgroup.subtree_control
# create cgroupv2 for nsjail
mkdir -p /sys/fs/cgroup/nsjail/init
chown -R ctf:ctf /sys/fs/cgroup/nsjail

# delegate controllers
echo '+cpu +memory +pids' >/sys/fs/cgroup/nsjail/cgroup.subtree_control
echo "$$" >/sys/fs/cgroup/nsjail/init/cgroup.procs

exec runuser -u ctf socat tcp-l:1337,fork,reuseaddr exec:./starter.sh
