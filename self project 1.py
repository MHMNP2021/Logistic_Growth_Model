import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LogisticGrowthModelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Logistic Growth Model Simulator")
        self.root.geometry("1000x800")  #  window size
        self.root.resizable(True, True)  # Allow resizing

        # Style
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 10))

        # Title
        title_label = ttk.Label(root, text="Logistic Growth Model Simulator", 
                                font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=10)

        # Input Frame
        input_frame = ttk.LabelFrame(root, text="Model Parameters")
        input_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="ew")

        #Create Parameters Inputs
        params = [
            ("Initial Population (N0)", "initial_pop"),
            ("Carrying Capacity (K)", "carrying_capacity"),
            ("Growth Rate (r)", "growth_rate"),
            ("Time Steps", "time_steps")
        ]

# create entry widgets for each parameter
        self.entries = {}
        for i, (label, attr) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=i//2, column=(i%2)*2, padx=5, pady=5)
            self.entries[attr] = ttk.Entry(input_frame, width=20)
            self.entries[attr].grid(row=i//2, column=(i%2)*2+1, padx=5, pady=5)

        # Harvest Type Dropdown
        ttk.Label(input_frame, text="Harvest Type").grid(row=len(params)//2, column=0, padx=5, pady=5)
        self.harvest_type = ttk.Combobox(input_frame, 
            values=["No Harvest", "Constant Harvest", "Periodic Harvest", "Proportional Harvest"])
        self.harvest_type.grid(row=len(params)//2, column=1, padx=5, pady=5)
        self.harvest_type.bind('<<ComboboxSelected>>', self.toggle_harvest_input)

        # Fixed Harvest Input 
        ttk.Label(input_frame, text="Harvest Amount").grid(row=len(params)//2+1, column=0, padx=5, pady=5)
        self.fixed_harvest_entry = ttk.Entry(input_frame, width=20, state='disabled')
        self.fixed_harvest_entry.grid(row=len(params)//2+1, column=1, padx=5, pady=5)

        # Buttons Frame
        button_frame = ttk.Frame(root)
        button_frame.grid(row=2, column=0, pady=10)

        ttk.Button(button_frame, text="Simulate", command=self.simulate_model).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_inputs).grid(row=0, column=1, padx=5)

        # Matplotlib Figure Frame
        self.figure_frame = ttk.LabelFrame(root, text="Population Dynamics")
        self.figure_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")
        
        # Configure grid to allow expansion
        root.grid_rowconfigure(3, weight=1)
        root.grid_columnconfigure(0, weight=1)

    def toggle_harvest_input(self, event=None):
        """Enable/disable harvest amount input based on harvest type"""
        if self.harvest_type.get() == "Constant Harvest":
            self.fixed_harvest_entry.config(state='normal')
        else:
            self.fixed_harvest_entry.config(state='disabled')

    def simulate_model(self):
        try:
            # Validate and extract inputs
            N0 = float(self.entries['initial_pop'].get())
            K = float(self.entries['carrying_capacity'].get())
            r = float(self.entries['growth_rate'].get())
            T = int(self.entries['time_steps'].get())
            harvest_type = self.harvest_type.get()

            # Time array
            time = np.arange(T+1)
            population = np.zeros(T+1)
            population[0] = N0

            # Harvest amount
            H = 0
            if harvest_type == "Constant Harvest":
                H = float(self.fixed_harvest_entry.get())

            # Simulation logic
            for t in range(1, T+1):
                # Logistic growth with different harvest strategies
                if harvest_type == "No Harvest":
                    population[t] = population[t-1] + r * population[t-1] * (1 - population[t-1]/K)
                elif harvest_type == "Constant Harvest":
                    population[t] = max(0, population[t-1] + r * population[t-1] * (1 - population[t-1]/K) - H)
                elif harvest_type == "Proportional Harvest":
                    # Harvest proportional to current population
                    h_rate = 0.1  # 10% harvest rate
                    harvest = h_rate * population[t-1]
                    population[t] = max(0, population[t-1] + r * population[t-1] * (1 - population[t-1]/K) - harvest)
                elif harvest_type == "Periodic Harvest":
                    # Harvest every 3 time steps
                    harvest = H if t % 3 == 0 else 0
                    population[t] = max(0, population[t-1] + r * population[t-1] * (1 - population[t-1]/K) - harvest)

            # Plotting
            self.plot_results(time, population)

        except ValueError as e:
            messagebox.showerror("Input Error", f"Please enter valid numerical values: {str(e)}")

    def plot_results(self, time, population):
        # Clear previous plot
        for widget in self.figure_frame.winfo_children():
            widget.destroy()

        # Create matplotlib figure with increased size and high DPI
        plt.close('all')  # Close any existing figures
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        ax.plot(time, population, label='Population')
        ax.set_title("Population Dynamics")
        ax.set_xlabel("Time")
        ax.set_ylabel("Population")
        ax.legend()
        plt.tight_layout()  # Adjust layout to prevent cutting off labels

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.figure_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def clear_inputs(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.fixed_harvest_entry.delete(0, tk.END)
        self.fixed_harvest_entry.config(state='disabled')
        self.harvest_type.set('')

        # Clear the previous plot
        for widget in self.figure_frame.winfo_children():
            widget.destroy()

def main():
    root = tk.Tk()
    app = LogisticGrowthModelApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()