import _io
import os.path
import random
import string


def make_store_request_to_cdn_server(file_obj):
    # identifier is the filename. We can see that CDN server should maintain a database table with columns
    # "identifier" and "file_path", so that a reverse from file_path to identifier is possible

    # Something like:
    # import requests
    # url='http://nesssi.cacr.caltech.edu/cgi-bin/getmulticonedb_release2.cgi/post'
    # files={'files': open('file.txt','rb')}
    # values={'upload_file' : 'file.txt' , 'DB':'photcat' , 'OUT':'csv' , 'SHORT':'short'}
    # r=requests.post(url,files=files,data=values)

    # We temporarily store file in project directory for now for development's sake.
    # TODO: migrate store code once CDN server is ready

    file = file_obj.file  # this is the "files" data to send in requests.get()
    print(type(file_obj), type(file))  # <class 'django.core.files.uploadedfile.TemporaryUploadedFile'>
    # <class 'django.core.files.temp.TemporaryFile'>
    print(file_obj.temporary_file_path())  # C:\Users\Administrator\AppData\Local\Temp\_83aul64.upload.pdf

    # CDN server decides what filename it will use for this file
    file_name = file_obj.name
    root, ext = os.path.splitext(file_name)  # get suffix of file
    random_pool = string.ascii_letters + string.digits  # pool for generating random filename
    random_length = 10  # random filename length
    identifier = "".join(random.choices(random_pool, k=random_length)) + ext  # filename_in_cdn

    # Write file to disk
    project_dir = os.getcwd()  # assume we always start server in cwd
    base_dir = os.path.join(project_dir, "var", "www", "cdn")
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    file_path = os.path.join(base_dir, identifier)
    # in case of a collision
    while os.path.exists(file_path):
        identifier = "".join(random.choices(random_pool, k=random_length)) + ext
        file_path = os.path.join(base_dir, identifier)

    # FileNotFoundError: [Errno 2] No such file or directory:
    # 'C:\\Users\\Administrator\\AppData\\Local\\Temp\\_83aul64.upload.pdf'
    file = open(file_obj.temporary_file_path(), "rb")

    with open(file_path, "wb") as f:
        while chunk := file.read(1024):
            f.write(chunk)
    return file_path
