"""
Collaborative Dashboard Integration Module
==========================================

This module provides integration between the existing reconciliation app
and the new collaborative dashboard system. It handles:

- Automatic posting of reconciliation results
- Session management integration
- Real-time notifications
- Workflow automation
"""

import requests
import json
import uuid
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional, Any


class CollaborativeDashboardIntegration:
    """
    Integration class for connecting reconciliation app with collaborative dashboard
    """
    
    def __init__(self, dashboard_url: str = "http://localhost:5000", 
                 api_token: str = None, username: str = None, password: str = None):
        """
        Initialize the dashboard integration
        
        Args:
            dashboard_url: URL of the collaborative dashboard API
            api_token: JWT token for authentication (if available)
            username: Username for authentication (if token not available)
            password: Password for authentication (if token not available)
        """
        self.dashboard_url = dashboard_url.rstrip('/')
        self.api_token = api_token
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'BARD-RECO-Integration/1.0'
        })
        
        # Authenticate if token not provided
        if not api_token and username and password:
            self.authenticate(username, password)
        elif api_token:
            self.session.headers['Authorization'] = f'Bearer {api_token}'
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate with the collaborative dashboard
        
        Args:
            username: Username
            password: Password
            
        Returns:
            bool: True if authentication successful
        """
        try:
            response = self.session.post(
                f'{self.dashboard_url}/api/auth/login',
                json={'username': username, 'password': password}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.api_token = data['token']
                    self.session.headers['Authorization'] = f'Bearer {self.api_token}'
                    print("✅ Successfully authenticated with collaborative dashboard")
                    return True
            
            print(f"❌ Authentication failed: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def create_session(self, session_name: str, workflow_type: str, 
                      description: str = "", priority: str = "normal") -> Optional[str]:
        """
        Create a new reconciliation session in the collaborative dashboard
        
        Args:
            session_name: Name of the session
            workflow_type: Type of workflow (e.g., 'Bank', 'Branch', 'FNB', 'Bidvest')
            description: Session description
            priority: Session priority ('low', 'normal', 'high', 'urgent')
            
        Returns:
            str: Session ID if successful, None otherwise
        """
        try:
            response = self.session.post(
                f'{self.dashboard_url}/api/sessions',
                json={
                    'session_name': session_name,
                    'workflow_type': workflow_type,
                    'description': description,
                    'priority': priority
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    session_id = data['session_id']
                    print(f"✅ Created session: {session_name} (ID: {session_id})")
                    return session_id
            
            print(f"❌ Failed to create session: {response.text}")
            return None
            
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            return None
    
    def post_reconciliation_results(self, session_id: str, results: Dict, 
                                   metadata: Dict = None) -> bool:
        """
        Post reconciliation results to the collaborative dashboard
        
        Args:
            session_id: ID of the session to post results to
            results: Reconciliation results dictionary
            metadata: Additional metadata about the reconciliation
            
        Returns:
            bool: True if successful
        """
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                'posted_at': datetime.now().isoformat(),
                'integration_version': '1.0',
                'source': 'BARD-RECO-App'
            })
            
            # Convert pandas objects to serializable format
            serializable_results = self._serialize_results(results)
            
            # Post to dashboard
            response = self.session.post(
                f'{self.dashboard_url}/api/reconciliation/post',
                json={
                    'session_id': session_id,
                    'results': serializable_results,
                    'metadata': metadata
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    total_transactions = sum(len(transactions) for transactions in serializable_results.values())
                    print(f"✅ Posted {total_transactions} transactions to session {session_id}")
                    return True
            
            print(f"❌ Failed to post results: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ Error posting results: {e}")
            return False
    
    def _serialize_results(self, results: Dict) -> Dict:
        """
        Convert reconciliation results to JSON-serializable format
        
        Args:
            results: Raw reconciliation results
            
        Returns:
            Dict: Serializable results
        """
        serializable = {}
        
        for result_type, transactions in results.items():
            serializable[result_type] = []
            
            for transaction in transactions:
                if isinstance(transaction, tuple):
                    # Handle matched transactions (statement, cashbook pair)
                    if len(transaction) >= 2:
                        stmt_data, cb_data = transaction[0], transaction[1]
                        serialized_transaction = {
                            'statement_data': self._serialize_transaction_data(stmt_data),
                            'cashbook_data': self._serialize_transaction_data(cb_data),
                            'match_type': result_type
                        }
                    else:
                        serialized_transaction = {
                            'data': self._serialize_transaction_data(transaction[0]),
                            'match_type': result_type
                        }
                else:
                    # Handle single transactions
                    serialized_transaction = {
                        'data': self._serialize_transaction_data(transaction),
                        'match_type': result_type
                    }
                
                serializable[result_type].append(serialized_transaction)
        
        return serializable
    
    def _serialize_transaction_data(self, data) -> Dict:
        """
        Serialize individual transaction data
        
        Args:
            data: Transaction data (pandas Series, dict, or other)
            
        Returns:
            Dict: Serialized data
        """
        if data is None:
            return None
        
        if hasattr(data, 'to_dict'):
            # Pandas Series or DataFrame
            return data.to_dict()
        elif isinstance(data, dict):
            return data
        else:
            # Convert other types to string
            return {'raw_data': str(data)}
    
    def update_session_status(self, session_id: str, status: str) -> bool:
        """
        Update session status
        
        Args:
            session_id: Session ID
            status: New status ('active', 'under_review', 'approved', 'rejected', 'archived')
            
        Returns:
            bool: True if successful
        """
        try:
            response = self.session.put(
                f'{self.dashboard_url}/api/sessions/{session_id}/status',
                json={'status': status}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Updated session {session_id} status to {status}")
                    return True
            
            print(f"❌ Failed to update session status: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ Error updating session status: {e}")
            return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get session information
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict: Session information if successful
        """
        try:
            response = self.session.get(
                f'{self.dashboard_url}/api/sessions/{session_id}'
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data['session']
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting session info: {e}")
            return None
    
    def check_connection(self) -> bool:
        """
        Check if connection to dashboard is working
        
        Returns:
            bool: True if connection is working
        """
        try:
            response = self.session.get(f'{self.dashboard_url}/api/auth/me')
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Connection check failed: {e}")
            return False


# Utility functions for easy integration

def create_collaborative_session(session_name: str, workflow_type: str, 
                                description: str = "", priority: str = "normal",
                                dashboard_url: str = "http://localhost:5000",
                                username: str = "admin", password: str = "admin123") -> Optional[str]:
    """
    Quick function to create a collaborative session
    
    Args:
        session_name: Name of the session
        workflow_type: Type of workflow
        description: Session description
        priority: Session priority
        dashboard_url: Dashboard URL
        username: Username for authentication
        password: Password for authentication
        
    Returns:
        str: Session ID if successful
    """
    integration = CollaborativeDashboardIntegration(
        dashboard_url=dashboard_url,
        username=username,
        password=password
    )
    
    return integration.create_session(session_name, workflow_type, description, priority)


def post_reconciliation_to_dashboard(session_id: str, results: Dict, 
                                    metadata: Dict = None,
                                    dashboard_url: str = "http://localhost:5000",
                                    username: str = "admin", password: str = "admin123") -> bool:
    """
    Quick function to post reconciliation results to dashboard
    
    Args:
        session_id: Session ID
        results: Reconciliation results
        metadata: Additional metadata
        dashboard_url: Dashboard URL
        username: Username for authentication
        password: Password for authentication
        
    Returns:
        bool: True if successful
    """
    integration = CollaborativeDashboardIntegration(
        dashboard_url=dashboard_url,
        username=username,
        password=password
    )
    
    return integration.post_reconciliation_results(session_id, results, metadata)


def create_session_and_post_results(session_name: str, workflow_type: str, 
                                   results: Dict, description: str = "",
                                   dashboard_url: str = "http://localhost:5000",
                                   username: str = "admin", password: str = "admin123") -> Optional[str]:
    """
    Create a session and post results in one call
    
    Args:
        session_name: Name of the session
        workflow_type: Type of workflow
        results: Reconciliation results
        description: Session description
        dashboard_url: Dashboard URL
        username: Username for authentication
        password: Password for authentication
        
    Returns:
        str: Session ID if successful
    """
    integration = CollaborativeDashboardIntegration(
        dashboard_url=dashboard_url,
        username=username,
        password=password
    )
    
    # Create session
    session_id = integration.create_session(session_name, workflow_type, description)
    
    if session_id:
        # Post results
        if integration.post_reconciliation_results(session_id, results):
            print(f"✅ Successfully created session and posted results: {session_id}")
            return session_id
        else:
            print(f"❌ Failed to post results to session: {session_id}")
    
    return None


# Example usage and testing
if __name__ == "__main__":
    # Test the integration
    print("🧪 Testing Collaborative Dashboard Integration...")
    
    # Test connection
    integration = CollaborativeDashboardIntegration(
        dashboard_url="http://localhost:5000",
        username="admin",
        password="admin123"
    )
    
    if integration.check_connection():
        print("✅ Connection test passed")
        
        # Test session creation
        session_id = integration.create_session(
            session_name="Test Integration Session",
            workflow_type="Bank",
            description="Testing the integration module"
        )
        
        if session_id:
            print(f"✅ Session creation test passed: {session_id}")
            
            # Test posting dummy results
            dummy_results = {
                '100% MATCH': [
                    ({'amount': 1000, 'reference': 'TEST001'}, {'amount': 1000, 'reference': 'TEST001'})
                ],
                'UNMATCHED': [
                    {'amount': 500, 'reference': 'UNMATCHED001'}
                ]
            }
            
            if integration.post_reconciliation_results(session_id, dummy_results):
                print("✅ Results posting test passed")
            else:
                print("❌ Results posting test failed")
        else:
            print("❌ Session creation test failed")
    else:
        print("❌ Connection test failed")
        print("Make sure the collaborative dashboard server is running on http://localhost:5000")