"""
Fast Posting Integration for All Workflows
==========================================

Drop-in replacement functions for ultra-fast dashboard posting
in FNB, Bidvest, and Corporate Settlements workflows.

Usage in existing code:
    from fast_posting_integration import fast_post_to_dashboard

    # Replace old posting code with:
    success, session_id, count = fast_post_to_dashboard(
        results=self.reconciliation_results,
        workflow_type="FNB",  # or "Bidvest" or "Corporate"
        workflow_instance=self,
        show_success_dialog=True
    )
"""

import tkinter as tk
from tkinter import messagebox
from typing import Dict, Tuple, Optional
from datetime import datetime
import threading
from fast_bulk_poster import FastBulkPoster, UltraFastParallelPoster


def fast_post_to_dashboard(results: Dict, workflow_type: str, workflow_instance=None,
                           show_success_dialog: bool = True,
                           session_name: str = None) -> Tuple[bool, str, int]:
    """
    Ultra-fast posting to dashboard with progress UI

    Args:
        results: Reconciliation results dictionary
        workflow_type: "FNB", "Bidvest", or "Corporate"
        workflow_instance: Reference to workflow instance (for UI updates)
        show_success_dialog: Show success message dialog
        session_name: Custom session name

    Returns:
        (success, session_id, transactions_posted)
    """

    if not results:
        if workflow_instance:
            messagebox.showerror("No Results", "No reconciliation results to post!")
        return (False, "", 0)

    # Create progress dialog
    progress_window = None
    progress_var = None
    status_label = None
    details_label = None

    if workflow_instance and hasattr(workflow_instance, 'parent'):
        progress_window = tk.Toplevel(workflow_instance.parent)
        progress_window.title(f"🚀 Posting to Dashboard - {workflow_type}")
        progress_window.geometry("500x250")
        progress_window.configure(bg="#f8fafc")
        progress_window.transient(workflow_instance.parent)
        progress_window.grab_set()

        # Center window
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - 250
        y = (progress_window.winfo_screenheight() // 2) - 125
        progress_window.geometry(f"500x250+{x}+{y}")

        # Header
        header = tk.Frame(progress_window, bg="#10b981", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=f"🚀 Ultra-Fast Posting - {workflow_type}",
                font=("Segoe UI", 16, "bold"), fg="white", bg="#10b981").pack(expand=True)

        # Content
        content = tk.Frame(progress_window, bg="#f8fafc")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Progress bar
        from tkinter import ttk
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(content, variable=progress_var, maximum=100, length=400)
        progress_bar.pack(pady=15)

        # Status
        status_label = tk.Label(content, text="Initializing ultra-fast posting...",
                              font=("Segoe UI", 12, "bold"), fg="#059669", bg="#f8fafc")
        status_label.pack(pady=10)

        # Details
        details_label = tk.Label(content, text="", font=("Segoe UI", 10), fg="#6b7280", bg="#f8fafc")
        details_label.pack()

        progress_window.update()

    def progress_callback(current, total, message):
        """Update progress UI"""
        if progress_window and progress_window.winfo_exists():
            if total > 0:
                percent = (current / total) * 100
                progress_var.set(percent)
            status_label.config(text=message)
            details_label.config(text=f"{current:,} / {total:,} transactions")
            progress_window.update()

    # Choose poster based on data size
    total_items = sum(len(v) if v else 0 for v in results.values())

    if total_items > 50000:
        # Use ultra-fast parallel poster for large datasets
        poster = UltraFastParallelPoster(batch_size=2000)
        poster.set_progress_callback(progress_callback)
        success, session_id, count = poster.post_ultra_fast(
            results, workflow_type, session_name, num_threads=6
        )
    else:
        # Use fast bulk poster for normal datasets
        poster = FastBulkPoster(batch_size=1000)
        poster.set_progress_callback(progress_callback)
        success, session_id, count = poster.post_bulk_fast(
            results, workflow_type, session_name
        )

    # Close progress window
    if progress_window and progress_window.winfo_exists():
        progress_window.destroy()

    # Show success message
    if success and show_success_dialog and workflow_instance:
        show_posting_success(workflow_instance.parent, workflow_type, session_id, count)

    return (success, session_id, count)


def show_posting_success(parent, workflow_type: str, session_id: str, count: int):
    """Show success dialog after posting"""
    success_window = tk.Toplevel(parent)
    success_window.title("✅ Posted Successfully")
    success_window.geometry("550x400")
    success_window.configure(bg="white")
    success_window.transient(parent)
    success_window.grab_set()

    # Center
    success_window.update_idletasks()
    x = (success_window.winfo_screenwidth() // 2) - 275
    y = (success_window.winfo_screenheight() // 2) - 200
    success_window.geometry(f"550x400+{x}+{y}")

    # Header
    header = tk.Frame(success_window, bg="#10b981", height=80)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="✅ Successfully Posted to Dashboard!",
            font=("Segoe UI", 18, "bold"), fg="white", bg="#10b981").pack(expand=True)

    # Content
    content = tk.Frame(success_window, bg="white")
    content.pack(fill="both", expand=True, padx=30, pady=20)

    # Session info
    info_frame = tk.Frame(content, bg="#f0fdf4", relief="solid", bd=1)
    info_frame.pack(fill="x", pady=10)

    tk.Label(info_frame, text=f"📊 Workflow: {workflow_type}",
            font=("Segoe UI", 12), bg="#f0fdf4", fg="#059669",
            anchor="w").pack(fill="x", padx=15, pady=5)

    tk.Label(info_frame, text=f"🆔 Session ID: {session_id[:16]}...",
            font=("Segoe UI", 11), bg="#f0fdf4", fg="#047857",
            anchor="w").pack(fill="x", padx=15, pady=5)

    tk.Label(info_frame, text=f"💰 Transactions Posted: {count:,}",
            font=("Segoe UI", 12, "bold"), bg="#f0fdf4", fg="#065f46",
            anchor="w").pack(fill="x", padx=15, pady=5)

    # Dashboard URL
    url_frame = tk.Frame(content, bg="#eff6ff", relief="solid", bd=1)
    url_frame.pack(fill="x", pady=15)

    tk.Label(url_frame, text="🌐 View in Dashboard:",
            font=("Segoe UI", 11, "bold"), bg="#eff6ff", fg="#1e40af").pack(anchor="w", padx=15, pady=(10, 5))

    url = "http://localhost:5000"
    url_entry = tk.Entry(url_frame, font=("Consolas", 11), bg="white", fg="#0369a1", bd=1, relief="solid")
    url_entry.insert(0, url)
    url_entry.config(state="readonly")
    url_entry.pack(fill="x", padx=15, pady=5)

    def open_dashboard():
        import webbrowser
        webbrowser.open(url)
        success_window.destroy()

    tk.Button(url_frame, text="🚀 Open Dashboard in Browser",
             font=("Segoe UI", 11, "bold"), bg="#3b82f6", fg="white",
             bd=0, padx=20, pady=10, cursor="hand2",
             command=open_dashboard).pack(fill="x", padx=15, pady=10)

    # Instructions
    tk.Label(content, text="Navigate: Dashboard → Transactions",
            font=("Segoe UI", 10), bg="white", fg="#6b7280").pack(pady=5)

    tk.Label(content, text="Use tabs to view by category (Matched, Foreign, Split, Unmatched)",
            font=("Segoe UI", 9), bg="white", fg="#9ca3af").pack()

    # Close button
    tk.Button(content, text="✓ Close", font=("Segoe UI", 11), bg="#d1d5db", fg="#374151",
             bd=0, padx=30, pady=8, cursor="hand2",
             command=success_window.destroy).pack(pady=15)


# FNB-specific wrapper
def post_fnb_results_fast(workflow_instance, results: Dict = None) -> Tuple[bool, str, int]:
    """
    Fast posting for FNB workflow

    Usage in enhanced_fnb_workflow.py:
        Replace the post_to_collaborative_dashboard method with this:

        def post_to_collaborative_dashboard(self):
            from fast_posting_integration import post_fnb_results_fast
            return post_fnb_results_fast(self)
    """
    if results is None:
        if hasattr(workflow_instance, 'reconciliation_results'):
            results = workflow_instance.reconciliation_results
        else:
            messagebox.showerror("No Results", "No reconciliation results available!")
            return (False, "", 0)

    session_name = f"FNB - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    return fast_post_to_dashboard(results, "FNB", workflow_instance, True, session_name)


# Bidvest-specific wrapper
def post_bidvest_results_fast(workflow_instance, results: Dict = None) -> Tuple[bool, str, int]:
    """
    Fast posting for Bidvest workflow

    Usage in bidvest_workflow_page.py:
        Replace post_to_collaborative_dashboard function with:

        def post_to_collaborative_dashboard():
            from fast_posting_integration import post_bidvest_results_fast
            return post_bidvest_results_fast(self, self.results)
    """
    if results is None:
        messagebox.showerror("No Results", "No reconciliation results available!")
        return (False, "", 0)

    session_name = f"Bidvest - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    return fast_post_to_dashboard(results, "Bidvest", workflow_instance, True, session_name)


# Corporate Settlements-specific wrapper
def post_corporate_results_fast(workflow_instance, results: Dict = None) -> Tuple[bool, str, int]:
    """
    Fast posting for Corporate Settlements workflow

    Usage in corporate_settlements_workflow.py:
        Replace posting code with:

        def post_to_dashboard(self):
            from fast_posting_integration import post_corporate_results_fast
            return post_corporate_results_fast(self, self.results)
    """
    if results is None:
        messagebox.showerror("No Results", "No reconciliation results available!")
        return (False, "", 0)

    session_name = f"Corporate - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    return fast_post_to_dashboard(results, "Corporate Settlements", workflow_instance, True, session_name)
