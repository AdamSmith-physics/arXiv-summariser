# arXiv-summariser
Python scripts to download and summarise daily arXiv postings using the arXiv python API and local LLM models through Ollama. You will need to install Ollama and have a local model available before you start.

This will serch arXiv for new papers in your specified categories, authors, and topics, summarise the most relevant ones using your chosen local LLM model, and email you the summaries. This summary includes the paper title, authors, abstract for the top 3 papers, and gives the titles and authors of any further relevant papers. All papers are linked to their arXiv page.

The summariser keeps track of previously summarised papers to avoid duplicates, storing up to 1000 previous arXiv IDs in a file named `previous_ids.dno`.

The summariser works by searching arXiv for new papers in your specified categories. It then gives each paper an individual relevance score based on your specified authors and topics using your chosen local LLM model. The top 10 most relevant papers are then passed to the model again to get a more accurate ranking.


## Setup Instructions
1. **Create the conda environment**:
```bash
conda env create -f environment.yml
```

2. **Find the path to the conda environment you just created**:
```bash
conda activate arxiv-summariser
which python
```
Copy the output path (e.g. `/Users/username/miniconda3/envs/arxiv-summariser/bin/python`), and paste it into the `run.sh` script, replacing the `PYTHON` variable.

3. **Set up your email details**: Fill in your details in settings/email_details_template.json and rename it as settings/email_details.json (this file is gitignored to protect your credentials). The template is as follows:
```json
{
    "email_address": "YOUR_EMAIL_ADDRESS",
    "email_password": "YOUR_EMAIL_PASSWORD",
    "smtp_server": "smtp.your_email_provider.com",
    "smtp_port": "YOUR_SMTP_PORT"
}
```

4. **Set up your user settings**:
Create a folder named `settings/user_settings/` in the root directory of the project. Add a JSON file in this folder with your desired settings. An example settings file is as follows:
```json
{
    "Name": "Adam Gammon-Smith",
    "Email": "RECEIVER_EMAIL_ADDRESS",
    "Categories": ["quant-ph", "cond-mat.*"],
    "Authors": ["Adam Gammon-Smith", "Adam Smith"],
    "Topics": ["condensed matter", "quantum computing"],
    "Model": "gemma3:27b"
}
```
You should choose an appropriate model available in your local Ollama installation.

5. **Run the summariser**:
You can run the summariser script manually using:
```bash
bash run.sh
```


## Running automated Daily Summariser
To run the summariser daily at a specific time, you can set up a cron job on mac and linux. Open your crontab file by running:
```bash
crontab -e
```
Then, add the following line to schedule the script to run every day at 3 AM:
```bash
0 3 * * * /path/to/arXiv-summariser/run.sh > /path/to/arXiv-summariser/logs/cron_log.out 2>&1
```
Make sure to replace `/path/to/arXiv-summariser/` with the actual path to the cloned repository on your system.

Note, on Mac, you may need to give cron permission to run scripts in System Preferences > Security & Privacy > Privacy > Full Disk Access. Click on the + button then navigate to `/usr/sbin/cron` and add it. This is a hidden folder, so use Cmd+Shift+G to go to the folder directly.