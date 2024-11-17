import array
from ctypes import *
from enum import IntEnum
import logging
from typing import Any

import usb.backend.libusb1
import usb.core
import usb.util

from .it8951_structs import CommandBlockWrapper, CommandStatusWrapper

logger = logging.getLogger(__name__)


class TransferDirection(IntEnum):
    In = 0x80
    Out = 0x00


TAG: int = 1


def get_command_block_wrapper(data, transfer_size: int, direction: TransferDirection) -> CommandBlockWrapper:
    global TAG
    cbw = CommandBlockWrapper()
    signature = [0x55, 0x53, 0x42, 0x43]
    cbw.signature = (c_uint8 * 4)(*signature)  # noqa
    cbw.tag = TAG
    cbw.data_transfer_length = transfer_size
    cbw.flags = direction.value
    cbw.lun = 0x00
    cbw.block_length = 16
    cbw.block_data = (c_uint8 * 16)(*data)  # noqa
    TAG += 1
    return cbw


class IT8951_USB:
    def __init__(self, vendor_id: int = 0x48D, product_id: int = 0x8951, name: str = 'USB Device',
                 config_id: int | None = None):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.product_name = name

        self.dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        assert self.dev is not None, f'Failed to find {self.product_name}'

        # Set the active configuration. With no arguments, the first configuration will be the active one
        for config in self.dev:
            for i in range(config.bNumInterfaces):
                if self.dev.is_kernel_driver_active(i):
                    self.dev.detach_kernel_driver(i)

        if config_id is None:
            self.dev.set_configuration()
        else:
            self.dev.set_configuration(config_id)

        self.cfg = self.dev.get_active_configuration()
        self.iface = self.cfg[(0, 0)]
        self.in_endpoint = usb.util.find_descriptor(
            self.iface,
            # Match the first IN endpoint
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
        assert self.in_endpoint is not None, 'Failed to find IN endpoint'

        self.out_endpoint = usb.util.find_descriptor(
            self.iface,
            # Match the first OUT endpoint
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        assert self.out_endpoint is not None, 'Failed to find OUT endpoint'

    def write(self, data, encoding='utf8', timeout=None):
        if isinstance(data,  str):
            data = data.encode(encoding)
        data = bytearray(data)
        written = 0  # Total bytes written
        wrote_once = False  # Flag to allow writing an empty message

        while data or not wrote_once:
            bytes_written = self.dev.write(self.out_endpoint.bEndpointAddress, data[:self.out_endpoint.wMaxPacketSize],
                                           timeout)
            data = data[bytes_written:]
            wrote_once = True
            written += bytes_written
        return written

    def read(self, size: int, timeout: float | None = None):
        """
        Attempts to read the specified number of bytes from the USB device. This function does NOT
        guarantee that the specified number of bytes will be returned. Multiple reads are performed
        ONLY IF the read size is greater than the maximum packet size of the endpoint.
        """
        data = bytearray()
        remaining = size - len(data)
        while remaining:
            read_data = self.dev.read(self.in_endpoint.bEndpointAddress, min(self.in_endpoint.wMaxPacketSize,
                                                                             remaining), timeout)
            data += read_data
            remaining = size - len(data)
        return data

    def read_command(self, command: bytes, commandType: Any) -> Any:
        cbw = get_command_block_wrapper(command, sizeof(commandType), TransferDirection.In)
        self.write(cbw)
        result_buffer = array.array('B', [0, ] * sizeof(commandType))
        self.dev.read(self.in_endpoint, result_buffer)
        return commandType.from_buffer(result_buffer)

    def write_command(self, command: bytes | bytearray, value: bytes, data: bytes):
        bulk_data = bytearray(value) + bytearray(data)
        cbw = get_command_block_wrapper(command,
                                        len(bulk_data), TransferDirection.Out)
        self.write(cbw)
        self.write(bulk_data)
        return self.send_status_block_wrapper()

    def send_status_block_wrapper(self):
        try:
            try:
                data = self.read(sizeof(CommandStatusWrapper))
            except Exception as e:
                logger.error('Read failed: %s, retrying', e)
                self.clear_halt(self.in_endpoint)
                data = self.read(sizeof(CommandStatusWrapper))
            return CommandStatusWrapper.from_buffer(data)
        except Exception as e:
            logger.exception('Send Status Failed: %s', e)

    def reset(self):
        return self.dev.reset()

    def clear_halt(self, endpoint):
        self.dev.clear_halt(endpoint)
