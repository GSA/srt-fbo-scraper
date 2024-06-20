import pytest
from fbo_scraper.util.ebuy_csv import grab_ebuy_csv, parse_csv, filter_out_no_attachments, rfq_relabeling, EBUY_DEFAULT_DIR, make_sql_statment, filter_out_no_naics
from selenium.webdriver import Edge, Safari, Firefox
from unittest.mock import Mock

from pathlib import Path
from unittest.mock import patch, mock_open

def test_grab_ebuy_csv():
    class Options:
        file = 'test.csv'
    options = Options()
    grab_ebuy_csv(options)
    assert options.file_path == Path(EBUY_DEFAULT_DIR, 'test.csv')

@patch("builtins.open", new_callable=mock_open, read_data="col1,col2\nval1,val2")
def test_parse_csv(mock_file):
    result = parse_csv('dummy_path')
    assert result == [{'col1': 'val1', 'col2': 'val2'}]

def test_filter_out_no_attachments():
    data = [
        {'Attachments': 'test', 'other_key': 'value'},
        {'Attachments': None, 'other_key': 'value'},
        {'Attachments': 'test', 'other_key': 'value', 'extra_key': 'extra_value'},
    ]
    result = filter_out_no_attachments(data)
    assert result == []

def test_filter_out_no_naics():
    data = [
        {'Category': '334111', 'Name': 'Product A'},
        {'Category': '67890', 'Name': 'Product B'},
        {'Category': 'ABCDE', 'Name': 'Product C'}
    ]
    # Assuming NAICS_CODES contains '12345' and '67890' but not 'ABCDE'
    expected = [
        {'Category': '334111', 'Name': 'Product A'},
    ]
    result = filter_out_no_naics(data)
    assert result == expected

def test_rfq_relabeling():
    data = [
        {'Attachments': 'link1\nlink2', 'AttachmentCount': 2, 'other_key': 'value'}
    ]
    result = rfq_relabeling(data)
    assert result[0]['resourceLinks'] == ['link1', 'link2']
    assert result[0]['numDocs'] == 2

def test_make_sql_statment():
    # Create a mock table object
    mock_table = Mock()
    mock_table.__table__ = Mock()
    mock_table.__tablename__ = 'test_table'
    mock_table.__table__.columns.keys.return_value = ['id', 'column1', 'column2']

    # Create a list of dictionaries to pass to the function
    row_values = [{'id': '1', 'column1': 'value1', 'column2': 'value2'}]

    # Call the function and get the returned SQL statement
    sql_statement = make_sql_statment(row_values, mock_table)

    # Check that the returned SQL statement is as expected
    expected_sql_statement = (
        'INSERT INTO test_table ("id", "column1", "column2") '
        'VALUES (\'1\', \'value1\', \'value2\') '
        'ON CONFLICT (id) DO UPDATE SET "id" = EXCLUDED."id", "column1" = EXCLUDED."column1", "column2" = EXCLUDED."column2";'
    )
    assert sql_statement == expected_sql_statement