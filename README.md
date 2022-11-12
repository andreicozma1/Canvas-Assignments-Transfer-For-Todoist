# Canvas-Assignments-Transfer-For-Todoist

Modifications by Andrei Cozma which are based on the original code from the following repository:

- <https://github.com/scottquach/Canvas-Assignments-Transfer-For-Todoist>

not created by, affiliated with, or supported by Doist

Transferring assignments from your student Canvas account to your Todoist account couldn't be easier.

This project provides you with an easy way to transfer all of your assignments from a Canvas account into a Todoist account with appropraite due dates and assignment to auto-generated projects that match course names.

## How-To

### Easy Run

Easy run allows all configuration to be done inside of the program, avoiding the hassle of editing the api_keys file directly. Just install the dependencies and follow the instructions on screen.

- Install required packages with `pip install -r requirements.txt`
- Run `python easy_run.py`

### Manual Setup

If you don't want to use easy run for whatever reason, you can edit the `api_keys.txt` file directly, just follow the steps below.

**You will first need an API key for both Canvas and Todoist**

- On Canvas desktop go to settings and click on ```New Access Token``` under Approved Integrations
- On Todoist desktop go to settings and the API token will be listed under the ```Integrations Tab```

**Add the API Keys to the api_keys.txt file**

- Replace the prompted lines with the api keys. Remember to remove any trailing or leading spaces

**You will then need the course ID of the classes whose assignments you would like to transfer. This is easy to find thanks to an included script titled ```retrieve_canvas_course_ids```**

- Run the script by calling ```python retrieve_canvas_course_ids.py```
- Your courses will be listed with the associated ID
- This step is necessary and not automated **because some teachers don't archive their classes for the next quarter and old assignments could be added by mistake**

**Add course ID to the api_keys.txt file**

- Once you have retrieved the required course ID follow the prompt on the api_keys.txt file to add those IDs. An infinite number of courses can be added as long as each course ID is on it's own line.

**Install dependencies**

- Install dependencies with `pip install -r requirements.txt`

**Run the main script**

- Run the main script by calling ```python canvas_to_todoist.py```
- The script will run and transfer assignments over to Todoist
  - Assignments will be checked for overlap, so running the script multiple times won't re-add assignments that already exist in Todoist.
- Assignments will be added to automatically generated projects in Todoist. The project names will match with the official course names pulled from Canvas

## Contributing

I'm still active in the community so feel free to submit a PR for any contributions you'd like to make to the project!
