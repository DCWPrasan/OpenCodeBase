import time


class SlowResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Before the view (or next middleware) is called
        start_time = time.time()

        response = self.get_response(request)

        # After the view (or next middleware) has been called
        end_time = time.time()

        # Introduce a delay of 5 seconds
        delay = 2
        if end_time - start_time < delay:
            time.sleep(delay - (end_time - start_time))

        return response
