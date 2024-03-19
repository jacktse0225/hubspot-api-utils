<h1>Data Processing and Export Script</h1>
        <h2>Features</h2>
        <ul>
            <li>Fetch data from a specified API endpoint.</li>
            <li>Process the fetched data according to predefined rules.</li>
            <li>Export the processed data to an Excel spreadsheet.</li>
            <li>Customizable settings via a <code>config.json</code> file.</li>
        </ul>
        <h2>Getting Started</h2>
        <ol>
            <li>Clone the repository to your local machine.</li>
            <li>Install the required dependencies by running:
                <pre><code>pip install -r requirements.txt</code></pre>
            </li>
            <li>Create a <code>config.json</code> file in the /general directory of the project with the following structure:
                <pre><code>{
    "sandbox_api": "YOUR_SANDBOX_API_KEY",
    "production_api": "YOUR_PRODUCTION_API_KEY",
    "selected_api": "sandbox",
    "selected_directory": "YOUR_EXPORT_DIRECTORY_PATH"
}</code></pre>
            </li>
            <li>Replace <code>"YOUR_SANDBOX_API_KEY"</code> and <code>"YOUR_PRODUCTION_API_KEY"</code> with your actual API keys. Ensure that you specify the correct API key for the environment you want to use (<code>sandbox</code> or <code>production</code>).</li>
            <li>Replace <code>"YOUR_EXPORT_DIRECTORY_PATH"</code> with the directory where you want the exported Excel spreadsheet to be saved.</li>
            <li>Run the script by executing:
                <pre><code>python creating_preview_file_of_list.py</code></pre>
            </li>
            <li>Once the script finishes running, you will find the exported Excel spreadsheet in the specified directory.</li>
        </ol>
        <h2>Contributing</h2>
        <p>Contributions are welcome! Feel free to submit pull requests or open issues if you encounter any bugs or have suggestions for improvements.</p>
        <h2>License</h2>
        <p>This project is licensed under the <a href="LICENSE">MIT License</a>.</p>
