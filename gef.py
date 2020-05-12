import copy
import inspect


from binaryninja import (
    core_version,
    log_info,
    highlight,

)

from .constants import (
    PAGE_SIZE,
    DEBUG,
    HL_NO_COLOR,
    HL_CUR_INSN_COLOR,
)

from .helpers import (
    info,
    err,
    dbg,
    expose,
    is_exposed,
    ishex,
    g_breakpoints,
    g_current_instruction,
    hl,
    add_gef_breakpoint,
    delete_gef_breakpoint,
)

from xmlrpc.server import (
    SimpleXMLRPCRequestHandler,
    SimpleXMLRPCServer,
    list_public_methods
)





class Gef:
    """
    Top-level XMLPRC class where exposed methods are declared.
    """

    def __init__(self, server, bv, *args, **kwargs):
        self.server = server
        self.view = bv
        self.base = bv.entry_point & ~(PAGE_SIZE-1)
        self._version = ("Binary Ninja", core_version())
        self.old_bps = set()
        return


    def _dispatch(self, method, params):
        """
        Plugin dispatcher
        """
        func = getattr(self, method)
        if not is_exposed(func):
            raise NotImplementedError('Method "%s" is not exposed' % method)

        dbg("Executing %s(%s)" % (method, params))
        return func(*params)


    def _listMethods(self):
        """
        Class method listing (required for introspection API).
        """
        m = []
        for x in list_public_methods(self):
            if x.startswith("_"): continue
            if not is_exposed( getattr(self, x) ): continue
            m.append(x)
        return m


    def _methodHelp(self, method):
        """
        Method help (required for introspection API).
        """
        f = getattr(self, method)
        return inspect.getdoc(f)

    @expose
    def shutdown(self):
        """ shutdown() => None
        Cleanly shutdown the XML-RPC service.
        Example: binaryninja shutdown
        """
        self.server.server_close()
        log_info("[+] XMLRPC server stopped")
        setattr(self.server, "shutdown", True)
        return 0

    @expose
    def version(self):
        """ version() => None
        Return a tuple containing the tool used and its version
        Example: binaryninja version
        """
        return self._version

    @expose
    def jump(self, address):
        """ Jump(int addr) => None
        Move the EA pointer to the address pointed by `addr`.
        Example: binaryninja Jump 0x4049de
        """
        addr = int(address, 0)
        return self.view.file.navigate(self.view.file.view, addr)

    @expose
    def makecomm(self, address, comment):
        """ MakeComm(int addr, string comment) => None
        Add a comment at the location `address`.
        Example: binaryninja MakeComm 0x40000 "Important call here!"
        """
        addr = int(address, 0)
        start_addr = self.view.get_previous_function_start_before(addr)
        func = self.view.get_function_at(start_addr)
        return func.set_comment(addr, comment)

    @expose
    def setcolor(self, address, color='0xff0000'):
        """ SetColor(int addr [, int color]) => None
        Set the location pointed by `address` with `color`.
        Example: binaryninja SetColor 0x40000 0xff0000
        """
        addr = int(address, 0)
        color = int(color, 0)
        R,G,B = (color >> 16)&0xff, (color >> 8)&0xff, (color&0xff)
        color = highlight.HighlightColor(red=R, blue=G, green=B)
        return hl(self.view, addr, color)

    @expose
    def sync(self, off, added, removed):
        """ Sync(off, added, removed) => None
        Synchronize debug info with gef. This is an internal function. It is
        not recommended using it from the command line.
        """
        global g_current_instruction

        off = int(off, 0)
        pc = self.base + off
        if DEBUG: log_info("[*] current_pc=%#x , old_pc=%#x" % (pc, g_current_instruction))

        # unhighlight the _current_instruction
        if g_current_instruction > 0:
            hl(self.view, g_current_instruction, HL_NO_COLOR)
        hl(self.view, pc, HL_CUR_INSN_COLOR)

        # update the _current_instruction
        g_current_instruction = pc


        dbg("pre-gdb-add-breakpoints: %s" % (added,))
        dbg("pre-gdb-del-breakpoints: %s" % (removed,))
        dbg("pre-binja-breakpoints: %s" % (g_breakpoints))

        bn_added = [ x-self.base for x in g_breakpoints if x not in self.old_bps ]
        bn_removed = [ x-self.base for x in self.old_bps if x not in g_breakpoints ]

        for bp in added:
            add_gef_breakpoint(self.view, self.base + bp)

        for bp in removed:
            delete_gef_breakpoint(self.view, self.base + bp)

        self.old_bps = copy.deepcopy(g_breakpoints)

        dbg("post-gdb-add-breakpoints: %s" % (bn_added,))
        dbg("post-gdb-del-breakpoints: %s" % (bn_removed,))
        dbg("post-binja-breakpoints: %s" % (g_breakpoints,))
        return [bn_added, bn_removed]




class BinjaGefRequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)