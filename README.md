# GameDayAlerts
 
### This is a bot designed to alert you to when a baseball/football game is about to destroy your evening commute.
- Runs weekly
- Uses a timedelta of 3 hours from start (baseball) or 3.5 hours (football) to guestimate the end of the game.
- Looks for Orioles/Ravens games ending between 3:00pm and 5:30pm. Monday-Friday 
- In the event of a game notifications are sent to a Discord Webhook. 

# Setup

## Setup a Linux Host
I'm using Ubuntu LTS on an Oracle Cloud VM. There are free-tiers available as of today. Google Compute and Amazon AWS are similar products. You can also roll your own host with an old PC or a Raspberry Pi. You'll need to know a bit of Linux CLI or you'll need to be ready to learn!  

### Install necessary software prerequisites: 

#### 1) Install Python3
	sudo apt install python3

#### 2) Create a python virtual environment in a directory
	/usr/bin/python3 -m venv /home/ubuntu/GameDayAlerts

#### 3) Use the virtual python3 environment
	source /home/ubuntu/GameDayAlerts/bin/activate

#### 4) Install PIP Prereqs
	pip3 install requests pytz
	
#### 5) Setup Dicrosd Webhook
- A Discord webhook needs to be created and entered into webhook.txt - you can setup two channels or use the same webhook for both. Right clicking the channel in Discord --> Edit Channel --> Integrations --> Create Webhook. Make a note of your Webhook URL.
	sudo nano /home/ubuntu/GameDayAlerts/webhook.txt


## Setup Git
1. [Create a Github account.](https://github.com/join)

2. [Go here and install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) if you don’t have it already.

3. [Assuming you're reading this on the repo page](https://github.com/SaltySOMAdmin/Reddit-UFOs_Archive), select ‘fork’ to create a copy of it to your Github account. 

4. From your new repo, select **Code** and then under **Clone** copy the HTTPS URL (e.g. https://github.com/SaltySOMAdmin/Reddit-UFOs_Archive.git) to download a local copy

5. Navigate to a folder you want a local copy of the repo to live, and clone the Github repo to your host:
   1. It's up to you where to put the repo - recommended in a folder like /home/YourUserAcct/Github/ or /home/YourUserAcct/. Once you clone the directory it will create a subfolder with the name of your fork.
   2. `git clone <url>`
      1. e.g. `git clone https://github.com/SaltySOMAdmin/Reddit-UFOs_Archive.git`

## Configure the script.
There are several sections you need to customize in the main script (CopyPosts-UFOs_Archives.py). You'll need to enter your source and destination subs.

	source_subreddit = source_reddit.subreddit('ufos')

	destination_subreddit = archives_reddit.subreddit('UFOs_Archive')
	
You'll also need to set your timedelta. I run my script every 14 minutes but the script checks posts that are created within the past 28 minutes. This gives two opportunities for posts to be duplicated. 

	cutoff_time = current_time - timedelta(minutes=28)
	
Edit the path for the two log files to the path you cloned this repository to. 
	
	logging.basicConfig(filename='/home/YourUserAcct/Github/YourFork/error_log.txt', level=logging.ERROR, 

and

	PROCESSED_FILE = "/home/YourUserAcct/Github/YourFork/processed_posts.txt"
	
Enter your credentials into config.py. You can use different accounts for the source and destination subreddits or you can use one account for both. I'm using the credentials I have saved in destination_ for both. Specify in the main script under the section with "# Reddit API credentials"
	
	source_client_id=""
	source_client_secret=""
	source_password=""
	source_username=""
	
and

	destination_client_id=""
	destination_client_secret=""
	destination_password=""
	destination_username=""

DailyRemovedFlair.py will need quite a bit more customization and may not be necessary for your needs. If it's a feature you need you'll need to edit the script to include a list of 'removal flairs' if the home subreddit supports them. You'll also need to update the script with your subreddit name and the path to your log file. This can be implemented at a later point as well as the main script does not hinge on it. 

### Crontab Settings
This is where you will set your schedule to run. My script runs every 14 minutes (Example: 10:00, 10:14, 10:28, 10:42, 10:56) and it logs actions to cron_log.txt Errors are logged within the script to error_log.txt as they happen. To open your cron settings type this into your terminal: crontab -e

- Run main script

		*/14 * * * /usr/bin/python3 /home/ubuntu/Reddit-UFOs_Archive/CopyPosts-UFOs_Archives.py >> /home/ubuntu/Reddit-UFOs_Archive/cron_log.txt 2>&1

- Update flair for removed posts script, if incorporated.

		2 */8 * * * /usr/bin/python3 /home/ubuntu/Reddit-UFOs_Archive/DailyRemovedFlair.py >> /home/ubuntu/Reddit-UFOs_Archive/removed_posts_log.txt 2>&1


- Upload logs to Discord Webhook then wipe the log

		*/15 * * * * /home/ubuntu/Reddit-UFOs_Archive/forward_error_log.sh
		*/15 * * * * /home/ubuntu/Reddit-UFOs_Archive/forward_cron_log.sh
		10 */8 * * * /home/ubuntu/Reddit-UFOs_Archive/forward_removed_posts_log.sh

### Setup Continuous Deployment with Github Actions

Allows you to deploy your code via Github vs logging into the VPS and updating the code/uploading a new file. Allows for easier collaboration as well. I followed a guide similar to this one:
https://docs.github.com/en/actions/use-cases-and-examples/deploying/deploying-with-github-actions
