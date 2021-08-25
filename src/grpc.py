from __future__ import print_function
from skyproto_pb import media_pb2


def upload_request(file_name, content_type, content, content_kind):
    yield media_pb2.UploadRequest(Name=file_name, ContentType=content_type,
                                  Content=content, Kind=content_kind)


def upload(stub, file_name, content_type, content, content_kind):
    """
    file_name: file name
    content_type: Content-Type (MIME тип контента согласно RFC)/ <image/png>
    content: bytes
    """


    # chank = []
    # for item in range(int(len(content)/4096)+1):
    #     chank.append(content[item*4096:(item+1)*4096])
    # for item in chank:

    response = stub.Upload(upload_request(file_name, content_type, content, content_kind))

    if response is None:
        return None

    if response.ErrorCode > 0:
        print("grpc media_upload failed, ERROR=", response.ErrorCode)
        return None

    if response.ErrorCode == 6000:
        return None
    return response.ContentID
