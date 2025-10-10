# =================================================================================
# PREAMBLE
# =================================================================================
#
# Project: Advanced Weather Analysis System
#
# Description:
# This script provides a powerful command-line interface for analyzing yearly
# weather data. It leverages an advanced Segment Tree data structure to perform
# queries and updates with high efficiency. The system is designed to handle
# a variety of analytical tasks, from simple daily lookups to complex
# seasonal reports.
#
# Core Data Structure:
# The backend is powered by a Segment Tree that supports lazy propagation.
# Each node in the tree stores a tuple of aggregated data:
# (max_value, max_index, min_value, min_index, sum, count).
# This structure allows for efficient range queries and enables "soft-deleting"
# records without rebuilding the tree.
#
# Key Features:
#   - Fast range queries for min, max, and average temperature (O(log n)).
#   - Efficient single-day data recording, updating, and removal (O(log n)).
#   - Linear scan for threshold-based alerts (O(n)).
#   - Advanced seasonal analysis using a moving average algorithm (O(n log n)).
#
# Usage:
# Run the script from your terminal. It requires a 'yearly_weather_data.csv'
# file in the same directory. The CSV should have a header row followed by
# daily temperature readings, one per row.
#
# =================================================================================
import math
import csv

# =================================================================================
#  ADVANCED SEGMENT TREE BACKEND
# =================================================================================
class SegmentTree:
    """
    An advanced Segment Tree supporting complex nodes with counts for soft deletes
    and lazy propagation for range additions.

    Node Structure: (max_val, max_idx, min_val, min_idx, sum, count)
    
    Time Complexity Summary:
    - __init__: O(n) for building the tree from initial data.
    - _merge_nodes: O(1) for combining two nodes.
    - _build: O(n) for the recursive construction of the tree.
    - query: O(log n) for the public range query method.
    - _query_recursive: O(log n) for the internal recursive query logic.
    - _apply_lazy: O(1) for applying a pending update to a single node.
    - update_point: O(log n) for the public point update method.
    - _update_point_recursive: O(log n) for the internal recursive point update logic.
    - update_range_add: O(log n) for range addition updates (not used in menu).
    - _update_range_recursive: O(log n) for internal range update logic.
    """
    def __init__(self, data):
        self.data = data
        self.n = len(data)
        
        # NEW NODE: (max_val, max_idx, min_val, min_idx, sum, count)
        self.default_node = (-math.inf, -1, math.inf, -1, 0, 0)
        
        self.tree = [self.default_node] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        
        if self.n > 0:
            self._build(0, 0, self.n - 1)

    def _merge_nodes(self, left_node, right_node):
        max_v1, max_i1, min_v1, min_i1, sum1, count1 = left_node
        max_v2, max_i2, min_v2, min_i2, sum2, count2 = right_node

        # Determine overall max
        if max_v1 >= max_v2: new_max_v, new_max_i = max_v1, max_i1
        else: new_max_v, new_max_i = max_v2, max_i2

        # Determine overall min
        if min_v1 <= min_v2: new_min_v, new_min_i = min_v1, min_i1
        else: new_min_v, new_min_i = min_v2, min_i2
            
        new_sum = sum1 + sum2
        new_count = count1 + count2
        
        return (new_max_v, new_max_i, new_min_v, new_min_i, new_sum, new_count)

    def _build(self, node, start, end):
        if start == end:
            val = self.data[start]
            if val is not None:
                self.tree[node] = (val, start, val, start, val, 1)
            else:
                self.tree[node] = self.default_node
            return
        
        mid = (start + end) // 2
        self._build(2 * node + 1, start, mid)
        self._build(2 * node + 2, mid + 1, end)
        self.tree[node] = self._merge_nodes(self.tree[2 * node + 1], self.tree[2 * node + 2])

    def _apply_lazy(self, node, start, end, val):
        max_v, max_i, min_v, min_i, current_sum, current_count = self.tree[node]
        # Lazy value affects sum based on how many valid nodes are in the range
        # Min/max are also shifted by the lazy value.
        if current_count > 0: # Only apply if there's data in the node
             self.tree[node] = (max_v + val, max_i, min_v + val, min_i, current_sum + val * current_count, current_count)
        if start != end:
            self.lazy[2 * node + 1] += val
            self.lazy[2 * node + 2] += val

    def _query_recursive(self, node, start, end, l, r):
        if self.lazy[node] != 0:
            self._apply_lazy(node, start, end, self.lazy[node])
            self.lazy[node] = 0

        if start > r or end < l: return self.default_node
        
        if l <= start and end <= r: return self.tree[node]
        
        mid = (start + end) // 2
        left_result = self._query_recursive(2 * node + 1, start, mid, l, r)
        right_result = self._query_recursive(2 * node + 2, mid + 1, end, l, r)
        
        return self._merge_nodes(left_result, right_result)
        
    def query(self, l, r):
        if l > r or self.n == 0: return self.default_node
        return self._query_recursive(0, 0, self.n - 1, l, r)

    def update_point(self, idx, val):
        if not (0 <= idx < self.n): return
        self.data[idx] = val # val can be a number or None for removal
        self._update_point_recursive(0, 0, self.n - 1, idx)

    def _update_point_recursive(self, node, start, end, idx):
        if self.lazy[node] != 0:
            self._apply_lazy(node, start, end, self.lazy[node])
            self.lazy[node] = 0

        if start == end:
            val = self.data[idx]
            if val is not None:
                self.tree[node] = (val, idx, val, idx, val, 1)
            else: # This handles the removal
                self.tree[node] = self.default_node
            return
            
        mid = (start + end) // 2
        if start <= idx <= mid:
            self._update_point_recursive(2 * node + 1, start, mid, idx)
        else:
            self._update_point_recursive(2 * node + 2, mid + 1, end, idx)
            
        self.tree[node] = self._merge_nodes(self.tree[2 * node + 1], self.tree[2 * node + 2])

# =================================================================================
#  MENU-DRIVEN INTERFACE
# =================================================================================
def load_data_from_csv(filename):
    """Loads data from a CSV file, returning a list of temperatures."""
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader) # Skip header
            return [int(row[0]) for row in reader]
    except FileNotFoundError:
        print(f"❌ Error: Dataset file '{filename}' not found.")
        return None
    except Exception as e:
        print(f"❌ Error: Failed to load or parse data: {e}")
        return None

def main():
    """The main driver function to run the interactive program."""
    print("☀️ Welcome to the Advanced Weather Analysis System!")
    print("-------------------------------------------------")
    
    weather_data = load_data_from_csv("yearly_weather_data.csv")
    if weather_data is None:
        return

    num_days = len(weather_data)
    weather_tree = SegmentTree(weather_data)
    print(f"✅ Successfully loaded temperature data for {num_days} days.")

    while True:
        print("\n" + "="*15 + " MENU " + "="*15)
        print("1. Record/Update Weather Data ")
        print("2. Remove Weather Data ")
        print("3. View Daily Report        ")
        print("4. Check Weather Extremes   ")
        print("5. Generate Climate Summary ")
        print("6. Analytics: Range Queries ")
        print("7. Analytics: Threshold Alerts")
        print("8. Seasonal Utilization Report")
        print("9. Exit")
        print("="*38)
        
        try:
            choice = int(input("Enter your choice (1-9): "))
            
            if choice == 1: # Record/Update Weather Data
                day = int(input(f"Enter Day to Update (0-{num_days-1}): "))
                temp = int(input("Enter new temperature value: "))
                if 0 <= day < num_days:
                    weather_tree.update_point(day, temp)
                    print(f"✅ Success: Day {day} updated to {temp}°C.")
                else:
                    print("❌ Error: Invalid day.")

            elif choice == 2: # Remove Weather Data
                day = int(input(f"Enter Day to Remove (0-{num_days-1}): "))
                if 0 <= day < num_days:
                    weather_tree.update_point(day, None) # Use None for soft delete
                    print(f"✅ Success: Weather data for day {day} has been removed.")
                else:
                    print("❌ Error: Invalid day.")

            elif choice == 3: # View Daily Report
                day = int(input(f"Enter Day to View (0-{num_days-1}): "))
                if 0 <= day < num_days:
                    temp = weather_tree.data[day]
                    if temp is not None:
                        print(f"✅ Report for Day {day}: {temp}°C")
                    else:
                        print(f"✅ Report for Day {day}: No data recorded.")
                else:
                    print("❌ Error: Invalid day.")

            elif choice == 4: # Check Weather Extremes
                result = weather_tree.query(0, num_days - 1)
                max_v, max_i, min_v, min_i, _, _ = result
                print("📈 Yearly Weather Extremes:")
                if max_i != -1:
                    print(f"   - Hottest Day: {max_v}°C on Day {max_i}")
                    print(f"   - Coldest Day: {min_v}°C on Day {min_i}")
                else:
                    print("   - No data available.")
            
            elif choice == 5: # Generate Climate Summary
                result = weather_tree.query(0, num_days - 1)
                _, _, _, _, total_sum, count = result
                print("📊 Yearly Climate Summary:")
                if count > 0:
                    avg = round(total_sum / count, 2)
                    print(f"   - Average Temperature: {avg}°C")
                    print(f"   - Total Valid Records: {count}")
                else:
                    print("   - No data to generate a summary.")

            elif choice == 6: # Analytics: Range Queries
                start = int(input(f"Enter Start Day (0-{num_days-1}): "))
                end = int(input(f"Enter End Day (0-{num_days-1}): "))
                if not (0 <= start <= end < num_days):
                    print("❌ Error: Invalid date range.")
                    continue
                
                result = weather_tree.query(start, end)
                max_v, max_i, min_v, min_i, total_sum, count = result
                
                print(f"🔍 Analytics for Days {start}-{end}:")
                if count > 0:
                    avg = round(total_sum / count, 2)
                    print(f"   - Max Temp: {max_v}°C (on Day {max_i})")
                    print(f"   - Min Temp: {min_v}°C (on Day {min_i})")
                    print(f"   - Avg Temp: {avg}°C")
                else:
                    print("   - No data in the selected range.")

            elif choice == 7: # Analytics: Threshold Alerts
                threshold = int(input("Enter temperature threshold (°C): "))
                mode = input("Find days [above] or [below] threshold? ").lower()
                alerts = []
                for day, temp in enumerate(weather_tree.data):
                    if temp is None: continue
                    if mode == "above" and temp > threshold:
                        alerts.append((day, temp))
                    elif mode == "below" and temp < threshold:
                        alerts.append((day, temp))
                
                print(f"🚨 Found {len(alerts)} days {mode} {threshold}°C:")
                if alerts:
                    print("   " + ", ".join([f"Day {d} ({t}°C)" for d, t in alerts]))
                else:
                    print("   None.")
            
            elif choice == 8: # Seasonal Utilization Report
                k = int(input("Enter window size for moving average (e.g., 7 for a weekly window): "))
                moving_averages = []
                print("Processing... This may take a moment.")
                for day in range(num_days):
                    start = max(0, day - k)
                    end = min(num_days - 1, day + k)
                    _, _, _, _, total_sum, count = weather_tree.query(start, end)
                    avg = round(total_sum / count, 2) if count > 0 else 0
                    moving_averages.append(avg)
                print(f"✅ Generated moving average report with a {k}-day window.")
                print(f"   First {k} values:", moving_averages[:k])
                print(f"   Last {k}  values:", moving_averages[-k:])

            elif choice == 9:
                print("Exiting the system. Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1 and 9.")

        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()