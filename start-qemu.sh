#!/bin/bash
qemu-system-i386 --kernel output/images/bzImage --hda output/images/rootfs.ext2 --hdb sdb.bin --nographic --append "console=ttyS0 root=/dev/sda"

# modprobe sstf-iosched 
# echo sstf > /sys/block/sdb/queue/scheduler
# cat /sys/block/sdb/queue/scheduler