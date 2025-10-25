# advanced_weather_app.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import csv
import math
import matplotlib.pyplot as plt

# =================================================================================
#  ADVANCED SEGMENT TREE BACKEND
# =================================================================================
class SegmentTree:
    """
    An advanced Segment Tree supporting complex nodes and lazy propagation
    for range additions. Designed for a 4-member team.

    Time Complexity Summary:
    - __init__: O(n) for building the tree.
    - _merge_nodes: O(1) for merging two nodes.
    - _build: O(n) for constructing the tree.
    - query: O(log n) for querying a range.
    - _query_recursive: O(log n) for recursive query.
    - _apply_lazy: O(1) for applying lazy updates.
    - update_range_add: O(log n) for range addition.
    - _update_range_recursive: O(log n) for recursive range update.
    - update_point: O(log n) for point update.
    - _update_point_recursive: O(log n) for recursive point update.
    """
    # Member 1: The Core Architect & Builder
    # -----------------------------------------------------------------------------
    def __init__(self, data):
        """
        Responsibility 1.1: Initialize all data structures.
        Sets up the main data array, the tree for storing complex nodes,
        and the lazy array for pending updates.

        
        """
        self.data = data
        self.n = len(data)
        
        # Default node: (max_val, max_idx, min_val, min_idx, sum)
        self.default_node = (-math.inf, -1, math.inf, -1, 0)
        
        # The tree stores the merged node data
        self.tree = [self.default_node] * (4 * self.n)
        
        # The lazy array stores pending additions for a range
        self.lazy = [0] * (4 * self.n)
        
        if self.n > 0:
            self._build(0, 0, self.n - 1)

    def _merge_nodes(self, left_node, right_node):
        """
        Responsibility 1.2: Merge two child nodes into a parent node.
        This logic is crucial for building and updating the tree correctly.

        """
        # Unpack children
        max_v1, max_i1, min_v1, min_i1, sum1 = left_node
        max_v2, max_i2, min_v2, min_i2, sum2 = right_node

        # Combine max value and its index
        if max_v1 >= max_v2:
            new_max_v, new_max_i = max_v1, max_i1
        else:
            new_max_v, new_max_i = max_v2, max_i2

        # Combine min value and its index
        if min_v1 <= min_v2:
            new_min_v, new_min_i = min_v1, min_i1
        else:
            new_min_v, new_min_i = min_v2, min_i2
            
        # Combine sum
        new_sum = sum1 + sum2
        
        return (new_max_v, new_max_i, new_min_v, new_min_i, new_sum)

    def _build(self, node, start, end):
        """
        Responsibility 1.3: Recursively construct the Segment Tree.
        Builds the tree from the bottom up using the merge logic.

        Time Complexity: O(n), where n is the number of elements in the data.
        This is because each element is processed once during the build.
        """
        if start == end:
            val = self.data[start]
            self.tree[node] = (val, start, val, start, val)
            return
        
        mid = (start + end) // 2
        self._build(2 * node + 1, start, mid)
        self._build(2 * node + 2, mid + 1, end)
        self.tree[node] = self._merge_nodes(self.tree[2 * node + 1], self.tree[2 * node + 2])

    # Member 2: The Query Specialist
    # -----------------------------------------------------------------------------
    def query(self, l, r):
        """
        Responsibility 2.1 & 2.2: Public method to start a query.
        This provides the final, merged node for a given range [l, r].
        The GUI will then extract max, min, or average from this result.

        """
        if l > r: return self.default_node
        return self._query_recursive(0, 0, self.n - 1, l, r)

    def _query_recursive(self, node, start, end, l, r):
        """ The recursive workhorse for the query function. """
        # Apply lazy propagation before querying
        if self.lazy[node] != 0:
            self._apply_lazy(node, start, end, self.lazy[node])
            self.lazy[node] = 0

        # No overlap
        if start > r or end < l:
            return self.default_node
        
        # Total overlap
        if l <= start and end <= r:
            return self.tree[node]

        # Partial overlap
        mid = (start + end) // 2
        left_result = self._query_recursive(2 * node + 1, start, mid, l, r)
        right_result = self._query_recursive(2 * node + 2, mid + 1, end, l, r)
        
        return self._merge_nodes(left_result, right_result)


    def _apply_lazy(self, node, start, end, val):
        """
        Responsibility 2.3 (Helper): Applies a lazy value to a node's data.
        Updates max, min, and sum based on the value to add.

        """
        max_v, max_i, min_v, min_i, current_sum = self.tree[node]
        range_size = end - start + 1
        self.tree[node] = (max_v + val, max_i, min_v + val, min_i, current_sum + val * range_size)
        if start != end: # Mark children as lazy
            self.lazy[2 * node + 1] += val
            self.lazy[2 * node + 2] += val


    # Member 3: The Range Update Specialist (Lazy Propagation)
    # -----------------------------------------------------------------------------
    def update_range_add(self, l, r, val):
        """
        Responsibility 3.1: Public method to add a value to a range.
        This is the entry point for the "heatwave" scenario.
        """
        if l > r: return
        self._update_range_recursive(0, 0, self.n - 1, l, r, val)

    def _update_range_recursive(self, node, start, end, l, r, val):
        """
        Responsibility 3.2 & 3.3: The main recursive range update function.
        Finds the relevant nodes and applies updates to the lazy array.
        """
        # First, apply any pending updates at this node
        if self.lazy[node] != 0:
            self._apply_lazy(node, start, end, self.lazy[node])
            self.lazy[node] = 0 # Clear the lazy mark

        # No overlap
        if start > r or end < l: return
        
        # Total overlap: Apply update to current node and mark children as lazy
        if l <= start and end <= r:
            self._apply_lazy(node, start, end, val)
            return

        # Partial overlap: Recurse on children
        mid = (start + end) // 2
        self._update_range_recursive(2 * node + 1, start, mid, l, r, val)
        self._update_range_recursive(2 * node + 2, mid + 1, end, l, r, val)
        
        # Update parent from children after recursion
        self.tree[node] = self._merge_nodes(self.tree[2 * node + 1], self.tree[2 * node + 2])
        
    # Member 4: The Point Updater & GUI Integrator
    # -----------------------------------------------------------------------------
    def update_point(self, idx, val):
        """
        Responsibility 4.1: Public method to update a single point.
        Used for correcting a single day's temperature.
        """
        if not (0 <= idx < self.n): return
        self.data[idx] = val
        self._update_point_recursive(0, 0, self.n - 1, idx)

    def _update_point_recursive(self, node, start, end, idx):
        """
        Responsibility 4.2 & 4.3: The recursive point update function.
        Similar to build, but only follows the path to a single leaf.
        """
        # Push lazy values down the path to the point we are updating
        if self.lazy[node] != 0:
            self._apply_lazy(node, start, end, self.lazy[node])
            self.lazy[node] = 0

        if start == end:
            self.tree[node] = (self.data[idx], idx, self.data[idx], idx, self.data[idx])
            return
            
        mid = (start + end) // 2
        if start <= idx <= mid:
            # Before recursing, ensure children of the other path are up-to-date
            if self.lazy[2*node+1] != 0: self._apply_lazy(2*node+1, start, mid, self.lazy[2*node+1]); self.lazy[2*node+1] = 0
            self._update_point_recursive(2 * node + 1, start, mid, idx)
        else:
            # Before recursing, ensure children of the other path are up-to-date
            if self.lazy[2*node+2] != 0: self._apply_lazy(2*node+2, mid+1, end, self.lazy[2*node+2]); self.lazy[2*node+2] = 0
            self._update_point_recursive(2 * node + 2, mid + 1, end, idx)
            
        self.tree[node] = self._merge_nodes(self.tree[2 * node + 1], self.tree[2 * node + 2])

# =================================================================================
#  GUI (Responsibility of Member 4)
# =================================================================================
class WeatherApp(ctk.CTk):
    def __init__(self, weather_data):
        super().__init__()
        self.weather_data = weather_data
        self.num_days = len(weather_data)
        self.weather_tree = SegmentTree(self.weather_data)
        
        self.title("☀️ Advanced Weather Analysis Dashboard"); self.geometry("850x750") # Increased height for new button
        ctk.set_appearance_mode("light"); ctk.set_default_color_theme("blue")
        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1); self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Advanced Weather Analysis Dashboard", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")

        # Query Section
        query_frame = ctk.CTkFrame(controls_frame)
        query_frame.pack(pady=15, padx=20, fill="x")
        ctk.CTkLabel(query_frame, text="Analyze Date Range", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        self.query_type = ctk.CTkOptionMenu(query_frame, values=["Max Temperature", "Min Temperature", "Average Temperature"])
        self.query_type.pack(pady=10, padx=10, fill="x")
        self.start_day_entry = ctk.CTkEntry(query_frame, placeholder_text="Start Day")
        self.start_day_entry.pack(pady=5, padx=10, fill="x")
        self.end_day_entry = ctk.CTkEntry(query_frame, placeholder_text="End Day")
        self.end_day_entry.pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(query_frame, text="Run Analysis", command=self.perform_query).pack(pady=15, padx=10)

        # Range Update Section
        rupdate_frame = ctk.CTkFrame(controls_frame)
        rupdate_frame.pack(pady=15, padx=20, fill="x")
        ctk.CTkLabel(rupdate_frame, text="Range Update (e.g., Heatwave)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        self.r_start_entry = ctk.CTkEntry(rupdate_frame, placeholder_text="Start Day")
        self.r_start_entry.pack(pady=5, padx=10, fill="x")
        self.r_end_entry = ctk.CTkEntry(rupdate_frame, placeholder_text="End Day")
        self.r_end_entry.pack(pady=5, padx=10, fill="x")
        self.r_val_entry = ctk.CTkEntry(rupdate_frame, placeholder_text="Value to Add (e.g., 3 or -2)")
        self.r_val_entry.pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(rupdate_frame, text="Apply Range Update", command=self.perform_range_update).pack(pady=15, padx=10)
        
        # Visualization Buttons Frame
        vis_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        vis_frame.pack(pady=15, padx=20, fill="x")
        vis_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(vis_frame, text="📊 Show Weather Graph", command=self.show_graph).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # ### START OF NEW CODE ###
        ctk.CTkButton(vis_frame, text="🌳 Visualize Segment Tree", command=self.visualize_tree).grid(row=0, column=1, padx=(5, 0), sticky="ew")
        # ### END OF NEW CODE ###

        data_frame = ctk.CTkFrame(self)
        data_frame.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        ctk.CTkLabel(data_frame, text="Current Data Array Viewer", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        self.data_display = ctk.CTkTextbox(data_frame, wrap="none", font=("Courier New", 11))
        self.data_display.pack(pady=10, padx=10, fill="both", expand=True)
        self.refresh_data_display()

        result_frame = ctk.CTkFrame(self, fg_color="transparent")
        result_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.result_label = ctk.CTkLabel(result_frame, text="Results will be shown here.", font=ctk.CTkFont(size=14))
        self.result_label.pack()

    # ### START OF NEW CODE ###
    def visualize_tree(self):
        """Generates a plot of the segment tree structure."""
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.set_title("Segment Tree Structure (Top 4 Levels)", fontsize=16)
        ax.axis('off')
        
        # Start the recursive drawing from the root node (index 0)
        self._draw_node_recursive(ax, 0, 0, 0, 1.0, 0.5, 0)
        
        plt.tight_layout()
        plt.show()

    def _draw_node_recursive(self, ax, node_idx, x, y, dx, dy, depth):
        """Recursively draws a node and its children."""
        MAX_DEPTH = 4 
        if depth >= MAX_DEPTH or node_idx >= len(self.weather_tree.tree):
            return

        # Get node data and format it for display
        node_data = self.weather_tree.tree[node_idx]
        max_v, _, min_v, _, total_sum = node_data
        
        # Check if the node is a default/empty node
        if max_v == -math.inf:
            return

        # Format text for the node
        node_text = f"Max: {max_v}\nMin: {min_v}\nSum: {total_sum}"
        
        # Define properties for the node's appearance
        bbox_props = dict(boxstyle="round,pad=0.5", fc="lightblue", ec="black", lw=1)
        ax.text(x, y, node_text, ha="center", va="center", bbox=bbox_props, fontsize=9)
        
        # Calculate positions for children
        left_child_idx = 2 * node_idx + 1
        right_child_idx = 2 * node_idx + 2
        
        # Draw left child and the connecting line
        if left_child_idx < len(self.weather_tree.tree):
            x_left, y_child = x - dx, y - dy
            ax.plot([x, x_left], [y, y_child], 'k-')
            self._draw_node_recursive(ax, left_child_idx, x_left, y_child, dx/2, dy, depth + 1)
            
        # Draw right child and the connecting line
        if right_child_idx < len(self.weather_tree.tree):
            x_right, y_child = x + dx, y - dy
            ax.plot([x, x_right], [y, y_child], 'k-')
            self._draw_node_recursive(ax, right_child_idx, x_right, y_child, dx/2, dy, depth + 1)
    # ### END OF NEW CODE ###

    def perform_query(self):
        try:
            start, end = int(self.start_day_entry.get()), int(self.end_day_entry.get())
            if not (0 <= start <= end < self.num_days):
                messagebox.showerror("Invalid Range", f"Range must be between 0 and {self.num_days - 1}.")
                return
            
            # This is the crucial part that uses the Segment Tree
            result_node = self.weather_tree.query(start, end)
            
            max_v, max_i, min_v, min_i, total_sum = result_node
            q_type = self.query_type.get()
            
            if q_type == "Max Temperature":
                self.result_label.configure(text=f"✅ Max Temp: {max_v}°C (on Day {max_i})")
            elif q_type == "Min Temperature":
                self.result_label.configure(text=f"✅ Min Temp: {min_v}°C (on Day {min_i})")
            elif q_type == "Average Temperature":
                count = end - start + 1
                avg = round(total_sum / count, 2) if count > 0 else 0
                self.result_label.configure(text=f"✅ Average Temp: {avg}°C from Day {start} to {end}")
        except ValueError: messagebox.showerror("Invalid Input", "Please enter valid numbers.")

    def perform_range_update(self):
        try:
            start, end, val = int(self.r_start_entry.get()), int(self.r_end_entry.get()), int(self.r_val_entry.get())
            if not (0 <= start <= end < self.num_days):
                messagebox.showerror("Invalid Range", f"Range must be between 0 and {self.num_days - 1}.")
                return
                
            self.weather_tree.update_range_add(start, end, val)
            
            # After updating, the internal data array also needs to be updated for the display
            for i in range(start, end + 1):
                self.weather_tree.data[i] += val

            self.result_label.configure(text=f"✅ Applied {val:+}°C to days {start}-{end}.")
            self.refresh_data_display()
        except ValueError: messagebox.showerror("Invalid Input", "Please enter valid numbers.")
            
    def refresh_data_display(self):
        self.data_display.configure(state="normal")
        self.data_display.delete('1.0', tk.END)
        
        # Display 10 numbers per line for better readability
        data_str = ""
        for i, val in enumerate(self.weather_tree.data):
            data_str += f"{val:3d} "
            if (i + 1) % 15 == 0:
                data_str += "\n"
        
        self.data_display.insert(tk.END, data_str)
        self.data_display.configure(state="disabled")

    def show_graph(self):
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(range(self.num_days), self.weather_tree.data, color='#3498db', linewidth=2)
        ax.set_title('Maximum Daily Temperatures Over a Year', fontsize=16)
        ax.set_xlabel('Day of the Year'); ax.set_ylabel('Temperature (°C)')
        ax.fill_between(range(self.num_days), self.weather_tree.data, color='#3498db', alpha=0.1)
        plt.tight_layout(); plt.show()

# =========================================================
#  APPLICATION BOOTSTRAP
# =========================================================
def load_data_from_csv(filename):
    try:
        with open(filename, 'r') as f: return [int(row[0]) for row in list(csv.reader(f))[1:]]
    except FileNotFoundError: messagebox.showerror("Error", f"'{filename}' not found. Please create a CSV file with temperature data."); return None
    except Exception as e: messagebox.showerror("Error", f"Failed to load data: {e}"); return None

if __name__ == "__main__":
    if (weather_data := load_data_from_csv("yearly_weather_data.csv")):
        app = WeatherApp(weather_data)
        app.mainloop()