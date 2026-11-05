// Comprehensive IEEE OUI Vendor Prefix Lookup & Device Type / Hierarchy Classifier
export const OUI_VENDORS = {
  // Enterprise Gateways, Switches & Wireless Controllers discovered on LAN
  'C4:B2:5B': 'Huawei / Ruijie Enterprise Gateway',
  'C8:CD:55': 'Ruijie / Reyee Managed Wireless AP',
  'E0:5D:54': 'Ruijie / Reyee Managed PoE Switch',
  '7C:01:3E': 'Ruijie / Enterprise Wireless AP',
  '9C:CE:88': 'Enterprise Network Switch / AP',
  '00:22:6C': 'Cisco / Linksys Network Endpoint',
  '28:7B:11': 'Enterprise Smart Terminal / IoT',
  '10:82:3D': 'Ruijie / Network Infrastructure',
  '50:2E:91': 'Realtek WiFi 6 Wireless NIC',
  '52:2E:91': 'Microsoft Wi-Fi Direct Virtual NIC',
  '56:2E:91': 'Microsoft Wi-Fi Direct Virtual NIC',
  '88:AE:DD': 'Realtek PCIe GbE Controller',
  '38:8C:EF': 'Enterprise Workstation / Endpoint',
  '28:07:08': 'Network Connected Endpoint',
  '44:F7:9F': 'Enterprise Wireless Client',
  'B0:F2:F6': 'Smart Controller / Network Node',
  '80:0D:3F': 'Embedded IoT / Network Controller',
  '44:25:38': 'Enterprise Workstation NIC',
  '44:F5:3E': 'Connected Smart Device',
  '98:4E:8A': 'Enterprise Network Node',
  'A4:D7:3C': 'Smart Terminal / Workstation',
  '80:03:0D': 'Embedded Network Device',
  // Cisco / Meraki
  '00:00:0C': 'Cisco Systems',
  '00:01:42': 'Cisco Systems',
  '00:01:43': 'Cisco Systems',
  '00:0B:BE': 'Cisco Systems',
  '00:18:0A': 'Cisco Meraki',
  '0C:85:25': 'Cisco Systems',
  '58:AC:78': 'Cisco Systems',
  '88:15:44': 'Cisco Meraki',
  'E0:55:3D': 'Cisco Meraki',
  'F0:7F:06': 'Cisco Systems',
  // Ubiquiti (UniFi / EdgeMAX)
  '00:15:6D': 'Ubiquiti Inc.',
  '00:27:22': 'Ubiquiti Inc.',
  '04:18:D6': 'Ubiquiti Inc.',
  '18:E8:29': 'Ubiquiti Inc.',
  '24:5A:4C': 'Ubiquiti Inc.',
  '44:D9:E7': 'Ubiquiti Inc.',
  '60:22:32': 'Ubiquiti Inc.',
  '68:D7:9A': 'Ubiquiti Inc.',
  '70:A7:41': 'Ubiquiti Inc.',
  '74:83:C2': 'Ubiquiti Inc.',
  '78:45:58': 'Ubiquiti Inc.',
  '78:8A:20': 'Ubiquiti Inc.',
  '80:2A:A8': 'Ubiquiti Inc.',
  'B4:FB:E4': 'Ubiquiti Inc.',
  'D0:21:F9': 'Ubiquiti Inc.',
  'E0:63:DA': 'Ubiquiti Inc.',
  'F0:9F:C2': 'Ubiquiti Inc.',
  'FC:EC:DA': 'Ubiquiti Inc.',
  // MikroTik
  '00:0C:42': 'MikroTik',
  '08:55:31': 'MikroTik',
  '18:FD:74': 'MikroTik',
  '2C:C8:1B': 'MikroTik',
  '48:8F:5A': 'MikroTik',
  '4C:5E:0C': 'MikroTik',
  '64:D1:54': 'MikroTik',
  '6C:3B:6B': 'MikroTik',
  '74:4D:28': 'MikroTik',
  'B8:69:F4': 'MikroTik',
  'C4:AD:34': 'MikroTik',
  'CC:2D:E0': 'MikroTik',
  'D4:CA:6D': 'MikroTik',
  'DC:2C:6E': 'MikroTik',
  'E4:8D:8C': 'MikroTik',
  // Fortinet / Palo Alto
  '00:09:0F': 'Fortinet',
  '08:5B:0E': 'Fortinet',
  '70:4C:A5': 'Fortinet',
  '90:6C:AC': 'Fortinet',
  'E8:1C:BA': 'Fortinet',
  '00:1B:17': 'Palo Alto Networks',
  '00:86:9C': 'Palo Alto Networks',
  // Aruba / HPE
  '00:0B:86': 'Aruba Networks (HPE)',
  '00:1A:1E': 'Aruba Networks (HPE)',
  '20:4C:03': 'Aruba Networks (HPE)',
  '24:DE:C6': 'Aruba Networks (HPE)',
  '38:21:C7': 'Aruba Networks (HPE)',
  '40:E3:D6': 'Aruba Networks (HPE)',
  '6C:F3:7F': 'Aruba Networks (HPE)',
  '94:B4:0F': 'Aruba Networks (HPE)',
  '00:17:A4': 'Hewlett Packard Enterprise',
  '3C:D9:2B': 'Hewlett Packard Enterprise',
  '98:F2:B3': 'Hewlett Packard Enterprise',
  // TP-Link / D-Link / Netgear / Asus
  '00:31:92': 'TP-Link Systems',
  '14:CC:20': 'TP-Link Systems',
  '18:A6:F7': 'TP-Link Systems',
  '28:87:BA': 'TP-Link Systems',
  '30:DE:4B': 'TP-Link Systems',
  '50:C7:BF': 'TP-Link Systems',
  '54:AF:97': 'TP-Link Systems',
  '60:32:B1': 'TP-Link Systems',
  '70:4F:57': 'TP-Link Systems',
  '84:16:F9': 'TP-Link Systems',
  '98:DA:C4': 'TP-Link Systems',
  'AC:84:C6': 'TP-Link Systems',
  'B0:95:75': 'TP-Link Systems',
  'C0:06:C3': 'TP-Link Systems',
  'D8:07:B6': 'TP-Link Systems',
  'E8:48:B8': 'TP-Link Systems',
  'F4:F2:6D': 'TP-Link Systems',
  '00:05:5D': 'D-Link Corporation',
  '1C:7E:E5': 'D-Link Corporation',
  '28:10:7B': 'D-Link Corporation',
  'C8:D3:A3': 'D-Link Corporation',
  '00:09:5B': 'Netgear',
  '20:E5:2A': 'Netgear',
  '9C:3D:CF': 'Netgear',
  '04:92:26': 'ASUSTek Computer',
  '04:D4:C4': 'ASUSTek Computer',
  '10:7B:44': 'ASUSTek Computer',
  '2C:FD:A1': 'ASUSTek Computer',
  // Huawei / Ruijie / H3C
  '00:18:82': 'Huawei Technologies',
  '00:25:9E': 'Huawei Technologies',
  '00:E0:FC': 'Huawei Technologies',
  '28:6E:D4': 'Huawei Technologies',
  '48:46:FB': 'Huawei Technologies',
  '88:53:D4': 'Huawei Technologies',
  '00:1A:A9': 'Ruijie Networks',
  '58:69:6C': 'Ruijie Networks',
  '38:91:D5': 'H3C Technologies',
  // CCTV: Hikvision / Dahua / Axis / Uniview
  '00:40:8C': 'Axis Communications',
  'AC:CC:8E': 'Axis Communications',
  'B8:A4:4F': 'Axis Communications',
  '18:68:CB': 'Hangzhou Hikvision',
  '24:0F:9B': 'Hangzhou Hikvision',
  '28:57:BE': 'Hangzhou Hikvision',
  '44:19:B6': 'Hangzhou Hikvision',
  '4C:BD:8F': 'Hangzhou Hikvision',
  '54:C4:15': 'Hangzhou Hikvision',
  '64:DB:8B': 'Hangzhou Hikvision',
  '80:7C:62': 'Hangzhou Hikvision',
  'A4:14:37': 'Hangzhou Hikvision',
  'BC:AD:28': 'Hangzhou Hikvision',
  'C0:56:E3': 'Hangzhou Hikvision',
  'C4:2F:90': 'Hangzhou Hikvision',
  'E0:50:8B': 'Hangzhou Hikvision',
  '08:ED:ED': 'Zhejiang Dahua',
  '14:A7:8B': 'Zhejiang Dahua',
  '38:AF:29': 'Zhejiang Dahua',
  '3C:EF:8C': 'Zhejiang Dahua',
  '4C:11:BF': 'Zhejiang Dahua',
  '90:02:A9': 'Zhejiang Dahua',
  'A0:BD:1D': 'Zhejiang Dahua',
  '48:EA:63': 'Uniview Technologies',
  // Synology / QNAP / Dell / Supermicro / VMware / Proxmox / Hyper-V
  '00:11:32': 'Synology Inc.',
  '90:09:D0': 'Synology Inc.',
  '00:08:9B': 'QNAP Systems',
  '24:5E:BE': 'QNAP Systems',
  '00:14:22': 'Dell Inc.',
  '18:66:DA': 'Dell Inc.',
  'D4:BE:D9': 'Dell Inc.',
  'F8:B1:56': 'Dell Inc.',
  '00:25:90': 'Super Micro Computer',
  'AC:1F:6B': 'Super Micro Computer',
  '00:0C:29': 'VMware ESXi / vSphere',
  '00:50:56': 'VMware ESXi / vSphere',
  'BC:24:11': 'Proxmox Server Solutions',
  '00:15:5D': 'Microsoft Hyper-V Virtual Machine',
  // IoT / Embedded / Intel / Realtek
  '24:0A:C4': 'Espressif (ESP32/IoT)',
  '30:AE:A4': 'Espressif (ESP32/IoT)',
  '84:CC:A8': 'Espressif (ESP32/IoT)',
  'A4:CF:12': 'Espressif (ESP32/IoT)',
  'B8:27:EB': 'Raspberry Pi Foundation',
  'DC:A6:32': 'Raspberry Pi Foundation',
  'E4:5F:01': 'Raspberry Pi Foundation',
  '28:CD:C1': 'Raspberry Pi Foundation',
  '00:1B:21': 'Intel Corporate',
  '3C:97:0E': 'Intel Corporate',
  '8C:8D:28': 'Intel Corporate',
  'A4:BB:6D': 'Intel Corporate',
  '00:E0:4C': 'Realtek Semiconductor',
  '08:62:66': 'ASUSTek / Realtek',
  '50:EB:F6': 'ASUSTek Computer',
};

export function lookupMacVendor(mac) {
  if (!mac || typeof mac !== 'string') return 'Unknown Vendor';
  const clean = mac.trim().toUpperCase().replace(/-/g, ':');
  const prefix = clean.slice(0, 8);
  if (OUI_VENDORS[prefix]) return OUI_VENDORS[prefix];
  if (clean.length >= 2 && ['2', '6', 'A', 'E'].includes(clean[1])) {
    return 'Locally Administered / Virtual NIC';
  }
  return 'Generic Network Device';
}

export const WELL_KNOWN_PORTS = [
  { port: 21, service: 'FTP', protocol: 'tcp', isWeb: false },
  { port: 22, service: 'SSH', protocol: 'tcp', isWeb: false, scheme: 'ssh' },
  { port: 23, service: 'Telnet', protocol: 'tcp', isWeb: false, scheme: 'telnet' },
  { port: 25, service: 'SMTP', protocol: 'tcp', isWeb: false },
  { port: 53, service: 'DNS', protocol: 'tcp', isWeb: false },
  { port: 80, service: 'HTTP', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 81, service: 'HTTP-Alt', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 88, service: 'Kerberos / Web', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 110, service: 'POP3', protocol: 'tcp', isWeb: false },
  { port: 111, service: 'RPCBind', protocol: 'tcp', isWeb: false },
  { port: 135, service: 'MS-RPC', protocol: 'tcp', isWeb: false },
  { port: 139, service: 'NetBIOS-SSN', protocol: 'tcp', isWeb: false },
  { port: 161, service: 'SNMP', protocol: 'udp', isWeb: false },
  { port: 179, service: 'BGP Router', protocol: 'tcp', isWeb: false },
  { port: 389, service: 'LDAP', protocol: 'tcp', isWeb: false },
  { port: 443, service: 'HTTPS', protocol: 'tcp', isWeb: true, scheme: 'https' },
  { port: 445, service: 'SMB / CIFS', protocol: 'tcp', isWeb: false },
  { port: 502, service: 'Modbus TCP (BMS/HVAC)', protocol: 'tcp', isWeb: false },
  { port: 515, service: 'LPD Printer', protocol: 'tcp', isWeb: false },
  { port: 554, service: 'RTSP Stream (CCTV)', protocol: 'tcp', isWeb: false, scheme: 'rtsp' },
  { port: 631, service: 'IPP / CUPS Printer', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 1883, service: 'MQTT Broker (IoT)', protocol: 'tcp', isWeb: false },
  { port: 1935, service: 'RTMP Video', protocol: 'tcp', isWeb: false },
  { port: 2049, service: 'NFS Storage', protocol: 'tcp', isWeb: false },
  { port: 3000, service: 'Web App / Grafana', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 3306, service: 'MySQL / MariaDB', protocol: 'tcp', isWeb: false },
  { port: 3389, service: 'RDP Remote Desktop', protocol: 'tcp', isWeb: false, scheme: 'rdp' },
  { port: 5000, service: 'UPnP / Synology HTTP', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 5001, service: 'Synology HTTPS / WebUI', protocol: 'tcp', isWeb: true, scheme: 'https' },
  { port: 5432, service: 'PostgreSQL', protocol: 'tcp', isWeb: false },
  { port: 5900, service: 'VNC Remote', protocol: 'tcp', isWeb: false },
  { port: 6379, service: 'Redis / Switch Control Bus', protocol: 'tcp', isWeb: false },
  { port: 8000, service: 'HTTP-Mgmt / Hikvision SDK', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 8006, service: 'Proxmox VE WebUI', protocol: 'tcp', isWeb: true, scheme: 'https' },
  { port: 8008, service: 'HTTP-Alt', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 8080, service: 'HTTP-Proxy / Web Admin', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 8081, service: 'HTTP-Admin Alt', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 8291, service: 'MikroTik Winbox', protocol: 'tcp', isWeb: false },
  { port: 8443, service: 'HTTPS-Admin / UniFi', protocol: 'tcp', isWeb: true, scheme: 'https' },
  { port: 8554, service: 'RTSP-Alt Stream', protocol: 'tcp', isWeb: false, scheme: 'rtsp' },
  { port: 8728, service: 'MikroTik RouterOS API', protocol: 'tcp', isWeb: false },
  { port: 8883, service: 'MQTTS (Secure IoT)', protocol: 'tcp', isWeb: false },
  { port: 8888, service: 'HTTP Web Portal', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 9000, service: 'Portainer / Sonar / Web', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 9090, service: 'Cockpit / Prometheus Web', protocol: 'tcp', isWeb: true, scheme: 'http' },
  { port: 9100, service: 'JetDirect Network Printer', protocol: 'tcp', isWeb: false },
  { port: 10000, service: 'Webmin Admin', protocol: 'tcp', isWeb: true, scheme: 'https' },
  { port: 27017, service: 'MongoDB', protocol: 'tcp', isWeb: false },
  { port: 34567, service: 'DVR / XMeye Video', protocol: 'tcp', isWeb: false },
  { port: 37777, service: 'Dahua CCTV Protocol', protocol: 'tcp', isWeb: false },
];

export function inferDeviceCategory({ ip = '', mac = '', vendor = '', openPorts = [], snmpInfo = {}, hostname = '', isGateway = false }) {
  const v = (vendor || '').toLowerCase();
  const h = (hostname || '').toLowerCase();
  const m = (mac || '').toUpperCase();
  const sys = ((snmpInfo && snmpInfo.sysDescr) || '').toLowerCase();
  const portSet = new Set(openPorts.map((p) => p.port));
  const titles = openPorts.map((p) => `${p.title || ''} ${p.banner || ''}`).join(' ').toLowerCase();

  if (
    isGateway ||
    ip === '192.168.110.50' ||
    ip.endsWith('.1') ||
    ip.endsWith('.254') ||
    m.startsWith('C4:B2:5B:F3') ||
    portSet.has(179) ||
    portSet.has(8291) ||
    portSet.has(8728) ||
    v.includes('gateway') ||
    v.includes('mikrotik') ||
    v.includes('fortinet') ||
    v.includes('palo alto') ||
    titles.includes('routeros') ||
    titles.includes('fortigate') ||
    titles.includes('gateway') ||
    sys.includes('router')
  ) {
    return 'Router';
  }

  // Managed PoE Switches (e.g. E0:5D:54, C4:B2:5B:66, 9C:CE:88)
  if (
    m.startsWith('E0:5D:54') ||
    m.startsWith('C4:B2:5B') ||
    m.startsWith('9C:CE:88') ||
    v.includes('switch') ||
    titles.includes('switch') ||
    sys.includes('switch')
  ) {
    return 'Switch';
  }

  // Wireless Access Points (e.g. C8:CD:55, 7C:01:3E)
  if (
    m.startsWith('C8:CD:55') ||
    m.startsWith('7C:01:3E') ||
    v.includes('wireless ap') ||
    titles.includes('unifi') ||
    titles.includes('airmax') ||
    titles.includes('omada') ||
    h.includes('ap')
  ) {
    return 'Access Point';
  }

  // Check CCTV / Camera
  if (
    v.includes('hikvision') ||
    v.includes('dahua') ||
    v.includes('axis') ||
    v.includes('uniview') ||
    portSet.has(554) ||
    portSet.has(37777) ||
    portSet.has(34567) ||
    titles.includes('webcam') ||
    titles.includes('ipcam') ||
    titles.includes('hikvision') ||
    titles.includes('dahua')
  ) {
    return 'CCTV';
  }

  // Check Cisco / Ubiquiti / Aruba / TP-Link / D-Link
  if (
    v.includes('cisco') ||
    v.includes('ubiquiti') ||
    v.includes('aruba') ||
    v.includes('ruijie') ||
    v.includes('h3c') ||
    v.includes('tp-link') ||
    v.includes('d-link') ||
    v.includes('netgear')
  ) {
    if (portSet.has(80) || portSet.has(443) || portSet.has(22) || portSet.has(23)) {
      return 'Switch';
    }
    return 'Network';
  }

  // Check HVAC / BMS / IoT
  if (
    portSet.has(502) ||
    portSet.has(1883) ||
    portSet.has(8883) ||
    v.includes('espressif') ||
    v.includes('raspberry') ||
    v.includes('iot')
  ) {
    return portSet.has(502) ? 'HVAC' : 'Sensor';
  }

  // Check Printer
  if (portSet.has(9100) || portSet.has(515) || (portSet.has(631) && !portSet.has(22))) {
    return 'Printer';
  }

  // Check Server / NAS / Virtualization
  if (
    v.includes('synology') ||
    v.includes('qnap') ||
    v.includes('vmware') ||
    v.includes('proxmox') ||
    v.includes('hyper-v') ||
    v.includes('super micro') ||
    portSet.has(5000) ||
    portSet.has(5001) ||
    portSet.has(8006) ||
    portSet.has(3306) ||
    portSet.has(5432) ||
    portSet.has(445) ||
    portSet.has(3389) ||
    portSet.has(22)
  ) {
    return 'Server';
  }

  return 'Network';
}

export function getHierarchyTierAndRole(category, isGateway = false) {
  if (isGateway || category === 'Router') {
    return { tier: 1, role: 'Core Gateway / Router' };
  }
  if (category === 'Switch') {
    return { tier: 2, role: 'Distribution / PoE Switch' };
  }
  if (category === 'Access Point') {
    return { tier: 3, role: 'Wireless Access Point (AP)' };
  }
  if (category === 'Server') {
    return { tier: 3, role: 'Infrastructure Server / VM' };
  }
  return { tier: 4, role: `Endpoint (${category || 'Network'})` };
}
