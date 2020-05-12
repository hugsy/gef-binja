# GEF-Binja

Author: **@hugsy**

Interface [GDB-GEF](https://github.com/hugsy/gef) with Binary Ninja



## Description

`gef-binja` is a plugin that is the server-side of the XML-RPC defined for gef for BinaryNinja.
It will spawn a threaded XMLRPC server from your current BN session making it possible for gef to interact with Binary Ninja.


## Youtube Tutorial

[![](https://i.imgur.com/xvoUACt.png)](https://www.youtube.com/watch?v=QJKmcZumWyA)



### GUI installation

(soon available directly from the Plugin Manager)


### Manual installation

#### Linux

```bash
$ git clone https://github.com/hugsy/gef-binja/ "~/.binaryninja/plugins/gef-binja"
```

#### Windows

```powershell
PS :\> git clone https://github.com/hugsy/gef-binja  "$Env:APPDATA\Binary Ninja\plugins\gef-binja"
```


#### Darwin

Untested but should work

```bash
$ git clone https://github.com/hugsy/gef-binja/ "~/Library/Application Support/Binary Ninja/plugins/gef-binja"
```



## Minimum Version

This plugin requires the following minimum version of Binary Ninja:

 * 1200



## Required Dependencies

The following dependencies are required for this plugin:

 * apt - gdb 7.7+ (or gdb-multiarch) with Python3 support
 * other - https://github.com/hugsy/gef ([easy install](https://github.com/hugsy/gef#instant-setup))


## License

This plugin is released under a MIT license.


## Metadata Version

2
