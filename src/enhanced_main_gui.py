"""
Enhanced Main GUI with Multi-User Integration
===========================================
Updated main application entry point with multi-user authentication and session management
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
from datetime import datetime
import threading

# Authentication components removed for simplified version
from enhanced_fnb_workflow_complete import create_enhanced_fnb_workflow

# Dashboard launcher
try:
    from dashboard_launcher import launch_dashboard_threaded
except ImportError:
    def launch_dashboard_threaded():
        messagebox.showerror("Error", "Dashboard launcher module not found")

class EnhancedMainApp(tk.Tk):
    """Enhanced Main Application with Multi-User Support"""
    
    def __init__(self):
        super().__init__()
        
        # Basic window setup
        self.title("BARD-RECO - Bank Reconciliation Platform")
        self.geometry("1200x900")
        self.configure(bg="#f8fafc")
        self.minsize(1000, 700)
        
        # Window state variables
        self.is_fullscreen = False
        self.is_maximized = False
        self.normal_geometry = "1200x900"
        
        # Try to set icon
        try:
            self.iconbitmap("bardreco.ico")
        except Exception:
            pass
        
        # Application state
        self.current_frame = None
        self.current_workflow = None
        
        # Setup UI components
        self._setup_window_controls()
        self._setup_keyboard_shortcuts()
        self._setup_modern_ui()
        
        # Show main UI directly
        self.after(100, self._setup_main_ui)
        
        # Center and maximize window
        self._center_window()
        self.after(200, self._toggle_maximize)
    
    def _setup_main_ui(self):
        """Setup the main UI without authentication"""
        # Show main interface (authentication removed in simplified version)
        self._show_main_interface()

        # Update window title
        self.title("BARD-RECO - Bank Reconciliation Platform")

    def _show_workflow_selection(self):
        """Show workflow selection interface (stub)"""
        pass
    
    def _show_main_interface(self):
        """Show the main application interface"""
        # Clear any existing content
        if self.current_frame:
            self.current_frame.destroy()
        
        # Create main interface
        self._create_main_interface()
    
    def _create_main_interface(self):
        """Create the main application interface"""
        # Main container
        main_container = tk.Frame(self, bg="#f8fafc")
        main_container.pack(fill="both", expand=True)
        
        # Create header
        self._create_header(main_container)
        
        # Create navigation sidebar
        self._create_sidebar(main_container)
        
        # Create main content area
        self._create_content_area(main_container)
        
        # Create status bar
        self._create_status_bar(main_container)
        
        # Show welcome dashboard by default
        self._show_welcome_dashboard()
    
    def _create_header(self, parent):
        """Create the application header"""
        header_frame = tk.Frame(parent, bg="#1e40af", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg="#1e40af")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Left side - Logo and title
        left_frame = tk.Frame(header_content, bg="#1e40af")
        left_frame.pack(side="left", fill="y")
        
        # Logo
        logo_label = tk.Label(left_frame, text="🏦", font=("Segoe UI Emoji", 24), 
                             bg="#1e40af", fg="#fbbf24")
        logo_label.pack(side="left")
        
        # Title section
        title_frame = tk.Frame(left_frame, bg="#1e40af")
        title_frame.pack(side="left", padx=(15, 0))
        
        # Main title
        title_label = tk.Label(title_frame, text="BARD-RECO", 
                             font=("Segoe UI", 20, "bold"), fg="white", bg="#1e40af")
        title_label.pack(anchor="w")
        
        # Subtitle
        subtitle_label = tk.Label(title_frame, text="Multi-User Bank Reconciliation Platform", 
                                font=("Segoe UI", 12), fg="#cbd5e1", bg="#1e40af")
        subtitle_label.pack(anchor="w")
        
        # Right side - User info and controls
        right_frame = tk.Frame(header_content, bg="#1e40af")
        right_frame.pack(side="right", fill="y")
        
        # User info card
        user_card = tk.Frame(right_frame, bg="#1e293b", relief="solid", bd=1)
        user_card.pack(side="right")
        
        user_content = tk.Frame(user_card, bg="#1e293b")
        user_content.pack(padx=15, pady=10)
        
        # User details (simplified - no authentication)
        user_name = tk.Label(user_content, text="👤 User", 
                           font=("Segoe UI", 11, "bold"), fg="white", bg="#1e293b")
        user_name.pack(anchor="w")
        
        user_role = tk.Label(user_content, text="🏢 Administrator", 
                           font=("Segoe UI", 9), fg="#cbd5e1", bg="#1e293b")
        user_role.pack(anchor="w")
        
        # Logout button
        logout_btn = tk.Button(user_content, text="🚪 Exit", 
                             font=("Segoe UI", 9, "bold"), bg="#dc2626", fg="white",
                             relief="flat", padx=10, pady=5, command=self._logout,
                             cursor="hand2")
        logout_btn.pack(pady=(5, 0))
    
    def _create_sidebar(self, parent):
        """Create navigation sidebar"""
        # Sidebar container
        sidebar_container = tk.Frame(parent, bg="#f8fafc")
        sidebar_container.pack(side="left", fill="y")
        
        # Sidebar frame
        self.sidebar = tk.Frame(sidebar_container, bg="#ffffff", width=250, relief="solid", bd=1)
        self.sidebar.pack(fill="y", padx=(10, 5), pady=10)
        self.sidebar.pack_propagate(False)
        
        # Sidebar header
        sidebar_header = tk.Frame(self.sidebar, bg="#f1f5f9", height=50)
        sidebar_header.pack(fill="x")
        sidebar_header.pack_propagate(False)
        
        tk.Label(sidebar_header, text="🧭 Navigation", font=("Segoe UI", 14, "bold"), 
                fg="#1e293b", bg="#f1f5f9").pack(expand=True)
        
        # Navigation items
        nav_frame = tk.Frame(self.sidebar, bg="#ffffff")
        nav_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Navigation buttons
        nav_items = [
            ("🏠 Dashboard", self._show_welcome_dashboard),
            ("� Web Dashboard", self._open_web_dashboard),
            ("�🏦 FNB Workflow", self._show_fnb_workflow),
            ("🏛️ Bidvest Workflow", self._show_bidvest_workflow),
            ("🏢 Nedbank Workflow", self._show_nedbank_workflow),
            ("📊 Results History", self._show_results_history),
            ("👥 User Management", self._show_user_management),
            ("⚙️ Settings", self._show_settings)
        ]
        
        self.nav_buttons = []
        for i, (text, command) in enumerate(nav_items):
            btn = tk.Button(nav_frame, text=text, font=("Segoe UI", 11), 
                           bg="#f8fafc", fg="#374151", relief="flat", 
                           padx=20, pady=12, anchor="w", width=25,
                           command=command, cursor="hand2")
            btn.pack(fill="x", pady=2)
            
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e5e7eb"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#f8fafc"))
            
            self.nav_buttons.append(btn)
    
    def _create_content_area(self, parent):
        """Create main content area"""
        # Content container
        content_container = tk.Frame(parent, bg="#f8fafc")
        content_container.pack(side="right", fill="both", expand=True)
        
        # Content frame
        self.content_frame = tk.Frame(content_container, bg="#ffffff", relief="solid", bd=1)
        self.content_frame.pack(fill="both", expand=True, padx=(5, 10), pady=10)
        
        self.current_frame = self.content_frame
    
    def _create_status_bar(self, parent):
        """Create status bar"""
        self.status_frame = tk.Frame(parent, bg="#e5e7eb", height=30)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        
        # Status content
        status_content = tk.Frame(self.status_frame, bg="#e5e7eb")
        status_content.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Status text
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Multi-user system active")
        
        status_label = tk.Label(status_content, textvariable=self.status_var,
                              font=("Segoe UI", 9), bg="#e5e7eb", fg="#374151", anchor="w")
        status_label.pack(side="left", fill="x", expand=True)
        
        # Session info (simplified - no session manager)
        session_info = "📂 No active session"
        
        session_label = tk.Label(status_content, text=session_info,
                               font=("Segoe UI", 9), bg="#e5e7eb", fg="#6b7280", anchor="e")
        session_label.pack(side="right")
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_var.set(message)
    
    def _show_welcome_dashboard(self):
        """Show welcome dashboard"""
        self._clear_content()
        self._highlight_nav_button(0)
        
        # Create dashboard content
        dashboard_frame = tk.Frame(self.content_frame, bg="#ffffff")
        dashboard_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Dashboard header
        header_frame = tk.Frame(dashboard_frame, bg="#ffffff")
        header_frame.pack(fill="x", pady=(0, 30))
        
        welcome_label = tk.Label(header_frame, 
                               text="Welcome to BARD-RECO! 👋", 
                               font=("Segoe UI", 24, "bold"), fg="#1e293b", bg="#ffffff")
        welcome_label.pack(anchor="w")
        
        subtitle_label = tk.Label(header_frame, 
                                text="Choose a workflow to begin reconciliation", 
                                font=("Segoe UI", 14), fg="#6b7280", bg="#ffffff")
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Quick action cards
        cards_frame = tk.Frame(dashboard_frame, bg="#ffffff")
        cards_frame.pack(fill="x", pady=(0, 30))
        
        # FNB Card
        self._create_workflow_card(cards_frame, "🏦 FNB Workflow", 
                                 "First National Bank reconciliation with advanced matching",
                                 "#059669", self._show_fnb_workflow)
        
        # Bidvest Card
        self._create_workflow_card(cards_frame, "🏛️ Bidvest Workflow", 
                                 "Bidvest Bank reconciliation with specialized features",
                                 "#3b82f6", self._show_bidvest_workflow)
        
        # Nedbank Card
        self._create_workflow_card(cards_frame, "🏢 Nedbank Workflow", 
                                 "Nedbank reconciliation with intelligent processing",
                                 "#7c3aed", self._show_nedbank_workflow)
        
        # Web Dashboard Card
        self._create_workflow_card(cards_frame, "🌐 Web Dashboard", 
                                 "Open collaborative web dashboard in browser",
                                 "#ef4444", self._open_web_dashboard)
        
        # Recent activity section
        self._create_recent_activity_section(dashboard_frame)
        
        self.update_status("Dashboard loaded - Ready to start reconciliation")
    
    def _create_workflow_card(self, parent, title, description, color, command):
        """Create a workflow selection card"""
        card = tk.Frame(parent, bg=color, relief="solid", bd=1, cursor="hand2")
        card.pack(side="left", fill="both", expand=True, padx=10)
        
        # Card content
        content = tk.Frame(card, bg=color)
        content.pack(fill="both", expand=True, padx=20, pady=25)
        
        # Title
        title_label = tk.Label(content, text=title, font=("Segoe UI", 16, "bold"), 
                             fg="white", bg=color)
        title_label.pack(anchor="w")
        
        # Description
        desc_label = tk.Label(content, text=description, font=("Segoe UI", 11), 
                            fg="#ffffff", bg=color, wraplength=200, justify="left")
        desc_label.pack(anchor="w", pady=(10, 0))
        
        # Click handler
        def on_click(event):
            command()
        
        # Bind click events
        for widget in [card, content, title_label, desc_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", lambda e: card.config(relief="raised"))
            widget.bind("<Leave>", lambda e: card.config(relief="solid"))
    
    def _create_recent_activity_section(self, parent):
        """Create recent activity section"""
        activity_frame = tk.Frame(parent, bg="#f8fafc", relief="solid", bd=1)
        activity_frame.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(activity_frame, bg="#1e293b", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="📈 Recent Activity", font=("Segoe UI", 14, "bold"), 
                fg="white", bg="#1e293b").pack(expand=True)
        
        # Content
        content = tk.Frame(activity_frame, bg="#f8fafc")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # TODO: Add recent activity from multi-user database
        placeholder_label = tk.Label(content, 
                                    text="Recent reconciliation sessions and activity will appear here...", 
                                    font=("Segoe UI", 12), fg="#6b7280", bg="#f8fafc")
        placeholder_label.pack(expand=True)
    
    def _open_web_dashboard(self):
        """Open the web-based collaborative dashboard"""
        self._highlight_nav_button(1)
        
        # Show loading message
        messagebox.showinfo(
            "Web Dashboard", 
            "Starting web dashboard server...\nThis may take a few seconds.\n\nThe dashboard will open in your browser automatically."
        )
        
        # Launch dashboard in background thread
        launch_dashboard_threaded()
        
        # Update status
        self.update_status("Web Dashboard launching... Check your browser")
    
    def _show_fnb_workflow(self):
        """Show FNB workflow"""
        self._clear_content()
        self._highlight_nav_button(1)
        
        # Create enhanced FNB workflow
        try:
            self.current_workflow = create_enhanced_fnb_workflow(self.content_frame, self)
            if self.current_workflow:
                # Check if it's a frame-based widget
                if hasattr(self.current_workflow, 'pack'):
                    self.current_workflow.pack(fill="both", expand=True)
                elif hasattr(self.current_workflow, 'frame'):
                    self.current_workflow.frame.pack(fill="both", expand=True)
                self.update_status("FNB Workflow loaded - Enhanced multi-user features active")
            else:
                # Fallback to basic message
                self._show_workflow_placeholder("FNB Workflow", "🏦")
        except Exception as e:
            messagebox.showerror("Workflow Error", f"Failed to load FNB workflow: {str(e)}")
            self._show_workflow_placeholder("FNB Workflow", "🏦")
    
    def _show_bidvest_workflow(self):
        """Show Bidvest workflow"""
        self._clear_content()
        self._highlight_nav_button(2)
        self._show_workflow_placeholder("Bidvest Workflow", "🏛️")
        self.update_status("Bidvest Workflow - Coming soon with multi-user features")
    
    def _show_nedbank_workflow(self):
        """Show Nedbank workflow"""
        self._clear_content()
        self._highlight_nav_button(3)
        self._show_workflow_placeholder("Nedbank Workflow", "🏢")
        self.update_status("Nedbank Workflow - Coming soon with multi-user features")
    
    def _show_results_history(self):
        """Show results history"""
        self._clear_content()
        self._highlight_nav_button(4)
        self._show_workflow_placeholder("Results History", "📊")
        self.update_status("Results History - View all reconciliation results")
    
    def _show_user_management(self):
        """Show user management"""
        self._clear_content()
        self._highlight_nav_button(5)
        self._show_workflow_placeholder("User Management", "👥")
        self.update_status("User Management - Manage users and permissions")
    
    def _show_settings(self):
        """Show settings"""
        self._clear_content()
        self._highlight_nav_button(6)
        self._show_workflow_placeholder("Settings", "⚙️")
        self.update_status("Settings - Configure application preferences")
    
    def _show_workflow_placeholder(self, title, icon):
        """Show placeholder for workflows under development"""
        placeholder_frame = tk.Frame(self.content_frame, bg="#ffffff")
        placeholder_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        icon_label = tk.Label(placeholder_frame, text=icon, font=("Segoe UI Emoji", 64), 
                            bg="#ffffff", fg="#6b7280")
        icon_label.pack(pady=(50, 20))
        
        title_label = tk.Label(placeholder_frame, text=title, font=("Segoe UI", 24, "bold"), 
                             fg="#1e293b", bg="#ffffff")
        title_label.pack()
        
        message_label = tk.Label(placeholder_frame, 
                               text="This workflow is being enhanced with multi-user features.\nComing soon!", 
                               font=("Segoe UI", 14), fg="#6b7280", bg="#ffffff")
        message_label.pack(pady=20)
    
    def _clear_content(self):
        """Clear current content"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _highlight_nav_button(self, index):
        """Highlight selected navigation button"""
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.config(bg="#3b82f6", fg="white")
            else:
                btn.config(bg="#f8fafc", fg="#374151")
    
    def _logout(self):
        """Handle user logout/exit"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            # Simplified version - just close the application
            self.quit()
            self.destroy()
            # Restart application
            self.__class__()
    
    def _setup_window_controls(self):
        """Setup window control functions"""
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.bind('<F11>', lambda e: self._toggle_fullscreen())
        self.bind('<Control-F11>', lambda e: self._toggle_maximize())
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.bind('<Control-q>', lambda e: self.quit())
        self.bind('<Escape>', lambda e: self._show_welcome_dashboard())
        self.bind('<F1>', lambda e: self._show_help())
    
    def _setup_modern_ui(self):
        """Setup modern UI elements"""
        # Configure ttk styles for modern look
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure modern colors
        style.configure('Modern.TButton', 
                       fieldbackground='#3b82f6',
                       foreground='white',
                       borderwidth=0)
    
    def _center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.attributes('-fullscreen', self.is_fullscreen)
    
    def _toggle_maximize(self):
        """Toggle maximize/restore window"""
        if self.is_maximized:
            self.state('normal')
            self.is_maximized = False
        else:
            self.state('zoomed')
            self.is_maximized = True
    
    def _on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Exit BARD-RECO?"):
            # Simplified version - just close
            self.quit()
            self.destroy()
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
BARD-RECO Multi-User Help

Keyboard Shortcuts:
• F11 - Toggle Fullscreen
• Ctrl+F11 - Toggle Maximize
• Ctrl+Q - Quit Application
• Esc - Return to Dashboard
• F1 - Show Help

Multi-User Features:
• Session-based collaboration
• Real-time user tracking
• Activity logging
• File sharing
• Role-based access

For support, contact your system administrator.
        """
        
        messagebox.showinfo("BARD-RECO Help", help_text)


def main():
    """Main application entry point"""
    try:
        # Create and run enhanced application
        app = EnhancedMainApp()
        app.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Application Error", f"Failed to start BARD-RECO: {str(e)}")


if __name__ == "__main__":
    main()
