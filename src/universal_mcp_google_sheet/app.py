from typing import Any

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class GoogleSheetApp(APIApplication):
    """
    Application for interacting with Google Sheets API.
    Provides tools to create and manage Google Spreadsheets.
    """

    def __init__(self, integration: Integration | None = None) -> None:
        super().__init__(name="google-sheet", integration=integration)
        self.base_api_url = "https://sheets.googleapis.com/v4/spreadsheets"
        self.base_url = "https://sheets.googleapis.com"

    def create_spreadsheet(self, title: str) -> dict[str, Any]:
        """
        Creates a new blank Google Spreadsheet with the specified title and returns the API response.

        Args:
            title: String representing the desired title for the new spreadsheet

        Returns:
            Dictionary containing the full response from the Google Sheets API, including the spreadsheet's metadata and properties

        Raises:
            HTTPError: When the API request fails due to invalid authentication, network issues, or API limitations
            ValueError: When the title parameter is empty or contains invalid characters

        Tags:
            create, spreadsheet, google-sheets, api, important
        """
        url = self.base_api_url
        spreadsheet_data = {"properties": {"title": title}}
        response = self._post(url, data=spreadsheet_data)
        return response.json()

    def get_spreadsheet(self, spreadsheet_id: str) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific Google Spreadsheet using its ID.

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to retrieve (found in the spreadsheet's URL)

        Returns:
            A dictionary containing the full spreadsheet metadata and contents, including properties, sheets, named ranges, and other spreadsheet-specific information from the Google Sheets API

        Raises:
            HTTPError: When the API request fails due to invalid spreadsheet_id or insufficient permissions
            ConnectionError: When there's a network connectivity issue
            ValueError: When the response cannot be parsed as JSON

        Tags:
            get, retrieve, spreadsheet, api, metadata, read, important
        """
        url = f"{self.base_api_url}/{spreadsheet_id}"
        response = self._get(url)
        return response.json()

    def batch_get_values(
        self, spreadsheet_id: str, ranges: list[str] = None
    ) -> dict[str, Any]:
        """
        Retrieves multiple ranges of values from a Google Spreadsheet in a single batch request.

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to retrieve values from
            ranges: Optional list of A1 notation or R1C1 notation range strings (e.g., ['Sheet1!A1:B2', 'Sheet2!C3:D4']). If None, returns values from the entire spreadsheet

        Returns:
            A dictionary containing the API response with the requested spreadsheet values and metadata

        Raises:
            HTTPError: If the API request fails due to invalid spreadsheet_id, insufficient permissions, or invalid range format
            ValueError: If the spreadsheet_id is empty or invalid

        Tags:
            get, batch, read, spreadsheet, values, important
        """
        url = f"{self.base_api_url}/{spreadsheet_id}/values:batchGet"
        params = {}
        if ranges:
            params["ranges"] = ranges
        response = self._get(url, params=params)
        return response.json()

    def clear_values(self, spreadsheet_id: str, range: str) -> dict[str, Any]:
        """
        Clears all values from a specified range in a Google Spreadsheet while preserving cell formatting and other properties

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to modify
            range: The A1 or R1C1 notation range of cells to clear (e.g., 'Sheet1!A1:B2')

        Returns:
            A dictionary containing the Google Sheets API response

        Raises:
            HttpError: When the API request fails due to invalid spreadsheet_id, invalid range format, or insufficient permissions
            ValueError: When spreadsheet_id is empty or range is in invalid format

        Tags:
            clear, modify, spreadsheet, api, sheets, data-management, important
        """
        url = f"{self.base_api_url}/{spreadsheet_id}/values/{range}:clear"
        response = self._post(url, data={})
        return response.json()

    def update_values(
        self,
        spreadsheet_id: str,
        range: str,
        values: list[list[Any]],
        value_input_option: str = "RAW",
    ) -> dict[str, Any]:
        """
        Updates cell values in a specified range of a Google Spreadsheet using the Sheets API

        Args:
            spreadsheet_id: The unique identifier of the target Google Spreadsheet
            range: The A1 notation range where values will be updated (e.g., 'Sheet1!A1:B2')
            values: A list of lists containing the data to write, where each inner list represents a row of values
            value_input_option: Determines how input data should be interpreted: 'RAW' (as-is) or 'USER_ENTERED' (parsed as UI input). Defaults to 'RAW'

        Returns:
            A dictionary containing the Google Sheets API response with update details

        Raises:
            RequestError: When the API request fails due to invalid parameters or network issues
            AuthenticationError: When authentication with the Google Sheets API fails

        Tags:
            update, write, sheets, api, important, data-modification, google-sheets
        """
        url = f"{self.base_api_url}/{spreadsheet_id}/values/{range}"
        params = {"valueInputOption": value_input_option}
        data = {"range": range, "values": values}
        response = self._put(url, data=data, params=params)
        return response.json()

    def get_values(self, spreadsheetId, range, majorDimension=None, valueRenderOption=None, dateTimeRenderOption=None, access_token=None, alt=None, callback=None, fields=None, key=None, oauth_token=None, prettyPrint=None, quotaUser=None, upload_protocol=None, uploadType=None, xgafv=None) -> Any:
        """
        Get Values

        Args:
            spreadsheetId (string): spreadsheetId
            range (string): range
            majorDimension (string): No description provided. Example: '{{majorDimension}}'.
            valueRenderOption (string): No description provided. Example: '{{valueRenderOption}}'.
            dateTimeRenderOption (string): No description provided. Example: '{{dateTimeRenderOption}}'.
            access_token (string): OAuth access token. Example: '{{accessToken}}'.
            alt (string): Data format for response. Example: '{{alt}}'.
            callback (string): JSONP Example: '{{callback}}'.
            fields (string): Selector specifying which fields to include in a partial response. Example: '{{fields}}'.
            key (string): API key. Your API key identifies your project and provides you with API access, quota, and reports. Required unless you provide an OAuth 2.0 token. Example: '{{key}}'.
            oauth_token (string): OAuth 2.0 token for the current user. Example: '{{oauthToken}}'.
            prettyPrint (string): Returns response with indentations and line breaks. Example: '{{prettyPrint}}'.
            quotaUser (string): Available to use for quota purposes for server-side applications. Can be any arbitrary string assigned to a user, but should not exceed 40 characters. Example: '{{quotaUser}}'.
            upload_protocol (string): Upload protocol for media (e.g. "raw", "multipart"). Example: '{{uploadProtocol}}'.
            uploadType (string): Legacy upload protocol for media (e.g. "media", "multipart"). Example: '{{uploadType}}'.
            xgafv (string): V1 error format. Example: '{{.Xgafv}}'.

        Returns:
            Any: Successful response

        Tags:
            Values
        """
        if spreadsheetId is None:
            raise ValueError("Missing required parameter 'spreadsheetId'")
        if range is None:
            raise ValueError("Missing required parameter 'range'")
        url = f"{self.base_url}/v4/spreadsheets/{spreadsheetId}/values/{range}"
        query_params = {k: v for k, v in [('majorDimension', majorDimension), ('valueRenderOption', valueRenderOption), ('dateTimeRenderOption', dateTimeRenderOption), ('access_token', access_token), ('alt', alt), ('callback', callback), ('fields', fields), ('key', key), ('oauth_token', oauth_token), ('prettyPrint', prettyPrint), ('quotaUser', quotaUser), ('upload_protocol', upload_protocol), ('uploadType', uploadType), ('$.xgafv', xgafv)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def batch_clear_values(self, spreadsheetId, access_token=None, alt=None, callback=None, fields=None, key=None, oauth_token=None, prettyPrint=None, quotaUser=None, upload_protocol=None, uploadType=None, xgafv=None, ranges=None) -> dict[str, Any]:
        """
        Batch Clear Values

        Args:
            spreadsheetId (string): spreadsheetId
            access_token (string): OAuth access token. Example: '{{accessToken}}'.
            alt (string): Data format for response. Example: '{{alt}}'.
            callback (string): JSONP Example: '{{callback}}'.
            fields (string): Selector specifying which fields to include in a partial response. Example: '{{fields}}'.
            key (string): API key. Your API key identifies your project and provides you with API access, quota, and reports. Required unless you provide an OAuth 2.0 token. Example: '{{key}}'.
            oauth_token (string): OAuth 2.0 token for the current user. Example: '{{oauthToken}}'.
            prettyPrint (string): Returns response with indentations and line breaks. Example: '{{prettyPrint}}'.
            quotaUser (string): Available to use for quota purposes for server-side applications. Can be any arbitrary string assigned to a user, but should not exceed 40 characters. Example: '{{quotaUser}}'.
            upload_protocol (string): Upload protocol for media (e.g. "raw", "multipart"). Example: '{{uploadProtocol}}'.
            uploadType (string): Legacy upload protocol for media (e.g. "media", "multipart"). Example: '{{uploadType}}'.
            xgafv (string): V1 error format. Example: '{{.Xgafv}}'.
            ranges (array): ranges
                Example:
                ```json
                {
                  "ranges": [
                    "nostrud sunt reprehenderit proident cillum",
                    "laborum eiusmod dolor ali"
                  ]
                }
                ```

        Returns:
            dict[str, Any]: Successful response

        Tags:
            Batch Values Update
        """
        if spreadsheetId is None:
            raise ValueError("Missing required parameter 'spreadsheetId'")
        request_body = {
            'ranges': ranges,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v4/spreadsheets/{spreadsheetId}/values:batchClear"
        query_params = {k: v for k, v in [('access_token', access_token), ('alt', alt), ('callback', callback), ('fields', fields), ('key', key), ('oauth_token', oauth_token), ('prettyPrint', prettyPrint), ('quotaUser', quotaUser), ('upload_protocol', upload_protocol), ('uploadType', uploadType), ('$.xgafv', xgafv)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def batch_clear_values_by_data_filter(self, spreadsheetId, access_token=None, alt=None, callback=None, fields=None, key=None, oauth_token=None, prettyPrint=None, quotaUser=None, upload_protocol=None, uploadType=None, xgafv=None, dataFilters=None) -> dict[str, Any]:
        """
        Batch Clear Values by Data Filter

        Args:
            spreadsheetId (string): spreadsheetId
            access_token (string): OAuth access token. Example: '{{accessToken}}'.
            alt (string): Data format for response. Example: '{{alt}}'.
            callback (string): JSONP Example: '{{callback}}'.
            fields (string): Selector specifying which fields to include in a partial response. Example: '{{fields}}'.
            key (string): API key. Your API key identifies your project and provides you with API access, quota, and reports. Required unless you provide an OAuth 2.0 token. Example: '{{key}}'.
            oauth_token (string): OAuth 2.0 token for the current user. Example: '{{oauthToken}}'.
            prettyPrint (string): Returns response with indentations and line breaks. Example: '{{prettyPrint}}'.
            quotaUser (string): Available to use for quota purposes for server-side applications. Can be any arbitrary string assigned to a user, but should not exceed 40 characters. Example: '{{quotaUser}}'.
            upload_protocol (string): Upload protocol for media (e.g. "raw", "multipart"). Example: '{{uploadProtocol}}'.
            uploadType (string): Legacy upload protocol for media (e.g. "media", "multipart"). Example: '{{uploadType}}'.
            xgafv (string): V1 error format. Example: '{{.Xgafv}}'.
            dataFilters (array): dataFilters
                Example:
                ```json
                {
                  "dataFilters": [
                    {
                      "a1Range": "commodo ea in ut",
                      "developerMetadataLookup": {
                        "locationMatchingStrategy": "INTERSECTING_LOCATION",
                        "locationType": "SHEET",
                        "metadataId": -27000770,
                        "metadataKey": "ip",
                        "metadataLocation": {
                          "dimensionRange": {
                            "dimension": "DIMENSION_UNSPECIFIED",
                            "endIndex": 91540263,
                            "sheetId": -64167623,
                            "startIndex": 63800966
                          },
                          "locationType": "DEVELOPER_METADATA_LOCATION_TYPE_UNSPECIFIED",
                          "sheetId": 46858270,
                          "spreadsheet": false
                        },
                        "metadataValue": "Excepteur",
                        "visibility": "DOCUMENT"
                      },
                      "gridRange": {
                        "endColumnIndex": 6998754,
                        "endRowIndex": 43176042,
                        "sheetId": -9008085,
                        "startColumnIndex": -17508638,
                        "startRowIndex": 21352870
                      }
                    },
                    {
                      "a1Range": "esse eiusmod",
                      "developerMetadataLookup": {
                        "locationMatchingStrategy": "EXACT_LOCATION",
                        "locationType": "SHEET",
                        "metadataId": -9620585,
                        "metadataKey": "in",
                        "metadataLocation": {
                          "dimensionRange": {
                            "dimension": "COLUMNS",
                            "endIndex": -85774445,
                            "sheetId": 81988143,
                            "startIndex": -35232572
                          },
                          "locationType": "SPREADSHEET",
                          "sheetId": -39029265,
                          "spreadsheet": false
                        },
                        "metadataValue": "voluptate adipisicing amet dolor",
                        "visibility": "PROJECT"
                      },
                      "gridRange": {
                        "endColumnIndex": -87815739,
                        "endRowIndex": -52115573,
                        "sheetId": 67629865,
                        "startColumnIndex": 66943098,
                        "startRowIndex": 74725547
                      }
                    }
                  ]
                }
                ```

        Returns:
            dict[str, Any]: Successful response

        Tags:
            Batch Values Update
        """
        if spreadsheetId is None:
            raise ValueError("Missing required parameter 'spreadsheetId'")
        request_body = {
            'dataFilters': dataFilters,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v4/spreadsheets/{spreadsheetId}/values:batchClearByDataFilter"
        query_params = {k: v for k, v in [('access_token', access_token), ('alt', alt), ('callback', callback), ('fields', fields), ('key', key), ('oauth_token', oauth_token), ('prettyPrint', prettyPrint), ('quotaUser', quotaUser), ('upload_protocol', upload_protocol), ('uploadType', uploadType), ('$.xgafv', xgafv)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_values_by_data_filter(self, spreadsheetId, access_token=None, alt=None, callback=None, fields=None, key=None, oauth_token=None, prettyPrint=None, quotaUser=None, upload_protocol=None, uploadType=None, xgafv=None, dataFilters=None, dateTimeRenderOption=None, majorDimension=None, valueRenderOption=None) -> Any:
        """
        Get Values By Data Filter

        Args:
            spreadsheetId (string): spreadsheetId
            access_token (string): OAuth access token. Example: '{{accessToken}}'.
            alt (string): Data format for response. Example: '{{alt}}'.
            callback (string): JSONP Example: '{{callback}}'.
            fields (string): Selector specifying which fields to include in a partial response. Example: '{{fields}}'.
            key (string): API key. Your API key identifies your project and provides you with API access, quota, and reports. Required unless you provide an OAuth 2.0 token. Example: '{{key}}'.
            oauth_token (string): OAuth 2.0 token for the current user. Example: '{{oauthToken}}'.
            prettyPrint (string): Returns response with indentations and line breaks. Example: '{{prettyPrint}}'.
            quotaUser (string): Available to use for quota purposes for server-side applications. Can be any arbitrary string assigned to a user, but should not exceed 40 characters. Example: '{{quotaUser}}'.
            upload_protocol (string): Upload protocol for media (e.g. "raw", "multipart"). Example: '{{uploadProtocol}}'.
            uploadType (string): Legacy upload protocol for media (e.g. "media", "multipart"). Example: '{{uploadType}}'.
            xgafv (string): V1 error format. Example: '{{.Xgafv}}'.
            dataFilters (array): dataFilters Example: "[{'a1Range': 'eiusmod anim enim culpa', 'developerMetadataLookup': {'locationMatchingStrategy': 'INTERSECTING_LOCATION', 'locationType': 'SPREADSHEET', 'metadataId': -64798951, 'metadataKey': 'sint minim commodo', 'metadataLocation': {'dimensionRange': {'dimension': 'ROWS', 'endIndex': 34518543, 'sheetId': 68337575, 'startIndex': 91706381}, 'locationType': 'ROW', 'sheetId': -33783740, 'spreadsheet': True}, 'metadataValue': 'sunt', 'visibility': 'DEVELOPER_METADATA_VISIBILITY_UNSPECIFIED'}, 'gridRange': {'endColumnIndex': -96821047, 'endRowIndex': -9277805, 'sheetId': 7522437, 'startColumnIndex': 85603635, 'startRowIndex': -31384652}}, {'a1Range': 'sunt irure dolor', 'developerMetadataLookup': {'locationMatchingStrategy': 'DEVELOPER_METADATA_LOCATION_MATCHING_STRATEGY_UNSPECIFIED', 'locationType': 'SHEET', 'metadataId': 26360577, 'metadataKey': 'in minim nulla aliquip laboris', 'metadataLocation': {'dimensionRange': {'dimension': 'COLUMNS', 'endIndex': -14426665, 'sheetId': 88787400, 'startIndex': -98846780}, 'locationType': 'COLUMN', 'sheetId': -14062757, 'spreadsheet': True}, 'metadataValue': 'proident au', 'visibility': 'DOCUMENT'}, 'gridRange': {'endColumnIndex': -11696202, 'endRowIndex': -87528654, 'sheetId': 32991035, 'startColumnIndex': -95148112, 'startRowIndex': -72465558}}]".
            dateTimeRenderOption (string): dateTimeRenderOption Example: 'FORMATTED_STRING'.
            majorDimension (string): majorDimension Example: 'DIMENSION_UNSPECIFIED'.
            valueRenderOption (string): valueRenderOption
                Example:
                ```json
                {
                  "dataFilters": [
                    {
                      "a1Range": "eiusmod anim enim culpa",
                      "developerMetadataLookup": {
                        "locationMatchingStrategy": "INTERSECTING_LOCATION",
                        "locationType": "SPREADSHEET",
                        "metadataId": -64798951,
                        "metadataKey": "sint minim commodo",
                        "metadataLocation": {
                          "dimensionRange": {
                            "dimension": "ROWS",
                            "endIndex": 34518543,
                            "sheetId": 68337575,
                            "startIndex": 91706381
                          },
                          "locationType": "ROW",
                          "sheetId": -33783740,
                          "spreadsheet": true
                        },
                        "metadataValue": "sunt",
                        "visibility": "DEVELOPER_METADATA_VISIBILITY_UNSPECIFIED"
                      },
                      "gridRange": {
                        "endColumnIndex": -96821047,
                        "endRowIndex": -9277805,
                        "sheetId": 7522437,
                        "startColumnIndex": 85603635,
                        "startRowIndex": -31384652
                      }
                    },
                    {
                      "a1Range": "sunt irure dolor",
                      "developerMetadataLookup": {
                        "locationMatchingStrategy": "DEVELOPER_METADATA_LOCATION_MATCHING_STRATEGY_UNSPECIFIED",
                        "locationType": "SHEET",
                        "metadataId": 26360577,
                        "metadataKey": "in minim nulla aliquip laboris",
                        "metadataLocation": {
                          "dimensionRange": {
                            "dimension": "COLUMNS",
                            "endIndex": -14426665,
                            "sheetId": 88787400,
                            "startIndex": -98846780
                          },
                          "locationType": "COLUMN",
                          "sheetId": -14062757,
                          "spreadsheet": true
                        },
                        "metadataValue": "proident au",
                        "visibility": "DOCUMENT"
                      },
                      "gridRange": {
                        "endColumnIndex": -11696202,
                        "endRowIndex": -87528654,
                        "sheetId": 32991035,
                        "startColumnIndex": -95148112,
                        "startRowIndex": -72465558
                      }
                    }
                  ],
                  "dateTimeRenderOption": "FORMATTED_STRING",
                  "majorDimension": "DIMENSION_UNSPECIFIED",
                  "valueRenderOption": "FORMULA"
                }
                ```

        Returns:
            Any: Successful response

        Tags:
            Batch Values Update
        """
        if spreadsheetId is None:
            raise ValueError("Missing required parameter 'spreadsheetId'")
        request_body = {
            'dataFilters': dataFilters,
            'dateTimeRenderOption': dateTimeRenderOption,
            'majorDimension': majorDimension,
            'valueRenderOption': valueRenderOption,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v4/spreadsheets/{spreadsheetId}/values:batchGetByDataFilter"
        query_params = {k: v for k, v in [('access_token', access_token), ('alt', alt), ('callback', callback), ('fields', fields), ('key', key), ('oauth_token', oauth_token), ('prettyPrint', prettyPrint), ('quotaUser', quotaUser), ('upload_protocol', upload_protocol), ('uploadType', uploadType), ('$.xgafv', xgafv)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def copy_to_sheet(self, spreadsheetId, sheetId, access_token=None, alt=None, callback=None, fields=None, key=None, oauth_token=None, prettyPrint=None, quotaUser=None, upload_protocol=None, uploadType=None, xgafv=None, destinationSpreadsheetId=None) -> dict[str, Any]:
        """
        Copy To Sheet

        Args:
            spreadsheetId (string): spreadsheetId
            {sheetId (string): {sheetId
            access_token (string): OAuth access token. Example: '{{accessToken}}'.
            alt (string): Data format for response. Example: '{{alt}}'.
            callback (string): JSONP Example: '{{callback}}'.
            fields (string): Selector specifying which fields to include in a partial response. Example: '{{fields}}'.
            key (string): API key. Your API key identifies your project and provides you with API access, quota, and reports. Required unless you provide an OAuth 2.0 token. Example: '{{key}}'.
            oauth_token (string): OAuth 2.0 token for the current user. Example: '{{oauthToken}}'.
            prettyPrint (string): Returns response with indentations and line breaks. Example: '{{prettyPrint}}'.
            quotaUser (string): Available to use for quota purposes for server-side applications. Can be any arbitrary string assigned to a user, but should not exceed 40 characters. Example: '{{quotaUser}}'.
            upload_protocol (string): Upload protocol for media (e.g. "raw", "multipart"). Example: '{{uploadProtocol}}'.
            uploadType (string): Legacy upload protocol for media (e.g. "media", "multipart"). Example: '{{uploadType}}'.
            xgafv (string): V1 error format. Example: '{{.Xgafv}}'.
            destinationSpreadsheetId (string): destinationSpreadsheetId
                Example:
                ```json
                {
                  "destinationSpreadsheetId": "eu fugiat"
                }
                ```

        Returns:
            dict[str, Any]: Successful response

        Tags:
            Sheets
        """
        if spreadsheetId is None:
            raise ValueError("Missing required parameter 'spreadsheetId'")
        if sheetId is None:
            raise ValueError("Missing required parameter '{sheetId'")
        request_body = {
            'destinationSpreadsheetId': destinationSpreadsheetId,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v4/spreadsheets/{spreadsheetId}/sheets/{{sheetId}}:copyTo"
        query_params = {k: v for k, v in [('access_token', access_token), ('alt', alt), ('callback', callback), ('fields', fields), ('key', key), ('oauth_token', oauth_token), ('prettyPrint', prettyPrint), ('quotaUser', quotaUser), ('upload_protocol', upload_protocol), ('uploadType', uploadType), ('$.xgafv', xgafv)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()
    
    def get_developer_metadata(self, spreadsheetId, metadataId, access_token=None, alt=None, callback=None, fields=None, key=None, oauth_token=None, prettyPrint=None, quotaUser=None, upload_protocol=None, uploadType=None, xgafv=None) -> dict[str, Any]:
        """
        Get Developer Metadata

        Args:
            spreadsheetId (string): spreadsheetId
            metadataId (string): metadataId
            access_token (string): OAuth access token. Example: '{{accessToken}}'.
            alt (string): Data format for response. Example: '{{alt}}'.
            callback (string): JSONP Example: '{{callback}}'.
            fields (string): Selector specifying which fields to include in a partial response. Example: '{{fields}}'.
            key (string): API key. Your API key identifies your project and provides you with API access, quota, and reports. Required unless you provide an OAuth 2.0 token. Example: '{{key}}'.
            oauth_token (string): OAuth 2.0 token for the current user. Example: '{{oauthToken}}'.
            prettyPrint (string): Returns response with indentations and line breaks. Example: '{{prettyPrint}}'.
            quotaUser (string): Available to use for quota purposes for server-side applications. Can be any arbitrary string assigned to a user, but should not exceed 40 characters. Example: '{{quotaUser}}'.
            upload_protocol (string): Upload protocol for media (e.g. "raw", "multipart"). Example: '{{uploadProtocol}}'.
            uploadType (string): Legacy upload protocol for media (e.g. "media", "multipart"). Example: '{{uploadType}}'.
            xgafv (string): V1 error format. Example: '{{.Xgafv}}'.

        Returns:
            dict[str, Any]: Successful response

        Tags:
            Metadata
        """
        if spreadsheetId is None:
            raise ValueError("Missing required parameter 'spreadsheetId'")
        if metadataId is None:
            raise ValueError("Missing required parameter 'metadataId'")
        url = f"{self.base_url}/v4/spreadsheets/{spreadsheetId}/developerMetadata/{metadataId}"
        query_params = {k: v for k, v in [('access_token', access_token), ('alt', alt), ('callback', callback), ('fields', fields), ('key', key), ('oauth_token', oauth_token), ('prettyPrint', prettyPrint), ('quotaUser', quotaUser), ('upload_protocol', upload_protocol), ('uploadType', uploadType), ('$.xgafv', xgafv)] if v is not None}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_developer_metadata(self, spreadsheetId, access_token=None, alt=None, callback=None, fields=None, key=None, oauth_token=None, prettyPrint=None, quotaUser=None, upload_protocol=None, uploadType=None, xgafv=None, dataFilters=None) -> dict[str, Any]:
        """
        Search Developer Metadata

        Args:
            spreadsheetId (string): spreadsheetId
            access_token (string): OAuth access token. Example: '{{accessToken}}'.
            alt (string): Data format for response. Example: '{{alt}}'.
            callback (string): JSONP Example: '{{callback}}'.
            fields (string): Selector specifying which fields to include in a partial response. Example: '{{fields}}'.
            key (string): API key. Your API key identifies your project and provides you with API access, quota, and reports. Required unless you provide an OAuth 2.0 token. Example: '{{key}}'.
            oauth_token (string): OAuth 2.0 token for the current user. Example: '{{oauthToken}}'.
            prettyPrint (string): Returns response with indentations and line breaks. Example: '{{prettyPrint}}'.
            quotaUser (string): Available to use for quota purposes for server-side applications. Can be any arbitrary string assigned to a user, but should not exceed 40 characters. Example: '{{quotaUser}}'.
            upload_protocol (string): Upload protocol for media (e.g. "raw", "multipart"). Example: '{{uploadProtocol}}'.
            uploadType (string): Legacy upload protocol for media (e.g. "media", "multipart"). Example: '{{uploadType}}'.
            xgafv (string): V1 error format. Example: '{{.Xgafv}}'.
            dataFilters (array): dataFilters
                Example:
                ```json
                {
                  "dataFilters": [
                    {
                      "a1Range": "aute",
                      "developerMetadataLookup": {
                        "locationMatchingStrategy": "INTERSECTING_LOCATION",
                        "locationType": "DEVELOPER_METADATA_LOCATION_TYPE_UNSPECIFIED",
                        "metadataId": -761178,
                        "metadataKey": "consequat Duis",
                        "metadataLocation": {
                          "dimensionRange": {
                            "dimension": "COLUMNS",
                            "endIndex": -22955243,
                            "sheetId": 41865153,
                            "startIndex": -49712859
                          },
                          "locationType": "SHEET",
                          "sheetId": 77477058,
                          "spreadsheet": true
                        },
                        "metadataValue": "tempor",
                        "visibility": "DOCUMENT"
                      },
                      "gridRange": {
                        "endColumnIndex": -69789235,
                        "endRowIndex": -98601086,
                        "sheetId": 32219017,
                        "startColumnIndex": -61197874,
                        "startRowIndex": -91350843
                      }
                    },
                    {
                      "a1Range": "Ut cu",
                      "developerMetadataLookup": {
                        "locationMatchingStrategy": "INTERSECTING_LOCATION",
                        "locationType": "SHEET",
                        "metadataId": -32999997,
                        "metadataKey": "commodo sit esse consequat",
                        "metadataLocation": {
                          "dimensionRange": {
                            "dimension": "ROWS",
                            "endIndex": 1730530,
                            "sheetId": -56140506,
                            "startIndex": 82831554
                          },
                          "locationType": "SPREADSHEET",
                          "sheetId": 58086209,
                          "spreadsheet": false
                        },
                        "metadataValue": "in pariatur in Ut",
                        "visibility": "DEVELOPER_METADATA_VISIBILITY_UNSPECIFIED"
                      },
                      "gridRange": {
                        "endColumnIndex": 81731062,
                        "endRowIndex": 51216059,
                        "sheetId": -87090690,
                        "startColumnIndex": -26697783,
                        "startRowIndex": -36015480
                      }
                    }
                  ]
                }
                ```

        Returns:
            dict[str, Any]: Successful response

        Tags:
            Metadata
        """
        if spreadsheetId is None:
            raise ValueError("Missing required parameter 'spreadsheetId'")
        request_body = {
            'dataFilters': dataFilters,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/v4/spreadsheets/{spreadsheetId}/developerMetadata:search"
        query_params = {k: v for k, v in [('access_token', access_token), ('alt', alt), ('callback', callback), ('fields', fields), ('key', key), ('oauth_token', oauth_token), ('prettyPrint', prettyPrint), ('quotaUser', quotaUser), ('upload_protocol', upload_protocol), ('uploadType', uploadType), ('$.xgafv', xgafv)] if v is not None}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()
    
    
    def list_tools(self):
        """Returns a list of methods exposed as tools."""
        return [
            self.create_spreadsheet,
            self.get_spreadsheet,
            self.batch_get_values,
            self.clear_values,
            self.update_values,
            #Auto genearted tools from openapi spec
            self.get_values,
            self.batch_clear_values,
            self.batch_clear_values_by_data_filter,
            self.get_values_by_data_filter,  
            self.copy_to_sheet,
            self.get_developer_metadata,
            self.search_developer_metadata,
        ]
