'Default plugin implementations'
from .hookspec import hookimpl
from .hookspec import USBQPluginDef


@hookimpl
def usbq_declare_plugins():
    # These are the bundled plugins.
    return {
        'proxy': USBQPluginDef(
            name='proxy',
            desc='Send and receive USB packets from a USBQ proxy device using the usbq_core module.',
            mod='usbq.plugins.proxy',
            clsname='ProxyPlugin',
        ),
        'pcap': USBQPluginDef(
            name='pcap',
            desc='Write a PCAP file containing USB communications.',
            mod='usbq.plugins.pcap',
            clsname='PcapFileWriter',
        ),
        'decode': USBQPluginDef(
            name='decode',
            desc='Decode raw USBQ driver packets to Scapy representation.',
            mod='usbq.plugins.decode',
            clsname='USBDecode',
        ),
        'encode': USBQPluginDef(
            name='encode',
            desc='Encode raw USBQ driver packets to Scapy representation.',
            mod='usbq.plugins.encode',
            clsname='USBEncode',
        ),
        'hostscan': USBQPluginDef(
            name='hostscan',
            desc='WIP: Scan host for supported devices.',
            mod='usbq.plugins.hostscan',
            clsname='USBHostScan',
        ),
        'device': USBQPluginDef(
            name='device',
            desc='WIP: Emulate a USB device.',
            mod='usbq.plugins.device',
            clsname='USBDevice',
        ),
        'hexdump': USBQPluginDef(
            name='hexdump',
            desc='Display USBQ packet and hexdump of USB payload.',
            mod='usbq.plugins.hexdump',
            clsname='Hexdump',
        ),
        'hostfuzz': USBQPluginDef(
            name='hostfuzz',
            desc='WIP: Fuzz device packets headed to the host.',
            mod='usbq.plugins.hostfuzz',
            clsname='Hostfuzz',
        ),
        'clonedevice': USBQPluginDef(
            name='clonedevice',
            desc='WIP: Observe device behavior to clone device configuration and descriptors.',
            mod='usbq.plugins.clonedevice',
            clsname='CloneDevice',
        ),
        'reload': USBQPluginDef(
            name='reload',
            desc='Monitor usbq_hooks.py file and reload if changed.',
            mod='usbq.plugins.reload',
            clsname='ReloadUSBQHooks',
        ),
        'ipython': USBQPluginDef(
            name='ipython',
            desc='Start an IPython session so that USBQ can be updated on the fly.',
            mod='usbq.plugins.ipython',
            clsname='IPythonUI',
        ),
        'lookfor': USBQPluginDef(
            name='lookfor',
            desc='look for a specific USB device to appear',
            mod='usbq.plugins.lookfor',
            clsname='LookForDevice',
        ),
    }
