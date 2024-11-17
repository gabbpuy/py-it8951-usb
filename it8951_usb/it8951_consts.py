# -*- coding: utf-8 -*-
ENDPOINT_IN = 0x81
ENDPOINT_OUT = 0x02
MAX_TRANSFER = 60 * 1024
INQUIRY_CMD = bytearray([0x12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
GET_SYS_CMD = bytearray([0xfe, 0, 0x38, 0x39, 0x35, 0x31, 0x80, 0, 0x01, 0, 0x02, 0, 0, 0, 0, 0])
LD_IMAGE_AREA_CMD = bytearray([0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0xa2, 0, 0, 0, 0, 0, 0, 0, 0, 0])
DPY_AREA_CMD = bytearray([0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0])