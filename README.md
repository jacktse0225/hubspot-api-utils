<h1>Data Processing with HubSpot API</h1>
        <h2>Features</h2>
        <ul>
            <li>Fetch Contact and Company data from a HubSpot list, Format the data and export to an Excel spreadsheet.</li>
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

