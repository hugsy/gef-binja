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
    RunInBackground,
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


__service_thread = None
__gef_instance = None


def is_service_started():
    global __service_thread
    return __service_thread is not None


def gef_add_breakpoint(bv, addr):
    global __gef_instance
    if __gef_instance is None:
        return False
    return __gef_instance.add_breakpoint(bv, addr)


def gef_del_breakpoint(bv, addr):
    global __gef_instance
    if __gef_instance is None:
        return False
    return __gef_instance.delete_breakpoint(bv, addr)


def register_gef_breakpoint_menu():
    # Binja does not really support menu in its GUI just yet
    PluginCommand.register_for_address(
        "GEF\\Set breakpoint",
        "Add a breakpoint in gef at the specified location.",
        gef_add_breakpoint,
        is_valid = lambda view, addr: is_service_started()
    )

    PluginCommand.register_for_address(
        "GEF\\Delete breakpoint",
        "Remove a breakpoint in gef at the specified location.",
        gef_del_breakpoint,
        is_valid = lambda view, addr: is_service_started()
    )
    return


def start_service(host, port, bv):
    """ Starting the service """
    global __gef_instance
    info("Starting service on {}:{}".format(host, port))
    server = xmlrpc.server.SimpleXMLRPCServer(
        (host, port),
        requestHandler=BinjaGefRequestHandler,
        logRequests=False,
        allow_none=True
    )
    server.register_introspection_functions()
    __gef_instance = Gef(server, bv)
    server.register_instance(__gef_instance)
    dbg("Registered {} functions.".format( len(server.system_listMethods()) ))
    while True:
        if hasattr(server, "shutdown") and server.shutdown==True: break
        server.handle_request()
    return


def shutdown_service():
    try:
        cli = xmlrpc.client.ServerProxy("http://{:s}:{:d}".format(HOST, PORT))
        cli.shutdown()
    except socket.error:
        pass


def stop_service():
    """ Stopping the service """
    global __service_thread
    dbg("Trying to stop service thread")
    shutdown_service()
    __service_thread.join()
    __service_thread = None
    info("Server stopped")
    return


def gef_start(bv):
    global __service_thread
    dbg("Starting background service...")
    __service_thread = threading.Thread(target=start_service, args=(HOST, PORT, bv))
    __service_thread.daemon = True
    __service_thread.start()
    register_gef_breakpoint_menu()
    show_message_box(
        "GEF",
        "Service successfully started, you can now have gef connect to it",
        MessageBoxButtonSet.OKButtonSet,
        MessageBoxIcon.InformationIcon
    )
    return


def gef_stop(bv):
    "Stopping background service... "
    stop_service()
    show_message_box(
        "GEF",
        "Service successfully stopped",
        MessageBoxButtonSet.OKButtonSet,
        MessageBoxIcon.InformationIcon
    )
    return


PluginCommand.register(
    "GEF\\Start service",
    "Start the service for communicating with gef",
    gef_start,
    is_valid = lambda view: not is_service_started()
)


PluginCommand.register(
    "GEF\\Stop service",
    "Stop the service for communicating with gef",
    gef_stop,
    is_valid = lambda view: is_service_started()
)