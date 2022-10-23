from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from auth import sign_in, authenticate
from firestore import create_process, retrieve_process, process,  insert_document, insert_serfie, delete_serfie, delete_document
from storage import saveImage
import logging as logger


app = FastAPI(debug=True)


def authMiddleware(token):
    tokenParts = token.split(' ')
    isAuth = authenticate(tokenParts[1])
    if isAuth is None:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/signin")
def create_token_resource(request: Request):
    clientId = request.headers.get('clientId')
    clientSecret = request.headers.get('clientSecret')
    token = sign_in(clientId, clientSecret)

    if token is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"token": token}


@app.post("/process")
def create_process_resource(request: Request):
    bearer_token = request.headers.get('Authorization')
    authMiddleware(bearer_token)
    process_id = create_process()
    return {"processId": process_id}


@app.post("/process/{process_id}", status_code=204)
def process_resource(request: Request, process_id):
    bearer_token = request.headers.get('Authorization')
    authMiddleware(bearer_token)
    try:
        process(process_id)
    except Exception as e:
        logger.error('m=process_resource stage=error e={}'.format(e))
        raise HTTPException(status_code=500, detail="Error")


@app.get("/process/{process_id}")
def retrieve_process_resource(request: Request, process_id):
    bearer_token = request.headers.get('Authorization')
    authMiddleware(bearer_token)
    process = retrieve_process(process_id)

    if process is None:
        raise HTTPException(status_code=404, detail="Process not found")
    else:
        return process


@app.post("/process/{process_id}/selfie")
def upload_image_resource(selfie: UploadFile, request: Request, process_id):
    bearer_token = request.headers.get('Authorization')
    authMiddleware(bearer_token)
    file_name = saveImage(process_id, selfie)
    if file_name is None:
        raise HTTPException(status_code=500, detail="Failed to upload document, please try again later")

    try:
        insert_serfie(process_id, file_name)
        return {"fileName": file_name}
    except Exception as e:
        logger.error('m=upload_document_resource stage=error e={}'.format(e))
        raise HTTPException(status_code=500, detail="Failed to save selfie")


@app.post("/process/{process_id}/document")
def upload_document_resource(document: UploadFile, request: Request, process_id):
    bearer_token = request.headers.get('Authorization')
    authMiddleware(bearer_token)
    file_name = saveImage(process_id, document)
    if file_name is None:
        raise HTTPException(status_code=500, detail="Failed to upload document, please try again later")

    try:
        insert_document(process_id, file_name)
        return {"fileName": file_name}
    except Exception as e:
        logger.error('m=upload_document_resource stage=error e={}'.format(e))
        raise HTTPException(status_code=500, detail="Failed to save document")

@app.delete("/process/{process_id}/document/{file_name}", status_code=204)
def delete_document_resource(request: Request, process_id, file_name):
    bearer_token = request.headers.get('Authorization')
    authMiddleware(bearer_token)    
    try:
        delete_document(process_id, file_name)
    except Exception as e:
        logger.error('m=delete_document_resource stage=error e={}'.format(e))
        raise HTTPException(status_code=500, detail="Failed to delete document")

    
@app.delete("/process/{process_id}/selfie/{file_name}", status_code=204)
def delete_selfie_resource(request: Request, process_id, file_name):
    bearer_token = request.headers.get('Authorization')
    authMiddleware(bearer_token)    
    try:
        delete_serfie(process_id, file_name)
    except Exception as e:
        logger.error('m=delete_selfie_resource stage=error e={}'.format(e))
        raise HTTPException(status_code=500, detail="Failed to delete selfie")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=6662, reload=True, debug=True)
