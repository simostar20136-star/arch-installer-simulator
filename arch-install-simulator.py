import time
import sys
import shlex

class ArchInstallerSimulator:
    def __init__(self):
        self.in_chroot = False
        self.running = True
        
        # System State
        self.state = {
            "wifi_connected": False,
            "partitions_created": False,
            "filesystem_created": False,
            "mounted": False,
            "pacstrap_done": False,
            "fstab_generated": False,
            "password_set": False,
            "grub_installed": False,
            "grub_configured": False
        }

    def type_text(self, text, speed=0.02):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(speed)
        print()

    def simulate_delay(self, seconds, message):
        print(message, end="")
        sys.stdout.flush()
        for _ in range(seconds):
            time.sleep(1)
            print(".", end="")
            sys.stdout.flush()
        print(" Done.")

    def installer_guide(self):
        guide = """
=== Arch Linux Installer Guide (Simulation) ===
Follow these commands to complete the simulation:

0. Connect to Wi-Fi:          iwctl (type 'help' inside for commands)
1. Verify connection:         ping archlinux.org
2. Partition the disk:        cfdisk /dev/sda
3. Format the partition:      mkfs.ext4 /dev/sda1
4. Mount the filesystem:      mount /dev/sda1 /mnt
5. Install the base system:   pacstrap -K /mnt base linux linux-firmware
6. Generate fstab:            genfstab -U /mnt >> /mnt/etc/fstab
7. Enter chroot:              arch-chroot /mnt
8. Set root password:         passwd
9. Install bootloader:        pacman -S grub
10. Setup grub:               grub-install /dev/sda
11. Configure grub:           grub-mkconfig -o /boot/grub/grub.cfg
12. Exit chroot:              exit
13. Finish and restart:       reboot
===============================================
"""
        print(guide)

    def run_iwctl(self):
        """Simulates the interactive iwctl prompt."""
        print("Entering interactive iwd prompt. Type 'exit' to leave.")
        while True:
            try:
                cmd = input("[iwd]# ").strip()
                if not cmd:
                    continue
                    
                # Use shlex to properly parse quotes around Wi-Fi names
                parts = shlex.split(cmd)
                
                if cmd in ["exit", "quit"]:
                    break
                elif cmd == "device list":
                    print("                                    Devices                                   ")
                    print("------------------------------------------------------------------------------")
                    print("  Name                Address             Powered   Adapter   Mode      ")
                    print("------------------------------------------------------------------------------")
                    print("  wlan0               00:11:22:33:44:55   on        phy0      station   ")
                elif cmd == "station wlan0 scan":
                    # Scanning is silent in iwctl
                    pass
                elif cmd == "station wlan0 get-networks":
                    print("                               Available networks                             ")
                    print("------------------------------------------------------------------------------")
                    print("  Network name                    Security  Signal")
                    print("------------------------------------------------------------------------------")
                    print("  > Arch network                  psk       ***** ")
                    print("\n  [Tip] If the network name has spaces, enclose it in quotes (\"\").")
                elif parts[0] == "station" and len(parts) >= 4 and parts[2] == "connect":
                    ssid = parts[3]
                    if ssid == "Arch network":
                        print("password of this network is arch (this message will not be shown on the real arch installer)")
                        pwd = input("Passphrase: ")
                        self.simulate_delay(2, f"Authenticating and connecting to '{ssid}'")
                        if pwd == "arch":
                            self.state["wifi_connected"] = True
                            print(f"Connected to '{ssid}' successfully.")
                        else:
                            print("Operation failed")
                    else:
                        print(f"Network '{ssid}' not found. Type 'station wlan0 get-networks' to see available networks.")
                elif cmd == "help":
                    print("Simulated commands:")
                    print("  device list")
                    print("  station wlan0 scan")
                    print("  station wlan0 get-networks")
                    print("  station wlan0 connect <network> (use \"\" if name has spaces!)")
                    print("  exit")
                else:
                    print("Invalid command or not implemented in simulator. Type 'help'.")
            except ValueError:
                print("Error: Unmatched quote. Make sure to close your \"\" quotes.")
            except KeyboardInterrupt:
                print()
                break

    def process_command(self, cmd_str):
        if not cmd_str:
            return

        try:
            parts = shlex.split(cmd_str)
            cmd = parts[0]
        except ValueError:
            print("bash: syntax error: unmatched quote")
            return

        # --- Custom Simulator Commands ---
        if cmd == "installer_guide":
            self.installer_guide()
            return
        elif cmd in ["clear", "cls"]:
            print("\033[H\033[J", end="")
            return

        # --- Real Arch Commands ---
        elif cmd == "iwctl":
            if self.in_chroot:
                print("iwctl: command not found (you are in chroot)")
            else:
                self.run_iwctl()

        elif cmd == "ping":
            if not self.state["wifi_connected"]:
                print("ping: archlinux.org: Temporary failure in name resolution")
            else:
                print("PING archlinux.org (95.216.194.52) 56(84) bytes of data.")
                print("64 bytes from archlinux.org: icmp_seq=1 ttl=54 time=14.2 ms")
                print("64 bytes from archlinux.org: icmp_seq=2 ttl=54 time=13.8 ms")
                print("^C\n--- archlinux.org ping statistics ---\n2 packets transmitted, 2 received, 0% packet loss")
        
        elif cmd in ["cfdisk", "fdisk", "cgdisk"] and "/dev/sda" in cmd_str:
            self.type_text("Opening partitioning tool...")
            self.simulate_delay(2, "Writing partition table")
            self.state["partitions_created"] = True
            print("Syncing disks...")
            
        elif cmd.startswith("mkfs.ext4") and "/dev/sda1" in cmd_str:
            if not self.state["partitions_created"]:
                print("Error: /dev/sda1 does not exist. Run cfdisk /dev/sda first.")
                return
            self.type_text("mke2fs 1.47.0 (5-Feb-2023)")
            self.type_text("Creating filesystem with 5242880 4k blocks and 1310720 inodes")
            self.simulate_delay(2, "Writing inode tables")
            self.type_text("Writing superblocks and filesystem accounting information... done")
            self.state["filesystem_created"] = True
            
        elif cmd == "mount" and "/dev/sda1" in cmd_str and "/mnt" in cmd_str:
            if not self.state["filesystem_created"]:
                print("mount: /mnt: wrong fs type, bad option, bad superblock on /dev/sda1.")
                return
            self.state["mounted"] = True
            print("Mounted /dev/sda1 on /mnt")
            
        elif cmd.startswith("pacstrap") and "/mnt" in cmd_str:
            if not self.state["wifi_connected"]:
                print("==> ERROR: Failed to download packages. Could not resolve host: mirrors.kernel.org")
                return
            if not self.state["mounted"]:
                print("Error: /mnt is not a mountpoint.")
                return
            print("==> Creating install root at /mnt")
            self.simulate_delay(3, "==> Installing packages to /mnt")
            self.type_text("(1/3) installing base...", speed=0.01)
            self.type_text("(2/3) installing linux...", speed=0.01)
            self.type_text("(3/3) installing linux-firmware...", speed=0.01)
            self.state["pacstrap_done"] = True
            print("==> Pacstrap complete.")
            
        elif cmd.startswith("genfstab") and "/mnt" in cmd_str:
            if not self.state["mounted"]:
                print("Error: nothing mounted.")
                return
            if ">>" in cmd_str:
                self.state["fstab_generated"] = True
                print("[Simulator] fstab appended to /mnt/etc/fstab")
            else:
                print("# /dev/sda1\nUUID=xxxx-xxxx-xxxx-xxxx\t/mnt\text4\trw,relatime\t0 1")

        elif cmd == "arch-chroot" and "/mnt" in cmd_str:
            if not self.state["pacstrap_done"]:
                print("chroot: failed to run command ‘/bin/bash’: No such file or directory")
                return
            self.in_chroot = True
            print("Switched to /mnt chroot environment.")
            
        elif cmd == "passwd":
            if not self.in_chroot:
                print("Changing password for root.")
            pwd = input("New password: ")
            pwd2 = input("Retype new password: ")
            if pwd == pwd2:
                self.state["password_set"] = True
                print("passwd: password updated successfully")
            else:
                print("passwd: Authentication token manipulation error")
                
        elif cmd.startswith("pacman") and "-S" in cmd_str:
            if not self.state["wifi_connected"]:
                print("error: failed retrieving file... Could not resolve host")
                return
            pkg = parts[-1]
            print(f"resolving dependencies...\nlooking for conflicting packages...\nPackages (1) {pkg}-1.0-1")
            self.simulate_delay(2, f"Installing {pkg}")
            
        elif cmd == "grub-install" and "/dev/sda" in cmd_str:
            if not self.in_chroot:
                print("grub-install: error: failed to get canonical path of `/boot/grub`.")
                return
            self.simulate_delay(3, "Installing for i386-pc platform")
            self.state["grub_installed"] = True
            print("Installation finished. No error reported.")
            
        elif cmd == "grub-mkconfig" and "-o" in cmd_str:
            if not self.in_chroot:
                print("/usr/bin/grub-mkconfig: line 262: /boot/grub/grub.cfg.new: No such file or directory")
                return
            print("Generating grub configuration file ...")
            self.simulate_delay(1, "Found linux image: /boot/vmlinuz-linux")
            self.simulate_delay(1, "Found initrd image: /boot/initramfs-linux.img")
            self.state["grub_configured"] = True
            print("done")
            
        elif cmd == "exit":
            if self.in_chroot:
                self.in_chroot = False
                print("exit")
            else:
                self.running = False
                
        elif cmd == "reboot":
            if self.in_chroot:
                print("Running in chroot, ignoring request.")
            else:
                if all(self.state.values()):
                    print("\n[SUCCESS] Arch Linux installed successfully! Rebooting simulator...\n")
                    print("After this, you would normally reboot your PC. However, since this is a simulation,")
                    print("I am going to tell you directly what happens next: you need to install a desktop environment.\n")
                    
                    print("=== How to install KDE Plasma on your real PC ===")
                    print("Once you reboot your real machine, log in as 'root' with the password you just created and run:")
                    print("  1. Ensure you have an internet connection (you may need to run 'iwctl' again).")
                    print("  2. pacman -S plasma sddm networkmanager")
                    print("  3. systemctl enable sddm")
                    print("  4. systemctl enable NetworkManager")
                    print("  5. reboot")
                    print("=================================================\n")
                else:
                    missing = [k for k, v in self.state.items() if not v]
                    print(f"\n[WARNING] Rebooting, but installation is incomplete. Missing steps: {missing}")
                self.running = False

        else:
            print(f"bash: {cmd}: command not found (or not implemented in simulator)")

    def run(self):
        print("Arch Linux Installation ISO Simulator (v1.1)")
        print("Type 'installer_guide' for a list of steps.")
        print("Every 'installer_guide' or 'help' command will not appear in the real arch installer.")
        print("Remember that this tool is used only for single boot, for dual boot check simo's github.")
        print("---------------------------------------------------------------------------------------")
        
        while self.running:
            try:
                prompt = "[root@archiso /]# " if self.in_chroot else "root@archiso ~ # "
                cmd = input(prompt).strip()
                self.process_command(cmd)
            except KeyboardInterrupt:
                print("\nType 'exit' or 'reboot' to quit the simulator.")
            except Exception as e:
                print(f"Simulator Error: {e}")

if __name__ == "__main__":
    simulator = ArchInstallerSimulator()
    simulator.run()