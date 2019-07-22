import hashlib
import os
import posixpath
from aiohttp import web
from uuid_upload_path.uuid import uuid

app = web.Application()


async def index(request):
    return web.Response(text='Hello World!')


async def upload(request):
    reader = await request.multipart()

    # reader.next() will `yield` the fields of your form
    field = await reader.next()
    filename = field.filename
    name, ext = posixpath.splitext(filename)
    uuid_filename = uuid() + ext
    # You cannot rely on Content-Length if transfer is chunked.
    file_hash = hashlib.sha256()

    with open(os.path.join('media/', uuid_filename), 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break

            file_hash.update(chunk)
            # print("Read chunk of size {} for {}".format(len(chunk), uuid_filename))
            f.write(chunk)

    os.remove(os.path.join('media/', filename))

    # response = web.Response(text=f'{uuid_filename} sized of {size} successfully stored')
    response = web.Response(text='successfully stored')
    response['Hash'] = file_hash.hexdigest()
    return response


app.router.add_get('', index)
app.router.add_post('/file', upload)


if __name__ == '__main__':
    web.run_app(app, port=8100)
