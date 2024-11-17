# -*- coding: utf-8 -*-
from ctypes import BigEndianStructure, LittleEndianStructure, c_uint8, c_uint32


class Area(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('address', c_uint32),
        ('x', c_uint32),
        ('y', c_uint32),
        ('w', c_uint32),
        ('h', c_uint32)
    ]


class CommandBlockWrapper(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [('signature', c_uint8 * 4),  # noqa
                ('tag', c_uint32),
                ('data_transfer_length', c_uint32),
                ('flags', c_uint8),
                ('lun', c_uint8),
                ('block_length', c_uint8),
                ('block_data', c_uint8 * 16),  # noqa
                ]


class CommandInquiry(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('ignore_start', (c_uint8 * 8)),  # noqa
        ('vendor', (c_uint8 * 8)),  # noqa
        ('product', (c_uint8 * 16)),  # noqa
        ('revision', (c_uint8 * 4)),  # noqa
        ('ignore_end', (c_uint8 * 4))  # noqa
    ]


class CommandStatusWrapper(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [('signature', c_uint8 * 4),  # noqa
                ('tag', c_uint32),
                ('data_residue', c_uint32),
                ('status', c_uint8)
                ]

    def __repr__(self) -> str:
        values = ", ".join(f"{name}={value}" for name, value in self._asdict().items())
        return f"<{self.__class__.__name__}: {values}>"

    def _asdict(self) -> dict:
        return {field[0]: getattr(self, field[0]) for field in self._fields_}


class DisplayArea(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('address', c_uint32),
        ('display_mode', c_uint32),
        ('x', c_uint32),
        ('y', c_uint32),
        ('w', c_uint32),
        ('h', c_uint32),
        ('wait_ready', c_uint32)
    ]


class SystemInfo(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('standard_cmd_no', c_uint32),
        ('extended_cmd_no', c_uint32),
        ('signature', c_uint32),
        ('version', c_uint32),
        ('width', c_uint32),
        ('height', c_uint32),
        ('update_buf_base', c_uint32),
        ('image_buf_base', c_uint32),
        ('temperature_no', c_uint32),
        ('mode', c_uint32),
        ('frame_count', (c_uint32 * 8)),  # noqa
        ('num_img_buf', c_uint32),
        ('reserved', (c_uint32 * 9))  # noqa
    ]

    def __repr__(self) -> str:
        values = ", ".join(f"{name}={value}" for name, value in self._asdict().items())
        return f"<{self.__class__.__name__}: {values}>"

    def _asdict(self) -> dict:
        return {field[0]: getattr(self, field[0]) for field in self._fields_}
