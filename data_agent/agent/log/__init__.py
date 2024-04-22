import logging


def getLogger():
    return logging.getLogger("data_agent")


def getPromptLogger():
    return logging.getLogger("action_prompt")
