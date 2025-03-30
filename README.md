# Chip-8 Emulator in Python

This repository provides a simple implementation of the [Chip-8](#what-is-chip-8) virtual machine in Python using Pygame for graphics and audio. You can use this emulator to play classic Chip-8 games or run test ROMs. Demo can be found on [YouTube](https://www.youtube.com/watch?v=C0t2sXF5C34).

## Table of Contents

1. [What is Chip-8?](#what-is-chip-8)
2. [Project Structure](#project-structure)
3. [Key Features](#key-features)
4. [Setup and Installation](#setup-and-installation)
5. [Usage](#usage)
6. [Key Mapping](#key-mapping)
7. [Where to Get ROMs?](#where-to-get-roms)
8. [References & Further Reading](#references--further-reading)

---

## What is Chip-8?

Chip-8 is a simple, interpreted programming language designed in the 1970s to make game development easier on systems with limited resources. It’s often referred to as a “virtual machine” or “virtual system” because it specifies its own set of opcodes, memory layout, and display capabilities rather than running directly on physical hardware. Here are some key characteristics of the Chip-8 system:

- **Memory**: 4 KB (4,096 bytes)
- **CPU Registers**:
  - 16 8-bit data registers (`V0` to `VF`)
  - 16-bit address register (`I`)
  - Two special 8-bit registers used for timing: **delay** and **sound** timers
- **Screen Resolution**: 64×32 monochrome pixels
- **Keypad**: A hexadecimal (16-key) keypad
- **Program Counter**: Typically starts at address `0x200`, where the loaded program (ROM) resides
- **Stack**: Used for subroutines, can typically hold up to 16 return addresses

The Chip-8 specification has roughly 35 instructions/opcodes, which handle drawing sprites, keyboard input, timers, subroutine calls, conditional statements, and more. This simplicity makes Chip-8 an excellent platform for learning emulation concepts.

---

## Project Structure

```
.
├── chip8.py       # Core implementation of the Chip-8 interpreter/emulator
├── main.py        # Entry point: parse CLI args, load the ROM, and run the emulator
├── beep.wav       # Sound file used for the Chip-8 sound timer
└── README.md      # This file
```

### `chip8.py`
- **Memory Initialization**: 4 KB of memory (`MEMORY_SIZE = 4096`), with the interpreter-reserved area from `0x000` to `0x1FF`, and the program start at `0x200`.
- **Registers**: 16 general-purpose registers (`V0` through `VF`) and an index register (`I`).
- **Opcodes**: Each instruction is fetched (two consecutive bytes form one opcode) and decoded. Then the emulator executes the corresponding behavior (e.g., display manipulation, memory operations, register updates, etc.).
- **Timers**: The delay and sound timers are decremented at 60 Hz. The sound timer emits a beep when set to a nonzero value.
- **Display**: A 64×32 monochrome display stored in a 2D list. Each pixel is either on (1) or off (0).
- **Keyboard**: The keyboard state is stored in a 16-element boolean list, each element corresponding to a Chip-8 key. Pygame is used to detect actual key presses and map them to the Chip-8's key layout.

### `main.py`
- Simple command-line interface to:
  - Specify the ROM file to load (`--rom`)
  - Adjust the scale factor for the display (`--scale`)
  - Control the number of instructions to execute per frame (`--instructions`)
- Loads and runs the Chip-8 emulator.

---

## Key Features

1. **Instruction Set**: Implements all core Chip-8 opcodes, including drawing, memory/register operations, timers, jumps, conditionals, and more.
2. **Timers and Sound**: The implementation correctly handles the delay and sound timers. A `beep.wav` file is played when the sound timer is nonzero.
3. **Keyboard Support**: The hex-based keypad is mapped to your PC keyboard via Pygame.
4. **Sprite Drawing**: Sprites are 8 bits wide and up to 15 rows tall (in classic Chip-8). The display is XOR-drawn for basic sprite collision detection.

---

## Setup and Installation

1. **Clone or Download** this repository.
2. Ensure you have [Python 3](https://www.python.org/) installed.
3. Install the required dependencies:
   ```bash
   poetry install
   ```
4. Place a valid `beep.wav` file in the same directory (one is included if you have the repository as-is).

---

## Usage

1. **Open a Terminal** in the project directory.
2. **Run the Emulator** with the desired ROM:
   ```bash
   python main.py --rom path/to/your_rom.ch8
   ```
   Or use the provided defaults (by default, it tries to load `pong2.ch8`):
   ```bash
   python main.py
   ```

### Command-Line Arguments

| Argument           | Short | Default       | Description                                               |
|--------------------|-------|---------------|-----------------------------------------------------------|
| `--rom`            | `-r`  | `pong2.ch8`   | Path to the ROM file to load.                             |
| `--scale`          | `-s`  | `10`          | Scale factor for the screen’s rendering.                  |
| `--instructions`   | `-i`  | `11`          | Number of instructions to execute per frame.              |

Example usage:
```bash
python main.py -r INVADERS.ch8 -s 10 -i 12
```
This runs the `INVADERS.ch8` ROM with a scaling factor of 10 and executes 12 instructions per frame.

---

## Key Mapping

By default, Chip-8 has a 16-key hexadecimal keypad:

```
1 2 3 C
4 5 6 D
7 8 9 E
A 0 B F
```

This emulator maps them to your keyboard as follows:

| Chip-8 Key | Mapped PC Key |
|------------|---------------|
| `0x1`      | `1`           |
| `0x2`      | `2`           |
| `0x3`      | `3`           |
| `0xC`      | `4`           |
| `0x4`      | `Q`           |
| `0x5`      | `W`           |
| `0x6`      | `E`           |
| `0xD`      | `R`           |
| `0x7`      | `A`           |
| `0x8`      | `S`           |
| `0x9`      | `D`           |
| `0xE`      | `F`           |
| `0xA`      | `Z`           |
| `0x0`      | `X`           |
| `0xB`      | `C`           |
| `0xF`      | `V`           |

Pressing <kbd>ESC</kbd> will exit the emulator.

---

## Where to Get ROMs?

- **Test ROMs**: You can use the [Timendus chip8-test-suite](https://github.com/Timendus/chip8-test-suite) to verify that the emulator’s instruction set works correctly.
- **Game ROMs**: A variety of Chip-8 game ROMs can be found in [badlogic’s chip8 repository](https://github.com/badlogic/chip8/tree/master/roms).

Simply place any `.ch8` or `.rom` file in the project directory (or specify the full path to it), then use the command-line arguments to load it.

---

## References & Further Reading

1. [Chip-8 Test Suite (Timendus)](https://github.com/Timendus/chip8-test-suite)
2. [Game ROMs (badlogic’s repo)](https://github.com/badlogic/chip8/tree/master/roms)
3. [Wikipedia - CHIP-8](https://en.wikipedia.org/wiki/CHIP-8)
4. [Mastering CHIP-8: A brief tutorial covering the architecture & instructions](http://mattmik.com/files/chip8/mastering/chip8.html)

For more information on how Chip-8 works, consider reading through older, but still relevant, community forums and other Chip-8 emulation guides. 

Enjoy exploring the world of emulation with Chip-8! Feel free to open issues or submit pull requests if you find any bugs or have suggestions. 

Happy coding and gaming!
