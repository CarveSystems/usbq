import attr
import logging

from scapy.all import raw
from statemachine import StateMachine, State

from ..hookspec import hookimpl
from ..pm import pm
from ..usbmitm_proto import (
    USBMessageDevice,
    USBMessageHost,
    ManagementMessage,
    ManagementReset,
    ManagementNewDevice,
    USBMessageRequest,
    USBMessageResponse,
    NEW_DEVICE,
    RESET,
)
from ..model import DeviceIdentity
from ..dissect.defs import *
from ..dissect.usb import GetDescriptor

__all__ = ['USBDevice']

log = logging.getLogger(__name__)


@attr.s(cmp=False)
class USBDevice(StateMachine):
    'Plugin for a stubbed out emulated USB device.'

    #: USB device class, hex
    _dclass = attr.ib(converter=int)

    #: USB device class
    _dsubclass = attr.ib(converter=int)

    #: USB device class
    _dproto = attr.ib(converter=int)

    #: USB Device Identity
    _ident = attr.ib(default=attr.Factory(DeviceIdentity))

    # States
    disconnected = State('disconnected', initial=True)
    connected = State('connected')

    # Valid state transitions
    connect = disconnected.to(connected)
    disconnect = connected.to(disconnected)

    _msgtypes = {ManagementMessage: 2, USBMessageResponse: 0}

    def __attrs_post_init__(self):
        # Workaround to mesh attr and StateMachine
        super().__init__()
        self._pkt_out = []
        self._pkt_in = []

    # Proxy hooks

    @hookimpl
    def usbq_device_has_packet(self):
        return len(self._pkt_out) > 0

    @hookimpl
    def usbq_get_device_packet(self):
        if len(self._pkt_out) > 0:
            return self._pkt_out.pop(0)

    @hookimpl
    def usbq_send_device_packet(self, data):
        assert type(data) == USBMessageHost
        self._pkt_in.append(data)
        return True

    # Decode/Encode is not required

    @hookimpl
    def usbq_device_decode(self, data):
        # Message is already decoded since it came from an emulated device
        assert type(data) == USBMessageDevice
        return data

    @hookimpl
    def usbq_host_encode(self, pkt):
        # Message does not need to be encoded since it is going to an emulated device
        assert type(pkt) == USBMessageHost
        return pkt

    @hookimpl
    def usbq_device_tick(self):
        if self.is_disconnected:
            self.connect()

        while len(self._pkt_in) > 0:
            msg = self._pkt_in.pop(0)

            if type(msg.content) == USBMessageRequest:
                pm.hook.usbq_handle_device_request(dev=self, content=msg.content)
            else:
                raise NotImplementedError(f'Don\'t know how to handle {type(msg)} yet.')

        return True

    def _send_to_host(self, content):
        msgtype = self._msgtypes[type(content)]
        self._pkt_out.append(USBMessageDevice(type=msgtype, content=content))

    # State handlers

    def on_connect(self):
        'Connect to the USB Host by queuing a new identity packet.'

        # fetch device identity of the emulated device
        log.info('Connecting emulated USB device')
        self._send_to_host(
            ManagementMessage(
                management_type=NEW_DEVICE,
                management_content=self._ident.to_new_identity(),
            )
        )

    def on_disconnect(self):
        'Disconnect from the USB Host'

        log.info('Disconnecting emulated USB device')
        self._send_to_host(
            ManagementMessage(
                management_type=RESET, management_content=ManagementReset()
            )
        )

    # Message handling

    @hookimpl
    def usbq_handle_device_request(self, dev, content):
        'Process EP0 CONTROL requests for descriptors'

        ep = content.ep
        req = content.request

        # Handle EP0 CONTROL
        if not (
            ep.epnum == 0
            and ep.eptype == 0
            and ep.epdir == 0
            and type(req) == GetDescriptor
        ):
            return

        # Descriptor request
        if req.bRequest == 6:
            desc = self._ident.from_request(req)
            if desc is not None:
                self._send_to_host(
                    USBMessageResponse(ep=ep, request=req, response=desc)
                )
                return True
