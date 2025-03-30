import argparse

from chip8 import Chip8

parser = argparse.ArgumentParser(description="Chip8 Emulator/Interpreter")
parser.add_argument("-r", "--rom", default="pong2.ch8", help="Path to the ROM file")
parser.add_argument(
    "-s", "--scale", type=int, default=10, help="Scale factor for the screen dimensions"
)
parser.add_argument(
    "-i",
    "--instructions",
    type=int,
    default=11,
    help="Instructions to execute per frame",
)


if __name__ == "__main__":
    args = parser.parse_args()
    c = Chip8(scale=args.scale, instructions_per_frame=args.instructions)
    c.load_rom(args.rom)
    c.run()
