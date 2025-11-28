import sys
import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
from app.repositories.penalties_repo import load_all, save_all

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

class TestPenalties(unittest.TestCase):

    def setUp(self):
        self.module_name = 'app.repositories.penalties_repo' 

    def test_load_all_file_missing(self):
        """Test that load_all returns an empty list if the file does not exist."""
        with patch(f'{self.module_name}.DATA_PATH') as mock_path:
            mock_path.exists.return_value = False
            
            load_all
            result = load_all()
            
            self.assertEqual(result, [])
            mock_path.exists.assert_called_once()

    def test_load_all_success(self):
        """Test that load_all correctly reads and parses the CSV."""
        csv_content = "Name;Amount\nJohn;100\nJane;200"
        
        with patch(f'{self.module_name}.DATA_PATH') as mock_path:
            mock_path.exists.return_value = True
            
            with patch.object(mock_path, 'open', mock_open(read_data=csv_content)) as mocked_file:
                result = load_all()
                
                expected = [{'Name': 'John', 'Amount': '100'}, {'Name': 'Jane', 'Amount': '200'}]
                self.assertEqual(result, expected)
                mocked_file.assert_called_with("r", encoding="latin-1", newline="")

    def test_save_all_empty_record(self):
        """Test that save_all deletes the file if the record list is empty."""
        with patch(f'{self.module_name}.DATA_PATH') as mock_path:
           save_all([])
            
        mock_path.unlink.assert_called_once_with(missing_ok=True)
        mock_path.open.assert_not_called()

    @patch('os.replace')
    def test_save_all_success(self, mock_os_replace):
        """Test that save_all writes to a temp file and then renames it."""
        records = [{'Name': 'John', 'Amount': '100'}]
        
        with patch(f'{self.module_name}.DATA_PATH') as mock_path:
            mock_tmp_path = MagicMock()
            mock_path.with_suffix.return_value = mock_tmp_path
            
            m_open = mock_open()
            with patch.object(mock_tmp_path, 'open', m_open) as mocked_file:
                save_all(records)
                
                mocked_file.assert_called_once_with("w", encoding="latin-1", newline="")
                
                mock_os_replace.assert_called_once_with(mock_tmp_path, mock_path)

if __name__ == '__main__':
    unittest.main()