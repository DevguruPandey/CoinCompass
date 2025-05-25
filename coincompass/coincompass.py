import os
import datetime
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib
import time
import sys

class PasswordManager:
    def __init__(self):
        self.password_file = "password.json"
        self.max_attempts = 3
        self.attempts = 0
    
    def hash_password(self, password):
        """Hash the password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def password_exists(self):
        """Check if password file exists"""
        return os.path.exists(self.password_file)
    
    def set_password(self, password):
        """Set a new password"""
        hashed_password = self.hash_password(password)
        with open(self.password_file, 'w') as file:
            json.dump({"password": hashed_password}, file)
        return True
    
    def verify_password(self, password):
        """Verify if the password is correct"""
        if not self.password_exists():
            return False
        
        with open(self.password_file, 'r') as file:
            data = json.load(file)
            stored_hash = data.get("password", "")
            
        return self.hash_password(password) == stored_hash
    
    def login(self, password):
        """Try to login with password"""
        self.attempts += 1
        
        if self.verify_password(password):
            self.attempts = 0
            return True
        
        if self.attempts >= self.max_attempts:
            self.show_dead_screen()
            
        return False
    
    def show_dead_screen(self):
        """Show 'dead' message and exit application"""
        # Clear the console
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Display dead message
        print("\n" + "=" * 50)
        print("      UNAUTHORIZED ACCESS DETECTED")
        print("      SYSTEM LOCKDOWN ACTIVATED")
        print("=" * 50)
        print("\n      ACCESS PERMANENTLY DENIED\n")
        
        # Exit the application after a delay
        time.sleep(2)
        sys.exit()


class LoginWindow:
    def __init__(self, root, password_manager, on_login_success):
        self.root = root
        self.password_manager = password_manager
        self.on_login_success = on_login_success
        
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("Budget Tracker - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        window_width = 400
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # App title
        title_label = ttk.Label(main_frame, text="Budget Tracker", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Password exists check
        if not self.password_manager.password_exists():
            self.setup_new_password_ui(main_frame)
        else:
            self.setup_login_ui(main_frame)
    
    def setup_new_password_ui(self, parent):
        # New password frame
        password_frame = ttk.LabelFrame(parent, text="Create Password")
        password_frame.pack(fill=tk.BOTH, padx=20, pady=10)
        
        # Password entry
        password_label = ttk.Label(password_frame, text="New Password:")
        password_label.pack(pady=(10, 5))
        
        self.new_password = ttk.Entry(password_frame, show="*")
        self.new_password.pack(fill=tk.X, padx=20)
        
        # Confirm password entry
        confirm_label = ttk.Label(password_frame, text="Confirm Password:")
        confirm_label.pack(pady=(10, 5))
        
        self.confirm_password = ttk.Entry(password_frame, show="*")
        self.confirm_password.pack(fill=tk.X, padx=20)
        self.confirm_password.bind("<Return>", lambda e: self.create_password())
        
        # Set password button
        set_button = ttk.Button(password_frame, text="Set Password", command=self.create_password)
        set_button.pack(pady=20)
    
    def setup_login_ui(self, parent):
        # Login frame
        login_frame = ttk.LabelFrame(parent, text="Login")
        login_frame.pack(fill=tk.BOTH, padx=20, pady=10)
        
        # Password entry
        password_label = ttk.Label(login_frame, text="Enter Password:")
        password_label.pack(pady=(10, 5))
        
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.pack(fill=tk.X, padx=20)
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.password_entry.focus_set()
        
        # Login button
        login_button = ttk.Button(login_frame, text="Login", command=self.login)
        login_button.pack(pady=20)
        
        # Attempts label
        self.attempts_label = ttk.Label(login_frame, text=f"Attempts remaining: {self.password_manager.max_attempts}")
        self.attempts_label.pack(pady=5)
    
    def create_password(self):
        password = self.new_password.get()
        confirm = self.confirm_password.get()
        
        if not password:
            messagebox.showerror("Error", "Password cannot be empty")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        self.password_manager.set_password(password)
        messagebox.showinfo("Success", "Password set successfully!")
        
        # Destroy all widgets and setup login UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Budget Tracker", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        self.setup_login_ui(main_frame)
    
    def login(self):
        password = self.password_entry.get()
        
        if not password:
            messagebox.showerror("Error", "Please enter your password")
            return
        
        if self.password_manager.login(password):
            self.root.destroy()  # Close login window
            self.on_login_success()  # Launch the main application
        else:
            attempts_left = self.password_manager.max_attempts - self.password_manager.attempts
            if attempts_left > 0:
                self.attempts_label.config(text=f"Attempts remaining: {attempts_left}")
                messagebox.showerror("Error", f"Incorrect password! {attempts_left} attempts remaining.")
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus_set()
            # If no attempts left, the show_dead_screen will be called from the login method


class BudgetTracker:
    def __init__(self):
        self.transactions = []
        self.filename = "budget_data.json"
        self.load_data()
    
    def load_data(self):
        """Load transaction data from file if it exists"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as file:
                    self.transactions = json.load(file)
            except:
                messagebox.showerror("Error", "Error reading data file. Starting with empty transactions.")
                self.transactions = []
    
    def save_data(self):
        """Save transaction data to file"""
        with open(self.filename, 'w') as file:
            json.dump(self.transactions, file, indent=4)
    
    def add_transaction(self, amount, category, description, transaction_type, date=None):
        """Add a new transaction to the tracker"""
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                return False, "Amount must be greater than zero"
        except ValueError:
            return False, "Amount must be a valid number"
        
        # Validate category
        if not category or category.strip() == "":
            return False, "Category cannot be empty"
        
        transaction = {
            "id": len(self.transactions) + 1 if self.transactions else 1,
            "date": date,
            "type": transaction_type,
            "amount": amount,
            "category": category,
            "description": description
        }
        
        self.transactions.append(transaction)
        self.save_data()
        return True, f"{transaction_type.capitalize()} of ${amount:.2f} added successfully!"
    
    def get_balance(self):
        """Calculate current balance, total income, and total expenses"""
        total_income = 0
        total_expenses = 0
        
        for transaction in self.transactions:
            if transaction["type"] == "income":
                total_income += transaction["amount"]
            else:  # expense
                total_expenses += transaction["amount"]
                
        balance = total_income - total_expenses
        
        return {
            "income": total_income,
            "expenses": total_expenses,
            "balance": balance
        }
    
    def get_transactions(self, sort_by_date=True):
        """Get all transactions, optionally sorted by date"""
        if sort_by_date and self.transactions:
            # Create a copy to avoid modifying the original list
            sorted_transactions = sorted(
                self.transactions, 
                key=lambda x: x["date"],
                reverse=True  # Most recent first
            )
            return sorted_transactions
        return self.transactions
    
    def get_category_summary(self):
        """Get summary of expenses by category"""
        categories = {}
        
        for transaction in self.transactions:
            if transaction["type"] == "expense":
                category = transaction["category"]
                amount = transaction["amount"]
                
                if category in categories:
                    categories[category] += amount
                else:
                    categories[category] = amount
        
        return categories
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction by ID"""
        for i, transaction in enumerate(self.transactions):
            if transaction["id"] == transaction_id:
                self.transactions.pop(i)
                self.save_data()
                return True, f"Transaction {transaction_id} deleted successfully!"
        
        return False, f"Transaction with ID {transaction_id} not found."


class BudgetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Budget Tracker")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize the budget tracker
        self.budget = BudgetTracker()
        
        # Set up the tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.add_transaction_tab = ttk.Frame(self.notebook)
        self.transactions_tab = ttk.Frame(self.notebook)
        self.categories_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.add_transaction_tab, text="Add Transaction")
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.categories_tab, text="Categories")
        
        # Set up each tab
        self.setup_dashboard_tab()
        self.setup_add_transaction_tab()
        self.setup_transactions_tab()
        self.setup_categories_tab()
        
        # Update all tabs with current data
        self.update_all_tabs()
    
    def setup_dashboard_tab(self):
        # Title frame
        title_frame = ttk.Frame(self.dashboard_tab)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = ttk.Label(title_frame, text="Budget Summary", font=("Arial", 16, "bold"))
        title_label.pack()
        
        # Balance frame
        balance_frame = ttk.LabelFrame(self.dashboard_tab, text="Current Balance")
        balance_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Income
        income_frame = ttk.Frame(balance_frame)
        income_frame.pack(fill=tk.X, padx=10, pady=5)
        
        income_label = ttk.Label(income_frame, text="Total Income:", width=15)
        income_label.pack(side=tk.LEFT)
        
        self.income_value = ttk.Label(income_frame, text="$0.00", width=15)
        self.income_value.pack(side=tk.LEFT)
        
        # Expenses
        expenses_frame = ttk.Frame(balance_frame)
        expenses_frame.pack(fill=tk.X, padx=10, pady=5)
        
        expenses_label = ttk.Label(expenses_frame, text="Total Expenses:", width=15)
        expenses_label.pack(side=tk.LEFT)
        
        self.expenses_value = ttk.Label(expenses_frame, text="$0.00", width=15)
        self.expenses_value.pack(side=tk.LEFT)
        
        # Balance
        net_frame = ttk.Frame(balance_frame)
        net_frame.pack(fill=tk.X, padx=10, pady=5)
        
        net_label = ttk.Label(net_frame, text="Net Balance:", width=15)
        net_label.pack(side=tk.LEFT)
        
        self.net_value = ttk.Label(net_frame, text="$0.00", width=15)
        self.net_value.pack(side=tk.LEFT)
        
        # Recent transactions frame
        recent_frame = ttk.LabelFrame(self.dashboard_tab, text="Recent Transactions")
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create Treeview for recent transactions
        columns = ("Date", "Type", "Amount", "Category", "Description")
        self.recent_tree = ttk.Treeview(recent_frame, columns=columns, show="headings", height=10)
        
        # Define headings
        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=100)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=self.recent_tree.yview)
        self.recent_tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recent_tree.pack(fill=tk.BOTH, expand=True)
    
    def setup_add_transaction_tab(self):
        # Create a frame for the form
        form_frame = ttk.Frame(self.add_transaction_tab)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Transaction type
        type_frame = ttk.Frame(form_frame)
        type_frame.pack(fill=tk.X, pady=10)
        
        type_label = ttk.Label(type_frame, text="Transaction Type:", width=15)
        type_label.pack(side=tk.LEFT)
        
        self.transaction_type = tk.StringVar(value="income")
        income_radio = ttk.Radiobutton(type_frame, text="Income", variable=self.transaction_type, value="income")
        income_radio.pack(side=tk.LEFT, padx=10)
        
        expense_radio = ttk.Radiobutton(type_frame, text="Expense", variable=self.transaction_type, value="expense")
        expense_radio.pack(side=tk.LEFT, padx=10)
        
        # Amount
        amount_frame = ttk.Frame(form_frame)
        amount_frame.pack(fill=tk.X, pady=10)
        
        amount_label = ttk.Label(amount_frame, text="Amount:", width=15)
        amount_label.pack(side=tk.LEFT)
        
        self.amount_entry = ttk.Entry(amount_frame)
        self.amount_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Category
        category_frame = ttk.Frame(form_frame)
        category_frame.pack(fill=tk.X, pady=10)
        
        category_label = ttk.Label(category_frame, text="Category:", width=15)
        category_label.pack(side=tk.LEFT)
        
        common_categories = ["Salary", "Food", "Rent", "Transport", "Entertainment", "Bills", "Other"]
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, values=common_categories)
        self.category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Description
        description_frame = ttk.Frame(form_frame)
        description_frame.pack(fill=tk.X, pady=10)
        
        description_label = ttk.Label(description_frame, text="Description:", width=15)
        description_label.pack(side=tk.LEFT)
        
        self.description_entry = ttk.Entry(description_frame)
        self.description_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Date
        date_frame = ttk.Frame(form_frame)
        date_frame.pack(fill=tk.X, pady=10)
        
        date_label = ttk.Label(date_frame, text="Date:", width=15)
        date_label.pack(side=tk.LEFT)
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.date_var = tk.StringVar(value=today)
        self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var)
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Submit button
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        submit_button = ttk.Button(button_frame, text="Add Transaction", command=self.add_transaction)
        submit_button.pack(pady=10, padx=100)
        
        # Reset form button
        reset_button = ttk.Button(button_frame, text="Reset Form", command=self.reset_form)
        reset_button.pack(pady=10, padx=100)
    
    def setup_transactions_tab(self):
        # Create a frame for the transactions table
        transactions_frame = ttk.Frame(self.transactions_tab)
        transactions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create Treeview
        columns = ("ID", "Date", "Type", "Amount", "Category", "Description")
        self.transactions_tree = ttk.Treeview(transactions_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.transactions_tree.heading(col, text=col)
            width = 60 if col == "ID" else 100
            self.transactions_tree.column(col, width=width)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(transactions_frame, orient=tk.VERTICAL, command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transactions_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add buttons for actions
        button_frame = ttk.Frame(self.transactions_tab)
        button_frame.pack(fill=tk.X, pady=10)
        
        delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_transaction)
        delete_button.pack(side=tk.LEFT, padx=20)
        
        refresh_button = ttk.Button(button_frame, text="Refresh", command=self.refresh_transactions)
        refresh_button.pack(side=tk.LEFT, padx=20)
    
    def setup_categories_tab(self):
        # Create a frame for the categories summary
        categories_frame = ttk.LabelFrame(self.categories_tab, text="Expense Categories")
        categories_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create Treeview for categories
        columns = ("Category", "Amount", "Percentage")
        self.categories_tree = ttk.Treeview(categories_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.categories_tree.heading(col, text=col)
            self.categories_tree.column(col, width=150)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(categories_frame, orient=tk.VERTICAL, command=self.categories_tree.yview)
        self.categories_tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.categories_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add refresh button
        refresh_button = ttk.Button(self.categories_tab, text="Refresh", command=self.refresh_categories)
        refresh_button.pack(pady=10)
    
    def update_dashboard(self):
        # Update balance information
        balance_data = self.budget.get_balance()
        
        self.income_value.config(text=f"${balance_data['income']:.2f}")
        self.expenses_value.config(text=f"${balance_data['expenses']:.2f}")
        
        # Set color for net balance
        balance = balance_data['balance']
        self.net_value.config(text=f"${balance:.2f}")
        
        # Clear existing transactions
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        
        # Add recent transactions (top 5)
        transactions = self.budget.get_transactions(sort_by_date=True)[:5]
        
        for t in transactions:
            # Format based on transaction type
            amount = t["amount"]
            if t["type"] == "expense":
                amount_str = f"-${amount:.2f}"
            else:
                amount_str = f"${amount:.2f}"
            
            self.recent_tree.insert("", tk.END, values=(
                t["date"],
                t["type"].capitalize(),
                amount_str,
                t["category"],
                t["description"]
            ))
    
    def update_transactions(self):
        # Clear existing transactions
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Add all transactions
        transactions = self.budget.get_transactions(sort_by_date=True)
        
        for t in transactions:
            # Format based on transaction type
            amount = t["amount"]
            if t["type"] == "expense":
                amount_str = f"-${amount:.2f}"
            else:
                amount_str = f"${amount:.2f}"
            
            self.transactions_tree.insert("", tk.END, values=(
                t["id"],
                t["date"],
                t["type"].capitalize(),
                amount_str,
                t["category"],
                t["description"]
            ))
    
    def update_categories(self):
        # Clear existing categories
        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)
        
        # Get category summary
        categories = self.budget.get_category_summary()
        
        if categories:
            total_expenses = sum(categories.values())
            
            # Sort categories by amount (highest first)
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            
            for category, amount in sorted_categories:
                percentage = (amount / total_expenses) * 100
                
                self.categories_tree.insert("", tk.END, values=(
                    category,
                    f"${amount:.2f}",
                    f"{percentage:.1f}%"
                ))
    
    def update_all_tabs(self):
        self.update_dashboard()
        self.update_transactions()
        self.update_categories()
    
    def add_transaction(self):
        # Get values from form
        transaction_type = self.transaction_type.get()
        amount = self.amount_entry.get()
        category = self.category_var.get()
        description = self.description_entry.get()
        date = self.date_var.get()
        
        # Add transaction
        success, message = self.budget.add_transaction(amount, category, description, transaction_type, date)
        
        if success:
            messagebox.showinfo("Success", message)
            self.reset_form()
            self.update_all_tabs()
        else:
            messagebox.showerror("Error", message)
    
    def reset_form(self):
        # Reset form fields
        self.transaction_type.set("income")
        self.amount_entry.delete(0, tk.END)
        self.category_var.set("")
        self.description_entry.delete(0, tk.END)
        self.date_var.set(datetime.datetime.now().strftime("%Y-%m-%d"))
    
    def delete_transaction(self):
        # Get selected item
        selected_item = self.transactions_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a transaction to delete.")
            return
        
        # Get the transaction ID
        transaction_id = int(self.transactions_tree.item(selected_item[0])["values"][0])
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?")
        
        if confirm:
            success, message = self.budget.delete_transaction(transaction_id)
            
            if success:
                messagebox.showinfo("Success", message)
                self.update_all_tabs()
            else:
                messagebox.showerror("Error", message)
    
    def refresh_transactions(self):
        self.update_transactions()
    
    def refresh_categories(self):
        self.update_categories()

def launch_budget_app():
    """Function to launch the budget application after successful login"""
    root = tk.Tk()
    app = BudgetTrackerApp(root)
    root.mainloop()

def main():
    # Initialize login window
    login_root = tk.Tk()
    password_manager = PasswordManager()
    login_window = LoginWindow(login_root, password_manager, launch_budget_app)
    login_root.mainloop()

if __name__ == "__main__":
    main()