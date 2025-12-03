# arXiv-summariser
Python scripts to download and summarise daily arXiv postings using the arXiv python API and local LLM models.


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