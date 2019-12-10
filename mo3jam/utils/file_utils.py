import pyexcel as px

def get_records(data_file, file_type='xlsx'):
    records = px.get_records(file_type=file_type, file_content=data_file.read())
    return records

def get_spreadsheet(sheets, file_type='xlsx'):
    try:
        feedback_sheets = px.Book()
        feedback_sheets.load_from_sheets(
            sheets={key: px.get_sheet(records=value) for key, value in sheets.items()}
        ) 
        return getattr(feedback_sheets, file_type)
    except AttributeError:
        return feedback_sheets.xlsx
        
