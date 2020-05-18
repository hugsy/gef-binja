# GEF-Binja

Author: **@hugsy**

Interface easily [GDB-GEF](https://github.com/hugsy/gef) with [Binary Ninja](https://binary.ninja)



## Description

`gef-binja` is a plugin that is the server-side of the XML-RPC defined for gef for BinaryNinja.
It will spawn a threaded XMLRPC server from your current BN session making it possible for gef to interact with Binary Ninja.


## Youtube Tutorial

[![](https://i.imgur.com/xvoUACt.png)](https://www.youtube.com/watch?v=QJKmcZumWyA)


### Installation

#### GUI installation

In Binary Ninja, press `Ctrl-Shift-M` to open the Plugin Manager. Then search for `GEF-Binja` and install it.


#### Manual installation

##### Linux

```bash
$ git clone https://github.com/hugsy/gef-binja/ "~/.binaryninja/plugins/gef-binja"
```

##### Windows

```powershell
PS :\> git clone https://github.com/hugsy/gef-binja  "$Env:APPDATA\Binary Ninja\plugins\gef-binja"
```


##### Darwin

Untested but should work

```bash
$ git clone https://github.com/hugsy/gef-binja/ "~/Library/Application Support/Binary Ninja/plugins/gef-binja"
```

#### GEF Installation

If you don't have [`gef`](https://github.com/hugsy/gef) on the host where your GDB is running, the quickest way to install it is by running the following command from a shell prompt:


```bash
wget -q -O- https://github.com/hugsy/gef/raw/master/scripts/gef.sh | sh
```

In GDB, configure `gef` to connect to Binary Ninja:

```
gef➤  gef config ida-interact
```

*Note*: the config option is called `ida-interact` because GEF uses the same protocol for both communication with Binja and IDA.


## Minimum Version

This plugin requires the following minimum version of Binary Ninja:

 * 1300



## Required Dependencies

The following dependencies are required for this plugin:

 * apt - gdb 7.7+ (or gdb-multiarch) with Python3 support
 * other - https://github.com/hugsy/gef ([easy install](https://github.com/hugsy/gef#instant-setup))


## License

This plugin is released under a MIT license.


## Metadata Version

2
