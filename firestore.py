import firebase_admin
import uuid
import random
import threading
import logging as logger
from datetime import timedelta, datetime
from firebase_admin import credentials, firestore

cred = credentials.Certificate('./serviceAccount.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'estagio-opus.appspot.com'
})
db = firestore.client()
photos_ref = db.collection('photos')


def register_results(results):
    logger.error('m=registerResults stage=init results={}'.format(results))
    photos_ref.document(uuid.uuid4()).set(results)
    logger.error('m=registerResults stage=end')


def create_process():
    logger.error('m=create_process stage=init')
    process_id = str(uuid.uuid4())
    photos_ref.document(process_id).set({'createdAt': firestore.SERVER_TIMESTAMP, 'documents': [], 'selfies': []})
    logger.error('m=create_process stage=end process_id={}'.format(process_id))
    return process_id


def retrieve_process(process_id):
    logger.error(
        'm=retrieve_process stage=init process_id={}'.format(process_id))
    doc = photos_ref.document(process_id).get()
    if doc.exists:
        logger.error(
            'm=retrieve_process stage=end process_retrieved={}'.format(doc.to_dict()))
        return doc.to_dict()
    else:
        return None


def insert_document(process_id, file_name):
    logger.error('m=insert_document stage=init process_id={} file_name={}'.format(process_id, file_name))
    doc_ref = photos_ref.document(process_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        doc_ref.update({
            'documents': firestore.ArrayUnion([{'fileName': file_name, 'status': 'NOT_VALIDATED'}])
        })
        logger.error(
            'm=insert_document stage=end process_retrieved={}'.format(data))
    else:
        raise Exception('Erro on associate process id {} to file {}'.format(
            process_id, file_name))


def insert_serfie(process_id, file_name):
    logger.error('m=insert stage=init process_id={} file_name={}'.format(process_id, file_name))
    doc_ref = photos_ref.document(process_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        doc_ref.update({
            'selfies': firestore.ArrayUnion([{'fileName': file_name, 'status': 'NOT_VALIDATED'}])
        })
        logger.error('m=insert stage=end process_retrieved={}'.format(data))
    else:
        raise Exception('Erro on associate process id {} to file {}'.format(process_id, file_name))


def delete_serfie(process_id, file_name):
    logger.error('m=delete_serfie stage=init process_id={} file_name={}'.format(process_id, file_name))
    doc_ref = photos_ref.document(process_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        
        item = None
        for selfie in data['selfies']:
            if selfie['fileName'] == file_name:
                item = selfie
        if item == None:
            logger.error('m=delete_serfie stage=end Selfie not found {}'.format(file_name))
            raise Exception()
        
        doc_ref.update({
            'selfies': firestore.ArrayRemove([item])
        })
        logger.error('m=delete_serfie stage=end process_retrieved={}'.format(data))
    else:
        raise Exception('Erro on delete process id {} to file {}'.format(process_id, file_name))

def delete_document(process_id, file_name):
    logger.error('m=delete_document stage=init process_id={} file_name={}'.format(process_id, file_name))
    doc_ref = photos_ref.document(process_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        
        item = None
        for document in data['documents']:
            if document['fileName'] == file_name:
                item = document
        if item == None:
            logger.error('m=delete_document stage=end Document not found {}'.format(file_name))
            raise Exception()
        
        doc_ref.update({
            'documents': firestore.ArrayRemove([item])
        })
        logger.error('m=delete_document stage=end process_retrieved={}'.format(data))
    else:
        raise Exception('Erro on delete process id {} to file {}'.format(process_id, file_name))

def process(process_id):
    logger.error('m=process stage=init process_id={}'.format(process_id))
    now = datetime.now()
    randomDelta = random.randint(0, 60)
    run_at = now + timedelta(seconds=randomDelta)
    delay = (run_at - now).total_seconds()
    threading.Timer(delay, processor, args=(process_id, )).start()
    logger.error('m=process stage=end delta={} seconds'.format(randomDelta))

def processor(process_id):
    logger.error('m=processor stage=init process_id={}'.format(process_id))
    doc_ref = photos_ref.document(process_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        selfieResults = data['selfies']
        documentsResults = data['documents']

        for selfie in selfieResults:
            if selfie['status'] == 'NOT_VALIDATED':
                selfie['status'] = changing_status()

        for documents in documentsResults:
            if documents['status'] == 'NOT_VALIDATED':
                documents['status'] = changing_status()

        doc_ref.update({
            'selfies': selfieResults,
            'documents': documentsResults,
        })
        logger.error('m=processor stage=end')
    else:
        raise Exception('Erro on process id {}'.format(process_id))
    
def changing_status():
    rand = random.randint(0, 100)
    if rand < 80:
        return 'APR'
    if rand < 90:
        return 'PEN'
    return 'NEG'