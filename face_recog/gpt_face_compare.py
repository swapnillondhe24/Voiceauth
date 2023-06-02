import cv2
import dlib
import numpy as np
from skimage import io

# Load the face detector and shape predictor from dlib
face_detector = dlib.get_frontal_face_detector()

try:
    shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
except:
    shape_predictor = dlib.shape_predictor("face_recog/shape_predictor_68_face_landmarks.dat")  

# Function to extract face embeddings
def get_face_embeddings(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_detector(gray)

    face_embeddings = []
    # Iterate over detected faces
    for face in faces:
        # Determine the facial landmarks for the face region
        shape = shape_predictor(gray, face)

        # Compute the face descriptor using the shape of the face
        face_descriptor = np.array(shape_to_vector(shape))

        face_embeddings.append(face_descriptor)

    return face_embeddings

# Convert shape object to a numpy array
def shape_to_vector(shape, dtype=np.float64):
    num_parts = shape.num_parts
    vector = np.zeros(2 * num_parts, dtype=dtype)
    for i in range(num_parts):
        vector[i] = shape.part(i).x
        vector[i + num_parts] = shape.part(i).y
    return vector

# Function to compare face embeddings
def compare_faces(face1, face2):
    try: 
        image1 = io.imread(face1)
        image2 = io.imread(face2)
    except:
        print("Could not read input images")
        return False

# Get the face embeddings for each image
    faces1 = get_face_embeddings(image1)
    faces2 = get_face_embeddings(image2)

    distances = []
    # Calculate the Euclidean distances between the face embeddings
    for face1 in faces1:
        for face2 in faces2:
            distance = np.linalg.norm(face1 - face2)
            distances.append(distance)

    # If any distance is below the threshold, faces are considered the same
    threshold = 0.6
    if min(distances) < threshold:
        return True
    else:
        return False


if __name__ == "__main__":
    # Load the input images
    image1_path = "image1.jpg"
    image2_path = "image2.jpg"

    # Compare the faces
    result = compare_faces(image1_path, image2_path)

    # Print the result
    if result:
        print("The faces are the same.")
    else:
        print("The faces are different.")
