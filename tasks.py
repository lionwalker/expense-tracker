from robocorp import browser
from robocorp.tasks import task
from datetime import datetime

from RPA.HTTP import HTTP
from artefacts.PDF import PDF

ARTEFACTS = "artefacts"
REMOTE_EXPENSES_FILE = "https://fspacheco.github.io/rpa-challenge/assets/list-expenses.txt"
LOCAL_EXPENSES_FILE = f"{ARTEFACTS}\latest-expenses.txt"
TRACKER_APP = "https://fspacheco.github.io/rpa-challenge/expense-tracker.html"
DEBUG_MODE=True

@task
def robot_expense_tracker():
    """
    Transfers the list of daily expense entries from a note-taking app to a website, then to a PDF file.
    """
    
    browser.configure(
        browser_engine="chromium", 
        screenshot="only-on-failure", 
        headless=False if DEBUG_MODE else True,
        slowmo=50
    )
    try:
        # Download latest expenses list
        download_file(url=REMOTE_EXPENSES_FILE, save_to=LOCAL_EXPENSES_FILE)
        
        # Read and get sanitized data
        data = read_text_file(LOCAL_EXPENSES_FILE)
        
        open_the_expense_tacking_website(TRACKER_APP)
        fill_form_with_list(data)
        
        # Make a PDF with custom made class
        export_as_pdf(data)
    except Exception as e:
        return f"Error: An unexpected error occurred."
    finally:
        print("Automation finished!")

def download_file(url, save_to):
    """
    Downloads a file from the given URL into a custom folder & name.

    Args:
        url: The target URL from which we'll download the file.
        save_to: The destination directory in which we'll place the file..
    """
    
    http = HTTP()
    http.download(url=url, target_file=save_to, overwrite=True)
    
def read_text_file(file_path):
    """
    Reads a text file and returns processed contents as a list.

    Args: 
        file_path: Path to the text file.
        
    Return:
        Processed data of the text file
    """
    
    data = []
    categories = {
        "Food": ["food", "pizza", "lunch", "dinner"],
        "Utilities": ["utilities", "util", "utilit"],
        "Entertainment": ["Entertainment", "entert"],
        "Shopping": ["shopping", "shop", "shoping"],
        "Transportation": ["transport", "trasport", "tranport"],
        "Other": ["other", "othr", "oter"]
    }
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file: 
            # Strip any leading/trailing whitespace and split by spaces 
            columns = line.strip().split()
            
            if (len(columns) != 4):
                raise Exception("Invalid data in the text file")
            
            # Convert date format
            columns[0] = convert_date_format(columns[0])
            
            # Convert amount to float values
            columns[2] = convert_amount_format(columns[2])
            
            # Correct spelling mistakes in the category names
            is_changed = 0
            for cat in categories:
                if columns[3] in categories[cat]:
                    columns[3] = cat
                    is_changed = 1
                    break            
            if is_changed == 0:
                columns[3] = "other"
            
            data.append(columns)

    return data

def convert_date_format(date):
    """
    Converts a date in dd/mm format to mm/dd/yyyy with the current year. 
    
    Args:
        date_str: Date string in dd/mm format. 
        
    Return: 
        Date string in mm/dd/yyyy format with the current year.
    """ 
    
    current_year = datetime.now().year 
    # Convert the input date string to a datetime object 
    date_obj = datetime.strptime(date, '%d/%m') 
    # Format the date to mm/dd/yyyy 
    formatted_date = date_obj.strftime(f'%m/%d/{current_year}') 
    
    return formatted_date

def convert_amount_format(value):
    """
    Change a string with a comma as a decimal separator to a dot.
    If the value is already a number, it converts it to a string.

    Args:
        value: Value to be converted.
        
    Return: 
        Converted float value or the original value if it's already a string.
    """
    
    if isinstance(value, str):
        # Replace comma with dot
        value = value.replace(',', '.')        
        return value
    elif isinstance(value, (int, float)):        
        # Return the value if it's already a number
        return str(value)
    else:
        raise Exception("The provided value is not a string or a number.")

def open_the_expense_tacking_website(url):
    """
    Navigates to the given URL
    
    Args: 
        url: URL of the website need to be opened.
    """
    
    browser.goto(url)
    
def fill_form_with_list(data):
    """
    Fill the expenses form
    
    Args:
        data: List of sanitized data 
    """
    
    for row in data:
        page = browser.page()

        type_date_manually(page, "#date", row[0])
        page.fill("#description", row[1])
        page.fill("#amount", row[2])
        page.select_option("#category", str(row[3]))
        page.click("text=Add Expense")
        
def type_date_manually(page, selector, date):
    """
    Types the date string manually into the input field. 
    
    Args:
        page: Playwright page object. 
        selector: Selector for the date input field. 
        date: Date string to be typed. 
    """ 
    
    page.click(selector) 
    for char in date:
        page.keyboard.press(char)
        
def export_as_pdf(data):
    """
    Creates a PDF with a table from a list of lists. 
    
    Args: 
        data: List of lists to be included in the PDF as a table. 
        output_file: Path to the output PDF file. 
    """ 
    
    pdf = PDF(data)
    pdf.generate()