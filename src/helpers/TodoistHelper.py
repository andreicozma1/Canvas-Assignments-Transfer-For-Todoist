import logging
from datetime import datetime

from termcolor import colored
from todoist_api_python.api import TodoistAPI

from src.helpers.LogHelper import log_i, log_w
from src.Utils import p_info


class TodoistHelper:
    def __init__(self, api_key):
        p_info("# TodoistHelper: Initialized")
        logging.info(colored(f"  - Todoist API Key: {api_key}", "grey"))
        self.api = TodoistAPI(api_key.strip())
        self.tasks = self.api.get_tasks()
        self.projects = self.api.get_projects()

    def find_task(self, project_id, title):
        """
        Finds a task with the given title in the given project
        """
        tasks = []
        for task in self.tasks:
            if task.project_id == project_id and task.content == title:
                tasks.append(task)
        if len(tasks) == 0:
            log_i(
                f'Could not find task "{title}" in project "{project_id}"',
            )
            return None
        if len(tasks) > 1:
            log_w(
                f"Found multiple tasks with the name {title}",
                show_notify=True,
            )
            # delete all but the first task
            # for task in tasks[1:]:
            #     self.api.delete_task(task.id)
        return tasks[0]

    def get_project_names(self) -> list:
        """
        Loads all user projects from Todoist
        """
        project_names = []
        for project in self.projects:
            project_names.append(project.name)
        return project_names

    def get_project_id(self, project_name):
        """
        Returns the project id corresponding to project_name
        """
        project_ids = []
        for project in self.projects:
            if project.name == project_name:
                project_ids.append(project.id)

        if len(project_ids) == 0:
            log_i(
                f'Could not find project "{project_name}"',
            )
            return None

        if len(project_ids) > 1:
            log_w(
                f"Found multiple projects with the name {project_name}",
                show_notify=True,
            )

        return project_ids[0]

    def create_projects(self, proj_names_list: list):
        """
        Checks to see if the user has a project matching their course names.
        If there isn't, a new project will be created
        """
        logging.info("# Creating Todoist projects:")
        for i, course_name in enumerate(proj_names_list):
            if not self.create_project(course_name):
                logging.info(
                    f'  {i + 1}. INFO: "{course_name}" already exists; skipping...'
                )

    def create_project(self, proj_name):
        if proj_name in self.get_project_names():
            return False

        self.api.add_project(name=proj_name)
        logging.info(f' - OK: Created Project: "{proj_name}"')
        return True

    @staticmethod
    def make_link_title(title, url):
        """
        Creates a task title from an assignment object
        :param title:
        :param url:
        """
        return f"[{title}]({url})"

    @staticmethod
    def get_priority_name(priority: int):
        """
        Returns the name of the priority level
        """
        priorities = {1: "Normal", 2: "Medium", 3: "High", 4: "Urgent"}
        return priorities[priority]

    @staticmethod
    def find_priority(assignment_name, assignment_due_at) -> int:
        """
        Finds the priority level of an assignment
        Task priority from 1 (normal, default value) to 4 (urgent).
        1: Normal, 2: Medium, 3: High, 4: Urgent
        """
        priority = 1

        keywords = {
            4: ["exam", "test", "midterm", "final"],
            3: ["project", "paper", "quiz", "homework", "discussion"],
            2: ["reading", "assignment"],
        }

        for p, keywords in keywords.items():
            if p > priority and any(
                keyword in assignment_name.lower() for keyword in keywords
            ):
                priority = p

        if assignment_due_at is not None:
            due_at = datetime.strptime(assignment_due_at, "%Y-%m-%dT%H:%M:%SZ")

            # If there are less than 3 days left on the assignment, set priority to 4
            if (due_at - datetime.now()).days < 3:
                priority = 4

        return priority
