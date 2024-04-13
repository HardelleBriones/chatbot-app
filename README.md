# chatbot-app

## Getting Started
Follow these steps to run the app locally:

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
2. **Activate the virtual environment**:
   ```bash
   venv/Scripts/activate

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Navigate to the app folder**:
   ```bash
   cd app
5. **Run the app using uvicorn**:
   ```bash
   uvicorn main:app --reload
   
## Prerequisites
Before running the application, make sure you have the following environment variables set up in your .env file:
- `MONGODB_CONNECTION_STRING`: This variable should contain the connection string for your MongoDB database.
- `OPENAI_API_KEY`: This variable should contain the API key for accessing the OpenAI services.
