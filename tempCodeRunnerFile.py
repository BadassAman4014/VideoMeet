from flask import Flask, render_template
import csv
import markdown

app = Flask(__name__)

# Route to render the HTML page
@app.route('/')
def display_data():
    # Read the CSV file
    data = []
    with open('data/transcriptions.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert the MarkdownSummary into HTML
            html_summary = markdown.markdown(row['MarkedownSummary'])
            
            # Append relevant columns to the data list
            data.append({
                'Username': row['Username'],
                'Date': row['Date'],
                'Time': row['Time'],
                'MarkdownSummary': html_summary
            })
    
    # Render the HTML page with the data
    return render_template('Report.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
