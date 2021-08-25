import asyncio
from threading import Thread
from src.worker import Worker

class FatherThread(Thread):
    def __init__(self, kind):
        Thread.__init__(self)
        self.worker = Worker()
        self.file_kind = kind

    def run(self):
        if self.file_kind == 'photo':
            asyncio.run(self.worker.photo())
        elif self.file_kind == 'user':
            asyncio.run(self.worker.user())
        elif self.file_kind == 'chat_room':
            asyncio.run(self.worker.chat_room())
        elif self.file_kind == 'message':
            asyncio.run(self.worker.message())
        elif self.file_kind == 'event':
            asyncio.run(self.worker.event())
        elif self.file_kind == 'greeting':
            asyncio.run(self.worker.greeting())
        print(f"Родитель `{self.file_kind}` закончил работу ", flush=True)


def main():
    kind = ['photo',
            'user',
            'chat_room',
            'message',
            'event',
            'greeting']
    # kind = ['message']
    for i in kind:
        t = FatherThread(i)
        t.start()


if __name__ == '__main__':
    main()

