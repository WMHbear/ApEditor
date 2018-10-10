#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: WMH
# @Date  : 18-8-24
# @Desc  : ApEditor的全局变量管理


# type类型
global_type = {
    'ATTR_NULL': 0,
    'ATTR_REFERENCE': 1,
    'ATTR_ATTRIBUTE': 2,
    'ATTR_STRING': 3,
    'ATTR_FLOAT': 4,
    'ATTR_DIMENSION': 5,
    'ATTR_FRACTION': 6,
    'ATTR_FIRSTINT': 16,
    'ATTR_HEX': 17,
    'ATTR_BOOLEAN': 18,
    'ATTR_FIRSTCOLOR': 28,
    'ATTR_RGB8': 29,
    'ATTR_ARGB4': 30,
    'ATTR_RGB4': 31,
    'ATTR_LASTCOLOR': 31,
    'ATTR_LASTINT': 31
}

# 全局变量
global_param = {
    'AMHEADER': 0,
    'STRINGPOOLOFFSET': 0,
    'STYLEPOOLOFFSET': 0,
    'STRINGCHUNKEND': 0,
    'RESOURCEIDCHUNKSTAR': 0,
    'RESOURCEIDCHUNKEND': 0,
    'STARNAMESPACESTAR': 0,
    'STARNAMESPACEEND': 0,
    'ENDNAMESPACESTAR': 0,
    'ENDNAMESPACEEND': 0,
    'STARTTAGCHUNKSTAR': 0,
    'STARTTAGCHUNKEND': 0,
    'ENDTAGCHUNKSTAR': 0,
    'ENDTAGCHUNKEND': 0,
    'TEXTCHUNKSTAR': 0,
    'TEXTCHUNKEND': 0,
    'FILSIZEINDEX': 0,
    'STRINGCHUNKSIZEINDEX': 0,
    'STRINGCHUNKCOUNTINDEX': 0,
    'LASTSTRINGOFFSETSINDEX': 0,
    'LASTSTRINGINDEX': 0,
    'LASTSTRINGLEN': 0,
    'STRINGPOOLOFFSETINDEX': 0,
    'APPLICATIONPC': 0,
    'APPLICATIONNAMEFLAG': 0,
    'APPLICATIONNAMEINDEX': 0,
    'TAGCOUNTSTAR': 0,
    'TAGCOUNTEND': 0,
    'XMLFLAG':0
}

# 全局list
global_list = {
    'STRINGOFFSETS': [],
    'STYLEOFFSETS': [],
    'STRINGPOOL': [],
    'RESOURCEIDS': []
}


# 全局变量初始化
def init_global():
    global global_param, global_list
    for param in global_param:
        global_param[param] = 0
    for list_param in global_list:
        global_list[list_param] = []


def set_value(name, value):
    global global_param
    global_param[name] = value


def get_value(name, defValue=None):
    try:
        return global_param[name]
    except KeyError:
        return defValue
