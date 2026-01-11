import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import math
import struct
import random

# --- Hardware Constants ---
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 160
CYCLES_PER_FRAME = 280896
REFRESH_RATE = 16  # ms

class MMU:
    """
    Memory Management Unit
    Handles mapping the 4GB address space of the GBA.
    """
    def __init__(self):
        # 00000000-00003FFF: BIOS (Protected)
        self.bios = bytearray(0x4000)
        # 02000000-0203FFFF: On-board WRAM (256KB)
        self.ewram = bytearray(0x40000)
        # 03000000-03007FFF: On-chip WRAM (32KB)
        self.iwram = bytearray(0x8000)
        # 04000000-040003FF: I/O Registers
        self.io = bytearray(0x400)
        # 05000000-050003FF: Palette RAM
        self.palette = bytearray(0x400)
        # 06000000-06017FFF: VRAM (Video RAM)
        self.vram = bytearray(0x18000)
        # 07000000-070003FF: OAM (Object Attribute Memory)
        self.oam = bytearray(0x400)
        # 08000000-xx...: Game Pak ROM 1 (Wait state 0)
        self.gamepak = bytearray()

    def load_rom(self, data):
        self.gamepak = bytearray(data)

    # --- Read Operations ---
    def read8(self, addr):
        if 0x02000000 <= addr < 0x02040000:
            return self.ewram[addr - 0x02000000]
        elif 0x08000000 <= addr < 0x08000000 + len(self.gamepak):
            return self.gamepak[addr - 0x08000000]
        return 0

    def read16(self, addr):
        val = self.read8(addr) | (self.read8(addr + 1) << 8)
        return val

    def read32(self, addr):
        val = self.read8(addr) | (self.read8(addr + 1) << 8) | \
              (self.read8(addr + 2) << 16) | (self.read8(addr + 3) << 24)
        return val

    # --- Write Operations ---
    def write8(self, addr, value):
        if 0x02000000 <= addr < 0x02040000:
            self.ewram[addr - 0x02000000] = value & 0xFF
        # (Add other memory regions here as needed)

    def write32(self, addr, value):
        self.write8(addr, value & 0xFF)
        self.write8(addr + 1, (value >> 8) & 0xFF)
        self.write8(addr + 2, (value >> 16) & 0xFF)
        self.write8(addr + 3, (value >> 24) & 0xFF)

class ARM7TDMI:
    """
    ARM7TDMI CPU Core
    Now capable of basic Data Processing and Branching.
    """
    def __init__(self, mmu):
        self.mmu = mmu
        # R0-R12: General Purpose, R13: SP, R14: LR, R15: PC
        self.registers = [0] * 16 
        # CPSR bits: N(31) Z(30) C(29) V(28) ... Mode(0-4)
        self.cpsr = 0x1F  
        self.thumb_mode = False

    def reset(self):
        self.registers = [0] * 16
        self.registers[15] = 0x08000000  # Start at ROM
        self.cpsr = 0x1F
        self.thumb_mode = False
        print("CPU Reset: PC=0x08000000")

    def step(self):
        pc = self.registers[15]
        
        if self.thumb_mode:
            # Simple Thumb stub
            self.registers[15] += 2
        else:
            # ARM State (32-bit instructions)
            try:
                instruction = self.mmu.read32(pc)
                self.registers[15] += 4 # PC advances by 4 bytes
                self.execute_arm(instruction)
            except IndexError:
                pass # End of memory

    def check_condition(self, cond):
        # Stub for condition checking (EQ, NE, CS, CC, etc.)
        # For now, always return True to execute everything
        return True

    def execute_arm(self, instr):
        # 1. Condition Field (Bits 28-31)
        cond = (instr >> 28) & 0xF
        if not self.check_condition(cond):
            return

        # 2. Decode Group
        # Branch (B): 101L Offset (Bits 25-27 = 101)
        if (instr & 0x0E000000) == 0x0A000000:
            self.op_branch(instr)
        # Data Processing: 00 I Opcode S Rn Rd Operand2
        elif (instr & 0x0C000000) == 0:
            self.op_data_proc(instr)
        else:
            # Unknown or unimplemented, just skip
            pass

    def op_branch(self, instr):
        # 24-bit signed offset, shifted left 2
        offset = instr & 0xFFFFFF
        if offset & 0x800000: # Sign extend
            offset -= 0x1000000
        
        # PC is technically +8 ahead due to pipeline in real hardware
        # But for this simple step emulator, we just add the jump
        jump = (offset << 2) 
        # Adjust PC (We already added +4 in step(), but branch is relative to fetch)
        self.registers[15] += jump + 4

    def op_data_proc(self, instr):
        opcode = (instr >> 21) & 0xF
        rn_idx = (instr >> 16) & 0xF
        rd_idx = (instr >> 12) & 0xF
        operand2 = instr & 0xFFF # Immediate (stubbed rotation)
        
        op1 = self.registers[rn_idx]
        
        res = 0
        if opcode == 0x0: # AND
            res = op1 & operand2
        elif opcode == 0x2: # SUB
            res = op1 - operand2
        elif opcode == 0x4: # ADD
            res = op1 + operand2
        elif opcode == 0xD: # MOV
            res = operand2
        
        self.registers[rd_idx] = res & 0xFFFFFFFF

class PPU:
    """
    Picture Processing Unit
    Renders visual data to a buffer.
    """
    def __init__(self, mmu):
        self.mmu = mmu
        self.scanline = 0
        # A flat bytearray for the display (Width * Height * 3 bytes for RGB)
        # This allows us to write pixel data directly
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.frame_data = bytearray(self.width * self.height * 3)
        
    def update(self):
        # In a real emulator, we'd draw line-by-line.
        # Here we generate a test pattern to prove display works.
        self.draw_test_pattern()

    def draw_test_pattern(self):
        # Generate static/noise or a gradient to show the "screen" is alive
        # This simulates the electron beam moving across the screen
        base_color = int(time.time() * 50) % 255
        
        # Simple optimization: Don't rewrite every pixel every frame in Python
        # or it will lag. We'll just modify a chunk.
        for i in range(0, len(self.frame_data), 3):
            # Blue gradient effect
            self.frame_data[i] = 0   # R
            self.frame_data[i+1] = (i % 255) # G
            self.frame_data[i+2] = base_color # B

class Console:
    def __init__(self):
        self.mmu = MMU()
        self.cpu = ARM7TDMI(self.mmu)
        self.ppu = PPU(self.mmu)
        self.is_running = False
        self.rom_name = "None"

    def load_game(self, path):
        try:
            with open(path, "rb") as f:
                data = f.read()
                self.mmu.load_rom(data)
                self.cpu.reset()
                self.rom_name = path.split("/")[-1]
                return True
        except Exception as e:
            print(f"Load Error: {e}")
            return False

    def tick(self):
        if self.is_running:
            # Execute instructions
            for _ in range(500):
                self.cpu.step()
            
            # Update graphics
            self.ppu.update()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Cat's GBA EMULATOR 0.2")
        self.root.geometry("540x650")
        self.root.configure(bg="#2c3e50")
        
        self.console = Console()
        
        self.setup_ui()
        self.setup_input()
        self.update_loop()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#34495e", height=50)
        header.pack(fill="x")
        tk.Label(header, text="Cat's GBA Core v0.2", fg="white", bg="#34495e", 
                 font=("Verdana", 14, "bold")).pack(pady=10)

        # Game Screen
        screen_frame = tk.Frame(self.root, bg="black", padx=5, pady=5)
        screen_frame.pack(pady=10)
        
        # Create a blank image for the display
        self.screen_image = tk.PhotoImage(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.canvas = tk.Canvas(screen_frame, width=SCREEN_WIDTH*2, height=SCREEN_HEIGHT*2, 
                              bg="black", highlightthickness=0)
        self.canvas.pack()
        
        # We draw the image onto the canvas, scaled up 2x
        self.canvas_image_id = self.canvas.create_image(0, 0, image=self.screen_image, anchor="nw")
        self.canvas.scale("all", 0, 0, 2, 2) # Basic scaling (nearest neighbor-ish)

        # Status & Controls
        ctrl_frame = tk.Frame(self.root, bg="#2c3e50")
        ctrl_frame.pack(pady=10)
        
        self.load_btn = tk.Button(ctrl_frame, text="Load ROM", command=self.load_rom, width=10)
        self.load_btn.grid(row=0, column=0, padx=5)
        
        self.run_btn = tk.Button(ctrl_frame, text="Run", command=self.toggle_run, state="disabled", width=10)
        self.run_btn.grid(row=0, column=1, padx=5)

        # Registers
        self.reg_text = tk.Label(self.root, text="Waiting for Cartridge...", 
                               fg="#2ecc71", bg="#2c3e50", font=("Consolas", 9), justify="left")
        self.reg_text.pack(pady=10)

    def setup_input(self):
        # Keyboard mapping stub
        pass

    def load_rom(self):
        path = filedialog.askopenfilename(filetypes=[("GBA ROMs", "*.gba"), ("All", "*.*")])
        if path:
            if self.console.load_game(path):
                self.run_btn.config(state="normal", bg="#27ae60", fg="white")
                self.reg_text.config(text="Cartridge Loaded. Ready to boot.")
            else:
                messagebox.showerror("Error", "Failed to load ROM.")

    def toggle_run(self):
        self.console.is_running = not self.console.is_running
        self.run_btn.config(text="Pause" if self.console.is_running else "Run")

    def update_loop(self):
        if self.console.is_running:
            self.console.tick()
            
            # 1. Update Display
            # Construct a PPM header to stream raw bytes to PhotoImage
            # This is faster than plotting individual pixels
            header = f"P6 {SCREEN_WIDTH} {SCREEN_HEIGHT} 255 ".encode()
            data = header + self.console.ppu.frame_data
            try:
                self.screen_image.put(data)
                # Note: Scaling happening via canvas, not raw data
            except Exception:
                pass 

            # 2. Update Registers UI
            r = self.console.cpu.registers
            reg_str = (
                f"R0: {r[0]:08X}  R1: {r[1]:08X}  R2: {r[2]:08X}  R3: {r[3]:08X}\n"
                f"R4: {r[4]:08X}  R5: {r[5]:08X}  R6: {r[6]:08X}  R7: {r[7]:08X}\n"
                f"PC: {r[15]:08X}  SP: {r[13]:08X}  LR: {r[14]:08X}"
            )
            self.reg_text.config(text=reg_str)

        self.root.after(REFRESH_RATE, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
