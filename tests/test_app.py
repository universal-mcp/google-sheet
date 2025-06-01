from unittest.mock import MagicMock

import pytest
from universal_mcp.utils.testing import (
    check_application_instance,
)

from universal_mcp_google_sheet.app import GoogleSheetApp

@pytest.fixture
def app_instance():
    mock_integration = MagicMock()
    mock_integration.get_credentials.return_value = {"access_token": "dummy_access_token"}
    return GoogleSheetApp(integration=mock_integration)

def test_application(app_instance):
    check_application_instance(app_instance, app_name="google-sheet")
