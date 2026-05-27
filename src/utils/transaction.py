class TransactionManager:
    def __init__(self):
        self.rollback_stack = []

    def add_rollback(self, func, *args, **kwargs):
        self.rollback_stack.append((func, args, kwargs))

    def rollback(self):
        for func, args, kwargs in reversed(self.rollback_stack):
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"[ROLLBACK ERROR] {func.__name__}: {e}")
