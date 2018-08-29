# ApEditor

Application Name修改器（Python2、3）

## 项目介绍

针对`AndroidManife.xml`文件进行解析，并修改其中的`Application Name`为指定字段，若Application标签中没有name属性，则会`增加`name属性并修改为指定字段

## 使用方法

### 修改AplicationName功能

[**ApEditor**](https://github.com/WMHbear/ApEditor)的第一个功能是修改AndroidManifest.xml文件中的Application name属性为指定名称，对于Application标签中没有name属性的情况则会自动增加name属性为指定名称。

* 输入命令

    ```
    ApManager.changeApplication(source_filepath,target_filepath,application_name)  
    ```
    
* 参数说明

    ```
    source_filepath    : 需要修改的AndroidManifest.xml文件路径
    target_filepath      : 修改后的AndroidManifest.xml文件路径
    application_name : 需要替换的Application Name
    ```
    
### 解析AndroidManifest.xml功能

[**ApEditor**](https://github.com/WMHbear/ApEditor)的第二个功能是解析AndroidManifest.xml文件并将解析的结果打印。

* 修改ApUtils文件参数

>若想打印结果，则需修改ApUtils文件中的apprint函数，将参数默认值修改

```
    def apprint(print_string,default = False):
```
   
>修改默认参数，改为：
  
 
```
    def apprint(print_string,default = True):
```

* 输入命令

    ```
    ApManager.resolver(source_filepath)
    ```
   
 * 参数说明
 
     ```
     source_filepath : 需要解析的AndroidManifest.xml文件路径
     ```
 
## 特别提示

* 版本升级

*此工具使用python2编写，若想升级至python3，只需修改ApUtils.apprint中的打印函数及ApManager中的print函数即可*

* 更新

*2018/8/29更新：已经支持python3，涉及到的一些打印和编码已经修改，python3对应代码在ApEditor3中*

* 解析时部分字符串无法解析

*由于编码等原因，部分字符串会出现无法解析的情况，此时不影响application name的替换功能*


