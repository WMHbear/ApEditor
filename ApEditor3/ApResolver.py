#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : ApResolver.py
# @Author: WMH
# @Date  : 18-8-24
# @Desc  : ApEditor的Resolve，对AM文件进行解析


# 解析头部
from modules.ApEditor import config, ApUtils


def am_header(data):
    # 魔数，4字节
    magic_number = data[0:4]
    # 校验
    if ApUtils.printhex(magic_number) == "0x03000800":
        ApUtils.apprint("===========Resolve Header=============")
        ApUtils.apprint("[Header]Magic number : " + ApUtils.printhex(magic_number))
    else:
        ApUtils.apprint("[Error]This file may not an AndroidManifest.xml file! ")
        exit(-1)
    # 文件大小，4字节
    file_size = ApUtils.little_endian(data[4:8])
    ApUtils.apprint("[Header]File size is : " + ApUtils.printhex(file_size))
    config.set_value('AMHEADER', 8)
    config.set_value('FILSIZEINDEX', 4)


# 解析String Chunk
def am_stringchunk(data, pc):
    # StringChunk的类型，固定4个字节
    ChunkType = ApUtils.little_endian(data[pc:pc + 4])
    if ApUtils.printhex(ChunkType) == "0x001c0001":
        ApUtils.apprint("===========Resolve String Chunk=============")
        ApUtils.apprint("[String]ChunkType is : " + ApUtils.printhex(ChunkType))
    else:
        ApUtils.apprint("[Error]String Chunk resolve error!")
        exit(-1)

    # StringChunk的大小（4）
    ChunkSize = ApUtils.little_endian(data[pc + 4:pc + 8])
    ApUtils.apprint("[String]ChunkSize is : " + ApUtils.printhex(ChunkSize))
    config.set_value('STRINGCHUNKSIZEINDEX', pc + 4)

    # StringChunk中字符串的个数（4）
    StringCount = ApUtils.little_endian(data[pc + 8:pc + 12])
    ApUtils.apprint("[String]StringCount is : " + ApUtils.printhex(StringCount))
    config.set_value('STRINGCHUNKCOUNTINDEX', pc + 8)

    # StringChunk中样式的个数（4）
    StyleCount = ApUtils.little_endian(data[pc + 12:pc + 16])
    ApUtils.apprint("[String]StyleCount is : " + ApUtils.printhex(StyleCount))

    # Unknown（4）
    Unknown = ApUtils.little_endian(data[pc + 16:pc + 20])

    # 字符串池的偏移值（4）
    StringPoolOffset = ApUtils.little_endian(data[pc + 20:pc + 24])
    ApUtils.apprint("[String]StringPoolOffset is : " + ApUtils.printhex(StringPoolOffset))
    config.set_value('STRINGPOOLOFFSET', StringPoolOffset)
    config.set_value('STRINGPOOLOFFSETINDEX', pc + 20)

    # 样式池的偏移值（4）
    StylePoolOffset = ApUtils.little_endian(data[pc + 24:pc + 28])
    ApUtils.apprint("[String]StylePoolOffset is : " + ApUtils.printhex(StylePoolOffset))
    config.set_value('STYLEPOOLOFFSET', StylePoolOffset)

    # 每个字符串的偏移
    if int(ApUtils.printhex(StringCount), 16) != 0:
        StringOffsets = []
        for i in range(int(ApUtils.printhex(StringCount), 16)):
            StringOffset = ApUtils.little_endian(data[pc + 28 + i * 4:pc + 28 + i * 4 + 4])
            StringOffsets.append(StringOffset)
            config.set_value('LASTSTRINGOFFSETSINDEX', pc + 28 + i * 4)
        # 每个字符串的偏移列表
        config.global_list['STRINGOFFSETS'].extend(StringOffsets)
    else:
        ApUtils.apprint("[String]There is no String")

    # 每个样式的偏移
    if int(ApUtils.printhex(StyleCount), 16) != 0:
        StyleOffsets = []
        for j in range(int(ApUtils.printhex(StyleCount), 16)):
            StyleOffset = ApUtils.little_endian(data[pc + 28 + int(ApUtils.printhex(StringCount),
                                                                   16) * 4 + j * 4:pc + 28 + int(
                ApUtils.printhex(StringCount), 16) * 4 + j * 4 + 4])
            StyleOffsets.append(StyleOffset)
        # 每个字符串的偏移列表
        config.global_list['STYLEOFFSETS'].extend(StyleOffsets)
    else:
        ApUtils.apprint("[String]There is no Style")

    # =======开始解析字符串===========#
    count = 0
    for index in config.global_list['STRINGOFFSETS']:
        str_index = pc + int(ApUtils.printhex(config.get_value('STRINGPOOLOFFSET')), 16) + int(ApUtils.printhex(index),
                                                                                               16)
        str_len = int(ApUtils.printhex(ApUtils.little_endian(data[str_index:str_index + 2])), 16)
        str_end = data[str_index + (str_len + 1) * 2:str_index + (str_len + 1) * 2 + 2]
        # utf-8编码
        try:
            string = ApUtils.read_asc(data[str_index + 2:str_index + 2 + str_len * 2])\
                .encode("utf-8").decode('unicode_escape')
        except:
            try:
                string = ApUtils.read_asc(data[str_index + 2:str_index + 2 + str_len * 2])\
                    .encode("utf-8").decode('unicode_escape')
            except:
                string = "String resolve error !!"
        config.set_value('STRINGCHUNKEND', str_index + 2 + str_len * 2 + 2)
        ApUtils.apprint(" [StringPool][" + str(count) + "]" + string)
        config.global_list['STRINGPOOL'].append(string)
        count += 1
        config.set_value('LASTSTRINGLEN', str_len)
    config.set_value('LASTSTRINGINDEX', config.get_value('STRINGCHUNKEND'))


# 解析ResourceId Chunk
def am_resourceidchunk(data, pc):
    # ChunkType:ResourceId Chunk类型，固定四个字节0x00080180
    ChunkType = ApUtils.little_endian(data[pc:pc + 4])
    if ApUtils.printhex(ChunkType) == "0x00080180":
        ApUtils.apprint("===========Resolve ResourceId Chunk=============")
        ApUtils.apprint("[Resource]ChunkType is : " + ApUtils.printhex(ChunkType))
    else:
        ApUtils.apprint("[Error]ResourceId Chunk resolve error!")
        exit(-1)

    # ResourceId Chunk的大小（4）
    ChunkSize = ApUtils.little_endian(data[pc + 4:pc + 8])
    ApUtils.apprint("[Resource]ChunkSize is : " + ApUtils.printhex(ChunkSize))

    # ResourcesId的个数为（大小-头部8字节）/4
    ResourcesId_num = int((int(ApUtils.printhex(ChunkSize), 16) - 8) / 4)
    for i in range(ResourcesId_num):
        tmp_hex = ApUtils.printhex(ApUtils.little_endian(data[pc + 8 + i * 4:pc + 8 + i * 4 + 4]))
        tmp = int(tmp_hex, 16)
        ApUtils.apprint("[Resource][" + str(i) + "]Id : " + str(tmp) + ",hex : " + tmp_hex)
        config.global_list['RESOURCEIDS'].append(tmp_hex)

    config.set_value('RESOURCEIDCHUNKEND',
                     config.get_value('RESOURCEIDCHUNKSTAR') + int(ApUtils.printhex(ChunkSize), 16))


# 解析start namespace chunk
def am_namespacechunk_star(data, pc):
    # ChunkType:Namespace Chunk类型，固定四个字节0x00100100
    ChunkType = ApUtils.little_endian(data[pc:pc + 4])
    if ApUtils.printhex(ChunkType) == "0x00100100":
        ApUtils.apprint("===========Resolve Namespace Chunk Start=============")
        ApUtils.apprint("[startNamespace]ChunkType is : " + ApUtils.printhex(ChunkType))
    else:
        ApUtils.apprint("[Error]Namespace Chunk Start resolve error!")
        exit(-1)

    # Namespace Chunk的大小（4）
    ChunkSize = ApUtils.little_endian(data[pc + 4:pc + 8])
    ApUtils.apprint("[startNamespace]ChunkSize is : " + ApUtils.printhex(ChunkSize))

    # Line Number 行号（4）
    LineNumber = ApUtils.little_endian(data[pc + 8:pc + 12])
    ApUtils.apprint("[startNamespace]LineNumber is : " + ApUtils.printhex(LineNumber))

    # Unknown未知区域（4）
    Unknown = ApUtils.little_endian(data[pc + 12:pc + 16])

    # Prefix命名空间前缀（4）（字符串索引）
    Prefix = ApUtils.little_endian(data[pc + 16:pc + 20])
    PrefixName = config.global_list['STRINGPOOL'][int(ApUtils.printhex(Prefix), 16)]
    ApUtils.apprint("[startNamespace]Prefix is : " + ApUtils.printhex(Prefix) + " , str is : " + PrefixName)

    # Uri命名空间的URI（4）（字符串索引）
    Url = ApUtils.little_endian(data[pc + 20:pc + 24])
    UrlName = config.global_list['STRINGPOOL'][int(ApUtils.printhex(Url), 16)]
    ApUtils.apprint("[startNamespace]Url is : " + ApUtils.printhex(Url) + " , str is : " + UrlName)

    config.set_value('STARNAMESPACEEND', config.get_value('STARNAMESPACESTAR') + int(ApUtils.printhex(ChunkSize), 16))


# 解析end namespace chunk
def am_namespacechunk_end(data, pc):
    # ChunkType:Namespace Chunk类型，固定四个字节0x00100101
    ChunkType = ApUtils.little_endian(data[pc:pc + 4])
    if ApUtils.printhex(ChunkType) == "0x00100101":
        ApUtils.apprint("===========Resolve Namespace Chunk End=============")
        ApUtils.apprint("[endNamespace]ChunkType is : " + ApUtils.printhex(ChunkType))
    else:
        ApUtils.apprint("[Error]Namespace Chunk resolve error!")
        exit(-1)

    # Namespace Chunk的大小（4）
    ChunkSize = ApUtils.little_endian(data[pc + 4:pc + 8])
    ApUtils.apprint("[endNamespace]ChunkSize is : " + ApUtils.printhex(ChunkSize))

    # Line Number 行号（4）
    LineNumber = ApUtils.little_endian(data[pc + 8:pc + 12])
    ApUtils.apprint("[endNamespace]LineNumber is : " + ApUtils.printhex(LineNumber))

    # Unknown未知区域（4）
    Unknown = ApUtils.little_endian(data[pc + 12:pc + 16])

    # Prefix命名空间前缀（4）（字符串索引）
    Prefix = ApUtils.little_endian(data[pc + 16:pc + 20])
    PrefixName = config.global_list['STRINGPOOL'][int(ApUtils.printhex(Prefix), 16)]
    ApUtils.apprint("[endNamespace]Prefix is : " + ApUtils.printhex(Prefix) + " , str is : " + PrefixName)

    # Uri命名空间的URI（4）（字符串索引）
    Url = ApUtils.little_endian(data[pc + 20:pc + 24])
    UrlName = config.global_list['STRINGPOOL'][int(ApUtils.printhex(Url), 16)]
    ApUtils.apprint("[endNamespace]Url is : " + ApUtils.printhex(Url) + " , str is : " + UrlName)

    config.set_value('ENDNAMESPACEEND', config.get_value('ENDNAMESPACESTAR') + int(ApUtils.printhex(ChunkSize), 16))


# 解析start tag chunk
def am_tagchunk_star(data, pc):
    # ChunkType:Tag Chunk类型，固定四个字节0x00100102
    ChunkType = ApUtils.little_endian(data[pc:pc + 4])
    if ApUtils.printhex(ChunkType) == "0x00100102":
        ApUtils.apprint(" ===========Resolve Tag Chunk Start=============")
        ApUtils.apprint(
            " [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]ChunkType is : " + ApUtils.printhex(ChunkType))
    else:
        ApUtils.apprint(" [Error" + str(config.get_value('TAGCOUNTSTAR')) + "]Tag Chunk start resolve error!")
        exit(-1)

    # Tag Chunk的大小（4）
    ChunkSize = ApUtils.little_endian(data[pc + 4:pc + 8])
    ApUtils.apprint(
        " [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]ChunkSize is : " + ApUtils.printhex(ChunkSize))

    # Line Number 行号（4）
    LineNumber = ApUtils.little_endian(data[pc + 8:pc + 12])
    ApUtils.apprint(
        " [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]LineNumber is : " + ApUtils.printhex(LineNumber))

    # Unknown未知区域（4）
    Unknown = ApUtils.little_endian(data[pc + 12:pc + 16])

    # Namespace Uri
    NameSpcae = ApUtils.little_endian(data[pc + 16:pc + 20])
    if int(ApUtils.printhex(NameSpcae), 16) <= len(config.global_list['STRINGPOOL']):
        ApUtils.apprint(" [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]NameSpace is : " +
                        config.global_list['STRINGPOOL'][int(ApUtils.printhex(NameSpcae), 16)])
    else:
        ApUtils.apprint(" [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]NameSpace is : null")

    # name
    Name = ApUtils.little_endian(data[pc + 20:pc + 24])
    NameStr = config.global_list['STRINGPOOL'][int(ApUtils.printhex(Name), 16)]
    ApUtils.apprint(" [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]Tag name is : " + NameStr)
    if NameStr == "application":
        config.set_value('APPLICATIONPC', pc)

    # Flags好像没有意义，一般都是0x00140014
    Flags = ApUtils.little_endian(data[pc + 24:pc + 28])

    # Attribute Count
    AttributeCount = ApUtils.little_endian(data[pc + 28:pc + 32])
    ApUtils.apprint(" [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]Attribute Count is : " + ApUtils.printhex(
        AttributeCount))

    # Class Attribute一般也没用，0x00000000
    ClassAttibute = ApUtils.little_endian(data[pc + 32:pc + 36])

    # Attributes
    for i in range(int(ApUtils.printhex(AttributeCount), 16)):
        att_namespace = ApUtils.little_endian(data[pc + 36 + i * 5 * 4:pc + 36 + i * 5 * 4 + 4])
        att_name = ApUtils.little_endian(data[pc + 36 + i * 5 * 4 + 4:pc + 36 + i * 5 * 4 + 4 + 4])
        att_valuestr = ApUtils.little_endian(data[pc + 36 + i * 5 * 4 + 4 + 4:pc + 36 + i * 5 * 4 + 4 + 4 + 4])
        att_type = ApUtils.little_endian(data[pc + 36 + i * 5 * 4 + 4 + 4 + 4:pc + 36 + i * 5 * 4 + 4 + 4 + 4 + 4])
        att_data = ApUtils.little_endian(
            data[pc + 36 + i * 5 * 4 + 4 + 4 + 4 + 4:pc + 36 + i * 5 * 4 + 4 + 4 + 4 + 4 + 4])
        # 打印
        #print(" ----------------------------------------------")
        if int(ApUtils.printhex(att_namespace), 16) <= len(config.global_list['STRINGPOOL']):
            ApUtils.apprint(
                "     [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]Attribute[" + str(i) + "]NameSpace is : " +
                config.global_list['STRINGPOOL'][int(ApUtils.printhex(att_namespace), 16)])
        else:
            ApUtils.apprint("     [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]Attribute[" + str(
                i) + "]NameSpace is null ")

        if int(ApUtils.printhex(att_name), 16) <= len(config.global_list['STRINGPOOL']):
            attr_name = config.global_list['STRINGPOOL'][int(ApUtils.printhex(att_name), 16)]
            ApUtils.apprint("     [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]Attribute[" + str(
                i) + "]Name is : " + attr_name)
            # 修改application name
            if NameStr == "application":
                if attr_name == "name":
                    config.set_value('APPLICATIONNAMEFLAG', 1)
                    config.set_value('APPLICATIONNAMEINDEX', pc + 36 + i * 5 * 4)
        else:
            ApUtils.apprint(
                "     [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]Attribute[" + str(i) + "]Name is null ")

        if int(ApUtils.printhex(att_valuestr), 16) <= len(config.global_list['STRINGPOOL']):
            ApUtils.apprint("     [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]Attribute[" + str(
                i) + "]Valus String is : " + config.global_list['STRINGPOOL'][int(ApUtils.printhex(att_valuestr), 16)])
        else:
            ApUtils.apprint("     [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]Attribute[" + str(
                i) + "]Valus String is null ")

        type = ApUtils.getAttrType(int(ApUtils.printhex(att_type), 16) >> 24)
        ApUtils.apprint(
            "     [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]Attribute[" + str(i) + "]Type is : " + type)

        dataAtt = ApUtils.getAttrData(int(ApUtils.printhex(att_type), 16) >> 24, att_data)
        ApUtils.apprint(
            "     [startTag" + str(config.get_value('TAGCOUNTSTAR')) + "]Attribute[" + str(i) + "]Data is : " + dataAtt)
    # 修改结束指针
    config.set_value('STARTTAGCHUNKEND', config.get_value('STARTTAGCHUNKSTAR') + int(ApUtils.printhex(ChunkSize), 16))


# 解析end tag chunk
def am_tagchunk_end(data, pc):
    # ChunkType:end Tag Chunk类型，固定四个字节0x00100103
    ChunkType = ApUtils.little_endian(data[pc:pc + 4])
    if ApUtils.printhex(ChunkType) == "0x00100103":
        ApUtils.apprint(" ===========Resolve Tag Chunk End=============")
        ApUtils.apprint(
            " [endTag" + str(config.get_value('TAGCOUNTEND')) + "]ChunkType is : " + ApUtils.printhex(ChunkType))
    else:
        ApUtils.apprint(" [Error" + str(config.get_value('TAGCOUNTEND')) + "]Tag Chunk end resolve error!")
        exit(-1)

    # Tag Chunk的大小（4）
    ChunkSize = ApUtils.little_endian(data[pc + 4:pc + 8])
    ApUtils.apprint(
        " [endTag" + str(config.get_value('TAGCOUNTEND')) + "]ChunkSize is : " + ApUtils.printhex(ChunkSize))

    # Line Number 行号（4）
    LineNumber = ApUtils.little_endian(data[pc + 8:pc + 12])
    ApUtils.apprint(
        " [endTag" + str(config.get_value('TAGCOUNTEND')) + "]LineNumber is : " + ApUtils.printhex(LineNumber))

    # Unknown未知区域（4）
    Unknown = ApUtils.little_endian(data[pc + 12:pc + 16])

    # Namespace Uri
    NameSpcae = ApUtils.little_endian(data[pc + 16:pc + 20])
    if int(ApUtils.printhex(NameSpcae), 16) <= len(config.global_list['STRINGPOOL']):
        ApUtils.apprint(
            " [endTag" + str(config.get_value('TAGCOUNTEND')) + "]NameSpace is : " + config.global_list['STRINGPOOL'][
                int(ApUtils.printhex(NameSpcae), 16)])
    else:
        ApUtils.apprint(" [endTag" + str(config.get_value('TAGCOUNTEND')) + "]NameSpace is : null")

    # name
    Name = ApUtils.little_endian(data[pc + 20:pc + 24])
    NameStr = config.global_list['STRINGPOOL'][int(ApUtils.printhex(Name), 16)]
    ApUtils.apprint(" [endTag" + str(config.get_value('TAGCOUNTEND')) + "]Tag name is : " + NameStr)

    # 修改结束指针
    config.set_value('ENDTAGCHUNKEND', config.get_value('ENDTAGCHUNKSTAR') + int(ApUtils.printhex(ChunkSize), 16))


# 解析textchunk
def am_textchunk(data, pc):
    # ChunkType:text chunk 类型，固定四个字节0x00100104
    ChunkType = ApUtils.little_endian(data[pc:pc + 4])
    if ApUtils.printhex(ChunkType) == "0x00100104":
        ApUtils.apprint(" ===========Resolve Text Chunk=============")
        ApUtils.apprint(" [textChunk]" + ApUtils.printhex(ChunkType))
    else:
        ApUtils.apprint(" [Error]Text Chunk resolve error!")
        exit(-1)

    # Tag Chunk的大小（4）
    ChunkSize = ApUtils.little_endian(data[pc + 4:pc + 8])
    ApUtils.apprint(" [textChunk]ChunkSize is : " + ApUtils.printhex(ChunkSize))

    # Line Number 行号（4）
    LineNumber = ApUtils.little_endian(data[pc + 8:pc + 12])
    ApUtils.apprint(" [textChunk]LineNumber is : " + ApUtils.printhex(LineNumber))

    # Unknown未知区域（4）
    Unknown = ApUtils.little_endian(data[pc + 12:pc + 16])

    # nameApUtils
    Name = ApUtils.little_endian(data[pc + 16:pc + 20])
    NameStr = config.global_list['STRINGPOOL'][int(ApUtils.printhex(Name), 16)]
    ApUtils.apprint(" [textChunk]Text name is : " + NameStr)

    # Unknown未知区域（4）
    Unknown1 = ApUtils.little_endian(data[pc + 20:pc + 24])

    # Unknown未知区域（4）
    Unknown2 = ApUtils.little_endian(data[pc + 24:pc + 28])

    config.set_value('TEXTCHUNKEND', config.get_value('TEXTCHUNKSTAR') + int(ApUtils.printhex(ChunkSize), 16))
