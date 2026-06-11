import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pymongo
import csv
from config import MONGO_URI

# MongoDB connection
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["financeflow"]
    collection = db["expenses"]
    print("MongoDB connected successfully")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    collection = None

class FinanceFlow:
    def __init__(self, root):
        self.root = root
        self.root.title("FinanceFlow - Expense Tracker")
        self.root.geometry("900x600")
        
        # Title
        title = tk.Label(root, text="FinanceFlow", font=("Arial", 24, "bold"))
        title.pack(pady=10)
        
        subtitle = tk.Label(root, text="Track your expenses. Control your money.", font=("Arial", 10))
        subtitle.pack(pady=(0,10))
        
        # Main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Add expense form
        left_frame = tk.Frame(main_frame, relief="solid", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0,10))
        
        # Right side - Expense list
        right_frame = tk.Frame(main_frame, relief="solid", bd=1)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Form labels and entries
        tk.Label(left_frame, text="Add New Expense", font=("Arial", 16)).pack(pady=10)
        
        tk.Label(left_frame, text="Amount:").pack(anchor="w", padx=20, pady=(10,0))
        self.amount_entry = tk.Entry(left_frame, font=("Arial", 12))
        self.amount_entry.pack(fill="x", padx=20, pady=5)
        
        tk.Label(left_frame, text="Category:").pack(anchor="w", padx=20, pady=(10,0))
        self.category_var = tk.StringVar()
        categories = ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Healthcare", "Other"]
        self.category_menu = ttk.Combobox(left_frame, textvariable=self.category_var, values=categories)
        self.category_menu.pack(fill="x", padx=20, pady=5)
        
        tk.Label(left_frame, text="Description:").pack(anchor="w", padx=20, pady=(10,0))
        self.desc_entry = tk.Entry(left_frame, font=("Arial", 12))
        self.desc_entry.pack(fill="x", padx=20, pady=5)
        
        tk.Label(left_frame, text="Date (YYYY-MM-DD):").pack(anchor="w", padx=20, pady=(10,0))
        self.date_entry = tk.Entry(left_frame, font=("Arial", 12))
        self.date_entry.pack(fill="x", padx=20, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Add button
        self.add_btn = tk.Button(left_frame, text="Add Expense", bg="green", fg="white", font=("Arial", 12), command=self.add_expense)
        self.add_btn.pack(pady=20)
        
        # Right side - expense list title
        tk.Label(right_frame, text="Recent Expenses", font=("Arial", 16)).pack(pady=10)
        
        # Treeview for expenses
        columns = ("Date", "Category", "Description", "Amount")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Button frame for delete and export
        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=10)
        
        self.delete_btn = tk.Button(button_frame, text="Delete Selected", bg="red", fg="white", command=self.delete_expense)
        self.delete_btn.pack(side="left", padx=5)
        
        self.export_btn = tk.Button(button_frame, text="Export to CSV", bg="blue", fg="white", command=self.export_to_csv)
        self.export_btn.pack(side="left", padx=5)
        
        # Summary label at bottom
        self.summary_label = tk.Label(root, text="Total: $0", font=("Arial", 14), fg="blue")
        self.summary_label.pack(pady=10)
        
        # Load existing expenses from database
        self.load_expenses()

    def save_expense_to_db(self, amount, category, description, date):
        if collection is None:
            messagebox.showerror("Error", "Database not connected")
            return False
        
        expense = {
            "amount": amount,
            "category": category,
            "description": description,
            "date": date,
            "created_at": datetime.now()
        }
        
        try:
            collection.insert_one(expense)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            return False
    
    def load_expenses(self):
        if collection is None:
            return
        
        # Clear existing table items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            expenses = collection.find().sort("created_at", -1)
            for exp in expenses:
                self.tree.insert("", "end", values=(
                    exp["date"], 
                    exp["category"], 
                    exp["description"], 
                    f"${exp['amount']:.2f}"
                ))
            self.update_total()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")
    
    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_var.get()
            description = self.desc_entry.get()
            date = self.date_entry.get()
            
            if not category:
                category = "Other"
            
            if not description:
                description = "-"
            
            # Save to database
            if self.save_expense_to_db(amount, category, description, date):
                # Add to table
                self.tree.insert("", "end", values=(date, category, description, f"${amount:.2f}"))
                
                # Clear entries
                self.amount_entry.delete(0, tk.END)
                self.category_var.set("")
                self.desc_entry.delete(0, tk.END)
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
                
                self.update_total()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
    
    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an expense to delete")
            return
        
        if messagebox.askyesno("Confirm", "Delete this expense?"):
            # Get the expense details from the table
            item = self.tree.item(selected[0])
            values = item["values"]
            
            # Delete from table first
            self.tree.delete(selected[0])
            
            # Delete from database
            if collection:
                try:
                    amount_str = values[3].replace("$", "")
                    amount = float(amount_str)
                    date = values[0]
                    description = values[2]
                    category = values[1]
                    
                    collection.delete_one({
                        "amount": amount,
                        "date": date,
                        "description": description,
                        "category": category
                    })
                except Exception as e:
                    print(f"Database delete error: {e}")
            
            self.update_total()
            messagebox.showinfo("Success", "Expense deleted")
    
    def export_to_csv(self):
        if not self.tree.get_children():
            messagebox.showwarning("Warning", "No expenses to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Date", "Category", "Description", "Amount"])
                    
                    for item in self.tree.get_children():
                        values = self.tree.item(item)["values"]
                        writer.writerow(values)
                
                messagebox.showinfo("Success", f"Exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def update_total(self):
        total = 0
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            amount_str = values[3].replace("$", "")
            total += float(amount_str)
        
        self.summary_label.config(text=f"Total: ${total:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceFlow(root)
    root.mainloop()