# Note: This code requires the google-adk library to be installed.
# You also need to be authenticated with Google Cloud to use the Vertex AI services.

import matplotlib.pyplot as plt
import io
import base64
import json
import numpy as np
import sqlite3
import datetime
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

# Set backend to Agg for non-interactive environments (necessary when running 
# in the background or from a server like Flask).
plt.switch_backend('Agg')

# --- Tool Definition: Image Graph Generator ---
def generate_plot_base64(data):
    """
    Generates a simple scatter plot from input data, saves it to an in-memory
    buffer, and returns the base64 encoded string of the PNG image.
    
    Args:
        data (list of dict): Data extracted from a source (e.g., BigQuery/SQL).
                             Expected format: [{'x': x_val, 'y': y_val}, ...]
                             
    Returns:
        str: Base64 encoded PNG image data, or None on error.
    """
    
    # 1. Parse data into X and Y lists
    try:
        x_values = [d['x'] for d in data]
        y_values = [d['y'] for d in data]
    except KeyError as e:
        print(f"Error parsing data: Missing key {e}")
        return None

    # 2. Create Plot using matplotlib
    fig, ax = plt.subplots(figsize=(8, 5)) # Slightly larger for web
    
    ax.scatter(x_values, y_values, color='#4A90E2', edgecolor='#1F548F', s=150, zorder=3, label="Data Points")
    
    # Add trend line for context
    if len(x_values) > 1:
        z = np.polyfit(x_values, y_values, 1)
        p = np.poly1d(z)
        ax.plot(x_values, p(x_values), "r--", alpha=0.7, label=f"Trend: Y = {z[0]:.2f}X + {z[1]:.2f}")
    
    ax.set_title("ADK Agent Visualization: Performance Metrics (X vs. Y)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Metric X (Input/Time)", fontsize=12)
    ax.set_ylabel("Metric Y (Output/Value)", fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.4, zorder=0)
    ax.legend()
    
    plt.tight_layout()

    # 3. Save plot to an in-memory buffer (BytesIO)
    buffer = io.BytesIO()
    # Save the plot as a PNG image to the buffer
    plt.savefig(buffer, format='png')
    plt.close(fig)  # Close the figure to free memory

    # 4. Encode the buffer content to base64
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    
    return image_base64

# --- ADK Agent Logic ---
class Database:
    """
    A class to represent an in-memory SQLite database. This is a placeholder for a
    real database holding the data to be plot. The data can be extracted running
    an SQL statement that filters the data for the plot. 
    """
    def __init__(self):
        """
        Initializes the database and populates it with mock data.
        """
        self.conn = sqlite3.connect(':memory:')
        self.populate_mock_data()

    def populate_mock_data(self):
        """
        Populates the mock data into the database.
        """
        cursor = self.conn.cursor()

        # Create table
        cursor.execute('''
            CREATE TABLE metrics (
                id INTEGER PRIMARY KEY,
                x INTEGER,
                y INTEGER
            )
        ''')

        # Insert data
        mock_data = [
            (1, 10),
            (2, 15),
            (3, 12),
            (4, 18),
            (5, 22),
            (6, 20),
            (7, 25),
        ]
        cursor.executemany('INSERT INTO metrics (x, y) VALUES (?, ?)', mock_data)
        self.conn.commit()

    def query(self, sql_query):
        """
        Queries the database and returns the results.
        """
        cursor = self.conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        return rows

    def close(self):
        """
        Closes the database connection.
        """
        self.conn.close()

def generate_report_data():
    """
    Simulates the main ADK agent logic: mock data retrieval, tool execution,
    and structured output generation. Returns the final structured data dictionary.
    """
    
    # --- Step 1: Initialize the Database and Tools ---
    db = Database()
    plot_tool_declaration = FunctionDeclaration(
        name="generate_plot_base64",
        description="Generates a plot from a list of dicts.",
        parameters={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "description": "A list of dictionaries representing the data to plot."
                }
            },
            "required": ["data"],
        }
    )
    plot_tool = Tool(function_declarations=[plot_tool_declaration])

    # --- Step 2: Define and Initialize the Model ---
    model_name = "gemini-2.0-flash-001"
    model = GenerativeModel(
        model_name,
        system_instruction=["You are an assistant that can generate plots from data, using the generate_plot_base64 tool."],
        tools=[plot_tool]
    )
    chat = model.start_chat()

    # --- Step 3: Define an SQL Query to retrieve the data to plot ---
    # For this mock, we'll just use a fixed query. In principle, this can be implemented
    # as another ADK agent that transforms natural language into SQL to extract the
    # relevant data. In this example, we use a static query.
    mock_sql_query = "SELECT x, y FROM metrics"
    print(f"Agent: Simulated LLM generated SQL query: {mock_sql_query}")

    # --- Step 4: Execute the Query and Retrieve Data ---
    rows = db.query(mock_sql_query)
    mock_query_result = [{'x': row[0], 'y': row[1]} for row in rows]
    db.close()

    # --- Step 5: Use the Model to Generate the Plot ---
    print(f"Agent: Calling visualization tool to generate graph of this data: {mock_query_result}")
    response = chat.send_message(
        f"Use the plotting tool to generate a plot of the following data: {mock_query_result}"
    )
    function_call = response.candidates[0].content.parts[0].function_call
    if function_call.name == 'generate_plot_base64':
        image_data_base64 = generate_plot_base64(function_call.args['data'])
    else:
        image_data_base64 = None

    if not image_data_base64:
        # Fallback if image generation fails
        final_output = {
            "status": "error",
            "text": "Could not generate graph due to tool execution failure."
        }
    else:
        # --- Step 6: Structured Output Generation ---

        # The following defines a text message to be displayed in the UI together with the plot.
        # Here it is generated as semistatic string. In a real agentic framework, it would be
        # generated as the output of some other agent.
         
        y_values = [d['y'] for d in mock_query_result]
        avg_y = sum(y_values) / len(y_values)
        
        analysis_text = (
            "The ADK Agent analyzed the mock performance data. It shows a generally positive correlation "
            "between Metric X (Input/Time) and Metric Y (Output/Value). "
            f"Metric Y's values are increasing, ranging from {min(y_values)} to {max(y_values)}, with an overall average of approximately {avg_y:.2f}. "
            "The embedded plot provides the definitive visual trend."
        )
        
        # The following statment combines the text message with the base64 encoded plot. 
        # The application will unpack the information and diplay both text and plot.
        final_output = {
            "status": "success",
            "text": analysis_text,
            "visualization": {
                "mime_type": "image/png",
                "encoding": "base64",
                "data": image_data_base64
            }
        }
        
    return final_output

if __name__ == "__main__":
    print("--- Running ADK Agent in Standalone Mode ---")
    report = generate_report_data()
    print("\n--- Agent Output ---")
    print(json.dumps(report, indent=2))
