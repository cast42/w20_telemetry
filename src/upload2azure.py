"""Zip a local directory and upload to a blob storage on Azure"""

import logging
import logging.handlers
import os
import time
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union

import schedule

# from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import dotenv_values, find_dotenv
from tenacity import RetryError, retry, stop_after_attempt, wait_fixed

# pip install -f requirements.txt
# pip install azure-storage-blob azure-identity python-dotenv tenacity schedule


# Based on https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=managed-identity%2Croles-azure-portal%2Csign-in-azure-cli

# Create a .env file with
# ACCOUNT_NAME=GRAB_IT_FROM_AZURE_PORTAL
# SAS_TOKEN=GRAB_IT_FROM_AZURE_PORTAL
# CONTAINER_NAME=GRAB_IT_FROM_AZURE_PORTAL


@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def upload_to_blob_storage(
    local_filepath: str,
    remote_blob_file_name: str,
    config: dict,
    logger: logging.Logger,
):
    """
    Uploads a local file to a remote Azure Blob.
    """
    try:
        # blob_service_client = BlobServiceClient.from_connection_string(
        #     config["CONNECTION_STRING"]
        # )
        blob_service_client = BlobServiceClient(
            account_url=f"https://{config['ACCOUNT_NAME']}.blob.core.windows.net",
            credential=config["SAS_TOKEN"],
        )
        blob_client = blob_service_client.get_blob_client(
            container=config["CONTAINER_NAME"], blob=remote_blob_file_name
        )
        logger.debug(f"Start uploading to blob {config['CONTAINER_NAME']=}.")
        zipfile_content_setting = ContentSettings(content_type="application/zip")
        with open(local_filepath, "rb") as data:
            blob_client.upload_blob(
                data, overwrite=True, content_settings=zipfile_content_setting
            )
        logger.debug(f"Uploading {local_filepath} to blob done.")
    except Exception as e:
        logger.error(f"Error occurred while uploading local file {local_filepath}: {e}")
        raise e
    logger.debug(
        f"Local file {local_filepath} uploaded successfully"
        f" to {remote_blob_file_name} blob in {config['CONTAINER_NAME']} container."
    )


def zip_dir(dir_name: Union[str, os.PathLike], logger: logging.Logger) -> str:
    """
    Zips the directory wiht name dir_name into a file 'dirname'.zip .
    If the zipfile already excists it will be overwritten.
    """
    if isinstance(dir_name, str):
        dir_path = Path(dir_name)
    elif isinstance(dir_name, os.PathLike):
        dir_path = dir_name
    else:
        raise TypeError("url must be a string or a path object")
    if not dir_path.exists():
        logger.error(f"Directory {dir_path.as_posix()} does not exists.")
        return ""

    zipf_file_path = dir_path.with_suffix(".zip")

    # Create a ZipFile object
    zipf = zipfile.ZipFile(zipf_file_path.as_posix(), "w", zipfile.ZIP_DEFLATED)

    # Walk through the directory and add all files to the zip file
    for root, dirs, files in os.walk(dir_name):
        for file in files:
            zipf.write(os.path.join(root, file))

    # Close the ZipFile
    zipf.close()
    return zipf_file_path


def getLogger() -> logging.Logger:
    """
    Creates a logging object and returns it for logging.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger_file_handler = logging.handlers.RotatingFileHandler(
        "upload2azure.log",
        maxBytes=1024 * 1024,
        backupCount=1,
        encoding="utf8",
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger_file_handler.setFormatter(formatter)
    logger.addHandler(logger_file_handler)
    return logger


def upload_data_directory(directory_path: Union[str, os.PathLike]) -> None:
    """
    Creates a zipfile in directory directory_path of current date minus 1 day.
    For example if today is 08-06-2023, a zipfile 07062023.zip will be created.
    That zipfile is uploaded to Azure blob storage.
    By default, the local file or remote blob are overwritten if they already exists.
    In case the upload fails, the function retries a number of times.
    After 5 times, it logs an error in the log file and quits silently.
    The zipfile remains in the local file system.
    """
    if isinstance(directory_path, str):
        dir_path = Path(directory_path)
    elif isinstance(directory_path, os.PathLike):
        dir_path = directory_path
    else:
        raise TypeError(
            "directory_path argument must be a string or a path object "
            f"but is {directory_path}."
        )

    now = datetime.now()
    date_string = now.strftime("%d%m%Y")
    try:
        logger = getLogger()
    except Exception as e:
        logger.error(f"Could not initiate logger. Error: {e}")
        return
    if not dir_path.exists():
        logger.error(f"Directory {dir_path.as_posix()} does not exists.")
        return
    try:
        config = dotenv_values(find_dotenv())
    except Exception as e:
        logger.error(f"Could not load environemnt .env Error:{e}")
        return
    try:
        directory_name = (
            datetime.strptime(date_string, "%d%m%Y") - timedelta(days=1)
        ).strftime("%d%m%Y")
    except Exception as e:
        logger.error(f"Date argument {date_string} is not in %d%m%Y format. Error: {e}")
        return
    directory_name_path = dir_path / Path(directory_name)
    if not directory_name_path.exists():
        logger.error(f"Directory {directory_name_path} does not exists.")
        return
    zip_file_path = zip_dir(directory_name_path, logger)
    if not zip_file_path.exists():
        logger.error(f"Zip File {zip_file_path.as_posix()} is not created.")
        return
    try:
        logger.debug(
            f"Upload local file {zip_file_path=}"
            f"to Azure blog with name {zip_file_path.name=}."
        )
        upload_to_blob_storage(zip_file_path, zip_file_path.name, config, logger)
    except RetryError:
        logger.error("Maximum number of retries reached.")


if __name__ == "__main__":
    schedule.every().day.at("04:30").do(upload_data_directory, directory_path="./")

    while True:
        schedule.run_pending()
        time.sleep(10)
