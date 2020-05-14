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
    HL_BP_COLOR,
    HL_CUR_INSN_COLOR,
)

from .helpers import (
    info,
    err,
    dbg,
    expose,
    is_exposed,
    ishex,
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
        self.__old_bps = set()
        self.__breakpoints = set()
        tag_type = bv.tag_types["Breakpoints"] if "Breakpoints" in bv.tag_types else Tag
        self.__bp_tag = bv.create_tag(tag_type, "GEF Breakpoint", True)
        self.__current_instruction = 0
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
        """ jump(int addr) => None
        Move the EA pointer to the address pointed by `addr`.
        Example: binaryninja jump 0x4049de
        """
        try:
            addr = int(address, 0)
            self.view.offset = addr
            return True
        except:
            pass
        return False

    @expose
    def makecomm(self, address, comment):
        """ makecomm(int addr, string comment) => None
        Add a comment at the location `address`.
        Example: binaryninja makecomm 0x40000 "Important call here!"
        """
        addr = int(address, 0)
        start_addr = self.view.get_previous_function_start_before(addr)
        func = self.view.get_function_at(start_addr)
        return func.set_comment(addr, comment)

    @expose
    def setcolor(self, address, color='0xff0000'):
        """ setcolor(int addr [, int color]) => None
        Set the location pointed by `address` with `color`.
        Example: binaryninja setcolor 0x40000 0xff0000
        """
        addr = int(address, 0)
        color = int(color, 0)
        R,G,B = (color >> 16)&0xff, (color >> 8)&0xff, (color&0xff)
        color = highlight.HighlightColor(red=R, blue=G, green=B)
        return self.highlight(addr, color)

    @expose
    def sync(self, off, added, removed):
        """ sync(off, added, removed) => None
        Synchronize debug info with gef. This is an internal function. It is not recommended using it from the command line.
        Example: binaryninja sync
        """
        off = int(off, 0)
        pc = self.base + off
        if DEBUG: log_info("[*] current_pc=%#x , old_pc=%#x" % (pc, self.__current_instruction))

        # unhighlight the _current_instruction
        if self.__current_instruction > 0:
            self.highlight(self.__current_instruction, HL_NO_COLOR)
        self.highlight(pc, HL_CUR_INSN_COLOR)

        # update the _current_instruction
        self.__current_instruction = pc
        self.jump(self.__current_instruction)

        dbg("pre-gdb-add-breakpoints: %s" % (added,))
        dbg("pre-gdb-del-breakpoints: %s" % (removed,))
        dbg("pre-binja-breakpoints: %s" % (self.__breakpoints))

        bn_added = [ x-self.base for x in self.__breakpoints if x not in self.__old_bps ]
        bn_removed = [ x-self.base for x in self.__old_bps if x not in self.__breakpoints ]

        for bp in added:
            self.add_breakpoint(self.view, self.base + bp)

        for bp in removed:
            self.delete_breakpoint(self.view, self.base + bp)

        self.__old_bps = copy.deepcopy(self.__breakpoints)

        dbg("post-gdb-add-breakpoints: %s" % (bn_added,))
        dbg("post-gdb-del-breakpoints: %s" % (bn_removed,))
        dbg("post-binja-breakpoints: %s" % (self.__breakpoints,))
        return [bn_added, bn_removed]



    def highlight(self, addr, color):
        dbg("hl(%#x, %s)" % (addr, color))
        start_addr = self.view.get_previous_function_start_before(addr)
        func = self.view.get_function_at(start_addr)
        if func is None:
            return
        func.set_user_instr_highlight(addr, color)
        return


    def add_breakpoint(self, bv, addr):
        if addr in self.__breakpoints:
            return False

        self.__breakpoints.add(addr)
        info("Breakpoint {:#x} added".format(addr))
        self.highlight(addr, HL_BP_COLOR)
        self.view.add_user_data_tag(addr, self.__bp_tag)
        return True


    def delete_breakpoint(self, bv, addr):
        if addr not in self.__breakpoints:
            return False

        self.__breakpoints.discard(addr)
        info("Breakpoint {:#x} removed".format(addr))
        self.highlight(addr, HL_NO_COLOR)
        self.view.remove_user_data_tag(addr, self.__bp_tag)
        return True



class BinjaGefRequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)