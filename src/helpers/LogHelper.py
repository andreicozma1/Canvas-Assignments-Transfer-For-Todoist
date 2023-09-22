import logging

from notifypy import Notify


def notify(title, message):
    notification = Notify()
    notification.title = title
    notification.message = message
    notification.send()


def log_d(message, show_notify=False):
    logging.debug(message)
    if show_notify:
        notify("Canvas-Sync DEBUG", message)


def log_i(message, show_notify=False):
    logging.info(message)
    if show_notify:
        notify("Canvas-Sync INFO", message)


def log_w(message, show_notify=False):
    logging.warning(message)
    if show_notify:
        notify("Canvas-Sync WARNING", message)


def log_e(message, show_notify=False):
    logging.error(message)
    if show_notify:
        notify("Canvas-Sync ERROR", message)
