from robocorp import browser
from robocorp.tasks import task
from datetime import datetime

from RPA.HTTP import HTTP
from RPA.PDF import PDF

ARTEFACTS = "artefacts"
REMOTE_EXPENSES_FILE = "https://fspacheco.github.io/rpa-challenge/assets/list-expenses.txt"
LOCAL_EXPENSES_FILE = f"{ARTEFACTS}\latest-expenses.txt"
TRACKER_APP = "https://fspacheco.github.io/rpa-challenge/expense-tracker.html"
OUTPUT_REPORT = "expenses-report.pdf"
DEBUG_MODE=True

@task
def robot_expense_tracker():
    """
    Main task which solves the RPA challenge!

    Downloads the source data Excel file and uses Playwright to fill the entries inside
    rpachallenge.com.
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
        
        print(data)
    except Exception as e:
        return f"Error: An unexpected error occurred. {e}"
    finally:
        # A place for teardown and cleanups. (Playwright handles browser closing)
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
            
            # Format date
            columns[0] = f"{columns[0]}/{datetime.now().year}"
            
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

        page.fill("#description", row[1])
        page.fill("#amount", row[2])
        page.fill("#date", str(row[0]))
        page.select_option("#category", str(row[3]))
        page.click("text=Add Expense")
        
def export_as_pdf():
    """
    Export data to a PDF file
    
    Args:
        data: List of sanitized data
    """
    
    page = browser.page()
    expenses_history_html = page.locator("#expenses-list").inner_html()
    
    pdf = PDF()
    pdf.html_to_pdf(expenses_history_html, "output/expenses-history-report.pdf")