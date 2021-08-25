import asyncio
from queue import Queue
from threading import Thread
from documents import *
import grpc
from skyproto_pb import media_pb2_grpc
from config import *
from src.db import Connection, ConnectionSinc
from src.upload import upload_file


# from src.grpc_connect import channel

class Worker:
    async def photo(self):
        mongo_client = Connection().client
        mongo_db = mongo_client.profile_db
        res = mongo_db['photo'].find({"photo_content_id": {'$regex': 'http'}}).limit(LIMIT)

        queue = Queue()
        async for item in res:
            queue.put_nowait(item)
        print("photo", queue.qsize())

        channel = grpc.insecure_channel(UPLOAD_GRPC_ADDRESS, options=(('grpc.max_concurrent_streams', -1),))
        stub = media_pb2_grpc.MediaStub(channel)

        for i in range(COUNT_PHOTO_WORKER):
            print(i, "photo")
            t = WorkerThread(kind="photo", queue=queue, stub=stub)
            t.start()

    async def message(self):
        mongo_client = Connection().client
        mongo_db = mongo_client.chat_db
        res = mongo_db['dialog_message'].find({"$or": [{"message_content.data_id": {"$regex": "http"}},
                                                       {"message_content.preview_id": {"$regex": "http"}}]}).limit(
            LIMIT)

        # res = DialogMessage.objects(__raw__={"$or": [{"message_content.data_id": {"$regex": "http"}},
        #                                              {"message_content.preview_id": {"$regex": "http"}}]})

        channel = grpc.insecure_channel(UPLOAD_GRPC_ADDRESS, options=(('grpc.max_concurrent_streams', -1),))
        stub = media_pb2_grpc.MediaStub(channel)

        queue = Queue()
        async for item in res:
            queue.put_nowait(item)
        print("message", queue.qsize())

        for i in range(COUNT_MESSAGE_WORKER):
            print(i, "message")
            t = WorkerThread(kind="message", queue=queue, stub=stub)
            t.start()

    async def user(self):
        mongo_client = Connection().client
        mongo_db = mongo_client.profile_db
        res = mongo_db['user'].find({"user_avatar.content_id": {"$regex": "http"}}).limit(LIMIT)
        # res = User.objects(__raw__={"user_avatar.content_id": {"$regex": "http"}})
        channel = grpc.insecure_channel(UPLOAD_GRPC_ADDRESS, options=(('grpc.max_concurrent_streams', -1),))
        stub = media_pb2_grpc.MediaStub(channel)
        queue = Queue()
        async for item in res:
            queue.put_nowait(item)
        print("user", queue.qsize())

        for i in range(COUNT_USER_WORKER):
            print(i, "user")
            t = WorkerThread(kind="user", queue=queue, stub=stub)
            t.start()

    async def chat_room(self):
        mongo_client = Connection().client
        mongo_db = mongo_client.chat_db
        res = mongo_db['room'].find({"room_avatar_id": {"$regex": "http"}}).limit(LIMIT)
        # res = Room.objects(__raw__={"room_avatar_id": {"$regex": "http"}})
        channel = grpc.insecure_channel(UPLOAD_GRPC_ADDRESS, options=(('grpc.max_concurrent_streams', -1),))
        stub = media_pb2_grpc.MediaStub(channel)

        queue = Queue()
        async for item in res:
            queue.put_nowait(item)
        print("chat_room", queue.qsize())
        t = WorkerThread(kind="chat_room", queue=queue, stub=stub)
        t.start()

    async def event(self):
        mongo_client = Connection().client
        mongo_db = mongo_client.event_db
        res = mongo_db['event'].find({"$or": [{"event_image.avatar.id": {"$regex": "http"}},
                                              {"event_image.cover.id": {"$regex": "http"}},
                                              {"event_image.banner.id": {"$regex": "http"}}
                                              ]}).limit(LIMIT)

        channel = grpc.insecure_channel(UPLOAD_GRPC_ADDRESS, options=(('grpc.max_concurrent_streams', -1),))
        stub = media_pb2_grpc.MediaStub(channel)
        queue = Queue()
        async for item in res:
            queue.put_nowait(item)
        print("event", queue.qsize())

        t = WorkerThread(kind="event", queue=queue, stub=stub)
        t.start()

    async def greeting(self):
        mongo_client = Connection().client
        mongo_db = mongo_client.prodile_db
        res = mongo_db['greeting'].find({"greeting_avatar_id": {"$regex": "http"}}).limit(LIMIT)

        channel = grpc.insecure_channel(UPLOAD_GRPC_ADDRESS, options=(('grpc.max_concurrent_streams', -1),))
        stub = media_pb2_grpc.MediaStub(channel)

        queue = Queue()
        async for item in res:
            queue.put_nowait(item)
        print("greeting", queue.qsize())

        t = WorkerThread(kind="greeting", queue=queue, stub=stub)
        t.start()


class WorkerThread(Thread):

    def __init__(self, kind, queue, stub=None):
        """Инициализация потока"""
        Thread.__init__(self)
        self.con = ConnectionSinc()
        self.file_kind = kind
        self.task = queue
        self.stub_grpc = stub

    def run(self):
        """Запуск потока"""

        while self.task.qsize() > 0:
            update_object(kind=self.file_kind, item=self.task.get(), stub_grpc=self.stub_grpc)


def update_object(kind, item, stub_grpc):
    try:
        if kind == 'photo':
            if item['room_avatar_id'][-1] == '.':
                return
            file = upload_file(item['photo_content_id'], stub_grpc)
            if file:
                temp = Photo.objects(id=item['_id']).update_one(photo_content_id=file)
                if temp == 0:
                    print("err")

        elif kind == 'user':
            if item['room_avatar_id'][-1] == '.':

                return
            file = upload_file(item['user_avatar']['content_id'], stub_grpc)
            if file:
                temp = User.objects(id=item['_id']).update_one(user_avatar__content_id=file)
                if temp == 0:
                    print("err")

        elif kind == 'chat_room':
            if item['room_avatar_id'][-1] == '.':

                return
            file = upload_file(item['room_avatar_id'], stub_grpc)
            if file:
                temp = Room.objects(id=item['_id']).update_one(room_avatar_id=file)
                if temp == 0:
                    print("err")

        elif kind == 'message':
            if item['message_content'].get('data_id') and item['message_content'].get('preview_id'):
                if item['message_content']['data_id'][-1] == '.' or item['message_content']['preview_id'] == '.':

                    return
                data_id = upload_file(item['message_content']['data_id'], stub_grpc)
                preview_id = upload_file(item['message_content']['preview_id'], stub_grpc)
                if data_id and preview_id:
                    temp = DialogMessage.objects(id=item['_id']).update_one(
                        message_content__data_id=data_id,
                        message_content__preview_id=preview_id)
                    if temp == 0:
                        print("err")
            elif item['message_content'].get('data_id'):
                if item['message_content']['data_id'][-1] == '.':

                    return
                data_id = upload_file(item['message_content']['data_id'], stub_grpc)
                if data_id:
                    temp = DialogMessage.objects(id=item['_id']).update_one(
                        message_content__data_id=data_id)
                    if temp == 0:
                        print("err")

        elif kind == 'event':
            print("in event", item['event_image']['cover']['id'])
            if item['event_image']['cover']['id'][-1] == '.' or \
                    item['event_image']['banner']['id'][-1] == '.' or \
                    item['event_image']['avatar']['id'][-1] == '.':

                return
            cover = upload_file(item['event_image']['cover']['id'], stub_grpc)
            banner = upload_file(item['event_image']['banner']['id'], stub_grpc)
            avatar = upload_file(item['event_image']['avatar']['id'], stub_grpc)
            print("!!!!!!", cover, banner, avatar)
            if cover and banner and avatar:
                temp = Event.objects(id=item['_id']).update(__raw__={"$set": {"event_image.avatar.id": avatar,
                                                                              "event_image.cover.id": cover,
                                                                              "event_image.banner.id": banner}})
                print(temp)
                if temp == 0:
                    print("err")

        elif kind == 'greeting':
            if item['greeting_avatar_id'][-1] == '.':

                return
            file = upload_file(item['greeting_avatar_id'], stub_grpc)
            if file:
                temp = Greetings.objects(id=item['_id']).update_one(greeting_avatar_id=file)
                if temp == 0:
                    print("err")

    except BaseException as e:
        print(e, flush=True)
