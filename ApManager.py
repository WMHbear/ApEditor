#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : ApManager.py
# @Author: WMH
# @Date  : 18-8-24
# @Desc  : ApEditor:对AndroidManifest.xml文件实现解析和application name替换

import config
import ApUtils
import ApResolver

#开始解析AndroidManifest.xml文件
def resolver(am_path):
    print "[ApEditor]Begin to resolve AndroidManifest.xml"
    #全局变量初始化
    config.init_global()

    # 读取二进制文件并转化成16进制
    data_hex = ApUtils.am_read(am_path)

    #开始解析头部
    ApResolver.am_header(data_hex)
    #解析后当前指针
    pc = config.get_value('AMHEADER')

    #解析StringChunk
    ApResolver.am_stringchunk(data_hex,pc)
    pc = config.get_value('STRINGCHUNKEND')

    #调整指针,预留16位
    config.set_value('RESOURCEIDCHUNKSTAR',pc)
    for ind in range(16):
        if ApUtils.printhex(ApUtils.little_endian(data_hex[pc+ind:pc+ind+4])) == "0x00080180":
            config.set_value('RESOURCEIDCHUNKSTAR',config.get_value('RESOURCEIDCHUNKSTAR') + ind)
            break
    pc = config.get_value('RESOURCEIDCHUNKSTAR')

    #解析resource chunk
    ApResolver.am_resourceidchunk(data_hex,pc)
    pc = config.get_value('RESOURCEIDCHUNKEND')
    #print pc

    #开始进入循环解析
    while pc <len(data_hex):
        #namespace start
        if ApUtils.printhex(ApUtils.little_endian(data_hex[pc:pc+4])) == "0x00100100":
            config.set_value('STARNAMESPACESTAR',pc)
            ApResolver.am_namespacechunk_star(data_hex,pc)
            pc = config.get_value('STARNAMESPACEEND')
        #tag start
        elif ApUtils.printhex(ApUtils.little_endian(data_hex[pc:pc+4])) == "0x00100102":
            config.set_value('STARTTAGCHUNKSTAR',pc)
            ApResolver.am_tagchunk_star(data_hex,pc)
            pc = config.get_value('STARTTAGCHUNKEND')
            config.set_value('TAGCOUNTSTAR', config.get_value('TAGCOUNTSTAR')+ 1)
        #tag end
        elif ApUtils.printhex(ApUtils.little_endian(data_hex[pc:pc+4])) == "0x00100103":
            config.set_value('ENDTAGCHUNKSTAR', pc)
            ApResolver.am_tagchunk_end(data_hex,pc)
            pc = config.get_value('ENDTAGCHUNKEND')
            config.set_value('TAGCOUNTEND', config.get_value('TAGCOUNTEND') + 1)
        # tag end
        elif ApUtils.printhex(ApUtils.little_endian(data_hex[pc:pc+4])) == "0x00100101":
            config.set_value('ENDNAMESPACESTAR',pc)
            ApResolver.am_namespacechunk_end(data_hex,pc)
            pc = config.get_value('ENDNAMESPACEEND')
        # text end
        elif ApUtils.printhex(ApUtils.little_endian(data_hex[pc:pc + 4])) == "0x00100104":
            config.set_value('TEXTCHUNKSTAR',pc)
            ApResolver.am_textchunk(data_hex, pc)
            pc = config.get_value('TEXTCHUNKEND')
        else:
            ApUtils.apprint("[error]NO type of the chunk,the pc is " +str(pc))
            exit(-1)

    #解析结束
    print "[ApEditor]Resolve AndroidManifest.xml success!!!"
    return data_hex

#第二个功能，修改application
def changeApplication(source_filepath,target_filepath,application_name):
    #用于存储修改之后的AM文件
    cp_data=[]

    #解析要修改的字符串
    data_string = ApUtils.encodeutf(application_name)

    #解析AM文件
    data_hex = resolver(source_filepath)
    print "[ApEditor]Begin to change application"

    #处理头部
    cp_data.extend(data_hex[0:config.get_value('FILSIZEINDEX')])
    #file size
    old_filesize = ApUtils.printhex(ApUtils.little_endian(data_hex[config.get_value('FILSIZEINDEX'):config.get_value('FILSIZEINDEX')+4]))
    new_filesize = int(old_filesize,16) + 4 + len(data_string)
    if config.get_value('APPLICATIONNAMEFLAG') == 0:
        #此时需要新加application中name属性
        new_filesize += 5*4
    cp_data.extend(ApUtils.encodehex(new_filesize))

    cp_data.extend(data_hex[config.get_value('FILSIZEINDEX')+4:config.get_value('STRINGCHUNKSIZEINDEX')])
    #String chunk size
    old_stringchunk_size = ApUtils.printhex(ApUtils.little_endian(data_hex[config.get_value('STRINGCHUNKSIZEINDEX'):config.get_value('STRINGCHUNKSIZEINDEX')+4]))
    new_stringchunk_size = int(old_stringchunk_size,16) + 4 + len(data_string)
    cp_data.extend(ApUtils.encodehex(new_stringchunk_size))

    cp_data.extend(data_hex[config.get_value('STRINGCHUNKSIZEINDEX')+4:config.get_value('STRINGCHUNKCOUNTINDEX')])
    #String chunk count
    old_stringchunk_count = ApUtils.printhex(ApUtils.little_endian(data_hex[config.get_value('STRINGCHUNKCOUNTINDEX'):config.get_value('STRINGCHUNKCOUNTINDEX')+4]))
    new_stringchunk_count = int(old_stringchunk_count,16) + 1
    cp_data.extend(ApUtils.encodehex(new_stringchunk_count))

    cp_data.extend(data_hex[config.get_value('STRINGCHUNKCOUNTINDEX')+4:config.get_value('STRINGPOOLOFFSETINDEX')])
    #Stringpool off set
    old_stringpool_offset = ApUtils.printhex(ApUtils.little_endian(data_hex[config.get_value('STRINGPOOLOFFSETINDEX'):config.get_value('STRINGPOOLOFFSETINDEX')+4]))
    new_stringpool_offset =int(old_stringpool_offset,16) + 4
    cp_data.extend(ApUtils.encodehex(new_stringpool_offset))

    #String off sets
    cp_data.extend(data_hex[config.get_value('STRINGPOOLOFFSETINDEX')+4:config.get_value('LASTSTRINGOFFSETSINDEX')+4])
    old_laststring_offsets = ApUtils.printhex(ApUtils.little_endian(data_hex[config.get_value('LASTSTRINGOFFSETSINDEX'):config.get_value('LASTSTRINGOFFSETSINDEX')+4]))
    new_laststring_offsets = int(old_laststring_offsets, 16) +(config.get_value('LASTSTRINGLEN')+2)*2
    cp_data.extend(ApUtils.encodehex(new_laststring_offsets))

    cp_data.extend(data_hex[config.get_value('LASTSTRINGOFFSETSINDEX')+4:config.get_value('LASTSTRINGINDEX')])
    #sting
    cp_data.extend(data_string)



    #修改applicaiton name
    if config.get_value('APPLICATIONNAMEFLAG') == 1:
        #此时application中含有android:name属性，直接修改字符串指针即可
        cp_data.extend(data_hex[config.get_value('LASTSTRINGINDEX'):config.get_value('APPLICATIONNAMEINDEX')])
        #namespace不用换
        cp_data.extend(data_hex[config.get_value('APPLICATIONNAMEINDEX'):config.get_value('APPLICATIONNAMEINDEX') + 4])
        #name不换
        cp_data.extend(data_hex[config.get_value('APPLICATIONNAMEINDEX')+4:config.get_value('APPLICATIONNAMEINDEX')+4+4])
        #valuesstr换,这里是下标，从0开始，因此-1
        cp_data.extend(ApUtils.encodehex(new_stringchunk_count-1))
        #type不换
        cp_data.extend(data_hex[config.get_value('APPLICATIONNAMEINDEX')+4+4+4:config.get_value('APPLICATIONNAMEINDEX')+4+4+4+4])
        #data换
        cp_data.extend(ApUtils.encodehex(new_stringchunk_count-1))

        cp_data.extend(data_hex[config.get_value('APPLICATIONNAMEINDEX')+4+4+4+4+4:])
    elif config.get_value('APPLICATIONNAMEFLAG') ==0:
        #此时application中没有android:name属性，新增一个属性
        cp_data.extend(data_hex[config.get_value('LASTSTRINGINDEX'):config.get_value('APPLICATIONPC')])
        #type不变
        cp_data.extend(data_hex[config.get_value('APPLICATIONPC'):config.get_value('APPLICATIONPC')+4])
        #size+5*4
        old_application_size = ApUtils.printhex(ApUtils.little_endian(data_hex[config.get_value('APPLICATIONPC')+4:config.get_value('APPLICATIONPC')+8]))
        new_application_size = int(old_application_size,16) +5*4
        cp_data.extend(ApUtils.encodehex(new_application_size))
        #linenumber+unknown+namespace+name+flag不变
        cp_data.extend(data_hex[config.get_value('APPLICATIONPC')+8:config.get_value('APPLICATIONPC') + 28])
        #Attribute count +1
        old_attr_count = ApUtils.printhex(ApUtils.little_endian(data_hex[config.get_value('APPLICATIONPC')+28:config.get_value('APPLICATIONPC')+32]))
        new_attr_count = int(old_attr_count,16) +1
        cp_data.extend(ApUtils.encodehex(new_attr_count))
        #class attribute
        cp_data.extend(data_hex[config.get_value('APPLICATIONPC') + 32:config.get_value('APPLICATIONPC') + 36])

        #接下来只需要解析一个属性即可，为了初始化一些基本字段
        old_attr_namespace = data_hex[config.get_value('APPLICATIONPC') + 36:config.get_value('APPLICATIONPC') + 40]
        #定位到name在Stringpool的index
        name_index = config.global_list['STRINGPOOL'].index("name")

        #拷贝剩下的属性
        attr_index = config.get_value('APPLICATIONPC') + 36 +5*int(old_attr_count,16)*4
        cp_data.extend(data_hex[config.get_value('APPLICATIONPC') + 36:attr_index])
        #新增name属性
        #namespace
        cp_data.extend(old_attr_namespace)
        #name
        cp_data.extend(ApUtils.encodehex(name_index))
        #valuestr
        cp_data.extend(ApUtils.encodehex(new_stringchunk_count - 1))
        #type,这里是String固定type
        cp_data.extend(["08","00","00","03"])
        #data
        cp_data.extend(ApUtils.encodehex(new_stringchunk_count - 1))

        #剩下的拷贝
        cp_data.extend(data_hex[attr_index:])
    else:
        print "[ERROR]There is something wrong with application resolve!!!"
        exit(-1)

    ApUtils.writedata(cp_data,target_filepath)
    #结束
    print "[ApEditor]Change Application success!!!"






if __name__ == '__main__':
    #测试用
    r=r"/home/xxxx/AndroidManifest.xml"
    r1 = r"/home/oooo/AndroidManifest.xml"
    # resolver(r)
    sr="com.test.FirstApplication"
    changeApplication(r,r1,sr)
