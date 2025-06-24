PORTS = [5000, 8080]

EMPTY = 0
LIGHT = 1
DARK = 2
OUTSIDE = 3

LIGHT_COLOR = "darkgoldenrod1"
DARK_COLOR = "dodgerblue3"

# N_LIGHT       = 0b1110_0000_0000_0000_0000_0000_0000_0000
# N_DARK        = 0b0001_1100_0000_0000_0000_0000_0000_0000
# LIGHT_SIDE    = 0b0000_0011_1111_0000_0000_0000_0000_0000
# DARK_SIDE     = 0b0000_0000_0000_1111_1100_0000_0000_0000
# MIDDLE        = 0b0000_0000_0000_0000_0011_1111_1111_1110
# TURN          = 0b0000_0000_0000_0000_0000_0000_0000_0001

# N_LIGHT_SHIFT       = 29
# N_DARK_SHIFT        = 26
# LIGHT_SIDE_SHIFT    = 20
# DARK_SIDE_SHIFT     = 14
# MIDDLE_SHIFT        = 1
# TURN_SHIFT          = 0

# game_state = 0b0000_0000_0000_0000_0000_0000_0000_0000
#                aaab_bbxx_xxxx_yyyy_yyzz_zzzz_zzzz_zzzt
# a -- # of light pieces off board
# b -- # of dark pieces off board
# x -- light sides of the board (0 unoccupied, 1 occupied)
# y -- dark sides of the board (0 unoccupied, 1 occupied)
# z -- middle row of the board in ternary (0 unoccupied, 1 occupied by light, 2 occupied by dark)
# t -- turn (0 light, 1 dark)