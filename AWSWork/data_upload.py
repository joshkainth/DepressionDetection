import os
import json
import boto3
from botocore.exceptions import ClientError
import psycopg2

def fetchData(): 
    jsonFile = open("AWSWork/config-database.json", "r")
    dbConfig = json.load(jsonFile)

    conn = None
    try: 
        conn = psycopg2.connect(f"dbname={dbConfig['dbName']} user={dbConfig['user']} password={dbConfig['password']}")
        cursor = conn.cursor()

        cursor.execute("SELECT * from data")
        response = cursor.fetchall()
        return response

    except Exception as exception:
        print(exception)
        return None
    finally: 
        conn.close()

def fetchParticularRecordFromPostGreSQL(audio_name):
    print(audio_name)
    if audio_name is "":
        return None 

    jsonFile = open("AWSWork/config-database.json", "r")
    dbConfig = json.load(jsonFile)

    conn = None
    try: 
        conn = psycopg2.connect("dbname={0} user={1} password={2}".format(dbConfig['dbName'], dbConfig['user'], dbConfig['password']))
        cursor = conn.cursor()

        sql = "SELECT * FROM data where audio_name='{0}'".format(audio_name)
        cursor.execute(sql)
        response = cursor.fetchall()
        return response

    except Exception as exception:
        print(exception)
        return None
    finally: 
        conn.close()

def saveRecordOnPostGreSQL(audioRes, imageRes):
    jsonFile = open("AWSWork/config-database.json", "r")
    dbConfig = json.load(jsonFile)

    conn = None
    try: 
        conn = psycopg2.connect(f"dbname={dbConfig['dbName']} user={dbConfig['user']} password={dbConfig['password']}")
        cursor = conn.cursor()

        sql_query = "insert into data (audio_name, audio_s3_key, audio_url, image_name, image_s3_key, image_url) values (%s, %s, %s, %s, %s, %s)"
        row_data  = (audioRes['file'], audioRes['s3_file_key'], audioRes['s3_file_url'], imageRes['file'], imageRes['s3_file_key'], imageRes['s3_file_url'])
        cursor.execute(sql_query, row_data)

        conn.commit()
        count = cursor.rowcount
        print(count, "Record inserted successfully into data table")

    except Exception as exception:
        print(exception)
    finally: 
        conn.close()

def uploadFileOnS3(file, fileDirPath, audioBool): 
    jsonFile = open("AWSWork/config-aws.json", 'r')
    awsConfig = json.load(jsonFile)

    folderName = awsConfig['audio_folder_name'] if audioBool else awsConfig['image_folder_name']
    mimeType = 'audio/mpeg' if audioBool else 'image/png'
    client_s3 = boto3.client(
        's3',
        aws_access_key_id = awsConfig['access_key'],
        aws_secret_access_key = awsConfig['access_secret']
    )
    try: 
        client_s3.upload_file(
            os.path.join(fileDirPath, file), 
            awsConfig['bucket_name'], 
            "{}/{}/{}".format(awsConfig['root_folder_name'], folderName, file),
            ExtraArgs={
                'ACL': 'public-read', # Public Read
                'ContentType': mimeType,
            }
        )

        s3Key = f"s3://{awsConfig['bucket_name']}/{awsConfig['root_folder_name']}/{folderName}/{file}" # S3 Key of Uploaded File
        s3FileUrl = f"https://{awsConfig['bucket_name']}.s3.{awsConfig['aws_region']}.amazonaws.com/{awsConfig['root_folder_name']}/{folderName}/{file}" # URL of uploaded file
        return {
            "file": file,
            "s3_file_key": s3Key,
            "s3_file_url": s3FileUrl
        }
    except ClientError as clientError:
        print(">>> Client Error: \t" + clientError)
        return None
    except Exception as exception:
        print(">>> Excepetion: \t" + exception)
        return None

def readImageFiles(root_data_dir_path, fileName):
    images_dir_path = os.path.join(root_data_dir_path, "depressed_mels")
    for imageFile in os.listdir(images_dir_path):
        if imageFile == fileName:
            return {
                "imageFile": imageFile,
                "imageDirPath": images_dir_path
            }
    
    return None

def readAudioFiles():
    root_data_dir_path = os.path.join(os.getcwd(), "AWSWork/depressed_data")
    audio_data_dir_path = os.path.join(root_data_dir_path, "depressed_audios")

    for audioFile in os.listdir(audio_data_dir_path):
        audioFileName = audioFile.split(".")[0]
        imageFileName = f"Mel_{audioFileName}.png"

        imageResponse = readImageFiles(root_data_dir_path, imageFileName)
        audioUploadResponse = uploadFileOnS3(audioFile, audio_data_dir_path, True)
        imageUploadResponse = uploadFileOnS3(imageResponse["imageFile"], imageResponse["imageDirPath"], False)

        print(">>> Audio Upload Response: \t{0}".format(audioUploadResponse))
        print(">>> Image Upload Response: \t{0}".format(imageUploadResponse))
        # saveRecordOnPostGreSQL(audioUploadResponse, imageUploadResponse)
        print()
        

readAudioFiles()

print(os.getcwd())