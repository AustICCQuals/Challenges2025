# disk-oops

Players are provided with `disk.img.gz` which is a fragmented ext4 filesystem with the first 32KB randomized destroying the superblock.

The flag is stored in a compressed binary with 2MB of random data.

## Solution

The intended solution is to can the file for ext4 metadata and try to piece together the compressed file from the fragments.