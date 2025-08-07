from typing import Any

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration
from universal_mcp_google_sheet.helper import analyze_sheet_for_tables, analyze_table_schema


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
        Retrieves detailed information about a specific Google Spreadsheet using its ID  excluding cell data.

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

    def get_values(
        self, 
        spreadsheetId: str, 
        range: str,
        majorDimension: str = None,
        valueRenderOption: str = None,
        dateTimeRenderOption: str = None
    ) -> dict[str, Any]:
        """
        Retrieves values from a specific range in a Google Spreadsheet.

        Args:
            spreadsheetId: The unique identifier of the Google Spreadsheet to retrieve values from
            range: A1 notation range string (e.g., 'Sheet1!A1:B2')
            majorDimension: The major dimension that results should use. "ROWS" or "COLUMNS". Example: "ROWS"
            valueRenderOption: How values should be represented in the output. "FORMATTED_VALUE", "UNFORMATTED_VALUE", or "FORMULA". Example: "FORMATTED_VALUE"
            dateTimeRenderOption: How dates, times, and durations should be represented. "SERIAL_NUMBER" or "FORMATTED_STRING". Example: "FORMATTED_STRING"

        Returns:
            A dictionary containing the API response with the requested spreadsheet values and metadata

        Raises:
            HTTPError: If the API request fails due to invalid spreadsheet_id, insufficient permissions, or invalid range format
            ValueError: If the spreadsheet_id is empty or invalid

        Tags:
            get, read, spreadsheet, values, important
        """
        url = f"{self.base_url}/{spreadsheetId}/values/{range}"
        params = {}
        
        if majorDimension:
            params["majorDimension"] = majorDimension
        if valueRenderOption:
            params["valueRenderOption"] = valueRenderOption
        if dateTimeRenderOption:
            params["dateTimeRenderOption"] = dateTimeRenderOption
        
        response = self._get(url, params=params)
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
        include_spreadsheet_in_response: bool = None,
        response_include_grid_data: bool = None,
        response_ranges: list[str] = None,
    ) -> dict[str, Any]:
        """
        Inserts new rows or columns into a Google Sheet at a specific position within the sheet.

        This function inserts empty rows or columns at a specified location, shifting existing content.
        Use this when you need to add rows/columns in the middle of your data.

        Args:
            spreadsheet_id: The ID of the spreadsheet to update. Example: "abc123spreadsheetId"
            sheet_id: The ID of the sheet where the dimensions will be inserted. Example: 0
            dimension: The dimension to insert. Valid values are "ROWS" or "COLUMNS". Example: "ROWS"
            start_index: The start index (0-based) of the dimension range to insert. The inserted dimensions will be placed before this index. Example: 1
            end_index: The end index (0-based, exclusive) of the dimension range to insert. The number of rows/columns to insert is `endIndex - startIndex`. Example: 3
            inherit_from_before: If true, the new dimensions will inherit properties from the dimension before the startIndex. If false (default), they will inherit from the dimension at the startIndex. startIndex must be greater than 0 if inheritFromBefore is true. Example: True
            include_spreadsheet_in_response: True if the updated spreadsheet should be included in the response. Example: True
            response_include_grid_data: True if grid data should be included in the response (if includeSpreadsheetInResponse is true). Example: True
            response_ranges: Limits the ranges of the spreadsheet to include in the response. Example: ["Sheet1!A1:B10"]

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
        
        # Add optional parameters if provided
        if include_spreadsheet_in_response is not None:
            request_body["includeSpreadsheetInResponse"] = include_spreadsheet_in_response
        
        if response_include_grid_data is not None:
            request_body["responseIncludeGridData"] = response_include_grid_data
        
        if response_ranges is not None:
            request_body["responseRanges"] = response_ranges
        
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
        include_spreadsheet_in_response: bool = None,
        response_include_grid_data: bool = None,
        response_ranges: list[str] = None,
    ) -> dict[str, Any]:
        """
        Tool to delete specified rows or columns from a sheet in a google spreadsheet. use when you need to remove a range of rows or columns.
        or Use this when you need to remove unwanted rows or columns from your data.

        Args:
            spreadsheet_id: The ID of the spreadsheet. Example: "abc123xyz789"
            sheet_id: The ID of the sheet from which to delete the dimension. Example: 0 for first sheet
            dimension: The dimension to delete. Example: "ROWS"
            start_index: The zero-based start index of the range to delete, inclusive. The start index must be less than the end index. Example: 0
            end_index: The zero-based end index of the range to delete, exclusive. The end index must be greater than the start index. Example: 1
            include_spreadsheet_in_response: Determines if the update response should include the spreadsheet resource. Example: True
            response_include_grid_data: True if grid data should be returned. This parameter is ignored if a field mask was set in the request. Example: True
            response_ranges: Limits the ranges of cells included in the response spreadsheet. Example: ["Sheet1!A1:B2", "Sheet2!C:C"]

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
        
        # Add optional response parameters if provided
        if include_spreadsheet_in_response is not None:
            request_body["includeSpreadsheetInResponse"] = include_spreadsheet_in_response
        
        if response_include_grid_data is not None:
            request_body["responseIncludeGridData"] = response_include_grid_data
        
        if response_ranges is not None:
            request_body["responseRanges"] = response_ranges
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)

    def add_sheet(
        self,
        spreadsheetId: str,
        title: str = None,
        sheetId: int = None,
        index: int = None,
        sheetType: str = "GRID",
        hidden: bool = None,
        rightToLeft: bool = None,
        tabColorStyle: dict = None,
        # Grid properties
        rowCount: int = None,
        columnCount: int = None,
        frozenRowCount: int = None,
        frozenColumnCount: int = None,
        hideGridlines: bool = None,
        rowGroupControlAfter: bool = None,
        columnGroupControlAfter: bool = None,
        # Response options
        includeSpreadsheetInResponse: bool = False,
        responseIncludeGridData: bool = False,
    ) -> dict[str, Any]:
        """
        Adds a new sheet (worksheet) to a spreadsheet. use this tool to create a new tab within an existing google sheet, optionally specifying its title, index, size, and other properties.

        Args:
            spreadsheetId: The ID of the spreadsheet to add the sheet to. This is the long string of characters in the URL of your Google Sheet. Example: "abc123xyz789"
            title: The name of the sheet. Example: "Q3 Report"
            sheetId: The ID of the sheet. If not set, an ID will be randomly generated. Must be non-negative if set.
            index: The zero-based index of the sheet in the spreadsheet. Example: 0 for the first sheet.
            sheetType: The type of sheet. Options: "GRID", "OBJECT", "DATA_SOURCE". Defaults to "GRID"
            hidden: True if the sheet is hidden in the UI, false if it's visible.
            rightToLeft: True if the sheet is an RTL sheet, false if it's LTR.
            tabColorStyle: The color of the sheet tab. Can contain either 'rgbColor' (with red, green, blue, alpha values 0-1) or 'themeColor' (TEXT, BACKGROUND, ACCENT1-6, LINK).
            rowCount: The number of rows in the sheet.
            columnCount: The number of columns in the sheet.
            frozenRowCount: The number of rows that are frozen in the sheet.
            frozenColumnCount: The number of columns that are frozen in the sheet.
            hideGridlines: True if the gridlines are hidden, false if they are shown.
            rowGroupControlAfter: True if the row group control toggle is shown after the group, false if before.
            columnGroupControlAfter: True if the column group control toggle is shown after the group, false if before.
            includeSpreadsheetInResponse: Whether the response should include the entire spreadsheet resource. Defaults to false.
            responseIncludeGridData: True if grid data should be returned. This parameter is ignored if includeSpreadsheetInResponse is false. Defaults to false.

        Returns:
            A dictionary containing the Google Sheets API response with the new sheet details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty or invalid parameters are provided

        Tags:
            add, sheet, spreadsheet, create, important
        """
        if not spreadsheetId:
            raise ValueError("spreadsheetId cannot be empty")
        
        url = f"{self.base_url}/{spreadsheetId}:batchUpdate"
        
        # Build the addSheet request with properties
        add_sheet_request = {
            "properties": {}
        }
        
        if title is not None:
            add_sheet_request["properties"]["title"] = title
        
        if sheetId is not None:
            add_sheet_request["properties"]["sheetId"] = sheetId
        
        if index is not None:
            add_sheet_request["properties"]["index"] = index
        
        if sheetType is not None:
            add_sheet_request["properties"]["sheetType"] = sheetType
        
        if hidden is not None:
            add_sheet_request["properties"]["hidden"] = hidden
        
        if rightToLeft is not None:
            add_sheet_request["properties"]["rightToLeft"] = rightToLeft
        
        if tabColorStyle is not None:
            add_sheet_request["properties"]["tabColorStyle"] = tabColorStyle
        
        # Build grid properties if any grid-related parameters are provided
        grid_properties = {}
        if any(param is not None for param in [rowCount, columnCount, frozenRowCount, frozenColumnCount, 
                                             hideGridlines, rowGroupControlAfter, columnGroupControlAfter]):
            
            if rowCount is not None:
                grid_properties["rowCount"] = rowCount
            
            if columnCount is not None:
                grid_properties["columnCount"] = columnCount
            
            if frozenRowCount is not None:
                grid_properties["frozenRowCount"] = frozenRowCount
            
            if frozenColumnCount is not None:
                grid_properties["frozenColumnCount"] = frozenColumnCount
            
            if hideGridlines is not None:
                grid_properties["hideGridlines"] = hideGridlines
            
            if rowGroupControlAfter is not None:
                grid_properties["rowGroupControlAfter"] = rowGroupControlAfter
            
            if columnGroupControlAfter is not None:
                grid_properties["columnGroupControlAfter"] = columnGroupControlAfter
            
            add_sheet_request["properties"]["gridProperties"] = grid_properties
        
        request_body = {
            "requests": [
                {
                    "addSheet": add_sheet_request
                }
            ],
            "includeSpreadsheetInResponse": includeSpreadsheetInResponse,
            "responseIncludeGridData": responseIncludeGridData
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

    def get_values_by_data_filter(
        self,
        spreadsheet_id: str,
        data_filters: list[dict],
        include_grid_data: bool = None,
        exclude_tables_in_banded_ranges: bool = None,
    ) -> dict[str, Any]:
        """
        Returns the spreadsheet at the given id, filtered by the specified data filters. use this tool when you need to retrieve specific subsets of data from a google sheet based on criteria like a1 notation, developer metadata, or grid ranges.

        Args:
            spreadsheet_id: The ID of the spreadsheet to request. Example: "abc123xyz789"
            data_filters: The DataFilters used to select which ranges to retrieve. Each filter can contain:
                - a1Range: Selects data that matches the specified A1 range. Example: "Sheet1!A1:B2"
                - gridRange: Selects data that matches the range described by the GridRange with:
                    - sheetId: The ID of the sheet this range is on. Example: 0
                    - startRowIndex: The start row (0-based, inclusive) of the range. Example: 0
                    - endRowIndex: The end row (0-based, exclusive) of the range. Example: 10
                    - startColumnIndex: The start column (0-based, inclusive) of the range. Example: 0
                    - endColumnIndex: The end column (0-based, exclusive) of the range. Example: 5
                - developerMetadataLookup: Selects data associated with developer metadata with:
                    - locationType: Limits metadata to specific location types (ROW, COLUMN, SHEET, SPREADSHEET, OBJECT). Example: "ROW"
                    - metadataLocation: Limits metadata to specific locations with exact or intersecting matching
                    - locationMatchingStrategy: Determines location matching (EXACT_LOCATION, INTERSECTING_LOCATION). Example: "INTERSECTING_LOCATION"
                    - metadataId: Filter by metadata ID. Example: 123
                    - metadataKey: Filter by metadata key. Example: "project_id"
                    - metadataValue: Filter by metadata value. Example: "alpha"
                    - visibility: Metadata visibility (DOCUMENT, PROJECT). Example: "DOCUMENT"

                Example:
                
                Filter by GridRange:-
                 {
                   "dataFilters": [
                     {
                       "gridRange": {
                         "sheetId": 0,  # Assuming your sheet ID is 0 (the first sheet)
                         "startRowIndex": 0,
                         "endRowIndex": 10,
                         "startColumnIndex": 0,
                         "endColumnIndex": 2
                       }
                     }
                   ]
                 }

                Filter by A1Range:-
                {
                  "dataFilters": [
                    {
                      "a1Range": "Sheet1!A1:B10"  # Filters for data within cells A1 to B10 on "Sheet1".
                    }
                  ]
                }

                Filter by Developer Metadata:-
                {
                  "dataFilters": [
                    {
                      "developerMetadataLookup": {
                        "locationType": "ROW",
                        "locationMatchingStrategy": "INTERSECTING_LOCATION",
                        "metadataKey": "project_id",
                        "metadataValue": "alpha",
                        "visibility": "DOCUMENT"
                      }
                    }
                  ]
                }

                Filter by Multiple Criteria:-
                {
                  "dataFilters": [
                    {
                      "a1Range": "Sheet1!A1:B10"
                    },
                    {
                      "developerMetadataLookup": {
                        "metadataKey": "productId",
                        "metadataValue": "XYZ123",
                        "visibility": "DOCUMENT"
                      }
                    }
                  ]
                }
                

            include_grid_data: True if grid data should be returned. Ignored if a field mask is set. Example: True
            exclude_tables_in_banded_ranges: True if tables should be excluded in the banded ranges. False if not set. Example: False
                
                
        


        Returns:
            A dictionary containing the filtered spreadsheet data based on the specified criteria

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty or data_filters is empty

        Tags:
            get, filter, spreadsheet, data-filter, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if not data_filters or not isinstance(data_filters, list) or len(data_filters) == 0:
            raise ValueError("data_filters must be a non-empty list")
        
        url = f"{self.base_url}/{spreadsheet_id}:getByDataFilter"
        
        request_body = {
            "dataFilters": data_filters
        }
        
        # Add optional parameters if provided
        if include_grid_data is not None:
            request_body["includeGridData"] = include_grid_data
        
        if exclude_tables_in_banded_ranges is not None:
            request_body["excludeTablesInBandedRanges"] = exclude_tables_in_banded_ranges
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)

    def copy_to_sheet(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        destination_spreadsheet_id: str,
    ) -> dict[str, Any]:
        """
        Tool to copy a single sheet from a spreadsheet to another spreadsheet. Use when you need to duplicate a sheet into a different spreadsheet.
        

        Args:
            spreadsheet_id: The ID of the spreadsheet containing the sheet to copy. Example: "1qZ_..."
            sheet_id: The ID of the sheet to copy. Example: 0
            destination_spreadsheet_id: The ID of the spreadsheet to copy the sheet to. Example: "2rY_..."

        Returns:
            A dictionary containing the Google Sheets API response with copy details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When any required parameter is empty or invalid

        Tags:
            copy, sheet, spreadsheet, duplicate, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if sheet_id is None:
            raise ValueError("sheet_id cannot be empty")
        
        if not destination_spreadsheet_id:
            raise ValueError("destination_spreadsheet_id cannot be empty")
        
        url = f"{self.base_url}/{spreadsheet_id}/sheets/{sheet_id}:copyTo"
        
        request_body = {
            "destinationSpreadsheetId": destination_spreadsheet_id
        }
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)
    
    def batch_update(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        values: list[list[Any]],
        first_cell_location: str = None,
        value_input_option: str = "USER_ENTERED",
        include_values_in_response: bool = False,
    ) -> dict[str, Any]:
        """
        Updates a specified range in a google sheet with given values, or appends them as new rows if `first cell location` is omitted; ensure the target sheet exists and the spreadsheet contains at least one worksheet.

        Args:
            spreadsheet_id: The unique identifier of the Google Sheets spreadsheet to be updated. Example: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            sheet_name: The name of the specific sheet within the spreadsheet to update. Example: "Sheet1"
            values: A 2D list of cell values. Each inner list represents a row. Values can be strings, numbers, or booleans. Ensure columns are properly aligned across rows. Example: [['Item', 'Cost', 'Stocked', 'Ship Date'], ['Wheel', 20.5, True, '2020-06-01'], ['Screw', 0.5, True, '2020-06-03'], ['Nut', 0.25, False, '2020-06-02']]
            first_cell_location: The starting cell for the update range, specified in A1 notation (e.g., 'A1', 'B2'). The update will extend from this cell to the right and down, based on the provided values. If omitted, values are appended to the sheet. Example: "A1"
            value_input_option: How input data is interpreted. 'USER_ENTERED': Values parsed as if typed by a user (e.g., strings may become numbers/dates, formulas are calculated); recommended for formulas. 'RAW': Values stored as-is without parsing (e.g., '123' stays string, '=SUM(A1:B1)' stays string). Defaults to 'USER_ENTERED'. Example: "USER_ENTERED"
            include_values_in_response: If set to True, the response will include the updated values from the spreadsheet. Defaults to False. Example: True

        Returns:
            A dictionary containing the Google Sheets API response with update details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty, sheet_name is empty, or values is empty

        Tags:
            batch, update, write, sheets, api, important, data-modification, google-sheets
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if not sheet_name:
            raise ValueError("sheet_name cannot be empty")
        
        if not values or not isinstance(values, list) or len(values) == 0:
            raise ValueError("values must be a non-empty 2D list")
        
        if value_input_option not in ["RAW", "USER_ENTERED"]:
            raise ValueError('value_input_option must be either "RAW" or "USER_ENTERED"')
        
        # Determine the range based on first_cell_location
        if first_cell_location:
            # Update specific range starting from first_cell_location
            range_str = f"{sheet_name}!{first_cell_location}"
        else:
            # Append to the sheet (no specific range)
            range_str = f"{sheet_name}"
        
        url = f"{self.base_url}/{spreadsheet_id}/values/{range_str}"
        
        params = {
            "valueInputOption": value_input_option,
            "includeValuesInResponse": include_values_in_response
        }
        
        data = {"values": values}
        
        response = self._put(url, data=data, params=params)
        return self._handle_response(response)

    def clear_basic_filter(
        self,
        spreadsheet_id: str,
        sheet_id: int,
    ) -> dict[str, Any]:
        """
        Tool to clear the basic filter from a sheet. use when you need to remove an existing basic filter from a specific sheet within a google spreadsheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet. Example: "abc123xyz789"
            sheet_id: The ID of the sheet on which the basic filter should be cleared. Example: 0

        Returns:
            A dictionary containing the Google Sheets API response with update details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty or sheet_id is negative

        Tags:
            clear, filter, basic-filter, spreadsheet, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if sheet_id < 0:
            raise ValueError("sheet_id must be non-negative")
        
        url = f"{self.base_url}/{spreadsheet_id}:batchUpdate"
        
        request_body = {
            "requests": [
                {
                    "clearBasicFilter": {
                        "sheetId": sheet_id
                    }
                }
            ]
        }
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)

    def delete_sheet(
        self,
        spreadsheet_id: str,
        sheet_id: int,
    ) -> dict[str, Any]:
        """
        Tool to delete a sheet (worksheet) from a spreadsheet. use when you need to remove a specific sheet from a google sheet document.

        Args:
            spreadsheet_id: The ID of the spreadsheet from which to delete the sheet. Example: "abc123xyz789"
            sheet_id: The ID of the sheet to delete. If the sheet is of DATA_SOURCE type, the associated DataSource is also deleted. Example: 123456789

        Returns:
            A dictionary containing the Google Sheets API response with update details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty or sheet_id is negative

        Tags:
            delete, sheet, spreadsheet, worksheet, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if sheet_id < 0:
            raise ValueError("sheet_id must be non-negative")
        
        url = f"{self.base_url}/{spreadsheet_id}:batchUpdate"
        
        request_body = {
            "requests": [
                {
                    "deleteSheet": {
                        "sheetId": sheet_id
                    }
                }
            ]
        }
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)

    def list_tables(
        self,
        spreadsheet_id: str,
        min_rows: int = 2,
        min_columns: int = 1,
        min_confidence: float = 0.5,
    ) -> dict[str, Any]:
        """
        This action is used to list all tables in a google spreadsheet, call this action to get the list of tables in a spreadsheet. discover all tables in a google spreadsheet by analyzing sheet structure and detecting data patterns. uses heuristic analysis to find header rows, data boundaries, and table structures.

        Args:
            spreadsheet_id: Google Sheets ID from the URL (e.g., '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'). Example: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            min_rows: Minimum number of data rows to consider a valid table. Example: 2
            min_columns: Minimum number of columns to consider a valid table. Example: 1
            min_confidence: Minimum confidence score (0.0-1.0) to consider a valid table. Example: 0.5

        Returns:
            A dictionary containing the list of discovered tables with their properties

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty or parameters are invalid

        Tags:
            list, tables, discover, analyze, spreadsheet, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if min_rows < 1:
            raise ValueError("min_rows must be at least 1")
        
        if min_columns < 1:
            raise ValueError("min_columns must be at least 1")
        
        if not 0 <= min_confidence <= 1:
            raise ValueError("min_confidence must be between 0.0 and 1.0")
        
        # Get spreadsheet structure
        spreadsheet = self.get_spreadsheet(spreadsheet_id)
        
        tables = []
        
        for sheet in spreadsheet.get("sheets", []):
            sheet_properties = sheet.get("properties", {})
            sheet_id = sheet_properties.get("sheetId")
            sheet_title = sheet_properties.get("title", "Sheet1")
            
            # Analyze sheet for tables using helper function
            sheet_tables = analyze_sheet_for_tables(
                self.get_values,  # Pass the get_values method as a function
                spreadsheet_id, 
                sheet_id, 
                sheet_title, 
                min_rows, 
                min_columns, 
                min_confidence
            )
            
            tables.extend(sheet_tables)
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "total_tables": len(tables),
            "tables": tables,
            "analysis_parameters": {
                "min_rows": min_rows,
                "min_columns": min_columns,
            }
        }
    
    def get_table_schema(
        self,
        spreadsheet_id: str,
        table_name: str,
        sheet_name: str = None,
        sample_size: int = 50,
    ) -> dict[str, Any]:
        """
        Analyzes table structure and infers column names, types, and constraints.
        Uses statistical analysis of sample data to determine the most likely data type for each column.
        Call this action after calling the list tables action to get the schema of a table in a spreadsheet.

        Args:
            spreadsheet_id: Google Sheets ID from the URL (e.g., '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms')
            table_name: Specific table name from LIST_TABLES response (e.g., 'Sales_Data', 'Employee_List'). Use 'auto' to analyze the largest/most prominent table
            sheet_name: Sheet/tab name if table_name is ambiguous across multiple sheets
            sample_size: Number of rows to sample for type inference (1-1000, default 50)

        Returns:
            A dictionary containing the table schema with column names, types, and constraints

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty, table_name is empty, or sample_size is invalid

        Tags:
            schema, analyze, table, structure, types, columns, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if not table_name:
            raise ValueError("table_name cannot be empty")
        
        if not 1 <= sample_size <= 1000:
            raise ValueError("sample_size must be between 1 and 1000")
        
        # Get spreadsheet structure
        spreadsheet = self.get_spreadsheet(spreadsheet_id)
        
        # Find the target table
        target_table = None
        
        for sheet in spreadsheet.get("sheets", []):
            sheet_properties = sheet.get("properties", {})
            sheet_title = sheet_properties.get("title", "Sheet1")
            
            # If sheet_name is specified, only look in that sheet
            if sheet_name and sheet_title != sheet_name:
                continue
            
            # Get tables in this sheet
            sheet_tables = analyze_sheet_for_tables(
                self.get_values,
                spreadsheet_id,
                sheet_properties.get("sheetId", 0),
                sheet_title,
                min_rows=2,
                min_columns=1,
                min_confidence=0.3
            )
            
            for table in sheet_tables:
                if table_name == "auto":
                    # For auto mode, select the largest table
                    if target_table is None or (table["rows"] * table["columns"] > target_table["rows"] * target_table["columns"]):
                        target_table = table
                elif table["table_name"] == table_name:
                    target_table = table
                    break
            
            if target_table and table_name != "auto":
                break
        
        if not target_table:
            raise ValueError(f"Table '{table_name}' not found in spreadsheet")
        
        # Use the helper function to analyze the table schema
        return analyze_table_schema(
            self.get_values,
            spreadsheet_id,
            target_table,
            sample_size
        )

    def set_basic_filter(
        self,
        spreadsheet_id: str,
        filter: dict,
    ) -> dict[str, Any]:
        """
        Tool to set a basic filter on a sheet in a google spreadsheet. use when you need to filter or sort data within a specific range on a sheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet. Example: "abc123xyz789"
            filter: The filter to set. This parameter is required. Contains:
                - range: The range the filter covers (required)
                    - sheetId: The sheet this range is on (required)
                    - startRowIndex: The start row (inclusive) of the range (optional)
                    - endRowIndex: The end row (exclusive) of the range (optional)
                    - startColumnIndex: The start column (inclusive) of the range (optional)
                    - endColumnIndex: The end column (exclusive) of the range (optional)
                - sortSpecs: The sort specifications for the filter (optional)
                    - dimensionIndex: The dimension the sort should be applied to
                    - sortOrder: The order data should be sorted ("ASCENDING", "DESCENDING", "SORT_ORDER_UNSPECIFIED")

        Returns:
            A dictionary containing the Google Sheets API response with filter details

        Raises:
            HTTPError: When the API request fails due to invalid parameters or insufficient permissions
            ValueError: When spreadsheet_id is empty or filter is missing required fields

        Tags:
            filter, basic-filter, spreadsheet, sort, important
        """
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id cannot be empty")
        
        if not filter:
            raise ValueError("filter cannot be empty")
        
        # Validate required filter fields
        if "range" not in filter:
            raise ValueError("filter must contain 'range' field")
        
        # Validate required filter fields using Google API naming convention
        range_data = filter["range"]
        if "sheetId" not in range_data:
            raise ValueError("filter range must contain 'sheetId' field")
        
        url = f"{self.base_url}/{spreadsheet_id}:batchUpdate"
        
        request_body = {
            "requests": [
                {
                    "setBasicFilter": {
                        "filter": filter
                    }
                }
            ]
        }
        
        response = self._post(url, data=request_body)
        return self._handle_response(response)


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
            self.delete_sheet,
            self.add_column_chart,
            self.add_table,
            self.clear_values,
            self.update_values,
            self.batch_update,
            self.clear_basic_filter,
            self.get_values_by_data_filter,  
            self.list_tables,
            self.get_values,
            self.get_table_schema,
            self.set_basic_filter,
            self.copy_to_sheet,


            # Auto generated tools from openapi spec
            self.batch_clear_values,
            self.batch_clear_values_by_data_filter,
            
        ]
