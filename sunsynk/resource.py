class Resource:
    def __repr__(self):
        attrs = " ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"<{self.__class__.__name__} @{id(self) & 0xFFFFFF} {attrs}>"
