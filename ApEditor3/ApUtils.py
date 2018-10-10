#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : ApUtils.py
# @Author: WMH
# @Date  : 18-8-24
# @Desc  : ApEditor的Utils文件
import codecs
import struct

# 小端字节序
from modules.ApEditor import config


def little_endian(data):
    return data[::-1]


# 十六进制转化成ascii字符串
def read_asc(data):
    data_asc = ""
    for tmp in data:
        tmp_int = int(tmp, 16)
        if tmp_int == 0:
            continue
        data_asc += chr(tmp_int)
    return data_asc


# 把data按照16进制存储
# []==>[16,16,16]
def read_hex(data):
    hex_data = []
    for i in range(len(data)):
        if i % 2:
            continue
        else:
            tmp = []
            tmp1 = data[i]
            tmp2 = data[i + 1]
            hex_data.append(tmp1 + tmp2)
    return hex_data


# 打印十六进制
def printhex(data):
    print_hex = "0x"
    for tmp in data:
        print_hex += str(tmp)
    return print_hex


# 读取am文件
def am_read(am_path):
    # 读取二进制文件并转化成16进制
    with open(am_path, 'rb') as f_am:
        data = str(codecs.encode(f_am.read(), "hex_codec"))
        # 按字节存储
        data_hex = read_hex(data[2:-1])
        return data_hex


# type 格式处理
def getPackage(id_int):
    if (id_int >> 24) == 1:
        return "android"
    return ""


# Atribute的type
def getAttrType(arr_type):
    if arr_type == config.global_type["ATTR_NULL"]:
        return "ATTR_NULL"
    elif arr_type == config.global_type["ATTR_REFERENCE"]:
        return "ATTR_REFERENCE"
    elif arr_type == config.global_type["ATTR_ATTRIBUTE"]:
        return "ATTR_ATTRIBUTE"
    elif arr_type == config.global_type["ATTR_STRING"]:
        return "ATTR_STRING"
    elif arr_type == config.global_type["ATTR_FLOAT"]:
        return "ATTR_FLOAT"
    elif arr_type == config.global_type["ATTR_DIMENSION"]:
        return "ATTR_DIMENSION"
    elif arr_type == config.global_type["ATTR_FRACTION"]:
        return "ATTR_FRACTION"
    elif arr_type == config.global_type["ATTR_FIRSTINT"]:
        return "ATTR_FIRSTINT"
    elif arr_type == config.global_type["ATTR_HEX"]:
        return "ATTR_HEX"
    elif arr_type == config.global_type["ATTR_BOOLEAN"]:
        return "ATTR_BOOLEAN"
    elif arr_type == config.global_type["ATTR_FIRSTCOLOR"]:
        return "ATTR_FIRSTCOLOR"
    elif arr_type == config.global_type["ATTR_RGB8"]:
        return "ATTR_RGB8"
    elif arr_type == config.global_type["ATTR_ARGB4"]:
        return "ATTR_ARGB4"
    elif arr_type == config.global_type["ATTR_RGB4"]:
        return "ATTR_RGB4"
    else:
        return "Other_Type"


# Attribute的data的type
def getAttrData(attr_type, data):
    if attr_type == config.global_type["ATTR_STRING"]:
        return config.global_list["STRINGPOOL"][int(printhex(data), 16)]
    if attr_type == config.global_type["ATTR_ATTRIBUTE"]:
        return getPackage(int(printhex(data), 16))
    if attr_type == config.global_type["ATTR_BOOLEAN"]:
        if int(printhex(data), 16) != 0:
            return "true"
        return "false"
    else:
        return printhex(data)


# 封装打印函数
def apprint(print_string, default=False):
    if default:
        print(print_string)


# 插入字符串编码
def encodeutf(string):
    str_data = []
    str_count = 0
    if config.get_value('XMLFLAG') == 0:
        str_data.append(hex(len(string)))
        str_data.append(hex(0))
        for str_i in string:
            encod_str = hex(ord(str_i.encode("utf-8")))
            str_data.append(encod_str)
            str_data.append(hex(0))
        str_data.append(hex(0))
        str_data.append(hex(0))
    elif config.get_value('XMLFLAG') == 1:
        #此时为XML资源文件格式
        str_data.append(hex(len(string)))
        str_data.append(hex(len(string)))
        for str_i in string:
            encod_str = hex(ord(str_i.encode("utf-8")))
            str_data.append(encod_str)
        str_data.append(hex(0))
    #和4倍对齐，所以最多循环3次
    for i in range(3):
        if (str_count+1+2)%4 == 0:
            return str_data
        else:
            str_count += 1
            str_data.append(hex(0))
    # print str_data
    return str_data


# 将int型转化为小端hex型
def encodehex(int_string):
    hexdata_tmp = []
    hexdata = []
    encode_hex = str(hex(int_string))
    if len(encode_hex) % 2 == 0:
        for i in range(4):
            tmp = encode_hex[2 + i * 2:2 + i * 2 + 2]
            if tmp == "":
                break
            else:
                hexdata_tmp.append(tmp)
    else:
        hexdata_tmp.append("0" + encode_hex[2:3])
        for i in range(3):
            tmp = encode_hex[3 + i * 2:3 + i * 2 + 2]
            if tmp == "":
                break
            else:
                hexdata_tmp.append(tmp)
    hexdata.extend(hexdata_tmp[::-1])
    for j in range(4 - len(hexdata)):
        hexdata.append("00")
    return hexdata


def writedata(data, path):
    with open(path, 'wb') as f:
        for da in data:
            da_index = int(da, 16)
            dd = struct.pack('B', da_index)
            f.write(dd)
