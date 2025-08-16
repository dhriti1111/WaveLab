from tkinter import Tk, Label, Button, StringVar, OptionMenu, Frame, DoubleVar, IntVar, Canvas, Scrollbar, filedialog, messagebox, BooleanVar, Checkbutton
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

        self.freq1_var = DoubleVar(value=1.0)
        self.freq1_label = self.add_slider(control_frame, "Frequency", self.freq1_var, 1.0, 20.0, 1.0, self.theme["SIGNAL2_COLOR"])
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

        # Parameter slider
        self.param_var = DoubleVar(value=1.0)
        self.param_label = Label(control_frame, text="Scaling factor (a):", bg=self.theme["PANEL_COLOR"], fg=self.theme["ACCENT_COLOR"], font=("Helvetica Neue", 14, "bold"))
        self.param_slider = ttk.Scale(control_frame, from_=0.1, to=5.0, variable=self.param_var, orient="horizontal", style="Scaling.Horizontal.TScale")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Scaling.Horizontal.TScale", troughcolor=self.theme["SLIDER_BG"], background=self.theme["ACCENT_COLOR"], thickness=8)
        
        # Formula display
        self.formula_label = Label(control_frame, text="Formula: x(at)", bg=self.theme["PANEL_COLOR"], fg=self.theme["ACCENT_COLOR"], font=("Helvetica Neue", 14, "italic"))
        self.formula_label.pack(pady=10)

        # Discrete Time Controls
        view_options_frame = Frame(control_frame, bg=self.theme["PANEL_COLOR"])
        view_options_frame.pack(fill="x", padx=15, pady=(10, 5))
        self.is_discrete_var = BooleanVar(value=False)
        discrete_check = Checkbutton(view_options_frame, text="Discrete Time", variable=self.is_discrete_var,
                                       bg=self.theme["PANEL_COLOR"], fg=self.theme["TEXT_COLOR"],
                                       selectcolor=self.theme["BG_COLOR"], activebackground=self.theme["PANEL_COLOR"],
                                       font=("Helvetica Neue", 14, "bold"), command=self.toggle_discrete_controls)
        discrete_check.pack(side="left")

        self.samples_frame = Frame(control_frame, bg=self.theme["PANEL_COLOR"])
        self.samples_var = IntVar(value=50)
        self.samples_label = self.add_slider(self.samples_frame, "Number of Samples", self.samples_var, 10, 200, 1, self.theme["ACCENT_COLOR"])
        
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
        self.is_discrete_var.trace_add("write", lambda *args: self.dynamic_update())
        self.samples_var.trace_add("write", lambda *args: self.dynamic_update())

        self.update_parameter_controls(self.operation_type.get())
        self.toggle_discrete_controls()


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
        
        format_spec = "{:.0f}" if isinstance(var, IntVar) else "{:.2f}"
        
        lbl = Label(frame, text=f"{text}: {format_spec.format(var.get())}", bg=self.theme["PANEL_COLOR"], fg=color, font=("Helvetica Neue", 14, "bold"))
        lbl.pack(side="left")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(f"{text}.Horizontal.TScale", troughcolor=self.theme["SLIDER_BG"], background=color, thickness=8)
        
        slider = ttk.Scale(frame, from_=frm, to=to, variable=var, orient="horizontal",
                           style=f"{text}.Horizontal.TScale", 
                           command=lambda v, l=lbl, name=text: l.config(text=f"{name}: {format_spec.format(float(v))}"))
        slider.pack(side="right", fill="x", expand=True)
        return lbl

    def update_parameter_controls(self, operation):
        self.signal2_frame.pack_forget()
        self.param_label.pack_forget()
        self.param_slider.pack_forget()

        before_formula = self.formula_label

        if operation in ["Signal Addition", "Signal Multiplication"]:
            self.signal2_frame.pack(before=before_formula, fill="x")
        
        param_controls_to_show = []

        if operation == "Time Scaling":
            self.param_label.config(text=f"Scaling factor (a): {self.param_var.get():.2f}")
            self.param_slider.config(from_=0.1, to=5.0)
            param_controls_to_show = [self.param_label, self.param_slider]
        elif operation == "Amplitude Scaling":
            self.param_label.config(text=f"Amplitude (A): {self.param_var.get():.2f}")
            self.param_slider.config(from_=0.1, to=5.0)
            param_controls_to_show = [self.param_label, self.param_slider]
        elif operation == "Time Shifting":
            self.param_label.config(text=f"Shift (t₀): {self.param_var.get():.2f}")
            self.param_slider.config(from_=-5.0, to=5.0)
            param_controls_to_show = [self.param_label, self.param_slider]

        for widget in param_controls_to_show:
            if widget == self.param_label:
                widget.pack(before=before_formula, anchor="w", padx=15, pady=(15, 0))
            else:
                widget.pack(before=before_formula, fill="x", padx=15, pady=5)
        
        self.formula_label.config(text=f"Formula: {OPERATION_FORMULAS.get(operation, '')}")

        def update_label(val):
            val = float(val)
            if operation == "Time Shifting":
                self.param_label.config(text=f"Shift (t₀): {val:.2f}")
            elif operation == "Time Scaling":
                self.param_label.config(text=f"Scaling factor (a): {val:.2f}")
            elif operation == "Amplitude Scaling":
                self.param_label.config(text=f"Amplitude (A): {val:.2f}")

        self.param_slider.config(command=update_label)

    def toggle_discrete_controls(self):
        if self.is_discrete_var.get():
            self.samples_frame.pack(before=self.process_button, fill="x", pady=5)
        else:
            self.samples_frame.pack_forget()

    def process_signal(self):
        self.last_operation = self.operation_type.get()
        self.last_params = self.get_current_params()
        self.plot_current_signal()

    def get_current_params(self):
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
            "param": self.param_var.get(),
            "is_discrete": self.is_discrete_var.get(),
            "samples": self.samples_var.get()
        }

    def dynamic_update(self):
        if self.last_operation is not None:
            self.plot_current_signal()

    def plot_current_signal(self):
        operation = self.operation_type.get()
        params = self.get_current_params()
        
        num_points = params["samples"] if params["is_discrete"] else 500
        t_input = np.linspace(0, 1, num_points)

        t_min, t_max = 0, 1
        if operation == "Time Shifting":
            t0 = params["param"]
            t_min, t_max = 0 + t0, 1 + t0
        elif operation == "Time Scaling":
            a = params["param"]
            if a != 0:
                t_min, t_max = min(0/a, 1/a), max(0/a, 1/a)
        elif operation == "Time Reversal":
            t_min, t_max = -1, 0
        
        t_output = np.linspace(t_min, t_max, num_points)
        s1 = self.generate_signal(params["signal_type"], t_input, params["amp1"], params["freq1"], params["phase1"])
        
        processed = None
        s2 = None

        if operation == "Time Shifting":
            processed = self.generate_signal(params["signal_type"], t_output - params["param"], params["amp1"], params["freq1"], params["phase1"])
            self.plot_signals([t_input, t_output], s1, processed, is_discrete=params["is_discrete"])
        elif operation == "Time Scaling":
            a = params["param"]
            processed = self.generate_signal(params["signal_type"], a * t_output, params["amp1"], params["freq1"], params["phase1"])
            self.plot_signals([t_input, t_output], s1, processed, is_discrete=params["is_discrete"])
        elif operation == "Time Reversal":
            processed = self.generate_signal(params["signal_type"], -t_output, params["amp1"], params["freq1"], params["phase1"])
            self.plot_signals([t_input, t_output], s1, processed, is_discrete=params["is_discrete"])
        elif operation in ["Signal Addition", "Signal Multiplication"]:
            s2 = self.generate_signal(params["signal2_type"], t_input, params["amp2"], params["freq2"], params["phase2"])
            processed = s1 + s2 if operation == "Signal Addition" else s1 * s2
            self.plot_signals(t_input, s1, processed, s2, is_discrete=params["is_discrete"])
        elif operation == "Amplitude Scaling":
            processed = params["param"] * s1
            self.plot_signals(t_input, s1, processed, is_discrete=params["is_discrete"])
        else:
            processed = s1
            self.plot_signals(t_input, s1, processed, is_discrete=params["is_discrete"])

    def plot_signals(self, t, s1, processed, s2=None, is_discrete=False):
        self.figure.clf()
        n_plots = 3 if s2 is not None else 2
        axs = self.figure.subplots(n_plots, 1)
        axs = np.array(axs).flatten()

        for ax in axs:
            ax.set_facecolor(self.theme["PANEL_COLOR"])
            ax.grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
            ax.set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
            ax.set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
            ax.tick_params(colors=self.theme["TEXT_COLOR"])
            ax.axhline(0, color="#22C0D5", linewidth=2, alpha=0.8)
            ax.axvline(0, color="#22C0D5", linewidth=2, alpha=0.8)
        
        # --- FIX START ---
        # Helper function to correctly handle plotting for both modes
        def plot_or_stem(ax, x_data, y_data, color):
            if is_discrete:
                # For stem, we set the color of each part individually
                markerline, stemlines, baseline = ax.stem(x_data, y_data, basefmt=" ")
                plt.setp(markerline, 'color', color)
                plt.setp(stemlines, 'color', color)
            else:
                ax.plot(x_data, y_data, color=color, linewidth=2)
        # --- FIX END ---

        t_s1 = t[0] if isinstance(t, list) else t
        t_processed = t[1] if isinstance(t, list) else t
        
        axs[0].set_title("Signal 1", color=self.theme["SIGNAL1_COLOR"])
        plot_or_stem(axs[0], t_s1, s1, self.theme["SIGNAL1_COLOR"]) # Use helper

        if s2 is not None:
            axs[1].set_title("Signal 2", color=self.theme["SIGNAL2_COLOR"])
            plot_or_stem(axs[1], t, s2, self.theme["SIGNAL2_COLOR"]) # Use helper
            axs[2].set_title("Resultant Signal", color=self.theme["RESULT_COLOR"])
            plot_or_stem(axs[2], t, processed, self.theme["RESULT_COLOR"]) # Use helper
        else:
            axs[1].set_title("Processed Signal", color=self.theme["RESULT_COLOR"])
            plot_or_stem(axs[1], t_processed, processed, self.theme["RESULT_COLOR"]) # Use helper
            
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
                try:
                    ax_idx = list(axs).index(ax)
                except ValueError:
                    return
                
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
                self.hover_label.place(x=event.x + 10, y=event.y + 10)
            else:
                self.hover_label.place_forget()

        self.hover_cid = self.canvas_plot.mpl_connect("motion_notify_event", on_motion)

    def generate_signal(self, sig_type, t, amp, freq, phase=0):
        phase_rad = np.deg2rad(phase)
        with np.errstate(divide='ignore', invalid='ignore'):
            if sig_type == "Sine":
                return amp * np.sin(2 * np.pi * freq * t + phase_rad)
            elif sig_type == "Square":
                return amp * np.sign(np.sin(2 * np.pi * freq * t + phase_rad))
            elif sig_type == "Sawtooth":
                return amp * (2 * (freq * t - np.floor(0.5 + freq * t)))
            elif sig_type == "Step":
                return amp * np.heaviside(t, 1)
            elif sig_type == "Impulse":
                idx = (np.abs(t)).argmin()
                arr = np.zeros_like(t)
                arr[idx] = amp
                return arr
            elif sig_type == "Ramp":
                return amp * t
        return np.zeros_like(t)

    def open_signals_window(self):
        params = self.get_current_params()
        operation = params["operation"]
        is_discrete = params["is_discrete"]
        num_points = params["samples"] if is_discrete else 500
        
        win = tk.Toplevel(self.master)
        win.title("All Signals")
        win.configure(bg=self.theme["BG_COLOR"])

        t_input = np.linspace(0, 1, num_points)
        s1 = self.generate_signal(params["signal_type"], t_input, params["amp1"], params["freq1"], params["phase1"])
        
        fig = None
        
        def setup_ax(ax, title, color):
            ax.set_facecolor(self.theme["PANEL_COLOR"])
            ax.grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
            ax.set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
            ax.set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
            ax.tick_params(colors=self.theme["TEXT_COLOR"])
            ax.set_title(title, color=color)
            ax.axhline(0, color="#22C0D5", linewidth=1, alpha=0.7)
            ax.axvline(0, color="#22C0D5", linewidth=1, alpha=0.7)

        # --- FIX START ---
        # Re-use the same robust plotting helper here
        def plot_or_stem(ax, x_data, y_data, color):
            if is_discrete:
                markerline, stemlines, baseline = ax.stem(x_data, y_data, basefmt=" ")
                plt.setp(markerline, 'color', color)
                plt.setp(stemlines, 'color', color)
            else:
                ax.plot(x_data, y_data, color=color, linewidth=2)
        # --- FIX END ---

        if operation in ["Signal Addition", "Signal Multiplication"]:
            fig, axs = plt.subplots(3, 1, figsize=(8, 8))
            s2 = self.generate_signal(params["signal2_type"], t_input, params["amp2"], params["freq2"], params["phase2"])
            processed = s1 + s2 if operation == "Signal Addition" else s1 * s2
            
            setup_ax(axs[0], "Signal 1", self.theme["SIGNAL1_COLOR"])
            plot_or_stem(axs[0], t_input, s1, self.theme["SIGNAL1_COLOR"])
            setup_ax(axs[1], "Signal 2", self.theme["SIGNAL2_COLOR"])
            plot_or_stem(axs[1], t_input, s2, self.theme["SIGNAL2_COLOR"])
            setup_ax(axs[2], "Resultant Signal", self.theme["RESULT_COLOR"])
            plot_or_stem(axs[2], t_input, processed, self.theme["RESULT_COLOR"])
        else:
            fig, axs = plt.subplots(2, 1, figsize=(8, 6))
            t_output = t_input
            processed = s1
            title2 = "Processed Signal"

            if operation == "Time Shifting":
                t0 = params["param"]
                t_output = np.linspace(t0, 1 + t0, num_points)
                processed = self.generate_signal(params["signal_type"], t_output - t0, params["amp1"], params["freq1"], params["phase1"])
                title2 = "Shifted Signal"
            elif operation == "Time Scaling":
                a = params["param"]
                if a != 0:
                    t_output = np.linspace(min(0/a, 1/a), max(0/a, 1/a), num_points)
                processed = self.generate_signal(params["signal_type"], t_output * a, params["amp1"], params["freq1"], params["phase1"])
                title2 = "Time-Scaled Signal"
            elif operation == "Time Reversal":
                t_output = np.linspace(-1, 0, num_points)
                processed = self.generate_signal(params["signal_type"], -t_output, params["amp1"], params["freq1"], params["phase1"])
                title2 = "Reversed Signal"
            elif operation == "Amplitude Scaling":
                processed = params["param"] * s1
                title2 = "Amplitude-Scaled Signal"

            setup_ax(axs[0], "Original Signal", self.theme["SIGNAL1_COLOR"])
            plot_or_stem(axs[0], t_input, s1, self.theme["SIGNAL1_COLOR"])
            setup_ax(axs[1], title2, self.theme["RESULT_COLOR"])
            plot_or_stem(axs[1], t_output, processed, self.theme["RESULT_COLOR"])

        if fig:
            fig.patch.set_facecolor(self.theme["PANEL_COLOR"])
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=win)
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            canvas.draw()
            
            def save_png():
                file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")], title="Save plot as PNG")
                if file_path:
                    fig.savefig(file_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
                    messagebox.showinfo("Saved", f"Plot saved as:\n{file_path}")

            save_btn = Button(win, text="Save as PNG", font=("Helvetica Neue", 14, "bold"),
                              bg=self.theme["BTN_COLOR"], fg=self.theme["BTN_TEXT_COLOR"], command=save_png)
            save_btn.pack(pady=10, padx=10, fill='x')

    def reset_parameters(self):
        self.signal_type.set("Sine")
        self.amp1_var.set(1.0)
        self.freq1_var.set(1.0)
        self.phase1_var.set(0.0)
        self.signal2_type.set("Sine")
        self.amp2_var.set(1.0)
        self.freq2_var.set(1.0)
        self.phase2_var.set(0.0)
        self.operation_type.set("Time Scaling")
        self.param_var.set(1.0)
        self.is_discrete_var.set(False)
        self.samples_var.set(50)
        self.toggle_discrete_controls()
        self.last_operation = self.operation_type.get()
        self.last_params = self.get_current_params()
        self.plot_current_signal()

    def run(self):
        self.master.mainloop()

if __name__ == "__main__":
    root = Tk()
    gui = SignalGUI(root)
    root.minsize(1200, 800)
    gui.run()