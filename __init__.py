# from binaryninja import *
#
# def do_nothing(bv,function):
# 	show_message_box("Do Nothing", "Congratulations! You have successfully done nothing.\n\n" +
# 					 "Pat yourself on the back.", MessageBoxButtonSet.OKButtonSet, MessageBoxIcon.ErrorIcon)
#
# PluginCommand.register_for_address("Useless Plugin", "Basically does nothing", do_nothing)

"""
This script is the server-side of the XML-RPC defined for gef for
BinaryNinja.
It will spawn a threaded XMLRPC server from your current BN session
making it possible for gef to interact with Binary Ninja.

To install this script as a plugin:
$ ln -sf /path/to/gef/binja_gef.py ~/.binaryninja/plugins/binaryninja_gef.py

Then run it from Binary Ninja:
- open a disassembly session
- click "Tools" -> "gef : start/stop server"

If all went well, you will see something like
[+] Creating new thread for XMLRPC server: Thread-1
[+] Starting XMLRPC server: 0.0.0.0:1337
[+] Registered 10 functions.

@_hugsy_
"""

import socket
import threading
import xmlrpc.server, xmlrpc.client



from binaryninja import (
    log_info,
    PluginCommand,
    show_message_box,
    MessageBoxButtonSet,
    MessageBoxIcon,
)

from .helpers import (
    info,
    err,
    dbg,
    add_gef_breakpoint,
    delete_gef_breakpoint,
)

from .constants import (
    HOST,
    PORT,
    DEBUG,
    HL_NO_COLOR,
    HL_BP_COLOR,
    HL_CUR_INSN_COLOR,
)

from .gef import (
    Gef,
    BinjaGefRequestHandler,
)


__service_started = False
__service_thread = None



def create_binja_menu():
    # Binja does not really support menu in its GUI just yet
    PluginCommand.register_for_address(
        "gef : add breakpoint",
        "Add a breakpoint in gef at the specified location.",
        add_gef_breakpoint
    )

    PluginCommand.register_for_address(
        "gef : delete breakpoint",
        "Remove a breakpoint in gef at the specified location.",
        delete_gef_breakpoint
    )
    return


def start_service(host, port, bv):
    info("Starting service on {}:{}".format(host, port))
    server = xmlrpc.server.SimpleXMLRPCServer(
        (host, port),
        requestHandler=BinjaGefRequestHandler,
        logRequests=False,
        allow_none=True
    )
    server.register_introspection_functions()
    server.register_instance(Gef(server, bv))
    dbg("Registered {} functions.".format( len(server.system_listMethods()) ))
    while True:
        if hasattr(server, "shutdown") and server.shutdown==True: break
        server.handle_request()
    return


def gef_start(bv):
    global __service_thread, __service_started
    __service_thread = threading.Thread(target=start_service, args=(HOST, PORT, bv))
    __service_thread.daemon = True
    __service_thread.start()
    dbg("Started new thread '{}'".format(__service_thread.name))

    if not __service_started:
        create_binja_menu()
        __service_started = True
    return


def gef_stop(bv):
    global __service_thread
    __service_thread.join()
    __service_thread = None
    info("Server stopped")
    return


def gef_start_stop(bv):
    if __service_thread is None:
        dbg("Trying to start service thread")
        gef_start(bv)
        show_message_box(
            "GEF",
            "Service successfully started, you can now have gef connect to it",
            MessageBoxButtonSet.OKButtonSet,
            MessageBoxIcon.InformationIcon
        )

    else:
        dbg("Trying to stop service thread")
        try:
            cli = xmlrpc.client.ServerProxy("http://{:s}:{:d}".format(HOST, PORT))
            cli.shutdown()
        except socket.error:
            pass

        gef_stop(bv)
        show_message_box(
            "GEF",
            "Service successfully stopped",
            MessageBoxButtonSet.OKButtonSet,
            MessageBoxIcon.InformationIcon
        )
    return







PluginCommand.register(
    "Start/stop server GEF interaction",
    "Start/stop the XMLRPC server for communicating with gef",
    gef_start_stop
)