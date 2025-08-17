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
    "SIGNAL1_COLOR": "#B4C6F5",
    "SIGNAL2_COLOR": "#F9CC98",
    "RESULT_COLOR": "#39FF14",
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
        main_frame.grid_columnconfigure(1, weight=2) 
        main_frame.grid_rowconfigure(0, weight=1)

                # --- REFINED SCALABLE CONTROL PANEL ---
        #
        # REFINED SCALABLE CONTROL PANEL
        control_panel_container = Frame(main_frame, bg=self.theme["PANEL_COLOR"], highlightbackground="#222233", highlightthickness=1)
        control_panel_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        control_panel_container.grid_rowconfigure(0, weight=1)
        control_panel_container.grid_columnconfigure(0, weight=1)

        canvas = Canvas(control_panel_container, bg=self.theme["PANEL_COLOR"], highlightthickness=0)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Vertical.TScrollbar", gripcount=0,
                        background=self.theme["ACCENT_COLOR"], darkcolor=self.theme["SLIDER_BG"], lightcolor=self.theme["SLIDER_BG"],
                        troughcolor=self.theme["PANEL_COLOR"], bordercolor=self.theme["BG_COLOR"], arrowcolor=self.theme["BG_COLOR"])

        scrollbar = ttk.Scrollbar(control_panel_container, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        canvas.configure(yscrollcommand=scrollbar.set)

        # We initially place the scrollbar with .grid() but will hide it if not needed.
        # The grid manager will remember its options.
        scrollbar.grid(row=0, column=1, sticky='ns')
        canvas.grid(row=0, column=0, sticky='nsew')

        control_frame = Frame(canvas, bg=self.theme["PANEL_COLOR"])
        frame_id = canvas.create_window((0, 0), window=control_frame, anchor="nw")


        # --- START OF MODIFIED SECTION ---

        def _update_scrollbar_visibility(event=None):
            """
            Checks if the scrollbar is needed based on content height vs. canvas height.
            Shows or hides the scrollbar accordingly.
            """
            # Update the scrollregion to encompass the entire height of the control_frame
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Bbox returns (x1, y1, x2, y2); index 3 is the bottom coordinate (total height)
            content_height = canvas.bbox("all")[3] 
            
            # Get the current visible height of the canvas widget
            canvas_height = canvas.winfo_height()

            # If the content is taller than the canvas, the scrollbar is needed
            if content_height > canvas_height:
                # Show the scrollbar using grid. It remembers its last options (row, column, sticky).
                scrollbar.grid()
            else:
                # If content fits, hide the scrollbar.
                scrollbar.grid_forget()

        def _on_canvas_configure(event):
            """
            Called when the canvas is resized. Scales the inner frame's width
            and then checks if the scrollbar should be visible.
            """
            # This makes the inner frame scale with the canvas's width
            canvas.itemconfig(frame_id, width=event.width)
            _update_scrollbar_visibility()


        # When the control_frame's content changes size, check if we need a scrollbar.
        control_frame.bind("<Configure>", _update_scrollbar_visibility)

        # When the canvas itself is resized (e.g., main window resize), update the frame width
        # and also re-check if we need the scrollbar.
        canvas.bind("<Configure>", _on_canvas_configure)

        # --- END OF MODIFIED SECTION ---


        def on_mousewheel(event):
            # Check if the scrollbar is currently visible before scrolling
            if scrollbar.winfo_ismapped():
                widget_under_cursor = master.winfo_containing(event.x_root, event.y_root)
                if widget_under_cursor:
                    current_widget = widget_under_cursor
                    while current_widget is not None:
                        if current_widget == control_panel_container:
                            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                            break
                        current_widget = current_widget.master

        def on_linux_scroll(event):
            # Check if the scrollbar is currently visible before scrolling
            if scrollbar.winfo_ismapped():
                widget_under_cursor = master.winfo_containing(event.x_root, event.y_root)
                if widget_under_cursor:
                    current_widget = widget_under_cursor
                    while current_widget is not None:
                        if current_widget == control_panel_container:
                            scroll_amount = 0
                            if event.num == 4:
                                scroll_amount = -1
                            elif event.num == 5:
                                scroll_amount = 1
                            canvas.yview_scroll(scroll_amount, "units")
                            break
                        current_widget = current_widget.master


        master.bind_all("<MouseWheel>", on_mousewheel)
        master.bind_all("<Button-4>", on_linux_scroll)
        master.bind_all("<Button-5>", on_linux_scroll)
        
        # Signal 1 controls
        self.signal_type = StringVar(master, "Sine")
        Label(control_frame, text="Signal 1 Type", bg=self.theme["PANEL_COLOR"], fg=self.theme["TEXT_COLOR"], font=("Helvetica Neue", 16, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        signal_type_menu = OptionMenu(control_frame, self.signal_type, "Sine", "Square", "Sawtooth", "Step", "Impulse", "Ramp")
        signal_type_menu.config(font=("Helvetica Neue", 14))
        signal_type_menu.pack(fill="x", padx=15, pady=5)
        menu = signal_type_menu["menu"]
        menu.config(font=("Helvetica Neue", 15))
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
        menu = operation_menu["menu"]
        menu.config(font=("Helvetica Neue", 15))

        # Signal 2 controls (for addition/multiplication)
        self.signal2_frame = Frame(control_frame, bg=self.theme["PANEL_COLOR"])
        Label(self.signal2_frame, text="Signal 2 Type", bg=self.theme["PANEL_COLOR"], fg=self.theme["TEXT_COLOR"], font=("Helvetica Neue", 16, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        self.signal2_type = StringVar(master, "Sine")
        signal2_type_menu = OptionMenu(self.signal2_frame, self.signal2_type, "Sine", "Square", "Sawtooth", "Step", "Impulse", "Ramp")
        signal2_type_menu.pack(fill="x", padx=15, pady=5)
        signal2_type_menu.config(font=("Helvetica Neue", 14)) 
        menu = signal2_type_menu["menu"]
        menu.config(font=("Helvetica Neue", 15))
        
        self.amp2_var = DoubleVar(value=1.0)
        self.amp2_label = self.add_slider(self.signal2_frame, "Amplitude", self.amp2_var, 0.1, 5.0, 0.1, self.theme["SIGNAL1_COLOR"])

        self.freq2_var = DoubleVar(value=1.0)
        self.freq2_label = self.add_slider(self.signal2_frame, "Frequency", self.freq2_var, 1.0, 20.0, 1.0, self.theme["SIGNAL2_COLOR"])

        self.phase2_var = DoubleVar(value=0.0)
        phase2_frame = Frame(self.signal2_frame, bg=self.theme["PANEL_COLOR"])
        phase2_frame.pack(fill="x", padx=15, pady=(10, 0))
        Label(phase2_frame, text="Phase (°):", bg=self.theme["PANEL_COLOR"], fg=self.theme["RESULT_COLOR"], font=("Helvetica Neue", 14, "bold")).pack(side="left")
        phase2_entry = tk.Entry(phase2_frame, textvariable=self.phase2_var, font=("Helvetica Neue", 14), width=8, bg=self.theme["BG_COLOR"], fg=self.theme["RESULT_COLOR"])
        phase2_entry.pack(side="left", padx=(10, 0))

        # Parameter slider
        self.param_var = DoubleVar(value=1.0)
        self.param_label = Label(control_frame, text="Scaling factor (a):", bg=self.theme["PANEL_COLOR"], fg=self.theme["ACCENT_COLOR"], font=("Helvetica Neue", 14, "bold"))
        self.param_slider = ttk.Scale(control_frame, from_=0.1, to=5.0, variable=self.param_var, orient="horizontal", style="Scaling.Horizontal.TScale")
        
        style.configure("Scaling.Horizontal.TScale", troughcolor=self.theme["SLIDER_BG"], background=self.theme["ACCENT_COLOR"], thickness=8)
        
        # Formula display
        self.formula_label = Label(control_frame, text="Formula: x(at)", bg=self.theme["PANEL_COLOR"], fg=self.theme["ACCENT_COLOR"], font=("Helvetica Neue", 14, "italic"))
        self.formula_label.pack(pady=10)

        # Discrete Time Controls
        view_options_frame = Frame(control_frame, bg=self.theme["PANEL_COLOR"])
        view_options_frame.pack(fill="x", padx=15, pady=(10, 5))
        self.is_discrete_var = BooleanVar(value=False)
        discrete_check = Checkbutton(view_options_frame, text="DISCRETE TIME", variable=self.is_discrete_var,
                                       bg=self.theme["PANEL_COLOR"], fg=self.theme["TEXT_COLOR"],
                                       selectcolor=self.theme["BG_COLOR"], activebackground=self.theme["PANEL_COLOR"],
                                       font=("Helvetica Neue", 16, "bold"), command=self.toggle_discrete_controls)
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
        self.show_all_button.pack(pady=(0, 10), fill="x", padx=15)

        self.save_button = Button(control_frame, text="Save This Plot", font=("Helvetica Neue", 16, "bold"),
                                  command=self.save_main_plot, bg="#EC49D4", fg=self.theme["BTN_TEXT_COLOR"], relief="flat")
        self.save_button.pack(pady=(0, 20), fill="x", padx=15)

        # Reset button
        self.reset_button = Button(control_frame, text="Reset to Default", font=("Helvetica Neue", 14, "bold"),
                                  command=self.reset_parameters, bg=self.theme["ACCENT_COLOR"], fg=self.theme["BTN_TEXT_COLOR"])
        self.reset_button.pack(pady=(0, 20), fill="x", padx=15)
        
       
        # Right panel - Plots
        plot_frame = Frame(main_frame, bg=self.theme["PANEL_COLOR"], highlightbackground="#222233", highlightthickness=1)
        plot_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.figure, self.axs = plt.subplots(1, 1, figsize=(6, 6))
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
            self.signal2_frame.pack(before=before_formula, fill="x", pady=5)
        
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
        params = self.get_current_params()
        operation = params["operation"]
        is_discrete = params["is_discrete"]
        num_points = params["samples"] if is_discrete else 500

        t_input = np.linspace(0, 1, num_points)
        s1 = self.generate_signal(params["signal_type"], t_input, params["amp1"], params["freq1"], params["phase1"])
        s2 = None

        t_processed = t_input
        processed = s1

        if operation == "Time Shifting":
            t0 = params["param"]
            t_processed = t_input + t0
            processed = s1
        
        elif operation == "Time Scaling":
            a = params["param"]
            if a > 1e-9:
                t_processed = t_input / a
                processed = s1
            else:
                t_processed = t_input
                val_at_zero = self.generate_signal(params["signal_type"], np.zeros(1), params["amp1"], params["freq1"], params["phase1"])[0]
                processed = np.full_like(t_input, val_at_zero)

        elif operation == "Time Reversal":
            t_processed = -t_input
            processed = s1
            
        elif operation in ["Signal Addition", "Signal Multiplication"]:
            s2 = self.generate_signal(params["signal2_type"], t_input, params["amp2"], params["freq2"], params["phase2"])
            processed = s1 + s2 if operation == "Signal Addition" else s1 * s2
        
        elif operation == "Amplitude Scaling":
            processed = params["param"] * s1

        self.plot_signals(t_input, s1, t_processed, processed, s2, is_discrete)

    def plot_signals(self, t_input, s1, t_processed, processed, s2=None, is_discrete=False):
        ax = self.axs
        ax.clear()

        ax.set_facecolor(self.theme["PANEL_COLOR"])
        ax.grid(True, linestyle='--', alpha=0.3, color=self.theme["ACCENT_COLOR"])
        ax.set_xlabel("Time (s)", color=self.theme["TEXT_COLOR"])
        ax.set_ylabel("Amplitude", color=self.theme["TEXT_COLOR"])
        ax.tick_params(colors=self.theme["TEXT_COLOR"])
        ax.axhline(0, color="#EDF344", linewidth=2, alpha=0.8) 
        ax.axvline(0, color="#EDF344", linewidth=2, alpha=0.8)
        ax.set_title("Combined Signal Plot", color=self.theme["ACCENT_COLOR"])
        
        ax.axvspan(0, 1, facecolor='#2c2c3a', alpha=0.6, zorder=0)

        def plot_or_stem(ax, x_data, y_data, color, label, style='-', linewidth=1.5):
            if is_discrete:
                markerline, stemlines, baseline = ax.stem(x_data, y_data, label=label, basefmt=" ")
                plt.setp(markerline, 'color', color)
                if style == '--':
                    plt.setp(stemlines, 'color', color, linestyle='dashed', linewidth=linewidth)
                else:
                    plt.setp(stemlines, 'color', color, linewidth=linewidth)
            else:
                ax.plot(x_data, y_data, color=color, linewidth=linewidth, label=label, linestyle=style)
        
        plot_or_stem(ax, t_input, s1, self.theme["SIGNAL1_COLOR"], label="Signal 1")
        if s2 is not None:
            plot_or_stem(ax, t_input, s2, self.theme["SIGNAL2_COLOR"], label="Signal 2")
        
        plot_or_stem(ax, t_processed, processed, self.theme["RESULT_COLOR"], label="Processed", style='-', linewidth=3)

        x_min = min(np.min(t_input), np.min(t_processed))
        x_max = max(np.max(t_input), np.max(t_processed))
        x_range = x_max - x_min
        if x_range > 1e-9:
            x_padding = x_range * 0.05
            ax.set_xlim(x_min - x_padding, x_max + x_padding)

        all_y_values = np.concatenate([s1, processed, s2 if s2 is not None else []])
        y_min, y_max = np.min(all_y_values), np.max(all_y_values)
        y_range = y_max - y_min
        if y_range > 1e-9:
            y_padding = y_range * 0.1
            ax.set_ylim(y_min - y_padding, y_max + y_padding)

        ax.legend(facecolor=self.theme["PANEL_COLOR"], edgecolor=self.theme["ACCENT_COLOR"], labelcolor=self.theme["TEXT_COLOR"])

        operation = self.operation_type.get()
        param = self.param_var.get()
        info_text = f"Operation: {operation}\n"
        if operation == "Time Scaling":
            info_text += f"Factor (a): {param:.2f}"
        elif operation == "Amplitude Scaling":
            info_text += f"Amplitude (A): {param:.2f}"
        elif operation == "Time Shifting":
            info_text += f"Shift (t₀): {param:.2f}"
        elif operation in ["Signal Addition", "Signal Multiplication", "Time Reversal"]:
             info_text = f"Operation: {operation}"

        ax.text(0.98, 0.98, info_text, transform=ax.transAxes, fontsize=11,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor=self.theme["SLIDER_BG"], alpha=0.8, edgecolor=self.theme["ACCENT_COLOR"]))

        self.figure.tight_layout()
        self.canvas_plot.draw()
        
        if hasattr(self, 'hover_cid'):
            self.canvas_plot.mpl_disconnect(self.hover_cid)
        if hasattr(self, 'hover_label'):
            self.hover_label.destroy()
            
        self.hover_label = Label(self.canvas_plot.get_tk_widget(), bg="#222233", fg="#39FF14", font=("Helvetica Neue", 12, "bold"), bd=1, relief="solid", justify='left')
        self.hover_label.place_forget()

        def on_motion(event):
            if event.inaxes:
                text_lines = []
                x = event.xdata
                
                idx1 = (np.abs(t_input - x)).argmin()
                if idx1 < len(s1):
                    text_lines.append(f"S1: (x={t_input[idx1]:.2f}, y={s1[idx1]:.2f})")
                
                if s2 is not None:
                    idx2 = (np.abs(t_input - x)).argmin()
                    if idx2 < len(s2):
                        text_lines.append(f"S2: (x={t_input[idx2]:.2f}, y={s2[idx2]:.2f})")
                    
                idx_p = (np.abs(t_processed - x)).argmin()
                if idx_p < len(processed):
                    text_lines.append(f"Proc: (x={t_processed[idx_p]:.2f}, y={processed[idx_p]:.2f})")
                
                self.hover_label.config(text="\n".join(text_lines))
                self.hover_label.place(x=event.x + 15, y=event.y + 15)
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

    def save_main_plot(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Combined Plot As..."
        )
        if file_path:
            watermark_text = self.figure.text(0.98, 0.02, 'WaveLab',
                                              fontsize=12, color='#cccccc',
                                              ha='right', va='bottom', alpha=0.4,
                                              transform=self.figure.transFigure)
            try:
                self.figure.savefig(
                    file_path,
                    dpi=300,
                    bbox_inches='tight',
                    facecolor=self.figure.get_facecolor()
                )
                messagebox.showinfo("Save Successful", f"Plot saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"An error occurred while saving the plot:\n{e}")
            finally:
                watermark_text.remove()
                self.canvas_plot.draw()

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

        def plot_or_stem(ax, x_data, y_data, color):
            if is_discrete:
                markerline, stemlines, baseline = ax.stem(x_data, y_data, basefmt=" ")
                plt.setp(markerline, 'color', color)
                plt.setp(stemlines, 'color', color)
            else:
                ax.plot(x_data, y_data, color=color, linewidth=2)

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
                t_output = t_input + t0
                processed = s1
                title2 = "Shifted Signal"
            elif operation == "Time Scaling":
                a = params["param"]
                if a != 0:
                    t_output = t_input / a
                processed = s1
                title2 = "Time-Scaled Signal"
            elif operation == "Time Reversal":
                t_output = -t_input
                processed = s1
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
                    watermark_text = fig.text(0.98, 0.02, 'WaveLab',
                                              fontsize=12, color='#cccccc',
                                              ha='right', va='bottom', alpha=0.4,
                                              transform=fig.transFigure)
                    try:
                        fig.savefig(file_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
                        messagebox.showinfo("Saved", f"Plot saved as:\n{file_path}")
                    finally:
                        watermark_text.remove()
                        canvas.draw()

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