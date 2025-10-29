from flask import Flask, render_template
from adk_agent import generate_report_data

# NOTE: Flask automatically looks for templates in a sub-folder named 'templates'.
app = Flask(__name__)

@app.route('/')
def dashboard():
    """
    The main route for the dashboard.
    1. Calls the ADK agent function to get the structured data.
    2. Renders the result using an HTML template.
    """
    
    # Call the agent to execute its full pipeline (data mock, tool call, text generation)
    report_data = generate_report_data()
    
    # Extract visualization data and format the Base64 string for direct HTML embedding
    viz = report_data.get('visualization')
    
    if viz and viz['encoding'] == 'base64' and viz['mime_type']:
        # Create the data URI for the HTML image tag: data:<mime_type>;base64,<data>
        image_src = f"data:{viz['mime_type']};base64,{viz['data']}"
    else:
        # Fallback image source if the agent fails to generate data
        image_src = None

    # Pass all relevant data to the template
    # Flask will look for index.html in /templates/index.html
    return render_template(
        'index.html',
        agent_status=report_data.get('status'),
        agent_text=report_data.get('text'),
        image_src=image_src
    )

if __name__ == '__main__':
    # Running this in a development environment.
    print("Starting Flask App...")
    app.run(debug=True)
