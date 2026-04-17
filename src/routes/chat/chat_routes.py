import hashlib
import os
import shutil
import tempfile

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from errors.domain_errors import DocumentNotReceived, DuplicateDocumentError
from models.conversations.conversations_model import ConversationCreate
from models.messages.messages_model import MessageCreate
from services.conversations.conversations_service import conversations_service
from services.document.document_service import document_service
from services.messages.messages_service import message_service
from services.plan.plan_service import plan_service
from services.upload_files.upload_files_service import upload_file_to_supabase
from workers.generic_worker import process_document_generic
from workers.process_and_answer_worker import process_and_answer_worker

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/new")
async def create_new_chat(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    content: str = Form(""),
    file: UploadFile = File(...),
):
    try:
        has_file = file is not None
        has_question = bool(content and content.strip())

        conversation = await conversations_service.create_conversation(
            ConversationCreate(user_id=user_id, title="New chat")
        )

        if not has_file:
            raise DocumentNotReceived("File is required")

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name

        size_mb = os.path.getsize(temp_path) / (1024 * 1024)

        await plan_service.validate_document_upload(user_id, size_mb)

        hasher = hashlib.sha256()
        with open(temp_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()

        if await document_service.exists_by_hash(user_id, file_hash):
            os.remove(temp_path)
            raise DuplicateDocumentError("File already uploaded")

        document = await run_in_threadpool(
            upload_file_to_supabase,
            temp_path,
            file.filename,
            file_hash,
            file.content_type,
            user_id,
            "processing",
        )

        os.remove(temp_path)

        message_send = await message_service.create_message(
            MessageCreate(
                role="user",
                content=content,
                document_id=document.id,
                conversation_id=conversation.id,
            )
        )

        message_response = await message_service.create_message(
            MessageCreate(
                role="assistant",
                content="Processing...",
                document_id=document.id,
                conversation_id=conversation.id,
            )
        )

        if has_question:
            background_tasks.add_task(
                process_and_answer_worker,
                document.id,
                document.storage_path,
                content,
                document.type,
                user_id,
                size_mb,
                conversation.id,
                message_response.id,
            )
        else:
            plan = await plan_service.get_user_plan_by_id(user_id)

            background_tasks.add_task(
                process_document_generic,
                document.id,
                plan,
                document.storage_path,
                document.type,
                user_id,
                size_mb,
                conversation.id,
                message_response.id,
            )

        return {"message_response": message_response, "message_send": message_send}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def get_all_conversation(user_id: str):
    try:
        response = await conversations_service.get_conversation_by_user_id(user_id)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error {e}")


@router.get("/{conversation_id}")
async def get_message_of_current_conversation(conversation_id: str):
    try:
        response = await message_service.get_message_by_conversation_id(conversation_id)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error {e}")


@router.delete("/delete/{conversation_id}")
async def delete_conversation(conversation_id: str):
    try:
        response = await conversations_service.delete_conversation_by_id(
            conversation_id
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error {e}")


@router.put("/message")
async def send_message(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    conversation_id: str = Form(...),
    content: str = Form(""),
    file: UploadFile = File(...),
):
    try:
        has_question = bool(content and content.strip())

        exists = (
            await conversations_service.validate_conversation_exists_by_conversation_id(
                conversation_id, user_id
            )
        )

        if not exists:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or does not belong to the user ",
            )

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name

        size_mb = os.path.getsize(temp_path) / (1024 * 1024)

        await plan_service.validate_document_upload(user_id, size_mb)

        plan = await plan_service.get_user_plan_by_id(user_id)

        hasher = hashlib.sha256()
        with open(temp_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        file_hash = hasher.hexdigest()

        exists = await document_service.exists_by_hash(user_id, file_hash)

        if exists:
            os.remove(temp_path)
            raise DuplicateDocumentError(
                message="You already uploaded this file",
                details={"filename": file.filename},
            )

        if not file.filename or not file.content_type:
            raise DocumentNotReceived("No se obtuvo correntamente el archivo")

        document = await run_in_threadpool(
            upload_file_to_supabase,
            temp_path,
            file.filename,
            file_hash,
            file.content_type,
            user_id,
            "processing",
        )

        os.remove(temp_path)

        message_send = await message_service.create_message(
            MessageCreate(
                role="user",
                content=content,
                document_id=document.id,
                conversation_id=conversation_id,
            )
        )

        message_response = await message_service.create_message(
            MessageCreate(
                role="system",
                content="Procesando archivo. Por favor espere un momento........",
                document_id=document.id,
                conversation_id=conversation_id,
            )
        )

        if has_question:
            background_tasks.add_task(
                process_and_answer_worker,
                document.id,
                document.storage_path,
                content,
                document.type,
                user_id,
                size_mb,
                conversation_id,
                message_response.id,
            )
        else:
            background_tasks.add_task(
                process_document_generic,
                document.id,
                plan,
                document.storage_path,
                document.type,
                user_id,
                size_mb,
                conversation_id,
                message_response.id,
            )

        return {
            "message_id": message_send.id,
            "status": "processing",
            "message": message_response,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error new chat {e}")
