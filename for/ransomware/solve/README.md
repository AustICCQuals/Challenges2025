The players are given a ext4 disk image contained the encrypted disk of the system.

The disk image has a top level executable that takes a encryption key and decrypts the manifest if the key is valid.

The key is the SHA256 hash of the key.

The encryption is very weak and uses a repeating XOR cipher so it's vulnerable to a known plaintext attack. Since the manifest starts with a magic value you can xor the cipher bytes with the magic value to get the key.

Breaking SHA256 to get the flag is impractical but luckily the shell captured the flag so it's contained inside `/root/.ash_history`.