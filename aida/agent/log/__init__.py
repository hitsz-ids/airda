import logging


def getLogger():
    return logging.getLogger("aida")


def getPromptLogger():
    return logging.getLogger("action_prompt")
