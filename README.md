# Enroll Student - Azure Function

This **Azure Function** handles the enrollment of a student into the **Azure Face API** Person Group, enabling face recognition capabilities for applications like automated attendance systems.

The function receives a student's **image** and **ID** (along with the class ID), checks the image quality, and registers the student in a designated **Large Person Group** within Azure Face API.

---

## 🚀 Function Overview

- **Trigger Type:** HTTP (anonymous access)
- **Method:** POST
- **Route:** `/enrollStudent`
- **Consumes:** Binary image (`image/jpeg` or `image/png`) as body + query parameters
- **Dependencies:**  
  - `azure-functions`  
  - `azure-core`  
  - `azure-ai-vision-face`

---

## 🧠 How It Works

1. **Input:**
   - Request body: binary image data (the student’s face)
   - Query parameters:
     - `student_id`: unique ID for the student (e.g., `"s12345"`)
     - `cur_class`: class name or identifier (e.g., `"cs101"`)

2. **Logic:**
   - If the class’s Person Group doesn’t exist, it is created.
   - A new person is added with the provided `student_id`.
   - The face image is validated for quality (must contain **only one high-quality face**).
   - The face is added to the person in the Person Group.
   - The Person Group is trained to include the new face.

3. **Output:**
   - `200 OK` – Student enrolled and training completed
   - `400 Bad Request` – Error messages for:
     - Missing image
     - No face detected
     - Multiple faces
     - Poor image quality
     - Other exceptions

---

## 🌐 Example Request

**POST** `/api/enrollStudent?student_id=12345&cur_class=I4`  
**Headers:** `Content-Type: image/jpeg`  
**Body:** binary image (JPEG/PNG)

---

## 🛠️ Local Development

To run the function locally:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables in local.settings.json:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "FACE_APIKEY": "<your-face-api-key>",
    "FACE_ENDPOINT": "<your-face-api-endpoint>"
  }
}
```

3. Start the local function host:
```bash
func start
```

## Refrences:
- [Azure Face API](https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/overview-identity)
- [Azure Functions Python Developer Guide](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python)