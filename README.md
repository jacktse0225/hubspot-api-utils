Data Processing and Export Script
This script allows users to fetch data from an API, process it, and export it to an Excel spreadsheet.

Features
Fetch data from a specified API endpoint.
Process the fetched data according to predefined rules.
Export the processed data to an Excel spreadsheet.
Customizable settings via a config.json file.
Getting Started
To use this script, follow these steps:

Clone the repository to your local machine.

Install the required dependencies by running:

Copy code
pip install -r requirements.txt
Create a config.json file in the root directory of the project with the following structure:

json
Copy code
{
    "sandbox_api": "YOUR_SANDBOX_API_KEY",
    "production_api": "YOUR_PRODUCTION_API_KEY",
    "selected_api": "sandbox",
    "selected_directory": "YOUR_EXPORT_DIRECTORY_PATH"
}
Replace "YOUR_SANDBOX_API_KEY" and "YOUR_PRODUCTION_API_KEY" with your actual API keys. Ensure that you specify the correct API key for the environment you want to use (sandbox or production).

Replace "YOUR_EXPORT_DIRECTORY_PATH" with the directory where you want the exported Excel spreadsheet to be saved.

Run the script by executing:

Copy code
python creating_preview_file_of_list.py
Once the script finishes running, you will find the exported Excel spreadsheet in the specified directory.

Contributing
Contributions are welcome! Feel free to submit pull requests or open issues if you encounter any bugs or have suggestions for improvements.

License
This project is licensed under the MIT License.

Feel free to customize the instructions and sections according to your project's specific requirements and preferences.
