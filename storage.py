from firebase_admin import storage
import logging as logger
import uuid
import io

def saveImage(process_id, file):
    logger.error('m=saveImage stage=init process_id={}'.format(process_id))
    if file.content_type != 'image/png' and file.content_type != 'image/jpeg':
        logger.error('m=saveImage stage=error Image with invalid format {}'.format(file.content_type))
        return None

    file_name = '{}_{}'.format(process_id, uuid.uuid4())
    imageBytes = io.BytesIO(file.file.read())
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    blob.upload_from_string(imageBytes.read(), content_type=file.content_type)
    logger.error('m=saveImage stage=end file_name={}'.format(file_name))
    return file_name
# https://stackoverflow.com/questions/46163940/upload-image-received-via-flask-to-firebase-storage
