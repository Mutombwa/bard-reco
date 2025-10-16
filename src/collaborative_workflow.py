"""
Enhanced Reconciliation Workflow with Collaborative Dashboard Integration
=========================================================================

This module enhances the existing reconciliation workflow to automatically
integrate with the collaborative dashboard. It provides:

- Automatic session creation
- Real-time result posting
- Progress tracking
- Collaborative notifications
- Professional workflow management
"""

import os
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
import pandas as pd

# Import existing reconciliation components
from reconciliation import Reconciliation
from results_db import ResultsDB
from collaborative_integration import CollaborativeDashboardIntegration, create_session_and_post_results


class CollaborativeReconciliationWorkflow:
    """
    Enhanced reconciliation workflow with collaborative dashboard integration
    """
    
    def __init__(self, dashboard_url: str = "http://localhost:5000",
                 dashboard_username: str = "admin", dashboard_password: str = "admin123",
                 enable_dashboard: bool = True):
        """
        Initialize the collaborative reconciliation workflow
        
        Args:
            dashboard_url: URL of the collaborative dashboard
            dashboard_username: Username for dashboard authentication
            dashboard_password: Password for dashboard authentication
            enable_dashboard: Whether to enable dashboard integration
        """
        self.dashboard_url = dashboard_url
        self.dashboard_username = dashboard_username
        self.dashboard_password = dashboard_password
        self.enable_dashboard = enable_dashboard
        
        # Initialize components
        self.results_db = ResultsDB()
        self.dashboard_integration = None
        
        # Initialize dashboard integration if enabled
        if self.enable_dashboard:
            try:
                self.dashboard_integration = CollaborativeDashboardIntegration(
                    dashboard_url=dashboard_url,
                    username=dashboard_username,
                    password=dashboard_password
                )
                print("✅ Dashboard integration enabled")
            except Exception as e:
                print(f"⚠️ Dashboard integration failed: {e}")
                print("Continuing without dashboard integration...")
                self.enable_dashboard = False
    
    def create_collaborative_session(self, session_name: str, workflow_type: str,
                                    description: str = "", priority: str = "normal") -> Optional[str]:
        """
        Create a new collaborative session
        
        Args:
            session_name: Name of the session
            workflow_type: Type of workflow (Bank, Branch, FNB, Bidvest, etc.)
            description: Session description
            priority: Session priority
            
        Returns:
            str: Session ID if successful
        """
        if not self.enable_dashboard or not self.dashboard_integration:
            print("⚠️ Dashboard integration not available")
            return None
        
        return self.dashboard_integration.create_session(
            session_name=session_name,
            workflow_type=workflow_type,
            description=description,
            priority=priority
        )
    
    def run_reconciliation(self, st_data_path: str, cb_data_path: str,
                          session_name: str = None, workflow_type: str = "Bank",
                          match_cols: List = None, fuzzy_flags: Dict = None,
                          mode: str = "Bank", progress_callback: Callable = None,
                          auto_post_to_dashboard: bool = True) -> Dict:
        """
        Run reconciliation with collaborative dashboard integration
        
        Args:
            st_data_path: Path to statement data file
            cb_data_path: Path to cashbook data file
            session_name: Name for the collaborative session
            workflow_type: Type of workflow
            match_cols: Column mapping for matching
            fuzzy_flags: Fuzzy matching configuration
            mode: Reconciliation mode
            progress_callback: Progress callback function
            auto_post_to_dashboard: Whether to automatically post to dashboard
            
        Returns:
            Dict: Reconciliation results with metadata
        """
        print("🚀 Starting Enhanced Reconciliation Workflow...")
        
        # Generate session name if not provided
        if not session_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = f"{workflow_type}_Reconciliation_{timestamp}"
        
        # Create collaborative session if dashboard is enabled
        dashboard_session_id = None
        if auto_post_to_dashboard and self.enable_dashboard:
            dashboard_session_id = self.create_collaborative_session(
                session_name=session_name,
                workflow_type=workflow_type,
                description=f"Reconciliation session created from {os.path.basename(st_data_path)} and {os.path.basename(cb_data_path)}"
            )
        
        # Initialize reconciliation
        print(f"📊 Initializing reconciliation: {session_name}")
        reconciliation = Reconciliation(st_data_path, cb_data_path)
        
        # Enhanced progress tracking
        def enhanced_progress_callback(processed: int, total: int):
            percentage = (processed / total) * 100 if total > 0 else 0
            print(f"⏳ Progress: {processed}/{total} ({percentage:.1f}%)")
            
            # Call original callback if provided
            if progress_callback:
                progress_callback(processed, total)
        
        # Run reconciliation
        print("🔄 Executing reconciliation logic...")
        reconciliation.reconcile(
            match_cols=match_cols,
            fuzzy_flags=fuzzy_flags,
            progress_callback=enhanced_progress_callback,
            mode=mode
        )
        
        # Get results
        results = reconciliation.results
        
        # Calculate statistics
        stats = self._calculate_statistics(results)
        print(f"📈 Reconciliation completed:")
        print(f"   • Total Transactions: {stats['total_transactions']}")
        print(f"   • Matched: {stats['matched_transactions']} ({stats['match_percentage']:.1f}%)")
        print(f"   • Unmatched: {stats['unmatched_transactions']}")
        
        # Save to local database
        batch_id = str(uuid.uuid4())
        metadata = {
            'session_name': session_name,
            'workflow_type': workflow_type,
            'mode': mode,
            'st_file': os.path.basename(st_data_path),
            'cb_file': os.path.basename(cb_data_path),
            'dashboard_session_id': dashboard_session_id,
            'statistics': stats,
            'created_at': datetime.now().isoformat()
        }
        
        # Save each result type
        for result_type, transactions in results.items():
            if transactions:  # Only save non-empty results
                df = self._convert_results_to_dataframe(transactions, result_type)
                self.results_db.save_reconciliation_result(
                    name=f"{session_name}_{result_type}",
                    result_type=result_type,
                    result_data=df,
                    metadata=metadata,
                    batch_id=batch_id
                )
        
        # Post to collaborative dashboard if enabled
        if auto_post_to_dashboard and self.enable_dashboard and dashboard_session_id:
            print("🌐 Posting results to collaborative dashboard...")
            success = self.dashboard_integration.post_reconciliation_results(
                session_id=dashboard_session_id,
                results=results,
                metadata=metadata
            )
            
            if success:
                print("✅ Results successfully posted to collaborative dashboard")
                print(f"🔗 Dashboard URL: {self.dashboard_url}")
                print(f"📋 Session ID: {dashboard_session_id}")
            else:
                print("❌ Failed to post results to dashboard")
        
        # Prepare return data
        return {
            'results': results,
            'statistics': stats,
            'metadata': metadata,
            'batch_id': batch_id,
            'dashboard_session_id': dashboard_session_id,
            'local_db_ids': self._get_saved_result_ids(batch_id)
        }
    
    def _calculate_statistics(self, results: Dict) -> Dict:
        """
        Calculate reconciliation statistics
        
        Args:
            results: Reconciliation results
            
        Returns:
            Dict: Statistics
        """
        total_transactions = sum(len(transactions) for transactions in results.values())
        matched_transactions = len(results.get('100% MATCH', [])) + \
                             len(results.get('85% FUZZY', [])) + \
                             len(results.get('60% FUZZY', []))
        unmatched_transactions = len(results.get('UNMATCHED', []))
        foreign_credits = len(results.get('FOREIGN CREDITS', []))
        
        match_percentage = (matched_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        return {
            'total_transactions': total_transactions,
            'matched_transactions': matched_transactions,
            'unmatched_transactions': unmatched_transactions,
            'foreign_credits': foreign_credits,
            'match_percentage': match_percentage,
            'result_types': list(results.keys()),
            'non_empty_types': [k for k, v in results.items() if v]
        }
    
    def _convert_results_to_dataframe(self, transactions: List, result_type: str) -> pd.DataFrame:
        """
        Convert transaction results to DataFrame for database storage
        
        Args:
            transactions: List of transactions
            result_type: Type of result
            
        Returns:
            pd.DataFrame: Converted data
        """
        if not transactions:
            return pd.DataFrame()
        
        converted_data = []
        
        for i, transaction in enumerate(transactions):
            row_data = {'result_type': result_type, 'index': i}
            
            if isinstance(transaction, tuple) and len(transaction) >= 2:
                # Matched transaction pair
                stmt_data, cb_data = transaction[0], transaction[1]
                
                # Extract statement data
                if stmt_data is not None:
                    if hasattr(stmt_data, 'to_dict'):
                        for k, v in stmt_data.to_dict().items():
                            row_data[f'statement_{k}'] = v
                    else:
                        row_data['statement_data'] = str(stmt_data)
                
                # Extract cashbook data
                if cb_data is not None:
                    if hasattr(cb_data, 'to_dict'):
                        for k, v in cb_data.to_dict().items():
                            row_data[f'cashbook_{k}'] = v
                    else:
                        row_data['cashbook_data'] = str(cb_data)
            else:
                # Single transaction
                if hasattr(transaction, 'to_dict'):
                    row_data.update(transaction.to_dict())
                elif isinstance(transaction, dict):
                    row_data.update(transaction)
                else:
                    row_data['transaction_data'] = str(transaction)
            
            converted_data.append(row_data)
        
        return pd.DataFrame(converted_data)
    
    def _get_saved_result_ids(self, batch_id: str) -> List[int]:
        """
        Get IDs of saved results for a batch
        
        Args:
            batch_id: Batch ID
            
        Returns:
            List[int]: List of result IDs
        """
        try:
            # This would need to be implemented in ResultsDB if not already available
            all_results = self.results_db.list_reconciliation_results()
            return [r[0] for r in all_results if len(r) > 5 and r[5] == batch_id]
        except:
            return []
    
    def get_session_status(self, dashboard_session_id: str) -> Optional[Dict]:
        """
        Get status of a collaborative session
        
        Args:
            dashboard_session_id: Dashboard session ID
            
        Returns:
            Dict: Session status information
        """
        if not self.enable_dashboard or not self.dashboard_integration:
            return None
        
        return self.dashboard_integration.get_session_info(dashboard_session_id)
    
    def update_session_status(self, dashboard_session_id: str, status: str) -> bool:
        """
        Update collaborative session status
        
        Args:
            dashboard_session_id: Dashboard session ID
            status: New status
            
        Returns:
            bool: True if successful
        """
        if not self.enable_dashboard or not self.dashboard_integration:
            return False
        
        return self.dashboard_integration.update_session_status(dashboard_session_id, status)
    
    def list_collaborative_sessions(self) -> List[Dict]:
        """
        List all collaborative sessions
        
        Returns:
            List[Dict]: List of sessions
        """
        if not self.enable_dashboard or not self.dashboard_integration:
            return []
        
        try:
            response = self.dashboard_integration.session.get(
                f'{self.dashboard_url}/api/sessions'
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('sessions', [])
        except Exception as e:
            print(f"Error listing sessions: {e}")
        
        return []


# Convenience functions for easy integration

def run_collaborative_reconciliation(st_data_path: str, cb_data_path: str,
                                    session_name: str = None, workflow_type: str = "Bank",
                                    dashboard_url: str = "http://localhost:5000",
                                    enable_dashboard: bool = True,
                                    **kwargs) -> Dict:
    """
    Run reconciliation with collaborative dashboard integration (convenience function)
    
    Args:
        st_data_path: Path to statement data
        cb_data_path: Path to cashbook data
        session_name: Session name
        workflow_type: Workflow type
        dashboard_url: Dashboard URL
        enable_dashboard: Enable dashboard integration
        **kwargs: Additional reconciliation parameters
        
    Returns:
        Dict: Reconciliation results and metadata
    """
    workflow = CollaborativeReconciliationWorkflow(
        dashboard_url=dashboard_url,
        enable_dashboard=enable_dashboard
    )
    
    return workflow.run_reconciliation(
        st_data_path=st_data_path,
        cb_data_path=cb_data_path,
        session_name=session_name,
        workflow_type=workflow_type,
        **kwargs
    )


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Enhanced Collaborative Reconciliation Workflow...")
    
    # Test with sample data (you would replace these with actual file paths)
    sample_st_path = "sample_statement.xlsx"  # Replace with actual path
    sample_cb_path = "sample_cashbook.xlsx"   # Replace with actual path
    
    # Check if sample files exist
    if os.path.exists(sample_st_path) and os.path.exists(sample_cb_path):
        # Run collaborative reconciliation
        results = run_collaborative_reconciliation(
            st_data_path=sample_st_path,
            cb_data_path=sample_cb_path,
            session_name="Test Collaborative Session",
            workflow_type="Bank",
            enable_dashboard=True
        )
        
        print("✅ Test completed successfully!")
        print(f"📊 Results: {results['statistics']}")
        
        if results['dashboard_session_id']:
            print(f"🌐 Dashboard Session: {results['dashboard_session_id']}")
    else:
        print("⚠️ Sample files not found. Testing with mock data...")
        
        # Create a test workflow instance
        workflow = CollaborativeReconciliationWorkflow(enable_dashboard=True)
        
        # Test session creation
        session_id = workflow.create_collaborative_session(
            session_name="Test Session",
            workflow_type="Bank",
            description="Testing the enhanced workflow"
        )
        
        if session_id:
            print(f"✅ Successfully created test session: {session_id}")
        else:
            print("❌ Failed to create test session")
        
        print("ℹ️ To test with real data, provide valid file paths to sample_st_path and sample_cb_path")