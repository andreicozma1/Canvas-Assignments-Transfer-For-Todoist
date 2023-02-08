import logging
from datetime import datetime
from pprint import pprint

from termcolor import colored

from src.helpers.CanvasHelper import CanvasHelper
from src.helpers.ConfigHelper import ConfigHelper
from src.helpers.LogHelper import notify
from src.helpers.TodoistHelper import TodoistHelper


class CanvasToTodoist:
    def __init__(self, args, config_path, skip_confirmation_prompts=False):
        logging.info(colored("Starting CanvasToTodoistr", attrs=["bold", "reverse"]))
        self.skip_confirmation_prompts = skip_confirmation_prompts
        self.param = {"per_page": "100", "include": "submission"}
        self.input_prompt = "> "
        self.selected_course_ids = None

        # Loaded configuration files
        self.config_helper = ConfigHelper(
            args, config_path, self.input_prompt, self.skip_confirmation_prompts
        )

        self.canvas_helper = CanvasHelper(
            self.config_helper.get("canvas_api_key"),
            canvas_api_heading=str(self.config_helper.get("canvas_api_heading")),
        )
        self.todoist_helper = TodoistHelper(self.config_helper.get("todoist_api_key"))

    def run(self):
        logging.info("###################################################")
        logging.info("#     Canvas-Assignments-Transfer-For-Todoist     #")
        logging.info("###################################################")

        todoist_project_names = self.todoist_helper.get_project_names()
        self.selected_course_ids = self.canvas_helper.select_courses(
            self.config_helper, todoist_project_names, self.skip_confirmation_prompts
        )
        logging.info(self.selected_course_ids)
        course_names = self.canvas_helper.get_course_names(self.selected_course_ids)

        self.todoist_helper.create_projects(course_names)

        assignments = self.canvas_helper.get_assignments(
            self.selected_course_ids, self.param
        )
        self.transfer_assignments_to_todoist(assignments)
        logging.info("# Finished!")

    # def check_existing_task(self, assignment, project_id):
    #     """
    #     Checks to see if a task already exists for the assignment.
    #     Return flags for whether the task exists and if it needs to be updated,
    #     as well as the corresponding task object.
    #     """
    #     is_added = False
    #     is_synced = True
    #     item = None
    #     for task in self.todoist_helper.tasks:
    #         # If title and project match, then the task already exists
    #         if task.project_id == project_id:
    #             task_title = TodoistHelper.make_link_title(
    #                 assignment["name"], assignment["html_url"]
    #             )
    #             if task.content == task_title:
    #                 is_added = True
    #                 # Check if the task is synced by comparing due dates and priority
    #                 if (
    #                     task.due and task.due.date != assignment["due_at"]
    #                 ) or task.priority != assignment["priority"]:
    #                     is_synced = False
    #                     item = task
    #                     break
    #     return is_added, is_synced, item

    def get_course_by_id(self, course_id: str):
        if course_id in self.selected_course_ids:
            return self.selected_course_ids[course_id]
        # otherwise if any of the ids end with the course id, return that
        for key, value in self.selected_course_ids.items():
            if key.endswith(str(course_id)):
                return value
        return None

    def transfer_assignments_to_todoist(self, assignments):
        """
        Transfers over assignments from Canvas over to Todoist.
        The method Checks to make sure the assignment has not already been transferred to prevent overlap.
        """
        logging.info("# Transferring assignments to Todoist...")

        summary = {"added": [], "updated": [], "is-submitted": [], "up-to-date": []}

        for i, canvas_assignment in enumerate(assignments):
            # Get the canvas assignment name, due date, course name, todoist project id
            course_id = str(canvas_assignment["course_id"])
            name = canvas_assignment["name"]
            due_at = canvas_assignment["due_at"]

            submitted = (
                "submission" in canvas_assignment
                and canvas_assignment["submission"]["workflow_state"] != "unsubmitted"
            )

            canvas_course_name = self.get_course_by_id(course_id)["name"]
            todoist_proj_id = self.todoist_helper.get_project_id(canvas_course_name)

            logging.info(f'  {i + 1}. Assignment: "{name}"')

            # Check if the assignment already exists in Todoist and if it needs updating
            # is_added, is_synced, task = self.check_existing_task(c_a, t_proj_id)
            task_title = TodoistHelper.make_link_title(
                canvas_assignment["name"], canvas_assignment["html_url"]
            )
            task_description = canvas_assignment["description"]
            task_priority = TodoistHelper.find_priority(name, due_at)
            assignments[i]["priority"] = task_priority

            logging.info(f"     Course: {canvas_course_name} (id: {course_id})")
            logging.info(f"     Due Date: {due_at}")
            logging.info(
                f"     Priority: {TodoistHelper.get_priority_name(task_priority)}"
            )
            logging.info(f"     Todoist Project ID: {todoist_proj_id}")

            task = self.todoist_helper.find_task(todoist_proj_id, task_title)

            # Handle cases for adding and updating tasks on Todoist
            if task is None:
                if submitted:
                    summary["is-submitted"].append(canvas_assignment)
                    logging.info(
                        "     INFO: Assignment submitted. Skipping Todoist task."
                    )
                    continue
                task = self.todoist_helper.api.add_task(
                    content=task_title,
                    description=task_description,
                    project_id=todoist_proj_id,
                    priority=task_priority,
                    due_string=due_at,
                )
                summary["added"].append(canvas_assignment)

            if task is not None:
                if submitted:
                    summary["is-submitted"].append(canvas_assignment)
                    logging.info(
                        "     INFO: Assignment submitted. Closing Todoist task."
                    )
                    self.todoist_helper.api.close_task(task_id=task.id)
                    continue
                updates_list = []
                if (task.due.string if task.due else None) != due_at:
                    logging.info(
                        f"     UPDATE: due date: {task.due.string if task.due else None} -> {due_at}"
                    )
                    updates_list.append("due date")
                if task.priority != task_priority:
                    updates_list.append("priority")
                    p1 = TodoistHelper.get_priority_name(task.priority)
                    p2 = TodoistHelper.get_priority_name(task_priority)
                    logging.info(f"     UPDATE: priority: {p1} -> {p2}")
                if task_description and task.description != task_description:
                    updates_list.append("description")
                    logging.info(
                        f"     UPDATE: description: {task.description} -> {task_description}"
                    )

                if len(updates_list) > 0:
                    self.todoist_helper.api.update_task(
                        task_id=task.id,
                        content=task_title,
                        description=task_description,
                        project_id=todoist_proj_id,
                        priority=task_priority,
                        due_string=due_at,
                    )
                    summary["updated"].append(canvas_assignment)
                else:
                    logging.info(f"     OK: Task is already up to date!")
                    summary["up-to-date"].append(canvas_assignment)

        # Print out short summary
        logging.info("")
        logging.info(f"# Short Summary:")
        logging.info(f"  * Added: {len(summary['added'])}")
        logging.info(f"  * Updated: {len(summary['updated'])}")
        logging.info(f"  * Already Submitted: {len(summary['is-submitted'])}")
        logging.info(f"  * Up to Date: {len(summary['up-to-date'])}")

        if len(summary["added"]) > 0 or len(summary["updated"]) > 0:
            logging.info("New tasks added or updated. Sending notification.")
            n_title = f"Canvas to Todoist (Total: {len(assignments)})"
            n_msg = (
                f"Added {len(summary['added'])} & Updated {len(summary['updated'])}.\n"
                f"Completed: {len(summary['is-submitted'])} & Up-to-Date {len(summary['up-to-date'])}."
            )
            notify(n_title, n_msg)
        else:
            logging.info("No new tasks added or updated. Skipping notification.")

        # Print detailed summary?
        # logging.info("")
        # if not self.skip_confirmation_prompts:
        #     answer = input("Q: Print Detailed Summary? (Y/n): ")
        # else:
        #     answer = "y"

        # if answer.lower() == "y":
        #     logging.info("")
        #     logging.info(f"# Detailed Summary:")
        #     for summary_key in reversed(summary.keys()):
        #         a_list = summary[summary_key]
        #         logging.info(f"  * {summary_key.upper()}: {len(a_list)}")
        #         for i, canvas_assignment in enumerate(a_list):
        #             name = canvas_assignment["name"]
        #             canvas_course_name = self.selected_course_ids[
        #                 str(canvas_assignment["course_id"])
        #             ]["name"]
        #             a_p = canvas_assignment["priority"]
        #             a_d = canvas_assignment["due_at"]
        #             d = None
        #             if a_d:
        #                 d = datetime.strptime(a_d, "%Y-%m-%dT%H:%M:%SZ")
        #             # Convert to format: May 22, 2022 at 12:00 PM
        #             d_nat = (
        #                 "Unknown" if d is None else d.strftime("%b %d, %Y at %I:%M %p")
        #             )
        #             logging.info(f'    {i + 1}. "{name}"')
        #             logging.info(f"         Course: {canvas_course_name}")
        #             logging.info(f"         Due Date: {d_nat}")
        #             logging.info(
        #                 f"         Priority: {TodoistHelper.get_priority_name(a_p)}"
        #             )
