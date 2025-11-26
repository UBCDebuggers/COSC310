import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from app.services.penalties_service import (
        create_penalty, 
        get_penalties,
        delete_penalty, 
        delete_penalties_for_user,
        update_penalty, 
        deactivate_penalty, 
        get_penalty
    )
from app.schemas.penalties import PenaltyCreate, PenaltyUpdate, Penalty, PERMANENT_BAN, TEMPORARY_BAN

class TestPenaltyService(unittest.TestCase):

    def setUp(self):
        self.module_path = 'penalties_service'
        
        self.mock_uuid = "test-uuid-123"
        self.mock_timestamp = datetime.now(timezone.utc)
        
        self.existing_record = {
            "penalty_id": "p1",
            "userid": "user123",
            "penalty_type": TEMPORARY_BAN,
            "description": "Late fees",
            "timestamp": self.mock_timestamp.isoformat(),
            "expiry_date": (self.mock_timestamp + timedelta(days=1)).isoformat(),
            "active": True
        }

    @patch('app.services.penalties_service.save_all')
    @patch('app.services.penalties_service.load_all')
    def test_create_penalty_success(self, mock_load, mock_save):
        """Test creating a penalty when user has no permanent bans."""
        mock_load.return_value = []
        
        payload = PenaltyCreate(userid="user123", penalty_type=TEMPORARY_BAN)
        
        create_penalty(payload)
        
        mock_load.assert_called_once()
        mock_save.assert_called_once()
        saved_args = mock_save.call_args[0][0]
        self.assertEqual(len(saved_args), 1)
        self.assertEqual(saved_args[0]['userid'], "user123")

    @patch('app.services.penalties_service.save_all')
    @patch('app.services.penalties_service.load_all')
    def test_create_penalty_fail_permanent_ban(self, mock_load, mock_save):
        """Test that creating a penalty fails if user is permanently banned."""
        banned_record = self.existing_record.copy()
        banned_record['penalty_type'] = PERMANENT_BAN
        mock_load.return_value = [banned_record]
        
        payload = PenaltyCreate(userid="user123", penalty_type=TEMPORARY_BAN)
        
        with self.assertRaises(HTTPException) as context:
            create_penalty(payload)
            
        self.assertEqual(context.exception.status_code, 406)
        self.assertIn("already been banned", context.exception.detail)
        mock_save.assert_not_called()
    
    @patch('app.services.penalties_service.load_all')
    def test_get_penalties_user_success(self, mock_load):
        from app.services.penalties_service import get_penalties_for_user 
        
        mock_load.return_value = [self.existing_record]
        
        result = get_penalties_for_user('user123')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].userid, 'user123')

    @patch('app.services.penalties_service.load_all')
    def test_get_penalty_by_id_success(self, mock_load):
        mock_load.return_value = [self.existing_record]
        
        result = get_penalty("p1")
        
        self.assertIsInstance(result, Penalty)
        self.assertEqual(result.penalty_id, "p1")

    @patch('app.services.penalties_service.load_all')
    def test_get_penalty_by_id_not_found(self, mock_load):
        mock_load.return_value = [self.existing_record]
        
        with self.assertRaises(HTTPException) as context:
            get_penalty("non-existent-id")
            
        self.assertEqual(context.exception.status_code, 404)

    @patch('app.services.penalties_service.save_all')
    @patch('app.services.penalties_service.load_all')
    def test_delete_penalty_success(self, mock_load, mock_save):
        mock_load.return_value = [self.existing_record]
        
        delete_penalty("p1")
        
        mock_save.assert_called_once_with([])

    @patch('app.services.penalties_service.save_all')
    @patch('app.services.penalties_service.load_all')
    def test_delete_penalty_not_found(self, mock_load, mock_save):
        mock_load.return_value = [self.existing_record]
        
        with self.assertRaises(HTTPException) as context:
            delete_penalty("wrong-id")
            
        self.assertEqual(context.exception.status_code, 404)
        mock_save.assert_not_called()

    @patch('app.services.penalties_service.save_all')
    @patch('app.services.penalties_service.load_all')
    def test_update_penalty_success(self, mock_load, mock_save):
        mock_load.return_value = [self.existing_record]
        
        update_payload = PenaltyUpdate(
            penalty_type=TEMPORARY_BAN,
            description="Updated Description",
            active=True
        )
        
        result = update_penalty("p1", update_payload)
        
        self.assertEqual(result.description, "Updated Description")
        
        saved_list = mock_save.call_args[0][0]
        self.assertEqual(saved_list[0]['description'], "Updated Description")

    @patch('app.services.penalties_service.save_all')
    @patch('app.services.penalties_service.load_all')
    def test_deactivate_penalty_success(self, mock_load, mock_save):
        active_record = self.existing_record.copy()
        active_record['active'] = True
        mock_load.return_value = [active_record]
        
        result = deactivate_penalty("p1")
        
        self.assertEqual(result.active, False)
        saved_list = mock_save.call_args[0][0]
        self.assertEqual(saved_list[0]['active'], False)

    @patch('app.services.penalties_service.save_all')
    @patch('app.services.penalties_service.load_all')
    def test_deactivate_penalty_already_inactive(self, mock_load, mock_save):
        inactive_record = self.existing_record.copy()
        inactive_record['active'] = False
        mock_load.return_value = [inactive_record]
        
        with self.assertRaises(HTTPException) as context:
            deactivate_penalty("p1")
            
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("not active", context.exception.detail)
        mock_save.assert_not_called()
        
    @patch('app.services.penalties_service.load_all')
    def test_get_penalties_success(self, mock_load):
        mock_load.return_value = [self.existing_record]

        result = get_penalties()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].penalty_id, "p1")

    @patch('app.services.penalties_service.load_all')
    def test_get_penalties_not_found(self, mock_load):
        mock_load.return_value = []

        with self.assertRaises(HTTPException) as context:
            get_penalties()

        self.assertEqual(context.exception.status_code, 404)

    @patch('app.services.penalties_service.save_all')
    @patch('app.services.penalties_service.load_all')
    def test_delete_penalties_for_user_success(self, mock_load, mock_save):
        mock_load.return_value = [self.existing_record]

        delete_penalties_for_user("user123")

        mock_save.assert_called_once_with([])

    @patch('app.services.penalties_service.save_all')
    @patch('app.services.penalties_service.load_all')
    def test_delete_penalties_for_user_not_found(self, mock_load, mock_save):
        other_user = self.existing_record.copy()
        other_user["userid"] = "different"
        mock_load.return_value = [other_user]

        with self.assertRaises(HTTPException) as context:
            delete_penalties_for_user("user123")

        self.assertEqual(context.exception.status_code, 404)
        mock_save.assert_not_called()

    @patch('app.services.penalties_service.save_all')
    @patch('app.services.penalties_service.load_all')
    def test_update_penalty_not_found(self, mock_load, mock_save):
        mock_load.return_value = [self.existing_record]

        update_payload = PenaltyUpdate(
            penalty_type=TEMPORARY_BAN,
            description="No change",
            active=True
        )

        with self.assertRaises(HTTPException) as context:
            update_penalty("wrong-id", update_payload)

        self.assertEqual(context.exception.status_code, 404)
        mock_save.assert_not_called()

    @patch('app.services.penalties_service.save_all')
    @patch('app.services.penalties_service.load_all')
    def test_deactivate_penalty_not_found(self, mock_load, mock_save):
        mock_load.return_value = [self.existing_record]

        with self.assertRaises(HTTPException) as context:
            deactivate_penalty("wrong-id")

        self.assertEqual(context.exception.status_code, 404)
        mock_save.assert_not_called()


if __name__ == '__main__':
    unittest.main()