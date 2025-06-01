import time
import azure.functions as func
import logging, os
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.vision.face import FaceAdministrationClient, FaceClient
from azure.ai.vision.face.models import FaceAttributeTypeRecognition04, FaceDetectionModel, FaceRecognitionModel, QualityForRecognition

KEY = os.environ["FACE_APIKEY"]
ENDPOINT = os.environ["FACE_ENDPOINT"]

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="enrollStudent", methods=["POST"])
def enrollStudent(req: func.HttpRequest) -> func.HttpResponse:
    try:
        real_image_bytes = req.get_body()

        if not real_image_bytes:
            return func.HttpResponse("No image provided", status_code=400)

        student_id = req.params.get('student_id').lower()

        LARGE_PERSON_GROUP_ID = str(req.params.get('cur_class').lower())

        with FaceAdministrationClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY)) as face_admin_client, \
        FaceClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY)) as face_client:
            '''
            Create the LargePersonGroup
            '''
            # Create empty Large Person Group. Large Person Group ID must be lower case, alphanumeric, and/or with '-', '_'.
            try: 
                face_admin_client.large_person_group.create(
                    large_person_group_id=LARGE_PERSON_GROUP_ID,
                    name=LARGE_PERSON_GROUP_ID,
                    recognition_model=FaceRecognitionModel.RECOGNITION04,
                )
            except:
                logging.info(f"Person group: {LARGE_PERSON_GROUP_ID} already exists")
                
            # Define student
            student = face_admin_client.large_person_group.create_person(
                large_person_group_id=LARGE_PERSON_GROUP_ID,
                name=student_id,
            )

            # Check if the image is of sufficent quality for recognition.
            detected_faces = face_client.detect(
                image_content=real_image_bytes,
                detection_model=FaceDetectionModel.DETECTION03,
                recognition_model=FaceRecognitionModel.RECOGNITION04,
                return_face_id=True,
                return_face_attributes=[FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION],
            )

            if not detected_faces:
                return func.HttpResponse("No faces in the image", status_code=400)
            
            if len(detected_faces) > 1:
                return func.HttpResponse("Only one face is allowed", status_code=400)
            
            for face in detected_faces:
                if face.face_attributes.quality_for_recognition != QualityForRecognition.HIGH:
                    return func.HttpResponse("Image quality not sufficient", status_code=400)

            face_admin_client.large_person_group.add_face(
                large_person_group_id=LARGE_PERSON_GROUP_ID,
                person_id=student.person_id,
                image_content=real_image_bytes,
                detection_model=FaceDetectionModel.DETECTION03,
            )

            # Train the large person group and set the polling interval to 5s
            face_admin_client.large_person_group.begin_train(
                large_person_group_id=LARGE_PERSON_GROUP_ID,
                polling_interval=5,
            )


            return func.HttpResponse("trainig completed", status_code=200)
        
    except Exception as e:
        # error_code = e.error.code if e.error else "UnknownError"
        # error_message = e.error.message if e.error else str(e)
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=400
        ) 