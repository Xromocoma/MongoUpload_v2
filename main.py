import asyncio
import time
from threading import Thread
from src.worker import photo, user, greeting, event, chat_room, message


class FatherThread(Thread):
    def __init__(self, kind):
        Thread.__init__(self)
        self.file_kind = kind

    def run(self):
        if self.file_kind == 'photo':
            asyncio.run(photo())
        elif self.file_kind == 'user':
            asyncio.run(user())
        elif self.file_kind == 'chat_room':
            asyncio.run(chat_room())
        elif self.file_kind == 'message':
            asyncio.run(message())
        elif self.file_kind == 'event':
            asyncio.run(event())
        elif self.file_kind == 'greeting':
            asyncio.run(greeting())
        print(f"Родитель `{self.file_kind}` закончил работу ", flush=True)


def main():
    kind = [
        'photo',
        'user',
        'chat_room',
        'message',
        'event',
        'greeting'
    ]
    t = []
    for i in kind:
        t.append(FatherThread(i))
    for item in t:
        item.start()
    for item in t:
        item.join()


if __name__ == '__main__':
    main()
