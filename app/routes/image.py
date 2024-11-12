import base64
import io
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
from flasgger import swag_from
from app import db
from app.models.image import  ImageModel
from app.models.user import User
from app.utils.auth_helpers import check_token_revoked
import numpy as np
from PIL import Image

import cv2

image_api = Blueprint('image_api', __name__)

# =====================================================================================================
#                                  Creating a Image From User
# ======================================================================================================
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@image_api.route('/create_image', methods=['POST'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Image'],
    'summary': 'Create a New Image',
    'description': 'Creates a new image entry for the authenticated user',
    'parameters': [
        {
            'name': 'image_file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'Image file to upload'
        },
        {
            'name': 'image_name',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Name of the image'
        }
    ],
    'responses': {
        201: {
            'description': 'Image created successfully'
        },
        400: {
            'description': 'Invalid request data'
        },
        401: {
            'description': 'Unauthorized access'
        }
    },
    'security': [{'Bearer': []}]
})

def create_image():
    user_id = get_jwt_identity()

    # Fetch the user from the database
    user = User.query.filter_by(username=user_id).first()
    print("user",user)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Check if an image file is provided
    if 'image_file' not in request.files:
        return jsonify({'message': 'No image file part'}), 400

    # Get the image file and image name from the request
    image_file = request.files['image_file']
    image_name = request.form.get('image_name')

    if not image_name:
        return jsonify({'message': 'Missing image name'}), 400

    # Read the image file content
    image_data = image_file.read()

    # Create a new Image instance and associate it with the user
    new_image = ImageModel(image_name=image_name, image_data=image_data, user=user)  # This should be valid

    db.session.add(new_image)
    db.session.commit()

    return jsonify({'message': 'Image uploaded successfully'}), 201
# ======================================================================================================================
#                                    Update in Image Files
# ======================================================================================================================

@image_api.route('/update_image/<int:id>', methods=['PUT'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Image'],
    'summary': 'Update an Image',
    'description': 'Update details of a specific image for the authenticated user',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the image to update'
        },
        {
            'in': 'formData',  # Change 'name' to 'in'
            'type': 'object',
            'required': False,
            'schema': {
                'type': 'object',
                'properties': {
                    'image_name': {
                        'type': 'string',
                        'description': 'New name for the image'
                    },
                    'image_file': {
                        'type': 'file',
                        'description': 'New image file'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Image updated successfully'
        },
        400: {
            'description': 'Invalid request data'
        },
        401: {
            'description': 'Unauthorized access'
        },
        404: {
            'description': 'Image not found'
        }
    },
    'security': [{'Bearer': []}]
})
def update_image(id):
    # Retrieve the image from the database
    image = ImageModel.query.filter_by(id=id).first()

    if not image:
        return jsonify({'message': 'Image not found'}), 404

    # Update the image data if a new image is uploaded
    if 'image_file' in request.files:
        image_file = request.files['image_file']
        image.image_data = image_file.read()

    # Update the image name if provided
    if 'image_name' in request.form:
        image.image_name = request.form['image_name']

    # Commit the changes to the database
    db.session.commit()

    # Convert the image data to base64 for JSON serialization
    image_data_base64 = base64.b64encode(image.image_data).decode('utf-8')

    # Return the updated image data
    return jsonify({
        'id': image.id,
        'image_name': image.image_name,
        'image_data': image_data_base64  # Return base64 encoded image data
    }), 200
# ====================================================================================================================
#                                                   List All Images
# ====================================================================================================================

@image_api.route('/list_all_images', methods=['Get'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Image'],
    'summary': 'List all Images for a User',
    'description': 'Retrieve a list of all image entries for the authenticated user',
    'responses': {
        200: {
            'description': 'List of images',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': 'ID of the image entry'},
                        'image_data': {'type': 'string', 'description': 'Image Base64 encoded'},
                        'image_name': {'type': 'string', 'description': 'Name of the image'}
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized access'
        }
    },
    'security': [{'Bearer': []}]
})
def list_all_image():
    user_id = get_jwt_identity()
    user = User.query.filter_by(username=user_id).first()
    image_data = ImageModel.query.filter_by(user=user).all()  # Use ImageModel, not Image

    data_list = []
    if image_data:
        for data in image_data:
            binary_data = data.image_data

            # Decode the binary data into an image using PIL's Image class
            image = Image.open(io.BytesIO(binary_data))

            # Convert the image to a base64 string
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')  # Or 'JPEG', depending on your format
            img_byte_arr = img_byte_arr.getvalue()
            image_base64 = base64.b64encode(img_byte_arr).decode('utf-8')  # Convert to base64 string

            data_dict = {
                'id': data.id,
                'image_name': data.image_name,
                'image_data': image_base64  # Return base64 encoded image data
            }
            data_list.append(data_dict)

    return jsonify(data_list)

# =====================================================================================================================
#                      Get a Specific Image and Generating Color Histograms and Segmentation Masks,
# =====================================================================================================================

@image_api.route('/get_image/<int:id>', methods=['GET'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Image'],
    'summary': 'Get and Analyze Image',
    'description': 'Retrieve and analyze a specific image for the authenticated user',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the image to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Image analysis results',
            'schema': {
                'type': 'object',
                'properties': {
                    'histogram': {
                        'type': 'array',
                        'description': 'Flattened color histogram of the image',
                        'items': {
                            'type': 'integer',
                            'description': 'Frequency of a specific color channel value (e.g., red, green, blue)'
                        }
                    },
                    'segmentation_mask': {
                        'type': 'array',
                        'description': 'Segmentation mask (example: binary threshold)',
                        'items': {
                            'type': 'integer',
                            'description': 'Pixel intensity value (0 or 1 in case of binary threshold)'
                        }
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized access'
        },
        404: {
            'description': 'Image not found'
        }
    },
    'security': [{'Bearer': []}]
})
def get_image(id):
    image_data = ImageModel.query.filter_by(id=id).first()

    if not image_data:
        return jsonify({'error': 'Data not found'}), 404

    image = Image.open(io.BytesIO(image_data.image_data))

    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    hist = cv2.calcHist([image_cv], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

    hist_flattened = hist.flatten()

    ret, thresh = cv2.threshold(image_cv, 127, 255, cv2.THRESH_BINARY)

    segmentation_mask = thresh.tolist()


    return jsonify({
        'histogram': hist_flattened.tolist(),
        'segmentation_mask': segmentation_mask
    })

# ==================================================================================================================
#                                Delete Specific Image
# ==================================================================================================================

@image_api.route('/delete_image/<int:id>', methods=['DELETE'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Image'],
    'summary': 'Delete an Image',
    'description': 'Deletes a specific image for the authenticated user',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the image to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Image deleted successfully'
        },
        401: {
            'description': 'Unauthorized access'
        },
        404: {
            'description': 'Image not found'
        }
    },
    'security': [{'Bearer': []}]
})
def delete_image(id):
    user_id = get_jwt_identity()
    image = ImageModel.query.filter_by(id=id).first()
    if image:
        db.session.delete(image)
        db.session.commit()
        return jsonify({'message': 'Image deleted successfully'}), 200
    else:
        return jsonify({'message': 'the image not found'})







