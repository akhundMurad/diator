from diator.requests import Request


class FirstMiddleware:
    async def __call__(self, request: Request, handle):
        print("Before 1 handling...")
        response = await handle(request)
        print("After 1 handling...")
        return response


class SecondMiddleware:
    async def __call__(self, request: Request, handle):
        print("Before 2  handling...")
        response = await handle(request)
        print("After 2 handling...")
        return response
