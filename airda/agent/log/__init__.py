import logging


def getLogger():
    return logging.getLogger("airda")


def getPromptLogger():
    return logging.getLogger("action_prompt")
