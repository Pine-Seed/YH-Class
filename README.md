# YH-Class

[EN](https://github.com/Pine-Seed/YH-Class/blob/main/README.md)|[简中](https://github.com/Pine-Seed/YH-Class/blob/main/README_zh.md)

A classroom video learning tool developed based on Python

------

This project follows the MIT open-source license and is intended for educational and technical communication only. Please use and develop it further only if it does not violate local laws and regulations.

- 24-hour unattended learning, can run in the background
- Supports multiple accounts and simultaneous use [Supports the same account to learn different courses at the same time, but please do not use the same account for the same course simultaneously (not tested, may be risky, use with caution)]
- It can simulate multiple models for learning and has comprehensive anti detection functions

------

Download the executable program from this link: https://github.com/Pine-Seed/YH-Class/releases

### How to Use

#### Windows

Simply open the `exe` executable program to use.

#### Linux

Please configure `Python>=3.8` environment yourself, use `install.sh` to install the required libraries, and then run `run.sh`.

### Configuration File Operation

Create a new file “yh_class.txt” in the program directory. The program will automatically recognize the contents of the configuration file. The contents of this configuration file are written in standard JSON format. Each configuration can be included or omitted. The program can also run normally without a configuration file. Here is an example:

```json
{
    "url": "Your school website",
    "username": "Your username",
    "password": "Your password",
    "user_agent": {
                       "Device Name one": "The UserAgent for this device",
                       "Device Name two": "The UserAgent for this device"
                  }
}
```

#### Configurable content

| Configuration item | Value                                                       | Illustrate                                                  |
| ------------------ | ----------------------------------------------------------- | ----------------------------------------------------------- |
| url                | Domain name of school classroom website                     |                                                             |
| username           | account number                                              |                                                             |
| password           | password                                                    |                                                             |
| user_agent         | Custom device User Agent, which can define multiple devices | The value is Dictionary: "Device Name": "Device User Agent" |
