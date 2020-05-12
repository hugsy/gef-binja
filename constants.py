from binaryninja import enums


DEBUG = True # change to True for a way more verbose output

# Python XML-RPC is highly insecure as it allows anyone
# to execute code on the server. It is recommended to change
# the host listening IP address to a HostOnly LAN address.
HOST, PORT = "0.0.0.0", 1337

# Adjust to your liking between the following colors:
# - HighlightStandardColor.NoHighlightColor
# - HighlightStandardColor.BlueHighlightColor
# - HighlightStandardColor.GreenHighlightColor
# - HighlightStandardColor.CyanHighlightColor
# - HighlightStandardColor.RedHighlightColor
# - HighlightStandardColor.MagentaHighlightColor
# - HighlightStandardColor.YellowHighlightColor
# - HighlightStandardColor.OrangeHighlightColor
# - HighlightStandardColor.WhiteHighlightColor
# - HighlightStandardColor.BlackHighlightColor
HL_NO_COLOR = enums.HighlightStandardColor.NoHighlightColor
HL_BP_COLOR = enums.HighlightStandardColor.RedHighlightColor
HL_CUR_INSN_COLOR = enums.HighlightStandardColor.GreenHighlightColor

#
# Some runtime constants
#
PAGE_SIZE = 0x1000