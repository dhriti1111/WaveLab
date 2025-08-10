from tkinter import Tk, Label, Button, StringVar, OptionMenu, Frame, DoubleVar, IntVar, Canvas, Scrollbar
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.style.use('dark_background')

# Neon Dark Theme (unchanged)
NEON_DARK_THEME = {
    "BG_COLOR": "#101014",
    "PANEL_COLOR": "#181820",
    "ACCENT_COLOR": "#C9E819",
    "TEXT_COLOR": "#00FFFF",
    "BTN_COLOR": "#0CC4F7",
    "BTN_TEXT_COLOR": "#101014",
    "SIGNAL1_COLOR": "#39FF14",
    "SIGNAL2_COLOR": "#00FFFF",
    "RESULT_COLOR": "#FF00FF",
    "SLIDER_BG": "#222233",
}

DARK_THEME = NEON_DARK_THEME

OPERATION_FORMULAS = {
    "Time Scaling": "x(at)",
    "Amplitude Scaling": "A·x(t)",
    "Time Shifting": "x(t - t₀)",
    "Time Reversal": "x(-t)",
    "Signal Addition": "x₁(t) + x₂(t) + ...",
    "Signal Multiplication": "x₁(t) · x₂(t) · ..."
}

class SignalGUI:
    def __init__(self, master):
        self.master = master
        self.theme = DARK_THEME
        self.apply_theme()
        self.master.title("WaveLab")
        self.master.configure(bg=self.theme["BG_COLOR"])

        # Title
        title_label = Label(master, text="WaveLab", font=("Segoe Script", 65, "bold"),
                            fg=self.theme["ACCENT_COLOR"], bg=self.theme["BG_COLOR"])
        title_label.pack(pady=(10, 10))

        # Remove theme switch button (dark only)
        # Main layout
        main_frame = Frame(master, bg=self.theme["BG_COLOR"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Left panel
        control_frame = Frame(main_frame, bg=self.theme["PANEL_COLOR"], highlightbackground="#222233", highlightthickness=1)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Signal 1 controls
        self.signal_type = StringVar(master, "Sine")
        Label(control_frame, text="Signal 1 Type", bg=self.theme["PANEL_COLOR"], fg=self.theme["TEXT_COLOR"], font=("Helvetica Neue", 16, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        OptionMenu(control_frame, self.signal_type, "Sine", "Square", "Sawtooth", "Step", "Impulse", "Ramp").pack(fill="x", padx=15, pady=5)

        self.amp1_var = DoubleVar(value=1.0)
        self.amp1_label = self.add_slider(control_frame, "Amplitude", self.amp1_var, 0.1, 5.0, 0.1, self.theme["SIGNAL1_COLOR"])

        self.freq1_var = DoubleVar(value=5.0)
        self.freq1_label = self.add_slider(control_frame, "Frequency", self.freq1_var, 1.0, 20.0, 1.0, self.theme["SIGNAL2_COLOR"])

        self.phase1_var = DoubleVar(value=0.0)
        self.phase1_label = self.add_slider(control_frame, "Phase (°)", self.phase1_var, 0, 360, 1, self.theme["RESULT_COLOR"])

        # Operation
        Label(control_frame, text="Operation", bg=self.theme["PANEL_COLOR"], fg=self.theme["TEXT_COLOR"], font=("Helvetica Neue", 16, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        self.operation_type = StringVar(master, "Time Scaling")
        OptionMenu(control_frame, self.operation_type, *OPERATION_FORMULAS.keys(), command=self.update_parameter_controls).pack(fill="x", padx=15, pady=5)

        # Signal 2 controls (for addition/multiplication)
        self.signal2_frame = Frame(control_frame, bg=self.theme["PANEL_COLOR"])
        Label(self.signal2_frame, text="Signal 2 Type", bg=self.theme["PANEL_COLOR"], fg=self.theme["TEXT_COLOR"], font=("Helvetica Neue", 16, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        self.signal2_type = StringVar(master, "Sine")
        OptionMenu(self.signal2_frame, self.signal2_type, "Sine", "Square", "Sawtooth", "Step", "Impulse", "Ramp").pack(fill="x", padx=15, pady=5)

        self.amp2_var = DoubleVar(value=1.0)
        self.amp2_label = self.add_slider(self.signal2_frame, "Amplitude", self.amp2_var, 0.1, 5.0, 0.1, self.theme["SIGNAL2_COLOR"])

        self.freq2_var = DoubleVar(value=5.0)
        self.freq2_label = self.add_slider(self.signal2_frame, "Frequency", self.freq2_var, 1.0, 20.0, 1.0, self.theme["RESULT_COLOR"])

        self.phase2_var = DoubleVar(value=0.0)
        self.phase2_label = self.add_slider(self.signal2_frame, "Phase (°)", self.phase2_var, 0, 360, 1, self.theme["ACCENT_COLOR"])

        # Parameter entry (for scaling/shifting)
        self.param_var = DoubleVar(value=1.0)
        self.param_label = Label(control_frame, text="Scaling factor (a):", bg=self.theme["PANEL_COLOR"], fg=self.theme["ACCENT_COLOR"], font=("Helvetica Neue", 14, "bold"))
        self.param_entry = tk.Entry(control_frame, textvariable=self.param_var, font=("Helvetica Neue", 14), bg=self.theme["BG_COLOR"], fg=self.theme["ACCENT_COLOR"])

        # Formula display
        self.formula_label = Label(control_frame, text="Formula: x(at)", bg=self.theme["PANEL_COLOR"], fg=self.theme["ACCENT_COLOR"], font=("Helvetica Neue", 14, "italic"))
        self.formula_label.pack(pady=10)

        # Process and show buttons
        self.process_button = Button(control_frame, text="Process Signal", font=("Helvetica Neue", 18, "bold"),
                                     command=self.process_signal, bg=self.theme["BTN_COLOR"], fg=self.theme["BTN_TEXT_COLOR"],
                                     activebackground=self.theme["ACCENT_COLOR"], relief="flat", height=2)
        self.process_button.pack(pady=10, fill="x", padx=15)

        self.show_all_button = Button(control_frame, text="Show All Signals", font=("Helvetica Neue", 16, "bold"),
                                      command=self.open_signals_window, bg=self.theme["RESULT_COLOR"], fg=self.theme["BTN_TEXT_COLOR"], relief="flat")
        self.show_all_button.pack(pady=(0, 20), fill="x", padx=15)

        # Right panel - Plots
        plot_frame = Frame(main_frame, bg=self.theme["PANEL_COLOR"], highlightbackground="#222233", highlightthickness=1)
        plot_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.figure, self.axs = plt.subplots(2, 1, figsize=(6, 6))
        self.figure.patch.set_facecolor(self.theme["PANEL_COLOR"])
        self.canvas_plot = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas_plot.get_tk_widget().pack(fill="both", expand=True)

        self.update_parameter_controls(self.operation_type.get())

    def apply_theme(self):
        plt.style.use('dark_background')
        plt.rcParams['axes.labelcolor'] = self.theme["TEXT_COLOR"]
        plt.rcParams['xtick.color'] = self.theme["TEXT_COLOR"]
        plt.rcParams['ytick.color'] = self.theme["TEXT_COLOR"]
        plt.rcParams['axes.edgecolor'] = self.theme["ACCENT_COLOR"]
        plt.rcParams['axes.titlecolor'] = self.theme["ACCENT_COLOR"]

    def add_slider(self, parent, text, var, frm, to, step, color):
        frame = Frame(parent, bg=self.theme["PANEL_COLOR"])
        frame.pack(fill="x", padx=15, pady=(10, 0))
        lbl = Label(frame, text=f"{text}: {var.get():.2f}", bg=self.theme["PANEL_COLOR"], fg=color, font=("Helvetica Neue", 14, "bold"))
        lbl.pack(side="left")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(f"{text}.Horizontal.TScale", troughcolor=self.theme["SLIDER_BG"], background=color, thickness=8)
        slider = ttk.Scale(frame, from_=frm, to=to, variable=var, orient="horizontal",
                           style=f"{text}.Horizontal.TScale", command=lambda v, l=lbl, name=text: l.config(text=f"{name}: {float(v):.2f}"))
        slider.pack(side="right", fill="x", expand=True)
        return lbl

    def update_parameter_controls(self, operation):
        self.signal2_frame.pack_forget()
        self.param_label.pack_forget()
        self.param_entry.pack_forget()
        if operation in ["Signal Addition", "Signal Multiplication"]:
            self.signal2_frame.pack_forget()
            self.signal2_frame.pack(before=self.process_button, fill="x", padx=15, pady=10)
        if operation == "Time Scaling":
            self.param_label.config(text="Scaling factor (a):")
            self.param_var.set(1.0)
            self.param_label.pack(anchor="w", padx=15, pady=(15, 0))
            self.param_entry.pack(fill="x", padx=15, pady=5)
        elif operation == "Amplitude Scaling":
            self.param_label.config(text="Amplitude (A):")
            self.param_var.set(2.0)
            self.param_label.pack(anchor="w", padx=15, pady=(15, 0))
            self.param_entry.pack(fill="x", padx=15, pady=5)
        elif operation == "Time Shifting":
            self.param_label.config(text="Shift (t₀):")
            self.param_var.set(0.1)
            self.param_label.pack(anchor="w", padx=15, pady=(15, 0))
            self.param_entry.pack(fill="x", padx=15, pady=5)
        self.formula_label.config(text=f"Formula: {OPERATION_FORMULAS.get(operation, '')}")

    def process_signal(self):
        t = np.linspace(0, 1, 500)
        operation = self.operation_type.get()
        if operation in ["Signal Addition", "Signal Multiplication"]:
            s1 = self.generate_signal(self.signal_type.get(), t, self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
            s2 = self.generate_signal(self.signal2_type.get(), t, self.amp2_var.get(), self.freq2_var.get(), self.phase2_var.get())
            if operation == "Signal Addition":
                processed = s1 + s2
            else:
                processed = s1 * s2
            self.plot_signals(t, s1, processed, s2)
        elif operation == "Time Scaling":
            s1 = self.generate_signal(self.signal_type.get(), t, self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
            processed = self.generate_signal(self.signal_type.get(), t * self.param_var.get(), self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
            self.plot_signals(t, s1, processed)
        elif operation == "Amplitude Scaling":
            s1 = self.generate_signal(self.signal_type.get(), t, self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
            processed = self.param_var.get() * s1
            self.plot_signals(t, s1, processed)
        elif operation == "Time Shifting":
            s1 = self.generate_signal(self.signal_type.get(), t, self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
            processed = self.generate_signal(self.signal_type.get(), t - self.param_var.get(), self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
            self.plot_signals(t, s1, processed)
        elif operation == "Time Reversal":
            s1 = self.generate_signal(self.signal_type.get(), t, self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
            processed = s1[::-1]
            self.plot_signals(t, s1, processed)
        else:
            s1 = self.generate_signal(self.signal_type.get(), t, self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
            processed = s1
            self.plot_signals(t, s1, processed)

    def plot_signals(self, t, s1, processed, s2=None):
        self.figure.clf()
        n_plots = 3 if s2 is not None else 2
        axs = self.figure.subplots(n_plots, 1, sharex=True)
        axs = axs.flatten() if n_plots > 1 else [axs]
        for ax in axs:
            ax.set_facecolor(self.theme["PANEL_COLOR"])
            ax.grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
            ax.set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
            ax.set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
            ax.tick_params(colors=self.theme["TEXT_COLOR"])
        axs[0].set_title("Signal 1", color=self.theme["SIGNAL1_COLOR"])
        axs[0].plot(t, s1, color=self.theme["SIGNAL1_COLOR"], linewidth=2)
        if s2 is not None:
            axs[1].set_title("Signal 2", color=self.theme["SIGNAL2_COLOR"])
            axs[1].plot(t, s2, color=self.theme["SIGNAL2_COLOR"], linewidth=2)
            axs[2].set_title("Resultant Signal", color=self.theme["RESULT_COLOR"])
            axs[2].plot(t, processed, color=self.theme["RESULT_COLOR"], linewidth=2)
        else:
            axs[1].set_title("Processed Signal", color=self.theme["RESULT_COLOR"])
            axs[1].plot(t, processed, color=self.theme["RESULT_COLOR"], linewidth=2)
        self.figure.tight_layout()
        self.canvas_plot.draw()

    def generate_signal(self, sig_type, t, amp, freq, phase=0):
        phase_rad = np.deg2rad(phase)
        if sig_type == "Sine":
            return amp * np.sin(2 * np.pi * freq * t + phase_rad)
        elif sig_type == "Square":
            return amp * np.sign(np.sin(2 * np.pi * freq * t + phase_rad))
        elif sig_type == "Sawtooth":
            return amp * (2 * (t - np.floor(t + 0.5)))
        elif sig_type == "Step":
            return amp * np.heaviside(t, 1)
        elif sig_type == "Impulse":
            arr = np.zeros_like(t)
            arr[len(t)//2] = amp
            return arr
        elif sig_type == "Ramp":
            return amp * t
        return np.zeros_like(t)

    def open_signals_window(self):
        t = np.linspace(0, 1, 500)
        operation = self.operation_type.get()
        if operation in ["Signal Addition", "Signal Multiplication"]:
            s1 = self.generate_signal(self.signal_type.get(), t, self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
            s2 = self.generate_signal(self.signal2_type.get(), t, self.amp2_var.get(), self.freq2_var.get(), self.phase2_var.get())
            if operation == "Signal Addition":
                processed = s1 + s2
            else:
                processed = s1 * s2
            win = tk.Toplevel(self.master)
            win.title("All Signals")
            win.configure(bg=self.theme["BG_COLOR"])
            fig, axs = plt.subplots(3, 1, figsize=(7, 7), sharex=True)
            fig.patch.set_facecolor(self.theme["PANEL_COLOR"])
            axs = axs.flatten()
            axs[0].set_facecolor(self.theme["PANEL_COLOR"])
            axs[0].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
            axs[0].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
            axs[0].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
            axs[0].tick_params(colors=self.theme["TEXT_COLOR"])
            axs[0].set_title("Signal 1", color=self.theme["SIGNAL1_COLOR"])
            axs[0].plot(t, s1, color=self.theme["SIGNAL1_COLOR"], linewidth=2)
            axs[1].set_facecolor(self.theme["PANEL_COLOR"])
            axs[1].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
            axs[1].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
            axs[1].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
            axs[1].tick_params(colors=self.theme["TEXT_COLOR"])
            axs[1].set_title("Signal 2", color=self.theme["SIGNAL2_COLOR"])
            axs[1].plot(t, s2, color=self.theme["SIGNAL2_COLOR"], linewidth=2)
            axs[2].set_facecolor(self.theme["PANEL_COLOR"])
            axs[2].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
            axs[2].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
            axs[2].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
            axs[2].tick_params(colors=self.theme["TEXT_COLOR"])
            axs[2].set_title("Resultant Signal", color=self.theme["RESULT_COLOR"])
            axs[2].plot(t, processed, color=self.theme["RESULT_COLOR"], linewidth=2)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=win)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()

            # Add Save as PNG button
            def save_png():
                fig.savefig("signals.png", dpi=300, bbox_inches='tight')
                tk.messagebox.showinfo("Saved", "Plot saved as signals.png")

            save_btn = Button(win, text="Save as PNG", font=("Helvetica Neue", 14, "bold"),
                              bg=self.theme["BTN_COLOR"], fg=self.theme["BTN_TEXT_COLOR"],
                              command=save_png)
            save_btn.pack(pady=10)
        else:
            # ...existing code for other operations...
            pass

    def run(self):
        self.master.mainloop()

if __name__ == "__main__":
    root = Tk()
    gui = SignalGUI(root)
    gui.run()
