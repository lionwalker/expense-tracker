import pdfkit

class PDF:
    
    OUTPUT_REPORT = "output\expenses-history-report.pdf"
    
    def __init__(self, data):
      self.data = data
      
    def generate(self):
        """
        Generate PDF file with given data
        """
        
        category_wise_spending = {} # To store category wise spendings
        merchant_wise_spending = {} # To store merchant wise spendings
        rows = ""
        for row in self.data:
            
            amount = float(row[2])
            if row[3] in category_wise_spending:
                category_wise_spending[row[3]] += amount
            else:
                category_wise_spending[row[3]] = amount
                
            if row[1] in merchant_wise_spending:
                merchant_wise_spending[row[1]] += amount
            else:
                merchant_wise_spending[row[1]] = amount
            
            rows += f"<tr><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{row[0]}</td>" \
                    f"<td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{row[1]}</td>" \
                    f"<td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{row[3]}</td>" \
                    f"<td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{amount}</td></tr>"
        
        most_spent_category = max(category_wise_spending, key=category_wise_spending.get)
        most_spent_merchant = max(merchant_wise_spending, key=merchant_wise_spending.get)
        rows += "<tr style='font-weight: 600;'>" \
                f"<td colspan='2' style='border: 1px solid #ddd; padding: 15px; text-align: left;'>Category with the highest expenses</td>" \
                f"<td colspan='2' style='border: 1px solid #ddd; padding: 15px; text-align: left;'>{most_spent_category} - {round(category_wise_spending[most_spent_category], 2)}</td>" \
                "</tr>" \
                "<tr style='font-weight: 600;'>" \
                f"<td colspan='2' style='border: 1px solid #ddd; padding: 15px; text-align: left;'>The shop/company where more money is spent</td>" \
                f"<td colspan='2' style='border: 1px solid #ddd; padding: 15px; text-align: left;'>{most_spent_merchant} - {round(merchant_wise_spending[most_spent_merchant], 2)}</td>" \
                "</tr>" \

        # Insert the rows into the template
        html_with_data = self.template().format(rows=rows)

        # Convert HTML to PDF
        pdfkit.from_string(html_with_data, self.OUTPUT_REPORT)
      
    def template(self):
        """
        Returns the HTML template
        """
        
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1 style="font-family: Calibri, sans-serif; text-align: left; margin-bottom: 20px;">Expenses History</h1>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px; font-family: Calibri, sans-serif;">
                <thead>
                    <tr>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: left; background-color: #f2f2f2;">Date</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: left; background-color: #f2f2f2;">Description</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: left; background-color: #f2f2f2;">Category</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: left; background-color: #f2f2f2;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </body>
        </html>
        """