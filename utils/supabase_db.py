"""
Supabase Database Service Layer
================================
Handles all database operations for BARD-RECO reconciliation system.
Provides methods for storing and retrieving reconciliation results.
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
import json
import pandas as pd
import uuid

class SupabaseDB:
    """
    Supabase database service for BARD-RECO.
    Handles reconciliation sessions, transactions, and audit logging.
    """

    def __init__(self):
        """Initialize Supabase connection"""
        self.client = None
        self.enabled = False
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Supabase client from secrets or environment"""
        try:
            supabase_url = ""
            supabase_key = ""

            # Try format 1: st.secrets["SUPABASE_URL"]
            try:
                supabase_url = st.secrets.get("SUPABASE_URL", "")
                supabase_key = st.secrets.get("SUPABASE_KEY", "")
            except:
                pass

            # Try format 2: st.secrets["supabase"]["url"]
            if not supabase_url or not supabase_key:
                try:
                    supabase_url = st.secrets["supabase"]["url"]
                    supabase_key = st.secrets["supabase"]["key"]
                except:
                    pass

            # Try environment variables as fallback
            if not supabase_url or not supabase_key:
                import os
                supabase_url = os.environ.get("SUPABASE_URL", "")
                supabase_key = os.environ.get("SUPABASE_KEY", "")

            if supabase_url and supabase_key:
                from supabase import create_client
                self.client = create_client(supabase_url, supabase_key)
                self.enabled = True
            else:
                self.enabled = False

        except Exception as e:
            print(f"Supabase initialization warning: {e}")
            self.enabled = False

    def is_enabled(self) -> bool:
        """Check if Supabase is enabled and connected"""
        return self.enabled and self.client is not None

    # =============================================
    # RECONCILIATION SESSIONS
    # =============================================

    def create_session(
        self,
        session_name: str,
        workflow_type: str,
        user_id: Optional[str] = None,
        ledger_filename: Optional[str] = None,
        ledger_rows: Optional[int] = None,
        statement_filename: Optional[str] = None,
        statement_rows: Optional[int] = None,
        fuzzy_threshold: int = 85,
        date_tolerance: int = 3,
        amount_tolerance: float = 0.01
    ) -> Optional[str]:
        """
        Create a new reconciliation session.
        Returns the session ID if successful, None otherwise.
        """
        if not self.is_enabled():
            return self._create_local_session(session_name, workflow_type)

        try:
            session_id = str(uuid.uuid4())
            data = {
                "id": session_id,
                "session_name": session_name,
                "workflow_type": workflow_type,
                "created_by": user_id,
                "status": "in_progress",
                "ledger_filename": ledger_filename,
                "ledger_rows": ledger_rows,
                "statement_filename": statement_filename,
                "statement_rows": statement_rows,
                "fuzzy_threshold": fuzzy_threshold,
                "date_tolerance": date_tolerance,
                "amount_tolerance": amount_tolerance,
                "started_at": datetime.now().isoformat()
            }

            result = self.client.table("reconciliation_sessions").insert(data).execute()

            if result.data:
                return session_id
            return None

        except Exception as e:
            print(f"Error creating session: {e}")
            return self._create_local_session(session_name, workflow_type)

    def _create_local_session(self, session_name: str, workflow_type: str) -> str:
        """Create a local session when Supabase is not available"""
        session_id = str(uuid.uuid4())

        if 'local_sessions' not in st.session_state:
            st.session_state.local_sessions = {}

        st.session_state.local_sessions[session_id] = {
            "id": session_id,
            "session_name": session_name,
            "workflow_type": workflow_type,
            "status": "in_progress",
            "created_at": datetime.now().isoformat(),
            "matched": [],
            "unmatched_ledger": [],
            "unmatched_statement": []
        }

        return session_id

    def update_session_results(
        self,
        session_id: str,
        total_matched: int,
        total_unmatched_ledger: int,
        total_unmatched_statement: int,
        total_foreign_credits: int = 0,
        total_split_matches: int = 0,
        processing_time_ms: Optional[int] = None
    ) -> bool:
        """Update session with reconciliation results"""
        if not self.is_enabled():
            return self._update_local_session(
                session_id, total_matched, total_unmatched_ledger,
                total_unmatched_statement
            )

        try:
            total = total_matched + total_unmatched_ledger + total_unmatched_statement
            match_rate = (total_matched / total * 100) if total > 0 else 0

            data = {
                "total_matched": total_matched,
                "total_unmatched_ledger": total_unmatched_ledger,
                "total_unmatched_statement": total_unmatched_statement,
                "total_foreign_credits": total_foreign_credits,
                "total_split_matches": total_split_matches,
                "match_rate": round(match_rate, 2),
                "processing_time_ms": processing_time_ms,
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            }

            result = self.client.table("reconciliation_sessions").update(data).eq("id", session_id).execute()
            return bool(result.data)

        except Exception as e:
            print(f"Error updating session: {e}")
            return False

    def _update_local_session(
        self,
        session_id: str,
        total_matched: int,
        total_unmatched_ledger: int,
        total_unmatched_statement: int
    ) -> bool:
        """Update local session"""
        if 'local_sessions' in st.session_state and session_id in st.session_state.local_sessions:
            st.session_state.local_sessions[session_id].update({
                "total_matched": total_matched,
                "total_unmatched_ledger": total_unmatched_ledger,
                "total_unmatched_statement": total_unmatched_statement,
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            })
            return True
        return False

    # =============================================
    # MATCHED TRANSACTIONS
    # =============================================

    def save_matched_transactions(
        self,
        session_id: str,
        matches: List[Dict[str, Any]],
        match_type: str = "perfect"
    ) -> bool:
        """
        Save matched transactions to database.

        Args:
            session_id: The reconciliation session ID
            matches: List of matched transaction dictionaries
            match_type: Type of match (perfect, fuzzy, split, foreign_credit, manual)
        """
        if not matches:
            return True

        if not self.is_enabled():
            return self._save_local_matches(session_id, matches, match_type)

        try:
            batch_size = 500
            for i in range(0, len(matches), batch_size):
                batch = matches[i:i + batch_size]
                records = []

                for match in batch:
                    record = {
                        "id": str(uuid.uuid4()),
                        "session_id": session_id,
                        "match_type": match_type,
                        "match_score": match.get("score", 100),
                        "ledger_date": self._format_date(match.get("ledger_date")),
                        "ledger_reference": str(match.get("ledger_reference", ""))[:255],
                        "ledger_description": str(match.get("ledger_description", "")),
                        "ledger_debit": self._to_decimal(match.get("ledger_debit")),
                        "ledger_credit": self._to_decimal(match.get("ledger_credit")),
                        "ledger_rj_number": str(match.get("rj_number", ""))[:50],
                        "ledger_payment_ref": str(match.get("payment_ref", ""))[:255],
                        "statement_date": self._format_date(match.get("statement_date")),
                        "statement_reference": str(match.get("statement_reference", ""))[:255],
                        "statement_description": str(match.get("statement_description", "")),
                        "statement_amount": self._to_decimal(match.get("statement_amount")),
                        "currency": match.get("currency", "ZAR"),
                        "variance": self._to_decimal(match.get("variance", 0))
                    }
                    records.append(record)

                self.client.table("matched_transactions").insert(records).execute()

            return True

        except Exception as e:
            print(f"Error saving matched transactions: {e}")
            return False

    def _save_local_matches(
        self,
        session_id: str,
        matches: List[Dict],
        match_type: str
    ) -> bool:
        """Save matches to local session state"""
        if 'local_sessions' in st.session_state and session_id in st.session_state.local_sessions:
            if 'matched' not in st.session_state.local_sessions[session_id]:
                st.session_state.local_sessions[session_id]['matched'] = []
            st.session_state.local_sessions[session_id]['matched'].extend(matches)
            return True
        return False

    # =============================================
    # UNMATCHED TRANSACTIONS
    # =============================================

    def save_unmatched_transactions(
        self,
        session_id: str,
        transactions: List[Dict[str, Any]],
        source: str  # 'ledger' or 'statement'
    ) -> bool:
        """
        Save unmatched transactions to database.

        Args:
            session_id: The reconciliation session ID
            transactions: List of unmatched transaction dictionaries
            source: Source of transactions ('ledger' or 'statement')
        """
        if not transactions:
            return True

        if not self.is_enabled():
            return self._save_local_unmatched(session_id, transactions, source)

        try:
            batch_size = 500
            for i in range(0, len(transactions), batch_size):
                batch = transactions[i:i + batch_size]
                records = []

                for txn in batch:
                    record = {
                        "id": str(uuid.uuid4()),
                        "session_id": session_id,
                        "source": source,
                        "transaction_date": self._format_date(txn.get("date")),
                        "reference": str(txn.get("reference", ""))[:255],
                        "description": str(txn.get("description", "")),
                        "debit": self._to_decimal(txn.get("debit")),
                        "credit": self._to_decimal(txn.get("credit")),
                        "amount": self._to_decimal(txn.get("amount")),
                        "rj_number": str(txn.get("rj_number", ""))[:50],
                        "payment_ref": str(txn.get("payment_ref", ""))[:255],
                        "currency": txn.get("currency", "ZAR"),
                        "status": "pending"
                    }
                    records.append(record)

                self.client.table("unmatched_transactions").insert(records).execute()

            return True

        except Exception as e:
            print(f"Error saving unmatched transactions: {e}")
            return False

    def _save_local_unmatched(
        self,
        session_id: str,
        transactions: List[Dict],
        source: str
    ) -> bool:
        """Save unmatched to local session state"""
        if 'local_sessions' in st.session_state and session_id in st.session_state.local_sessions:
            key = f'unmatched_{source}'
            if key not in st.session_state.local_sessions[session_id]:
                st.session_state.local_sessions[session_id][key] = []
            st.session_state.local_sessions[session_id][key].extend(transactions)
            return True
        return False

    # =============================================
    # AUDIT LOGGING
    # =============================================

    def log_action(
        self,
        user_id: Optional[str],
        action_type: str,
        session_id: Optional[str] = None,
        table_name: Optional[str] = None,
        record_id: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Log an action to the audit trail.

        Args:
            user_id: ID of the user performing the action
            action_type: Type of action (e.g., 'create_session', 'run_reconciliation')
            session_id: Related session ID if applicable
            table_name: Table affected
            record_id: Record affected
            old_values: Previous values (for updates)
            new_values: New values (for updates/creates)
        """
        if not self.is_enabled():
            return self._log_local_action(action_type, session_id)

        try:
            data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": session_id,
                "action_type": action_type,
                "table_name": table_name,
                "record_id": record_id,
                "old_values": json.dumps(old_values) if old_values else None,
                "new_values": json.dumps(new_values) if new_values else None,
                "ip_address": ip_address,
                "created_at": datetime.now().isoformat()
            }

            self.client.table("audit_log").insert(data).execute()
            return True

        except Exception as e:
            print(f"Error logging action: {e}")
            return False

    def _log_local_action(self, action_type: str, session_id: Optional[str]) -> bool:
        """Log action locally when Supabase not available"""
        if 'local_audit_log' not in st.session_state:
            st.session_state.local_audit_log = []

        st.session_state.local_audit_log.append({
            "action_type": action_type,
            "session_id": session_id,
            "created_at": datetime.now().isoformat()
        })
        return True

    # =============================================
    # SESSION HISTORY
    # =============================================

    def get_session_history(
        self,
        user_id: Optional[str] = None,
        workflow_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get reconciliation session history.

        Args:
            user_id: Filter by user ID
            workflow_type: Filter by workflow type
            limit: Maximum number of sessions to return
        """
        if not self.is_enabled():
            return self._get_local_session_history(workflow_type, limit)

        try:
            query = self.client.table("reconciliation_sessions").select("*")

            if user_id:
                query = query.eq("created_by", user_id)
            if workflow_type:
                query = query.eq("workflow_type", workflow_type)

            query = query.order("created_at", desc=True).limit(limit)
            result = query.execute()

            return result.data if result.data else []

        except Exception as e:
            print(f"Error getting session history: {e}")
            return []

    def _get_local_session_history(
        self,
        workflow_type: Optional[str],
        limit: int
    ) -> List[Dict]:
        """Get local session history"""
        if 'local_sessions' not in st.session_state:
            return []

        sessions = list(st.session_state.local_sessions.values())

        if workflow_type:
            sessions = [s for s in sessions if s.get("workflow_type") == workflow_type]

        # Sort by created_at descending
        sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return sessions[:limit]

    def get_session_details(self, session_id: str) -> Optional[Dict]:
        """Get detailed information about a session including all transactions"""
        if not self.is_enabled():
            if 'local_sessions' in st.session_state:
                return st.session_state.local_sessions.get(session_id)
            return None

        try:
            # Get session
            session = self.client.table("reconciliation_sessions").select("*").eq("id", session_id).single().execute()

            if not session.data:
                return None

            result = session.data

            # Get matched transactions
            matched = self.client.table("matched_transactions").select("*").eq("session_id", session_id).execute()
            result["matched_transactions"] = matched.data if matched.data else []

            # Get unmatched transactions
            unmatched = self.client.table("unmatched_transactions").select("*").eq("session_id", session_id).execute()
            result["unmatched_transactions"] = unmatched.data if unmatched.data else []

            return result

        except Exception as e:
            print(f"Error getting session details: {e}")
            return None

    # =============================================
    # HELPER METHODS
    # =============================================

    def _format_date(self, date_value) -> Optional[str]:
        """Format date value for database storage"""
        if date_value is None:
            return None
        if isinstance(date_value, str):
            return date_value[:10] if len(date_value) >= 10 else date_value
        if isinstance(date_value, datetime):
            return date_value.strftime("%Y-%m-%d")
        if hasattr(date_value, 'strftime'):
            return date_value.strftime("%Y-%m-%d")
        return str(date_value)[:10]

    def _to_decimal(self, value) -> Optional[float]:
        """Convert value to decimal for database storage"""
        if value is None:
            return None
        if pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


# =============================================
# CONVENIENCE FUNCTIONS
# =============================================

# Singleton instance
_db_instance = None

def get_db() -> SupabaseDB:
    """Get the singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SupabaseDB()
    return _db_instance


def save_reconciliation_results(
    workflow_type: str,
    session_name: str,
    matched_df: Optional[pd.DataFrame] = None,
    unmatched_ledger_df: Optional[pd.DataFrame] = None,
    unmatched_statement_df: Optional[pd.DataFrame] = None,
    foreign_credits_df: Optional[pd.DataFrame] = None,
    processing_time_ms: Optional[int] = None,
    user_id: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Convenience function to save all reconciliation results.

    Returns:
        Tuple of (success: bool, session_id: str)
    """
    db = get_db()

    # Create session
    session_id = db.create_session(
        session_name=session_name,
        workflow_type=workflow_type,
        user_id=user_id
    )

    if not session_id:
        return False, ""

    try:
        # Save matched transactions
        if matched_df is not None and len(matched_df) > 0:
            matches = matched_df.to_dict('records')
            db.save_matched_transactions(session_id, matches, "perfect")

        # Save unmatched ledger
        if unmatched_ledger_df is not None and len(unmatched_ledger_df) > 0:
            unmatched = unmatched_ledger_df.to_dict('records')
            db.save_unmatched_transactions(session_id, unmatched, "ledger")

        # Save unmatched statement
        if unmatched_statement_df is not None and len(unmatched_statement_df) > 0:
            unmatched = unmatched_statement_df.to_dict('records')
            db.save_unmatched_transactions(session_id, unmatched, "statement")

        # Update session with totals
        db.update_session_results(
            session_id=session_id,
            total_matched=len(matched_df) if matched_df is not None else 0,
            total_unmatched_ledger=len(unmatched_ledger_df) if unmatched_ledger_df is not None else 0,
            total_unmatched_statement=len(unmatched_statement_df) if unmatched_statement_df is not None else 0,
            total_foreign_credits=len(foreign_credits_df) if foreign_credits_df is not None else 0,
            processing_time_ms=processing_time_ms
        )

        # Log the action
        db.log_action(
            user_id=user_id,
            action_type="reconciliation_completed",
            session_id=session_id,
            new_values={
                "workflow_type": workflow_type,
                "total_matched": len(matched_df) if matched_df is not None else 0
            }
        )

        return True, session_id

    except Exception as e:
        print(f"Error saving reconciliation results: {e}")
        return False, session_id
