from dataclasses import dataclass
from ctypes import *
from enum import IntEnum, auto

from PIL import Image

from .it8951_consts import MAX_TRANSFER, INQUIRY_CMD, GET_SYS_CMD, LD_IMAGE_AREA_CMD, DPY_AREA_CMD
from .it8951_structs import CommandInquiry, DisplayArea, Area, SystemInfo, CommandStatusWrapper
from .it8951_usb import IT8951_USB


class Mode(IntEnum):
    INIT = 0    # Full Refresh
    DU = auto()

    GC16 = auto()
    GL16 = auto()
    GLR16 = auto()
    GLD16 = auto()
    DU4 = auto()
    A2 = auto()
    __Unknown = auto()


@dataclass(frozen=True)
class Inquiry:
    vendor: str
    product: str
    revision: str


class IT8951_SCSI:
    def __init__(self, device: IT8951_USB):
        self.connection: IT8951_USB = device
        self.system_info: SystemInfo = self._get_system()

    def drop(self):
        pass

    def inquiry(self) -> Inquiry:
        if c_inquiry := self.connection.read_command(INQUIRY_CMD, CommandInquiry):
            return Inquiry(
                bytes(c_inquiry.vendor).decode(),
                bytes(c_inquiry.product).decode(),
                bytes(c_inquiry.revision).decode()
            )

    def _get_system(self) -> SystemInfo:
        return self.connection.read_command(GET_SYS_CMD, SystemInfo)

    def get_system_info(self) -> SystemInfo:
        return self._get_system()

    def ld_image_area(self, area: Area, data: bytes) -> CommandStatusWrapper:
        return self.connection.write_command(
            LD_IMAGE_AREA_CMD,
            bytearray(area),
            data
        )

    def display_area(self, display_area: DisplayArea) -> CommandStatusWrapper:
        result = self.connection.write_command(
            DPY_AREA_CMD,
            bytearray(display_area),
            bytearray()
        )
        return result

    def update_region(self, image: Image, x: int, y: int, mode: Mode) -> CommandStatusWrapper:
        data = bytearray(image.getdata())
        width, height = image.size
        size = width * height
        i = 0
        row_height = (MAX_TRANSFER - sizeof(Area)) // width
        address = self.system_info.image_buf_base
        while i < size:
            if (i // width) + row_height > height:
                row_height = height - (i // width)

            self.ld_image_area(Area(address, x, y + (i // width), width, row_height),
                               data[i: i + width * row_height])
            i += row_height * width

        return self.display_area(DisplayArea(
            address, mode, x, y, width, height, 1
        ))
