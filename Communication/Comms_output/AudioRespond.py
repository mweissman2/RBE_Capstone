from multiprocessing import Queue


def audioRespond(response_q: Queue, response_string: str):
    """
    Push response to response queue
    """
    response_q.put(response_string)