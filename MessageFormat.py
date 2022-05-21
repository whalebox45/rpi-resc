import uuid
import socket



def get_cpuid():
    cpuserial = "000000000000000"
    try:
        cf = open('/proc/cpuinfo','r')
        for line in cf:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        cf.close()
    except:
        cpuserial = "ERROR0000000000"
    return cpuserial



def get_mac_address(hasColon=False):
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    if hasColon:
        return ":".join([mac[e:e+2] for e in range(0,11,2)])
    else: return str(mac)

def get_hostname():
    return socket.gethostname()

class MessageFormat():
    def __init__(self):
        self.cpuid = get_cpuid()
        self.macaddr = get_mac_address()
        self.hostname = get_hostname()
    
    def __str__(self):
        data_dict = dict({
            "Hostname": self.cpuid,
            "SerialNo.": self.macaddr,
            "MACAddress": self.hostname
        })
        return str(data_dict)

