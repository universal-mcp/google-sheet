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
        self.base_url = "https://sheets.googleapis.com/v4/spreadsheets"

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
        url = self.base_url
        spreadsheet_data = {"properties": {"title": title}}
        response = self._post(url, data=spreadsheet_data)
        return self._handle_response(response)

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
        url = f"{self.base_url}/{spreadsheet_id}"
        response = self._get(url)
        return self._handle_response(response)

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
        url = f"{self.base_url}/{spreadsheet_id}/values:batchGet"
        params = {}
        if ranges:
            params["ranges"] = ranges
        response = self._get(url, params=params)
        return self._handle_response(response)

    def insert_dimensions(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        dimension: str,
        start_index: int,
        end_index: int,
        inherit_from_before: bool = True,
    ) -> dict[str, Any]:
        """
        Inserts new rows or columns into a Google Sheet at a specific position within the sheet.

        This function inserts empty rows or columns at a specified location, shifting existing content.
        Use this when you need to add rows/columns in the middle of your data.

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to modify
            sheet_id: The ID of the sheet within the spreadsheet (0 for first sheet)
            dimension: The type of dimension to insert - "ROWS" or "COLUMNS"
            start_index: The 0-based starting index where insertion should begin
            end_index: The 0-based ending index (exclusive). Number of rows/columns inserted = end_index - start_index
            inherit_from_before: Whether the new dimensions should inherit properties from the dimensions before the insertion point. Defaults to True

        Returns:
            A dictionary containing the Google Sheets API response with update details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty or dimension is not "ROWS" or "COLUMNS"

        Tags:
            insert, modify, spreadsheet, rows, columns, dimensions, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if dimension not in ["ROWS", "COLUMNS"]:
            raise ValueError('dimension must be either "ROWS" or "COLUMNS"')
        
        if start_index < 0 or end_index < 0:
            raise ValueError("start_index and end_index must be non-negative")
        
        if start_index >= end_index:
            raise ValueError("end_index must be greater than start_index")
        
        url = f"{self.base_url}/{spreadsheet_id}:batchUpdate"
        
        request_body = {
            "requests": [
                {
                    "insertDimension": {
                        "inheritFromBefore": inherit_from_before,
                        "range": {
                            "dimension": dimension,
                            "sheetId": sheet_id,
                            "startIndex": start_index,
                            "endIndex": end_index,
                        }
                    }
                }
            ]
        }
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)

    def append_dimensions(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        dimension: str,
        length: int,
    ) -> dict[str, Any]:
        """
        Appends empty rows or columns to the end of a Google Sheet.

        This function adds empty rows or columns to the end of the sheet without affecting existing content.
        Use this when you need to extend the sheet with additional space at the bottom or right.

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to modify
            sheet_id: The ID of the sheet within the spreadsheet (0 for first sheet)
            dimension: The type of dimension to append - "ROWS" or "COLUMNS"
            length: The number of rows or columns to append to the end

        Returns:
            A dictionary containing the Google Sheets API response with update details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty, dimension is not "ROWS" or "COLUMNS", or length is not positive

        Tags:
            append, modify, spreadsheet, rows, columns, dimensions, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if dimension not in ["ROWS", "COLUMNS"]:
            raise ValueError('dimension must be either "ROWS" or "COLUMNS"')
        
        if length <= 0:
            raise ValueError("length must be a positive integer")
        
        url = f"{self.base_url}/{spreadsheet_id}:batchUpdate"
        
        request_body = {
            "requests": [
                {
                    "appendDimension": {
                        "sheetId": sheet_id,
                        "dimension": dimension,
                        "length": length
                    }
                }
            ]
        }
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)

    def delete_dimensions(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        dimension: str,
        start_index: int,
        end_index: int,
    ) -> dict[str, Any]:
        """
        Deletes rows or columns from a Google Sheet.

        This function removes the specified rows or columns from the sheet, shifting remaining content up or left.
        Use this when you need to remove unwanted rows or columns from your data.

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to modify
            sheet_id: The ID of the sheet within the spreadsheet (0 for first sheet)
            dimension: The type of dimension to delete - "ROWS" or "COLUMNS"
            start_index: The 0-based starting index of the range to delete (inclusive)
            end_index: The 0-based ending index of the range to delete (exclusive). Number of rows/columns deleted = end_index - start_index

        Returns:
            A dictionary containing the Google Sheets API response with update details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty, dimension is not "ROWS" or "COLUMNS", or indices are invalid

        Tags:
            delete, modify, spreadsheet, rows, columns, dimensions, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if dimension not in ["ROWS", "COLUMNS"]:
            raise ValueError('dimension must be either "ROWS" or "COLUMNS"')
        
        if start_index < 0 or end_index < 0:
            raise ValueError("start_index and end_index must be non-negative")
        
        if start_index >= end_index:
            raise ValueError("end_index must be greater than start_index")
        
        url = f"{self.base_url}/{spreadsheet_id}:batchUpdate"
        
        request_body = {
            "requests": [
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": dimension,
                            "startIndex": start_index,
                            "endIndex": end_index,
                        }
                    }
                }
            ]
        }
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)

    def add_sheet(
        self,
        spreadsheet_id: str,
        title: str = None,
        sheet_id: int = None,
        index: int = None,
    ) -> dict[str, Any]:
        """
        Adds a new sheet to an existing Google Spreadsheet.

        This function creates a new sheet within the specified spreadsheet with optional properties.
        Use this when you need to add additional sheets to organize your data.

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to modify
            title: Optional title for the new sheet. If not provided, a default title will be generated
            sheet_id: Optional custom sheet ID. If not provided, Google Sheets will assign one automatically
            index: Optional position where the new sheet should be inserted (0-based). If not provided, the sheet will be added at the end

        Returns:
            A dictionary containing the Google Sheets API response with the new sheet details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty

        Tags:
            add, sheet, spreadsheet, create, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        url = f"{self.base_url}/{spreadsheet_id}:batchUpdate"
        
        # Build the addSheet request with properties
        add_sheet_request = {
            "properties": {}
        }
        
        if title is not None:
            add_sheet_request["properties"]["title"] = title
        
        if sheet_id is not None:
            add_sheet_request["properties"]["sheetId"] = sheet_id
        
        if index is not None:
            add_sheet_request["properties"]["index"] = index
        
        request_body = {
            "requests": [
                {
                    "addSheet": add_sheet_request
                }
            ]
        }
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)

    def add_column_chart(
        self,
        spreadsheet_id: str,
        source_sheet_id: int,
        chart_title: str,
        domain_range: dict,
        series_ranges: list[dict],
        new_sheet: bool = True,
    ) -> dict[str, Any]:
        """
        Adds a column chart to a Google Spreadsheet.

        This function creates a column chart from the specified data ranges and places it in a new sheet or existing sheet.
        Use this when you need to visualize data in a column chart format.

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to modify
            source_sheet_id: The ID of the sheet containing the source data
            chart_title: The title for the chart
            domain_range: Dictionary containing domain range info (e.g., {"startRowIndex": 0, "endRowIndex": 7, "startColumnIndex": 0, "endColumnIndex": 1})
            series_ranges: List of dictionaries containing series range info for each data series
            new_sheet: Whether to create the chart in a new sheet (True) or existing sheet (False)

        Returns:
            A dictionary containing the Google Sheets API response with the chart details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty or invalid parameters are provided

        Tags:
            add, chart, column, visualization, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if not chart_title:
            raise ValueError("chart_title cannot be empty")
        
        url = f"{self.base_url}/{spreadsheet_id}:batchUpdate"
        
        # Build the chart specification
        chart_spec = {
            "title": chart_title,
            "basicChart": {
                "chartType": "COLUMN",
                "legendPosition": "BOTTOM_LEGEND",
                "axis": [
                    {
                        "position": "BOTTOM_AXIS",
                        "title": "Categories"
                    },
                    {
                        "position": "LEFT_AXIS",
                        "title": "Values"
                    }
                ],
                "domains": [
                    {
                        "domain": {
                            "sourceRange": {
                                "sources": [
                                    {
                                        "sheetId": source_sheet_id,
                                        "startRowIndex": domain_range.get("startRowIndex", 0),
                                        "endRowIndex": domain_range.get("endRowIndex", 1),
                                        "startColumnIndex": domain_range.get("startColumnIndex", 0),
                                        "endColumnIndex": domain_range.get("endColumnIndex", 1)
                                    }
                                ]
                            }
                        }
                    }
                ],
                "series": [],
                "headerCount": 1
            }
        }
        
        # Add series data
        for series_range in series_ranges:
            series = {
                "series": {
                    "sourceRange": {
                        "sources": [
                            {
                                "sheetId": source_sheet_id,
                                "startRowIndex": series_range.get("startRowIndex", 0),
                                "endRowIndex": series_range.get("endRowIndex", 1),
                                "startColumnIndex": series_range.get("startColumnIndex", 0),
                                "endColumnIndex": series_range.get("endColumnIndex", 1)
                            }
                        ]
                    }
                },
                "targetAxis": "LEFT_AXIS"
            }
            chart_spec["basicChart"]["series"].append(series)
        
        # Build the request body
        request_body = {
            "requests": [
                {
                    "addChart": {
                        "chart": {
                            "spec": chart_spec,
                            "position": {
                                "newSheet": new_sheet
                            }
                        }
                    }
                }
            ]
        }
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)

    def add_table(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        table_name: str,
        table_id: str,
        start_row_index: int,
        end_row_index: int,
        start_column_index: int,
        end_column_index: int,
        column_properties: list[dict] = None,
    ) -> dict[str, Any]:
        """
        Adds a table to a Google Spreadsheet.

        This function creates a table with specified properties and column types.
        Use this when you need to create structured data with headers, footers, and column types.

        Args:
            spreadsheet_id: The unique identifier of the Google Spreadsheet to modify
            sheet_id: The ID of the sheet where the table will be created
            table_name: The name of the table
            table_id: The unique identifier for the table
            start_row_index: The starting row index (0-based)
            end_row_index: The ending row index (exclusive)
            start_column_index: The starting column index (0-based)
            end_column_index: The ending column index (exclusive)
            column_properties: Optional list of column properties with types and validation rules.
                Example: [
                    {"columnIndex": 0, "columnName": "Model Number", "columnType": "TEXT"},
                    {"columnIndex": 1, "columnName": "Sales - Jan", "columnType": "NUMBER"},
                    {"columnIndex": 2, "columnName": "Progress", "columnType": "PERCENT"},
                    {"columnIndex": 3, "columnName": "Status", "columnType": "DROPDOWN", "dataValidationRule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": "Active"}, {"userEnteredValue": "Inactive"}]}}},
                    {"columnIndex": 4, "columnName": "Active", "columnType": "CHECKBOX"}
                ]

        Returns:
            A dictionary containing the Google Sheets API response with the table details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty or invalid parameters are provided

        Tags:
            add, table, structured-data, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if not table_name:
            raise ValueError("table_name cannot be empty")
        
        if not table_id:
            raise ValueError("table_id cannot be empty")
        
        if start_row_index < 0 or end_row_index < 0 or start_column_index < 0 or end_column_index < 0:
            raise ValueError("All indices must be non-negative")
        
        if start_row_index >= end_row_index:
            raise ValueError("end_row_index must be greater than start_row_index")
        
        if start_column_index >= end_column_index:
            raise ValueError("end_column_index must be greater than start_column_index")
        
        url = f"{self.base_url}/{spreadsheet_id}:batchUpdate"
        
        # Build the table specification
        table_spec = {
            "name": table_name,
            "tableId": table_id,
            "range": {
                "sheetId": sheet_id,
                "startColumnIndex": start_column_index,
                "endColumnIndex": end_column_index,
                "startRowIndex": start_row_index,
                "endRowIndex": end_row_index,
            }
        }
        
        # Add column properties if provided
        if column_properties:
            table_spec["columnProperties"] = column_properties
        
        # Build the request body
        request_body = {
            "requests": [
                {
                    "addTable": {
                        "table": table_spec
                    }
                }
            ]
        }
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)


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
        url = f"{self.base_url}/{spreadsheet_id}/values/{range}:clear"
        response = self._post(url, data={})
        return self._handle_response(response)

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
        url = f"{self.base_url}/{spreadsheet_id}/values/{range}"
        params = {"valueInputOption": value_input_option}
        data = {"range": range, "values": values}
        response = self._put(url, data=data, params=params)
        return self._handle_response(response)

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
        url = f"{self.base_url}/{spreadsheetId}/values/{range}"
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
        url = f"{self.base_url}/{spreadsheetId}/values:batchClear"
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
        url = f"{self.base_url}/{spreadsheetId}/values:batchClearByDataFilter"
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
        url = f"{self.base_url}/{spreadsheetId}/values:batchGetByDataFilter"
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
        url = f"{self.base_url}/{spreadsheetId}/sheets/{{sheetId}}:copyTo"
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
            self.insert_dimensions,
            self.append_dimensions,
            self.delete_dimensions,
            self.add_sheet,
            self.add_column_chart,
            self.add_table,
            self.clear_values,
            self.update_values,
            #Auto genearted tools from openapi spec
            self.get_values,
            self.batch_clear_values,
            self.batch_clear_values_by_data_filter,
            self.get_values_by_data_filter,  
            self.copy_to_sheet,
        ]
