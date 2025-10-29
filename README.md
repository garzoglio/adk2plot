# adk2image

<!-- Badges -->
<p align="center">
  <a href="https://opensource.org/licenses/Apache-2.0">
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0">
  </a>
</p>

> An example of a generative AI agent that uses tools to create and display data visualizations.

This repository demonstrates the implementation of an agent built with the Google Agent Development Kit (ADK). The agent uses input data from a mock in-memory database to produce a plot. The plotting function is made available to the agent as a tool, which the model can call to generate a visualization and encode it in base64.

A simple Flask web UI then uses the structured output from the agent to display a textual analysis and the generated plot together in a clean dashboard.

## ✨ Features

- **Generative AI Agent:** Uses a Gemini model (`gemini-2.0-flash-001`) to process requests.
- **Tool-Enabled:** The agent is equipped with a Python function (`generate_plot_base64`) as a tool to create visualizations.
- **Data-Driven Visualization:** Generates a scatter plot with a trendline from mock data using `matplotlib`.
- **Base64 Image Encoding:** The generated plot is encoded into a base64 string, making it easy to embed in web pages or transfer via APIs.
- **Simple Web UI:** A Flask application provides a clean dashboard to display the agent's output.
- **Structured Output:** The agent returns a JSON object containing the analysis text and the image data.

## 🚀 Installation

### Prerequisites

- Python 3.8+
- A Google Cloud project with the Vertex AI API enabled.
- Authenticated Google Cloud CLI or Application Default Credentials (ADC).

### Steps

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/garzoglio/adk2image.git
    cd adk2image
    ```

2.  **Create a virtual environment (recommended):**
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    This project requires a few Python packages. You can install them using pip.
    ```sh
    pip install Flask google-adk matplotlib numpy
    ```

## Usage

There are two ways to run this project: as a standalone script to see the agent's raw output, or through the Flask web application for a visual experience.

### 1. Run the Flask Web Application (Recommended)

This will start a local web server to display the report dashboard.

```sh
python flask_app.py
```

After running the command, you will see output similar to this:
```
Starting Flask App...
 * Serving Flask app 'flask_app'
 * Running on http://127.0.0.1:5000
```
Open your web browser and navigate to **http://127.0.0.1:5000** to see the dashboard.

### 2. Run the Agent Script Directly

You can execute the agent script by itself to see the raw JSON output printed to the console. This is useful for debugging or integrating the agent's logic into another system.

```sh
python adk_agent.py
```

The script will print the structured JSON containing the status, analysis text, and the base64-encoded image data.

## 📜 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
