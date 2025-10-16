"""
Collaborative Dashboard GUI Components
====================================

Professional dashboard interface for collaborative reconciliation management.
Integrates with existing BARD-RECO system and provides real-time collaboration features.

Key Features:
- Modern, professional UI design
- Real-time transaction grid with filtering
- User authentication and role management  
- Live collaboration and notifications
- Advanced search and export capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
from datetime import datetime, timedelta
import threading
import json
from typing import Dict, List, Optional, Any
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collaborative_dashboard_db import CollaborativeDashboardDB


class LoginDialog:
    """Professional login dialog with authentication"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.db = CollaborativeDashboardDB()
        
        # Create modal dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("BARD-RECO Collaborative Dashboard - Login")
        self.dialog.geometry("450x550")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
        self.dialog.geometry(f"450x550+{x}+{y}")
        
        self.create_ui()
        
        # Focus on username field
        self.username_entry.focus()
        
    def create_ui(self):
        """Create the login interface"""
        
        # Header with branding
        header_frame = tk.Frame(self.dialog, bg="#1e40af", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Logo and title
        title_frame = tk.Frame(header_frame, bg="#1e40af")
        title_frame.pack(expand=True)
        
        logo_label = tk.Label(title_frame, text="🔒", font=("Segoe UI Emoji", 32), 
                             bg="#1e40af", fg="#fbbf24")
        logo_label.pack(pady=(15, 5))
        
        title_label = tk.Label(title_frame, text="Collaborative Dashboard", 
                              font=("Segoe UI", 18, "bold"), bg="#1e40af", fg="white")
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="BARD-RECO Professional System",
                                 font=("Segoe UI", 10), bg="#1e40af", fg="#cbd5e1")
        subtitle_label.pack()
        
        # Main login form
        form_frame = tk.Frame(self.dialog, bg="#f8f9fc", padx=40, pady=30)
        form_frame.pack(fill="both", expand=True)
        
        # Welcome message
        welcome_label = tk.Label(form_frame, text="Welcome Back!", 
                                font=("Segoe UI", 16, "bold"), bg="#f8f9fc", fg="#1e293b")
        welcome_label.pack(pady=(0, 20))
        
        # Username field
        tk.Label(form_frame, text="Username", font=("Segoe UI", 11, "bold"),
                bg="#f8f9fc", fg="#374151").pack(anchor="w", pady=(0, 5))
        
        self.username_entry = tk.Entry(form_frame, font=("Segoe UI", 12), 
                                      relief="solid", bd=1, highlightthickness=1,
                                      highlightcolor="#3b82f6", width=30)
        self.username_entry.pack(fill="x", pady=(0, 15), ipady=8)
        
        # Password field  
        tk.Label(form_frame, text="Password", font=("Segoe UI", 11, "bold"),
                bg="#f8f9fc", fg="#374151").pack(anchor="w", pady=(0, 5))
        
        self.password_entry = tk.Entry(form_frame, font=("Segoe UI", 12), show="*",
                                      relief="solid", bd=1, highlightthickness=1,
                                      highlightcolor="#3b82f6", width=30)
        self.password_entry.pack(fill="x", pady=(0, 20), ipady=8)
        
        # Login button
        login_btn = tk.Button(form_frame, text="Sign In", font=("Segoe UI", 12, "bold"),
                             bg="#3b82f6", fg="white", relief="flat", bd=0,
                             padx=20, pady=12, cursor="hand2", command=self.login)
        login_btn.pack(fill="x", pady=(0, 15))
        
        # Hover effects
        def on_enter(e):
            login_btn.config(bg="#2563eb")
        def on_leave(e):
            login_btn.config(bg="#3b82f6")
        login_btn.bind("<Enter>", on_enter)
        login_btn.bind("<Leave>", on_leave)
        
        # Demo credentials info
        demo_frame = tk.Frame(form_frame, bg="#fef3c7", relief="solid", bd=1)
        demo_frame.pack(fill="x", pady=(15, 0), padx=10)
        
        demo_info = tk.Label(demo_frame, text="💡 Demo Credentials:\nUsername: admin\nPassword: admin123",
                            font=("Segoe UI", 9), bg="#fef3c7", fg="#92400e", justify="left")
        demo_info.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(form_frame, text="", font=("Segoe UI", 10),
                                    bg="#f8f9fc", fg="#dc2626")
        self.status_label.pack(pady=(10, 0))
        
        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())
        
    def login(self):
        """Authenticate user"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.status_label.config(text="Please enter both username and password")
            return
            
        # Authenticate
        user = self.db.authenticate_user(username, password)
        if user:
            self.result = user
            self.dialog.destroy()
        else:
            self.status_label.config(text="Invalid username or password")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()


class CollaborativeDashboard:
    """Main collaborative dashboard interface"""
    
    def __init__(self, parent, user_info: Dict):
        self.parent = parent
        self.user_info = user_info
        self.db = CollaborativeDashboardDB()
        
        # Create main dashboard window
        self.window = tk.Toplevel(parent)
        self.window.title(f"BARD-RECO Collaborative Dashboard - {user_info['full_name']}")
        self.window.state('zoomed')  # Maximize window
        self.window.configure(bg="#f1f5f9")
        
        # Session and transaction data
        self.current_sessions = []
        self.current_transactions = []
        self.selected_session_id = None
        
        # Auto-refresh settings
        self.auto_refresh_enabled = True
        self.refresh_interval = 30000  # 30 seconds
        
        self.create_ui()
        self.refresh_data()
        self.start_auto_refresh()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_ui(self):
        """Create the main dashboard interface"""
        
        # Header with user info and controls
        self.create_header()
        
        # Main content area with tabs
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create the dashboard header"""
        header_frame = tk.Frame(self.window, bg="#1e40af", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Left side - Logo and title
        left_frame = tk.Frame(header_frame, bg="#1e40af")
        left_frame.pack(side="left", fill="y", padx=20, pady=10)
        
        logo_title_frame = tk.Frame(left_frame, bg="#1e40af")
        logo_title_frame.pack(side="left")
        
        tk.Label(logo_title_frame, text="📊", font=("Segoe UI Emoji", 24), 
                bg="#1e40af", fg="#fbbf24").pack(side="left", padx=(0, 10))
        
        title_frame = tk.Frame(logo_title_frame, bg="#1e40af")
        title_frame.pack(side="left")
        
        tk.Label(title_frame, text="Collaborative Dashboard", 
                font=("Segoe UI", 16, "bold"), bg="#1e40af", fg="white").pack(anchor="w")
        tk.Label(title_frame, text="Real-time Reconciliation Management",
                font=("Segoe UI", 10), bg="#1e40af", fg="#cbd5e1").pack(anchor="w")
        
        # Right side - User info and controls
        right_frame = tk.Frame(header_frame, bg="#1e40af")
        right_frame.pack(side="right", fill="y", padx=20, pady=10)
        
        # Notifications
        notif_btn = tk.Button(right_frame, text="🔔", font=("Segoe UI Emoji", 16),
                             bg="#3b82f6", fg="white", relief="flat", bd=0,
                             padx=10, pady=5, cursor="hand2", command=self.show_notifications)
        notif_btn.pack(side="right", padx=(0, 10))
        
        # User info
        user_frame = tk.Frame(right_frame, bg="#1e40af")
        user_frame.pack(side="right", padx=(0, 15))
        
        tk.Label(user_frame, text=f"Welcome, {self.user_info['full_name']}", 
                font=("Segoe UI", 11, "bold"), bg="#1e40af", fg="white").pack(anchor="e")
        tk.Label(user_frame, text=f"Role: {self.user_info['role'].title()} | {self.user_info['department']}", 
                font=("Segoe UI", 9), bg="#1e40af", fg="#cbd5e1").pack(anchor="e")
        
        # Settings and logout
        settings_btn = tk.Button(right_frame, text="⚙️", font=("Segoe UI Emoji", 14),
                                bg="#6b7280", fg="white", relief="flat", bd=0,
                                padx=8, pady=5, cursor="hand2", command=self.show_settings)
        settings_btn.pack(side="right", padx=(0, 5))
        
        logout_btn = tk.Button(right_frame, text="🚪", font=("Segoe UI Emoji", 14),
                              bg="#dc2626", fg="white", relief="flat", bd=0,
                              padx=8, pady=5, cursor="hand2", command=self.logout)
        logout_btn.pack(side="right")
    
    def create_main_content(self):
        """Create the main tabbed content area"""
        main_frame = tk.Frame(self.window, bg="#f1f5f9")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Dashboard Overview tab
        self.create_overview_tab()
        
        # Sessions Management tab
        self.create_sessions_tab()
        
        # Transactions tab
        self.create_transactions_tab()
        
        # Analytics tab (if admin/reconciler)
        if self.user_info['role'] in ['admin', 'reconciler']:
            self.create_analytics_tab()
    
    def create_overview_tab(self):
        """Create the dashboard overview tab"""
        overview_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(overview_frame, text="📊 Dashboard Overview")
        
        # Quick stats cards
        stats_frame = tk.Frame(overview_frame, bg="white")
        stats_frame.pack(fill="x", padx=20, pady=20)
        
        # Create stats cards in a grid
        self.stats_cards = []
        card_configs = [
            ("Active Sessions", "0", "#3b82f6", "📁"),
            ("Pending Reviews", "0", "#f59e0b", "⏳"),
            ("Completed Today", "0", "#10b981", "✅"),
            ("Total Transactions", "0", "#8b5cf6", "💰")
        ]
        
        for i, (title, value, color, icon) in enumerate(card_configs):
            card = self.create_stats_card(stats_frame, title, value, color, icon)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.stats_cards.append(card)
        
        # Configure grid weights
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Recent activity section
        activity_frame = tk.Frame(overview_frame, bg="white")
        activity_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        tk.Label(activity_frame, text="📈 Recent Activity", font=("Segoe UI", 14, "bold"),
                bg="white", fg="#1e293b").pack(anchor="w", pady=(0, 10))
        
        # Activity list
        self.activity_tree = ttk.Treeview(activity_frame, columns=("time", "user", "action", "session"), 
                                         show="headings", height=10)
        
        self.activity_tree.heading("time", text="Time")
        self.activity_tree.heading("user", text="User") 
        self.activity_tree.heading("action", text="Action")
        self.activity_tree.heading("session", text="Session")
        
        self.activity_tree.column("time", width=120)
        self.activity_tree.column("user", width=150)
        self.activity_tree.column("action", width=200)
        self.activity_tree.column("session", width=200)
        
        self.activity_tree.pack(fill="both", expand=True)
        
        # Scrollbar for activity
        activity_scroll = ttk.Scrollbar(activity_frame, orient="vertical", command=self.activity_tree.yview)
        activity_scroll.pack(side="right", fill="y")
        self.activity_tree.configure(yscrollcommand=activity_scroll.set)
    
    def create_stats_card(self, parent, title, value, color, icon):
        """Create a statistics card widget"""
        card = tk.Frame(parent, bg="white", relief="solid", bd=1)
        
        # Header with icon and color
        header = tk.Frame(card, bg=color, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text=icon, font=("Segoe UI Emoji", 24), 
                bg=color, fg="white").pack(expand=True)
        
        # Content area
        content = tk.Frame(card, bg="white")
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        value_label = tk.Label(content, text=value, font=("Segoe UI", 20, "bold"),
                              bg="white", fg="#1e293b")
        value_label.pack()
        
        title_label = tk.Label(content, text=title, font=("Segoe UI", 11),
                              bg="white", fg="#6b7280")
        title_label.pack()
        
        # Store reference to value label for updates
        card.value_label = value_label
        
        return card
    
    def create_sessions_tab(self):
        """Create the sessions management tab"""
        sessions_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(sessions_frame, text="📁 Sessions")
        
        # Toolbar
        toolbar = tk.Frame(sessions_frame, bg="white")
        toolbar.pack(fill="x", padx=20, pady=10)
        
        # New session button (if authorized)
        if self.user_info['role'] in ['admin', 'reconciler']:
            new_btn = tk.Button(toolbar, text="➕ New Session", font=("Segoe UI", 10, "bold"),
                               bg="#10b981", fg="white", relief="flat", bd=0,
                               padx=15, pady=8, cursor="hand2", command=self.create_new_session)
            new_btn.pack(side="left", padx=(0, 10))
        
        # Refresh button
        refresh_btn = tk.Button(toolbar, text="🔄 Refresh", font=("Segoe UI", 10),
                               bg="#6b7280", fg="white", relief="flat", bd=0,
                               padx=15, pady=8, cursor="hand2", command=self.refresh_sessions)
        refresh_btn.pack(side="left", padx=(0, 10))
        
        # Filter dropdown
        tk.Label(toolbar, text="Filter:", font=("Segoe UI", 10), bg="white").pack(side="left", padx=(20, 5))
        self.session_filter = ttk.Combobox(toolbar, values=["All", "Active", "Under Review", "Approved", "Archived"],
                                          state="readonly", width=15)
        self.session_filter.set("All")
        self.session_filter.pack(side="left")
        self.session_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_sessions())
        
        # Sessions list
        sessions_list_frame = tk.Frame(sessions_frame, bg="white")
        sessions_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.sessions_tree = ttk.Treeview(sessions_list_frame, 
                                         columns=("name", "type", "status", "priority", "transactions", "created", "creator"), 
                                         show="headings", height=15)
        
        # Configure columns
        columns_config = [
            ("name", "Session Name", 200),
            ("type", "Type", 120),
            ("status", "Status", 100),
            ("priority", "Priority", 80),
            ("transactions", "Transactions", 100),
            ("created", "Created", 120),
            ("creator", "Created By", 150)
        ]
        
        for col, text, width in columns_config:
            self.sessions_tree.heading(col, text=text)
            self.sessions_tree.column(col, width=width)
        
        self.sessions_tree.pack(fill="both", expand=True)
        
        # Scrollbar
        sessions_scroll = ttk.Scrollbar(sessions_list_frame, orient="vertical", command=self.sessions_tree.yview)
        sessions_scroll.pack(side="right", fill="y")
        self.sessions_tree.configure(yscrollcommand=sessions_scroll.set)
        
        # Bind double-click to open session
        self.sessions_tree.bind("<Double-1>", self.open_session)
    
    def create_transactions_tab(self):
        """Create the transactions management tab"""
        transactions_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(transactions_frame, text="💰 Transactions")
        
        # Session selection
        session_frame = tk.Frame(transactions_frame, bg="white")
        session_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(session_frame, text="Session:", font=("Segoe UI", 11, "bold"), 
                bg="white").pack(side="left", padx=(0, 10))
        
        self.session_selector = ttk.Combobox(session_frame, width=40, state="readonly")
        self.session_selector.pack(side="left", padx=(0, 20))
        self.session_selector.bind('<<ComboboxSelected>>', self.load_session_transactions)
        
        # Transaction type filter
        tk.Label(session_frame, text="Type:", font=("Segoe UI", 11), bg="white").pack(side="left", padx=(20, 5))
        self.trans_type_filter = ttk.Combobox(session_frame, 
                                             values=["All", "Matched", "Unmatched Ledger", "Unmatched Statement", "Foreign Credit"],
                                             state="readonly", width=15)
        self.trans_type_filter.set("All")
        self.trans_type_filter.pack(side="left")
        self.trans_type_filter.bind('<<ComboboxSelected>>', self.filter_transactions)
        
        # Transactions list
        trans_list_frame = tk.Frame(transactions_frame, bg="white")
        trans_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.transactions_tree = ttk.Treeview(trans_list_frame,
                                             columns=("type", "amount", "reference", "status", "assigned", "confidence", "updated"),
                                             show="headings", height=12)
        
        # Configure transaction columns
        trans_columns_config = [
            ("type", "Type", 120),
            ("amount", "Amount", 100),
            ("reference", "Reference", 150),
            ("status", "Status", 100),
            ("assigned", "Assigned To", 120),
            ("confidence", "Confidence", 80),
            ("updated", "Updated", 120)
        ]
        
        for col, text, width in trans_columns_config:
            self.transactions_tree.heading(col, text=text)
            self.transactions_tree.column(col, width=width)
        
        self.transactions_tree.pack(fill="both", expand=True)
        
        # Transaction scrollbar
        trans_scroll = ttk.Scrollbar(trans_list_frame, orient="vertical", command=self.transactions_tree.yview)
        trans_scroll.pack(side="right", fill="y")
        self.transactions_tree.configure(yscrollcommand=trans_scroll.set)
        
        # Transaction actions frame
        actions_frame = tk.Frame(transactions_frame, bg="white")
        actions_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Action buttons (role-based)
        if self.user_info['role'] in ['admin', 'reconciler', 'approver']:
            approve_btn = tk.Button(actions_frame, text="✅ Approve", font=("Segoe UI", 10, "bold"),
                                   bg="#10b981", fg="white", relief="flat", bd=0,
                                   padx=15, pady=8, cursor="hand2", command=self.approve_transaction)
            approve_btn.pack(side="left", padx=(0, 10))
            
            reject_btn = tk.Button(actions_frame, text="❌ Reject", font=("Segoe UI", 10, "bold"),
                                  bg="#dc2626", fg="white", relief="flat", bd=0,
                                  padx=15, pady=8, cursor="hand2", command=self.reject_transaction)
            reject_btn.pack(side="left", padx=(0, 10))
        
        # Comment button (all users)
        comment_btn = tk.Button(actions_frame, text="💬 Comment", font=("Segoe UI", 10),
                               bg="#3b82f6", fg="white", relief="flat", bd=0,
                               padx=15, pady=8, cursor="hand2", command=self.add_transaction_comment)
        comment_btn.pack(side="left", padx=(0, 10))
        
        # Export button
        export_btn = tk.Button(actions_frame, text="📤 Export", font=("Segoe UI", 10),
                              bg="#6b7280", fg="white", relief="flat", bd=0,
                              padx=15, pady=8, cursor="hand2", command=self.export_transactions)
        export_btn.pack(side="right")
    
    def create_analytics_tab(self):
        """Create analytics tab for admin/reconciler roles"""
        analytics_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(analytics_frame, text="📈 Analytics")
        
        tk.Label(analytics_frame, text="Analytics Dashboard", font=("Segoe UI", 16, "bold"),
                bg="white", fg="#1e293b").pack(pady=20)
        
        tk.Label(analytics_frame, text="📊 Advanced analytics and reporting features coming soon...",
                font=("Segoe UI", 12), bg="white", fg="#6b7280").pack(pady=10)
    
    def create_status_bar(self):
        """Create the status bar"""
        status_frame = tk.Frame(self.window, bg="#e5e7eb", height=30)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        # Status text
        self.status_label = tk.Label(status_frame, text="Ready", font=("Segoe UI", 9),
                                    bg="#e5e7eb", fg="#374151")
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Connection status
        self.connection_label = tk.Label(status_frame, text="🟢 Connected", font=("Segoe UI", 9),
                                        bg="#e5e7eb", fg="#059669")
        self.connection_label.pack(side="right", padx=10, pady=5)
        
        # Auto-refresh indicator
        self.refresh_label = tk.Label(status_frame, text="🔄 Auto-refresh: ON", font=("Segoe UI", 9),
                                     bg="#e5e7eb", fg="#3b82f6")
        self.refresh_label.pack(side="right", padx=(0, 20), pady=5)
    
    # Event handlers and data methods will be in the next part...
    
    def refresh_data(self):
        """Refresh all dashboard data"""
        self.status_label.config(text="Refreshing data...")
        try:
            self.refresh_sessions()
            self.update_stats()
            self.status_label.config(text="Data refreshed successfully")
        except Exception as e:
            self.status_label.config(text=f"Error refreshing data: {str(e)}")
    
    def refresh_sessions(self):
        """Refresh sessions list"""
        try:
            # Get filter value
            status_filter = self.session_filter.get()
            filter_status = None if status_filter == "All" else status_filter.lower().replace(" ", "_")
            
            # Load sessions
            self.current_sessions = self.db.get_sessions(status=filter_status)
            
            # Clear and populate sessions tree
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)
            
            session_names = []
            for session in self.current_sessions:
                self.sessions_tree.insert("", "end", values=(
                    session['session_name'],
                    session['workflow_type'],
                    session['status'].replace('_', ' ').title(),
                    session['priority'].title(),
                    f"{session['matched_transactions']}/{session['total_transactions']}",
                    session['created_at'][:16],
                    session['created_by_name'] or 'Unknown'
                ))
                session_names.append(f"{session['session_name']} ({session['id'][:8]})")
            
            # Update session selector
            self.session_selector['values'] = session_names
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh sessions: {str(e)}")
    
    def update_stats(self):
        """Update dashboard statistics"""
        try:
            stats = self.db.get_dashboard_stats()
            
            # Update stats cards
            sessions_by_status = stats.get('sessions_by_status', {})
            self.stats_cards[0].value_label.config(text=str(sessions_by_status.get('active', 0)))
            self.stats_cards[1].value_label.config(text=str(sessions_by_status.get('under_review', 0)))
            self.stats_cards[2].value_label.config(text=str(sessions_by_status.get('approved', 0)))
            
            transactions_by_type = stats.get('transactions_by_type', {})
            total_transactions = sum(transactions_by_type.values())
            self.stats_cards[3].value_label.config(text=str(total_transactions))
            
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def start_auto_refresh(self):
        """Start auto-refresh timer"""
        if self.auto_refresh_enabled:
            self.refresh_data()
            self.window.after(self.refresh_interval, self.start_auto_refresh)
    
    def show_notifications(self):
        """Show user notifications"""
        notifications = self.db.get_user_notifications(self.user_info['id'])
        
        # Create notifications window
        notif_window = tk.Toplevel(self.window)
        notif_window.title("Notifications")
        notif_window.geometry("500x400")
        notif_window.transient(self.window)
        
        if notifications:
            for notif in notifications[:10]:  # Show last 10
                notif_frame = tk.Frame(notif_window, relief="solid", bd=1)
                notif_frame.pack(fill="x", padx=10, pady=5)
                
                tk.Label(notif_frame, text=notif['title'], font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=2)
                tk.Label(notif_frame, text=notif['message'], font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=2)
                tk.Label(notif_frame, text=notif['created_at'], font=("Segoe UI", 8), fg="gray").pack(anchor="e", padx=10, pady=2)
        else:
            tk.Label(notif_window, text="No new notifications", font=("Segoe UI", 12)).pack(expand=True)
    
    def show_settings(self):
        """Show dashboard settings"""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("Dashboard Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.window)
        
        tk.Label(settings_window, text="Dashboard Settings", font=("Segoe UI", 14, "bold")).pack(pady=20)
        tk.Label(settings_window, text="Settings panel coming soon...", font=("Segoe UI", 10)).pack(pady=10)
    
    def logout(self):
        """Logout and close dashboard"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.window.destroy()
    
    def on_closing(self):
        """Handle window closing"""
        self.auto_refresh_enabled = False
        self.db.close()
        self.window.destroy()
    
    # Placeholder methods for functionality - will be implemented in next steps
    def create_new_session(self):
        messagebox.showinfo("Coming Soon", "New session creation coming in next update!")
        
    def open_session(self, event):
        messagebox.showinfo("Coming Soon", "Session details view coming in next update!")
        
    def load_session_transactions(self, event):
        messagebox.showinfo("Coming Soon", "Transaction loading coming in next update!")
        
    def filter_transactions(self):
        messagebox.showinfo("Coming Soon", "Transaction filtering coming in next update!")
        
    def approve_transaction(self):
        messagebox.showinfo("Coming Soon", "Transaction approval coming in next update!")
        
    def reject_transaction(self):
        messagebox.showinfo("Coming Soon", "Transaction rejection coming in next update!")
        
    def add_transaction_comment(self):
        messagebox.showinfo("Coming Soon", "Comments system coming in next update!")
        
    def export_transactions(self):
        messagebox.showinfo("Coming Soon", "Export functionality coming in next update!")


def launch_collaborative_dashboard(parent=None):
    """Launch the collaborative dashboard with login"""
    if parent is None:
        root = tk.Tk()
        root.withdraw()  # Hide root window
        parent = root
    
    # Show login dialog
    login_dialog = LoginDialog(parent)
    parent.wait_window(login_dialog.dialog)
    
    if login_dialog.result:
        # Launch dashboard
        dashboard = CollaborativeDashboard(parent, login_dialog.result)
        return dashboard
    else:
        messagebox.showinfo("Login Cancelled", "Dashboard login was cancelled.")
        return None


if __name__ == "__main__":
    # Test the dashboard independently
    launch_collaborative_dashboard()