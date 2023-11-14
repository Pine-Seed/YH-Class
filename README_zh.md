# YH-Class

[EN](https://github.com/Pine-Seed/YH-Class/blob/main/README.md)|[简中](https://github.com/Pine-Seed/YH-Class/blob/main/README_zh.md)

基于Python开发的某课堂视频学习工具

------

本项目遵循MIT开源协议，仅供学习技术交流，请在没有违反当地法律法规的情况下进行使用与二次开发等

- 24小时无人监管随时学习，可挂后台
- 多账号可多开【支持同一账号多开学习不同课程，但是同一账号同一课程下请勿多开（未实验可能有风险，请谨慎多开）】
- 可模拟多个机型进行学习，拥有完善的防检测功能

------

从此链接下载可执行程序：https://github.com/Pine-Seed/YH-Class/releases

### 使用方法

#### Windows

直接打开`exe`可执行程序即可使用

#### Linux

请自行配置`Python>=3.8`环境，使用`install.sh`安装所需库，然后`run.sh`运行

### 配置文件操作

在程序目录下新建文件“yh_class.txt”，程序会自动识别配置文件中的内容，此配置文件中的内容以标准JSON格式编写，每条配置可写可不写，无配置文件也可正常使用程序，以下是一个例子

```json
{
    "url": "你的学校课堂网址/域名",
    "username": "你的账号",
    "password": "你的密码",
    "user_agent": {
                       "设备名称1": "此设备的User-Agent",
                       "设备名称2": "此设备的User-Agent"
                  }
}
```

#### 可配置内容

| 配置项     | 值                                   | 说明                                |
| ---------- | ------------------------------------ | ----------------------------------- |
| url        | 学校课堂网址域名                     |                                     |
| username   | 账号                                 |                                     |
| password   | 密码                                 |                                     |
| user_agent | 自定义设备User-Agent，可定义多个设备 | 值为字典："设备名":"设备User-Agent" |

