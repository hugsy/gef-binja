from binaryninja import (
    log_info,
    log_debug,
    log_error,
)

from .constants import (
    DEBUG,
    HL_BP_COLOR,
    HL_NO_COLOR,
)


g_breakpoints = set()

g_current_instruction = 0


def expose(f):
    "Decorator to set exposed flag on a function."
    f.exposed = True
    return f


def is_exposed(f):
    "Test whether another function should be publicly exposed."
    return getattr(f, 'exposed', False)


def ishex(s):
    return s.lower().startswith("0x") and map(lambda c: c in "0123456789abcdef", s[2:].lower())


def info(x):
    log_info("[+] {:s}".format(x))

def err(x):
    log_error("[-] {:s}".format(x))

def dbg(x):
    if DEBUG:
        log_debug("[*] {:s}".format(x))


def hl(bv, addr, color):
    dbg("hl(%#x, %s)" % (addr, color))
    start_addr = bv.get_previous_function_start_before(addr)
    func = bv.get_function_at(start_addr)
    if func is None:
        return
    func.set_user_instr_highlight(addr, color)
    return


def add_gef_breakpoint(bv, addr):
    global  g_breakpoints
    if addr in g_breakpoints: return False
    g_breakpoints.add(addr)
    info("Breakpoint {:#x} added".format(addr))
    hl(bv, addr, HL_BP_COLOR)
    return True


def delete_gef_breakpoint(bv, addr):
    global g_breakpoints
    if addr not in g_breakpoints: return False
    g_breakpoints.discard(addr)
    info("Breakpoint {:#x} removed".format(addr))
    hl(bv, addr, HL_NO_COLOR)
    return True