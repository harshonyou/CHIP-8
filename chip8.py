import random
import sys
import time

import pygame

MEMORY_SIZE = 4096
SPRITE_ADDRESS = 0x050
START_ADDRESS = 0x200
MAX_WIDTH = 64
MAX_HEIGHT = 32
SCALE = 10
INSTRUCTIONS_PER_FRAME = 11


class Chip8:
    def __init__(
        self, scale=SCALE, instructions_per_frame=INSTRUCTIONS_PER_FRAME
    ) -> None:
        pygame.init()
        pygame.mixer.init()

        self.memory = [0x0] * MEMORY_SIZE
        self.registers = [0x0] * 16
        self.index_register = 0x0
        self.program_counter = START_ADDRESS
        self.stack = []
        self.display = [[0x0 for _ in range(MAX_WIDTH)] for _ in range(MAX_HEIGHT)]
        self.delay_timer = 0x0
        self.sound_timer = 0x0
        self.keys = [False] * (0xF + 1)

        self.beep_sound = pygame.mixer.Sound("beep.wav")

        self.key_map = {
            pygame.K_1: 0x1,
            pygame.K_2: 0x2,
            pygame.K_3: 0x3,
            pygame.K_4: 0xC,
            pygame.K_q: 0x4,
            pygame.K_w: 0x5,
            pygame.K_e: 0x6,
            pygame.K_r: 0xD,
            pygame.K_a: 0x7,
            pygame.K_s: 0x8,
            pygame.K_d: 0x9,
            pygame.K_f: 0xE,
            pygame.K_z: 0xA,
            pygame.K_x: 0x0,
            pygame.K_c: 0xB,
            pygame.K_v: 0xF,
        }

        self.scale = scale
        self.instructions_per_frame = instructions_per_frame

    def load_rom(self, path):
        sprites = {
            0x0: [0xF0, 0x90, 0x90, 0x90, 0xF0],
            0x1: [0x20, 0x60, 0x20, 0x20, 0x70],
            0x2: [0xF0, 0x10, 0xF0, 0x80, 0xF0],
            0x3: [0xF0, 0x10, 0xF0, 0x10, 0xF0],
            0x4: [0x90, 0x90, 0xF0, 0x10, 0x10],
            0x5: [0xF0, 0x80, 0xF0, 0x10, 0xF0],
            0x6: [0xF0, 0x80, 0xF0, 0x90, 0xF0],
            0x7: [0xF0, 0x10, 0x20, 0x40, 0x40],
            0x8: [0xF0, 0x90, 0xF0, 0x90, 0xF0],
            0x9: [0xF0, 0x90, 0xF0, 0x10, 0xF0],
            0xA: [0xF0, 0x90, 0xF0, 0x90, 0x90],
            0xB: [0xE0, 0x90, 0xE0, 0x90, 0xE0],
            0xC: [0xF0, 0x80, 0x80, 0x80, 0xF0],
            0xD: [0xE0, 0x90, 0x90, 0x90, 0xE0],
            0xE: [0xF0, 0x80, 0xF0, 0x80, 0xF0],
            0xF: [0xF0, 0x80, 0xF0, 0x80, 0x80],
        }

        idx = SPRITE_ADDRESS
        for sprite in range(0x0, 0xF + 1):
            for blob in sprites[sprite]:
                self.memory[idx] = blob
                idx += 1

        with open(path, "rb") as f:
            blobs = f.read()
            idx = START_ADDRESS

            for blob in blobs:
                self.memory[idx] = blob
                idx += 1

    def fetch(self):
        instruction: int = (
            self.memory[self.program_counter] << 8
            | self.memory[self.program_counter + 1]
        )
        self.program_counter += 2

        return instruction

    def decode_and_execute(self, instruction):
        # instruction[16-bits] -> OPCODE[4-bits] X[4-bits] Y[4-bits] N[4-bits]
        # instruction[16-bits] -> OPCODE[4-bits] X[4-bits] NN[8-bits]
        # instruction[16-bits] -> OPCODE[4-bits] NNN[12-bits]
        opcode = instruction >> 12 & 0x0F
        X = instruction >> 8 & 0x0F
        Y = instruction >> 4 & 0x0F
        N = instruction & 0x0F
        NN = instruction & 0xFF
        NNN = instruction & 0xFFF

        match opcode:
            case 0x0:  # 00E0, 00EE
                if instruction == 0x00E0:
                    self.display = [
                        [0x0 for _ in range(MAX_WIDTH)] for _ in range(MAX_HEIGHT)
                    ]
                elif instruction == 0x00EE:
                    self.program_counter = self.stack.pop()
            case 0x1:  # 1NNN
                self.program_counter = NNN
            case 0x2:  # 2NNN
                self.stack.append(self.program_counter)
                self.program_counter = NNN
            case 0x3:  # 3XNN
                if self.registers[X] == NN:
                    self.program_counter += 2
            case 0x4:  # 4XNN
                if self.registers[X] != NN:
                    self.program_counter += 2
            case 0x5:  # 5XY0
                if self.registers[X] == self.registers[Y]:
                    self.program_counter += 2
            case 0x6:  # 6XNN
                self.registers[X] = NN
            case 0x7:  # 7XNN
                self.registers[X] = (self.registers[X] + NN) & 0xFF
            case 0x8:  # 8XY0, 8XY1, 8XY2, 8XY3, 8XY4, 8XY5, 8XY6, 8XY7, 8XYE
                match N:
                    case 0x0:
                        self.registers[X] = self.registers[Y]
                    case 0x1:
                        self.registers[X] |= self.registers[Y]
                    case 0x2:
                        self.registers[X] &= self.registers[Y]
                    case 0x3:
                        self.registers[X] ^= self.registers[Y]
                    case 0x4:
                        sum_val = self.registers[X] + self.registers[Y]
                        self.registers[X] = sum_val & 0xFF
                        self.registers[0xF] = 1 if sum_val > 0xFF else 0
                    case 0x5:
                        vx = self.registers[X]
                        vy = self.registers[Y]
                        diff = vx - vy
                        self.registers[X] = diff & 0xFF
                        self.registers[0xF] = 1 if vx >= vy else 0
                    case 0x6:
                        old_value = self.registers[X]
                        carry = old_value & 0x1  # LSB
                        shifted = old_value >> 1

                        self.registers[X] = shifted
                        self.registers[0xF] = carry
                    case 0x7:
                        vx = self.registers[X]
                        vy = self.registers[Y]
                        diff = vy - vx
                        self.registers[X] = diff & 0xFF
                        self.registers[0xF] = 1 if vy >= vx else 0
                    case 0xE:
                        old_value = self.registers[X]
                        carry = (old_value >> 7) & 0x1  # MSB
                        shifted = (old_value << 1) & 0xFF

                        self.registers[X] = shifted
                        self.registers[0xF] = carry
            case 0x9:  # 9XY0
                if self.registers[X] != self.registers[Y]:
                    self.program_counter += 2
            case 0xA:  # ANNN
                self.index_register = NNN
            case 0xB:  # BNNN
                self.program_counter = NNN + self.registers[0x0]
            case 0xC:  # CXNN
                self.registers[X] = random.randint(0, 0xFF) & NN
            case 0xD:  # DXYN
                VX = self.registers[X]
                VY = self.registers[Y]
                row, col, idx = VY, VX, 0
                flag = 0x0

                while idx < N:
                    sprite = self.memory[self.index_register + idx]
                    for i in range(8):
                        pixel = (sprite >> (7 - i)) & 0x1

                        if self.display[row % MAX_HEIGHT][col % MAX_WIDTH] & pixel:
                            flag = 0x1

                        self.display[row % MAX_HEIGHT][col % MAX_WIDTH] ^= pixel
                        col += 1

                    row += 1
                    col = VX
                    idx += 1

                self.registers[0xF] = flag
            case 0xE:  # EX9E, EXA1
                match NN:
                    case 0x9E:
                        if self.keys[self.registers[X]]:
                            self.program_counter += 2
                    case 0xA1:
                        if not self.keys[self.registers[X]]:
                            self.program_counter += 2
            case 0xF:  # FX07, FX0A, FX15, FX18, FX1E, FX29, FX33, FX55, FX65
                match NN:
                    case 0x07:
                        self.registers[X] = self.delay_timer
                    case 0x0A:  # TODO
                        if any(self.keys):
                            self.registers[X] = self.keys.index(True)
                        else:
                            self.program_counter -= 2
                    case 0x15:
                        self.delay_timer = self.registers[X]
                    case 0x18:
                        self.sound_timer = self.registers[X]
                    case 0x1E:
                        self.index_register += self.registers[X]
                    case 0x29:
                        self.index_register = SPRITE_ADDRESS + self.registers[X] * 0x5
                    case 0x33:
                        value = self.registers[X]
                        self.memory[self.index_register] = value // 100
                        self.memory[self.index_register + 1] = (value // 10) % 10
                        self.memory[self.index_register + 2] = value % 10
                    case 0x55:
                        for idx in range(X + 1):
                            self.memory[self.index_register + idx] = self.registers[idx]
                    case 0x65:
                        for idx in range(X + 1):
                            self.registers[idx] = self.memory[self.index_register + idx]
            case _:
                print(f"{opcode} not implemented!")
        return opcode

    def run(self):
        window_size = (MAX_WIDTH * SCALE, MAX_HEIGHT * SCALE)
        window = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Chip-8")
        clock = pygame.time.Clock()

        last_time = time.time()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key in self.key_map:
                        self.keys[self.key_map[event.key]] = True

                elif event.type == pygame.KEYUP:
                    if event.key in self.key_map:
                        self.keys[self.key_map[event.key]] = False

            # self.decode_and_execute(self.fetch())
            for _ in range(INSTRUCTIONS_PER_FRAME):
                self.decode_and_execute(self.fetch())

            current_time = time.time()
            if current_time - last_time >= 1 / 60:
                if self.delay_timer > 0:
                    self.delay_timer -= 1
                if self.sound_timer > 0:
                    if not pygame.mixer.get_busy():
                        self.beep_sound.play()
                    self.sound_timer -= 1
                else:
                    if pygame.mixer.get_busy():
                        self.beep_sound.stop()

                last_time = current_time

            window.fill((0, 0, 0))

            for y, row in enumerate(self.display):
                for x, col in enumerate(row):
                    if col:
                        pygame.draw.rect(
                            window,
                            (255, 255, 255),
                            (x * SCALE, y * SCALE, SCALE, SCALE),
                        )

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

    def debug_draw(self):
        for row in self.display:
            for col in row:
                if col:
                    print("⬜", end="")
                else:
                    print("⬛", end="")
            print()
        print()
