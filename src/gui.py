from tkinter import Tk, Label, Button, StringVar, OptionMenu, Frame, DoubleVar, IntVar, Canvas, Scrollbar, filedialog, messagebox
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
    "BTN_COLOR": "#53C4F1",
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
        signal_type_menu = OptionMenu(control_frame, self.signal_type, "Sine", "Square", "Sawtooth", "Step", "Impulse", "Ramp")
        signal_type_menu.config(font=("Helvetica Neue", 14))
        signal_type_menu.pack(fill="x", padx=15, pady=5)

        self.amp1_var = DoubleVar(value=1.0)
        self.amp1_label = self.add_slider(control_frame, "Amplitude", self.amp1_var, 0.1, 5.0, 0.1, self.theme["SIGNAL1_COLOR"])

        self.freq1_var = DoubleVar(value=5.0)
        self.freq1_label = self.add_slider(control_frame, "Frequency", self.freq1_var, 1.0, 20.0, 1.0, self.theme["SIGNAL2_COLOR"])

        # Remove phase slider, add manual entry for phase
        self.phase1_var = DoubleVar(value=0.0)
        phase_frame = Frame(control_frame, bg=self.theme["PANEL_COLOR"])
        phase_frame.pack(fill="x", padx=15, pady=(10, 0))
        Label(phase_frame, text="Phase (°):", bg=self.theme["PANEL_COLOR"], fg=self.theme["RESULT_COLOR"], font=("Helvetica Neue", 14, "bold")).pack(side="left")
        phase_entry = tk.Entry(phase_frame, textvariable=self.phase1_var, font=("Helvetica Neue", 14), width=8, bg=self.theme["BG_COLOR"], fg=self.theme["RESULT_COLOR"])
        phase_entry.pack(side="left", padx=(10, 0))

        # Operation
        Label(control_frame, text="Operation", bg=self.theme["PANEL_COLOR"], fg=self.theme["TEXT_COLOR"], font=("Helvetica Neue", 16, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        self.operation_type = StringVar(master, "Time Scaling")
        operation_menu = OptionMenu(control_frame, self.operation_type, *OPERATION_FORMULAS.keys(), command=self.update_parameter_controls)
        operation_menu.config(font=("Helvetica Neue", 14))
        operation_menu.pack(fill="x", padx=15, pady=5)

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

        # Scaling factor slider (replaces manual entry)
        self.param_var = DoubleVar(value=1.0)
        self.param_label = Label(control_frame, text="Scaling factor (a):", bg=self.theme["PANEL_COLOR"], fg=self.theme["ACCENT_COLOR"], font=("Helvetica Neue", 14, "bold"))
        self.param_label.pack(anchor="w", padx=15, pady=(15, 0))
        self.param_slider = ttk.Scale(control_frame, from_=0.1, to=5.0, variable=self.param_var, orient="horizontal",
                                      style="Scaling.Horizontal.TScale", command=lambda v: self.param_label.config(text=f"Scaling factor (a): {float(v):.2f}"))
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Scaling.Horizontal.TScale", troughcolor=self.theme["SLIDER_BG"], background=self.theme["ACCENT_COLOR"], thickness=8)
        self.param_slider.pack(fill="x", padx=15, pady=5)

        # Remove manual entry for scaling factor
        # self.param_entry = tk.Entry(control_frame, textvariable=self.param_var, font=("Helvetica Neue", 14), bg=self.theme["BG_COLOR"], fg=self.theme["ACCENT_COLOR"])

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

        # Reset button
        self.reset_button = Button(control_frame, text="Reset to Default", font=("Helvetica Neue", 14, "bold"),
                                  command=self.reset_parameters, bg=self.theme["ACCENT_COLOR"], fg=self.theme["BTN_TEXT_COLOR"])
        self.reset_button.pack(pady=(0, 10), fill="x", padx=15)

        # Right panel - Plots
        plot_frame = Frame(main_frame, bg=self.theme["PANEL_COLOR"], highlightbackground="#222233", highlightthickness=1)
        plot_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.figure, self.axs = plt.subplots(2, 1, figsize=(6, 6))
        self.figure.patch.set_facecolor(self.theme["PANEL_COLOR"])
        self.canvas_plot = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas_plot.get_tk_widget().pack(fill="both", expand=True)

        # Track last processed operation and parameters
        self.last_operation = None
        self.last_params = None

        # Bind variable changes for dynamic update
        self.amp1_var.trace_add("write", lambda *args: self.dynamic_update())
        self.freq1_var.trace_add("write", lambda *args: self.dynamic_update())
        self.phase1_var.trace_add("write", lambda *args: self.dynamic_update())
        self.amp2_var.trace_add("write", lambda *args: self.dynamic_update())
        self.freq2_var.trace_add("write", lambda *args: self.dynamic_update())
        self.phase2_var.trace_add("write", lambda *args: self.dynamic_update())
        self.param_var.trace_add("write", lambda *args: self.dynamic_update())
        self.signal_type.trace_add("write", lambda *args: self.dynamic_update())
        self.signal2_type.trace_add("write", lambda *args: self.dynamic_update())
        self.operation_type.trace_add("write", lambda *args: self.dynamic_update())

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
        self.param_slider.pack_forget()
        if operation in ["Signal Addition", "Signal Multiplication"]:
            self.signal2_frame.pack_forget()
            self.signal2_frame.pack(before=self.process_button, fill="x", padx=15, pady=10)
        if operation == "Time Scaling":
            self.param_label.config(text="Scaling factor (a):")
            self.param_var.set(1.0)
            self.param_slider.config(from_=0.1, to=5.0)
            self.param_label.pack_forget()
            self.param_slider.pack_forget()
            self.param_label.pack(before=self.process_button, anchor="w", padx=15, pady=(15, 0))
            self.param_slider.pack(before=self.process_button, fill="x", padx=15, pady=5)
        elif operation == "Amplitude Scaling":
            self.param_label.config(text="Amplitude (A):")
            self.param_var.set(2.0)
            self.param_slider.config(from_=0.1, to=5.0)
            self.param_label.pack_forget()
            self.param_slider.pack_forget()
            self.param_label.pack(before=self.process_button, anchor="w", padx=15, pady=(15, 0))
            self.param_slider.pack(before=self.process_button, fill="x", padx=15, pady=5)
        elif operation == "Time Shifting":
            self.param_label.config(text="Shift (t₀):")
            self.param_var.set(0.0)
            self.param_slider.config(from_=-10.0, to=10.0)
            self.param_label.pack_forget()
            self.param_slider.pack_forget()
            self.param_label.pack(before=self.process_button, anchor="w", padx=15, pady=(15, 0))
            self.param_slider.pack(before=self.process_button, fill="x", padx=15, pady=5)
        self.formula_label.config(text=f"Formula: {OPERATION_FORMULAS.get(operation, '')}")

        # Update label value dynamically for slider
        def update_label(val):
            if operation == "Time Shifting":
                self.param_label.config(text=f"Shift (t₀): {float(val):.2f}")
            elif operation == "Time Scaling":
                self.param_label.config(text=f"Scaling factor (a): {float(val):.2f}")
            elif operation == "Amplitude Scaling":
                self.param_label.config(text=f"Amplitude (A): {float(val):.2f}")

        self.param_slider.config(command=update_label)

    def process_signal(self):
        # Save current operation and parameters for dynamic update
        self.last_operation = self.operation_type.get()
        self.last_params = self.get_current_params()
        self.plot_current_signal()

    def get_current_params(self):
        # Gather all relevant parameters for current state
        return {
            "signal_type": self.signal_type.get(),
            "amp1": self.amp1_var.get(),
            "freq1": self.freq1_var.get(),
            "phase1": self.phase1_var.get(),
            "signal2_type": self.signal2_type.get(),
            "amp2": self.amp2_var.get(),
            "freq2": self.freq2_var.get(),
            "phase2": self.phase2_var.get(),
            "operation": self.operation_type.get(),
            "param": self.param_var.get()
        }

    def dynamic_update(self):
        # Only update if a signal has been processed before
        if self.last_operation is not None:
            self.plot_current_signal()

    def plot_current_signal(self):
        operation = self.operation_type.get()
        params = self.get_current_params()

        # Always keep the input range fixed
        t_input = np.linspace(0, 1, 500)

        # Determine output time range
        t_min, t_max = 0, 1
        if operation == "Time Shifting":
            t0 = params["param"]
            t_min = min(0, 0 - t0)
            t_max = max(0, 1 - t0)
        elif operation == "Time Scaling":
            a = params["param"]
            if a != 0:
                scaled_min = -1 / a
                scaled_max = 1 / a
                t_min = min(-1, scaled_min)
                t_max = max(1, scaled_max)
        elif operation == "Time Reversal":
            t_min, t_max = -1, 1
        elif params["signal_type"] in ["Ramp", "Impulse", "Step"]:
            t_min, t_max = -1, 1

        t_output = np.linspace(t_min, t_max, 500)

        # Original signal always from t_input
        s1 = self.generate_signal(params["signal_type"], t_input, params["amp1"], params["freq1"], params["phase1"])

        # Processed signal based on operation and t_output
        if operation == "Time Shifting":
            processed = self.generate_signal(params["signal_type"], t_output - params["param"], params["amp1"], params["freq1"], params["phase1"])
            self.plot_signals([t_input, t_output], s1, processed)

        elif operation == "Time Scaling":
            a = params["param"]
            processed = self.generate_signal(params["signal_type"], a * t_output, params["amp1"], params["freq1"], params["phase1"])
            self.plot_signals([t_input, t_output], s1, processed)

        elif operation == "Time Reversal":
            processed = self.generate_signal(params["signal_type"], -t_output, params["amp1"], params["freq1"], params["phase1"])
            self.plot_signals([t_input, t_output], s1, processed)

        elif operation in ["Signal Addition", "Signal Multiplication"]:
            s2 = self.generate_signal(params["signal2_type"], t_input, params["amp2"], params["freq2"], params["phase2"])
            processed = s1 + s2 if operation == "Signal Addition" else s1 * s2
            self.plot_signals(t_input, s1, processed, s2)

        elif operation == "Amplitude Scaling":
            processed = params["param"] * s1
            self.plot_signals(t_input, s1, processed)

        else:
            processed = s1
            self.plot_signals(t_input, s1, processed)

    def plot_signals(self, t, s1, processed, s2=None):
        self.figure.clf()
        n_plots = 3 if s2 is not None else 2
        axs = self.figure.subplots(n_plots, 1, sharex=True)
        axs = np.array(axs).flatten() if n_plots > 1 else np.array([axs])
        for i, ax in enumerate(axs):
            ax.set_facecolor(self.theme["PANEL_COLOR"])
            ax.grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
            ax.set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
            ax.set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
            ax.tick_params(colors=self.theme["TEXT_COLOR"])
            ax.axhline(0, color="#22C0D5", linewidth=2, alpha=0.8)
            ax.axvline(0, color="#22C0D5", linewidth=2, alpha=0.8)
        axs[0].set_title("Signal 1", color=self.theme["SIGNAL1_COLOR"])
        axs[0].plot(t[0] if isinstance(t, list) else t, s1, color=self.theme["SIGNAL1_COLOR"], linewidth=2)
        if s2 is not None:
            axs[1].set_title("Signal 2", color=self.theme["SIGNAL2_COLOR"])
            axs[1].plot(t, s2, color=self.theme["SIGNAL2_COLOR"], linewidth=2)
            axs[2].set_title("Resultant Signal", color=self.theme["RESULT_COLOR"])
            axs[2].plot(t, processed, color=self.theme["RESULT_COLOR"], linewidth=2)
        else:
            axs[1].set_title("Processed Signal", color=self.theme["RESULT_COLOR"])
            axs[1].plot(t[1] if isinstance(t, list) else t, processed, color=self.theme["RESULT_COLOR"], linewidth=2)
        self.figure.tight_layout()
        self.canvas_plot.draw()

        def format_coord(x, y, ax, t_data, y_data):
            idx = (np.abs(t_data - x)).argmin()
            if 0 <= idx < len(y_data):
                return f"x={t_data[idx]:.3f}, y={y_data[idx]:.3f}"
            return f"x={x:.3f}, y={y:.3f}"

        if hasattr(self, 'hover_cid'):
            self.canvas_plot.mpl_disconnect(self.hover_cid)
        if hasattr(self, 'hover_label'):
            self.hover_label.destroy()
        self.hover_label = Label(self.canvas_plot.get_tk_widget(), bg="#222233", fg="#39FF14", font=("Helvetica Neue", 12, "bold"), bd=1, relief="solid")
        self.hover_label.place_forget()

        def on_motion(event):
            if event.inaxes:
                ax = event.inaxes
                ax_idx = np.where(axs == ax)[0][0]
                if ax_idx == 0:
                    y_data = s1
                    t_data = t[0] if isinstance(t, list) else t
                elif ax_idx == 1 and s2 is not None:
                    y_data = s2
                    t_data = t
                else:
                    y_data = processed
                    t_data = t[1] if isinstance(t, list) else t
                text = format_coord(event.xdata, event.ydata, ax, t_data, y_data)
                self.hover_label.config(text=text)
                self.hover_label.place(x=event.guiEvent.x + 10, y=event.guiEvent.y + 10)
            else:
                self.hover_label.place_forget()

        self.hover_cid = self.canvas_plot.mpl_connect("motion_notify_event", on_motion)

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
        win = tk.Toplevel(self.master)
        win.title("All Signals")
        win.configure(bg=self.theme["BG_COLOR"])

        if operation in ["Signal Addition", "Signal Multiplication"]:
            s1 = self.generate_signal(self.signal_type.get(), t, self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
            s2 = self.generate_signal(self.signal2_type.get(), t, self.amp2_var.get(), self.freq2_var.get(), self.phase2_var.get())
            if operation == "Signal Addition":
                processed = s1 + s2
            else:
                processed = s1 * s2
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
        else:
            s1 = self.generate_signal(self.signal_type.get(), t, self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
            if operation == "Time Scaling":
                processed = self.generate_signal(self.signal_type.get(), t * self.param_var.get(), self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
                fig, axs = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
                axs = axs.flatten()
                axs[0].set_facecolor(self.theme["PANEL_COLOR"])
                axs[0].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
                axs[0].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
                axs[0].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
                axs[0].tick_params(colors=self.theme["TEXT_COLOR"])
                axs[0].set_title("Original Signal", color=self.theme["SIGNAL1_COLOR"])
                axs[0].plot(t, s1, color=self.theme["SIGNAL1_COLOR"], linewidth=2)
                axs[1].set_facecolor(self.theme["PANEL_COLOR"])
                axs[1].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
                axs[1].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
                axs[1].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
                axs[1].tick_params(colors=self.theme["TEXT_COLOR"])
                axs[1].set_title("Scaled Signal", color=self.theme["RESULT_COLOR"])
                axs[1].plot(t, processed, color=self.theme["RESULT_COLOR"], linewidth=2)
            elif operation == "Amplitude Scaling":
                processed = self.param_var.get() * s1
                fig, axs = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
                axs = axs.flatten()
                axs[0].set_facecolor(self.theme["PANEL_COLOR"])
                axs[0].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
                axs[0].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
                axs[0].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
                axs[0].tick_params(colors=self.theme["TEXT_COLOR"])
                axs[0].set_title("Original Signal", color=self.theme["SIGNAL1_COLOR"])
                axs[0].plot(t, s1, color=self.theme["SIGNAL1_COLOR"], linewidth=2)
                axs[1].set_facecolor(self.theme["PANEL_COLOR"])
                axs[1].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
                axs[1].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
                axs[1].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
                axs[1].tick_params(colors=self.theme["TEXT_COLOR"])
                axs[1].set_title("Amplitude Scaled Signal", color=self.theme["RESULT_COLOR"])
                axs[1].plot(t, processed, color=self.theme["RESULT_COLOR"], linewidth=2)
            elif operation == "Time Shifting":
                processed = self.generate_signal(self.signal_type.get(), t - self.param_var.get(), self.amp1_var.get(), self.freq1_var.get(), self.phase1_var.get())
                fig, axs = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
                axs = axs.flatten()
                axs[0].set_facecolor(self.theme["PANEL_COLOR"])
                axs[0].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
                axs[0].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
                axs[0].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
                axs[0].tick_params(colors=self.theme["TEXT_COLOR"])
                axs[0].set_title("Original Signal", color=self.theme["SIGNAL1_COLOR"])
                axs[0].plot(t, s1, color=self.theme["SIGNAL1_COLOR"], linewidth=2)
                axs[1].set_facecolor(self.theme["PANEL_COLOR"])
                axs[1].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
                axs[1].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
                axs[1].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
                axs[1].tick_params(colors=self.theme["TEXT_COLOR"])
                axs[1].set_title("Shifted Signal", color=self.theme["RESULT_COLOR"])
                axs[1].plot(t, processed, color=self.theme["RESULT_COLOR"], linewidth=2)
            elif operation == "Time Reversal":
                processed = s1[::-1]
                fig, axs = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
                axs = axs.flatten()
                axs[0].set_facecolor(self.theme["PANEL_COLOR"])
                axs[0].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
                axs[0].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
                axs[0].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
                axs[0].tick_params(colors=self.theme["TEXT_COLOR"])
                axs[0].set_title("Original Signal", color=self.theme["SIGNAL1_COLOR"])
                axs[0].plot(t, s1, color=self.theme["SIGNAL1_COLOR"], linewidth=2)
                axs[1].set_facecolor(self.theme["PANEL_COLOR"])
                axs[1].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
                axs[1].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
                axs[1].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
                axs[1].tick_params(colors=self.theme["TEXT_COLOR"])
                axs[1].set_title("Reversed Signal", color=self.theme["RESULT_COLOR"])
                axs[1].plot(t, processed, color=self.theme["RESULT_COLOR"], linewidth=2)
            else:
                processed = s1
                fig, axs = plt.subplots(1, 1, figsize=(7, 4), sharex=True)
                axs = np.array([axs])
                axs[0].set_facecolor(self.theme["PANEL_COLOR"])
                axs[0].grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
                axs[0].set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
                axs[0].set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
                axs[0].tick_params(colors=self.theme["TEXT_COLOR"])
                axs[0].set_title("Signal", color=self.theme["SIGNAL1_COLOR"])
                axs[0].plot(t, processed, color=self.theme["SIGNAL1_COLOR"], linewidth=2)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

        # Add Save as PNG button with file dialog for all signal types
        def save_png():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                title="Save plot as PNG"
            )
            if file_path:
                fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Saved", f"Plot saved as:\n{file_path}")

        save_btn = Button(win, text="Save as PNG", font=("Helvetica Neue", 14, "bold"),
                          bg=self.theme["BTN_COLOR"], fg=self.theme["BTN_TEXT_COLOR"],
                          command=save_png)
        save_btn.pack(pady=10)

    def reset_parameters(self):
        # Reset all parameters to their default values
        self.signal_type.set("Sine")
        self.amp1_var.set(1.0)
        self.freq1_var.set(5.0)
        self.phase1_var.set(0.0)
        self.signal2_type.set("Sine")
        self.amp2_var.set(1.0)
        self.freq2_var.set(5.0)
        self.phase2_var.set(0.0)
        self.operation_type.set("Time Scaling")
        self.param_var.set(1.0)
        self.plot_current_signal()
        # Show default graph after reset
        self.last_operation = self.operation_type.get()
        self.last_params = self.get_current_params()

    def run(self):
        self.master.mainloop()

if __name__ == "__main__":
    root = Tk()
    gui = SignalGUI(root)
    gui.run()
