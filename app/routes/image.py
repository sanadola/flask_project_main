import io
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
from flasgger import swag_from
from app import db
from app.models.image import Image
from app.models.user import User
from app.utils.auth_helpers import check_token_revoked
from PIL import Image
import numpy as np

import cv2

image_api = Blueprint('image_api', __name__)

# =====================================================================================================
#                                  Creating a Image From User
# ======================================================================================================
@image_api.route('/create_image', methods=['POST'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Image'],
    'summary': 'Create a New Image',
    'description': 'Creates a new image entry for the authenticated user',
    'parameters': [
        {
            'name': 'file',
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
    user = User.query.get(user_id)
    if not user:
        user = None
    if 'image_file' not in request.files:
        return jsonify({'message': 'No image file part'}), 400

    image_file = request.files['image_file']
    image_name = request.form.get('image_name')

    if not image_name:
        return jsonify({'message': 'Missing image name'}), 400

    # Read the image file content
    image_data = image_file.read()

    # Create a new Image instance
    new_image = Image(image_name=image_name, image_data=image_data,user=user)
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
            'name': 'body',
            'in': 'formData',
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
    user_id = get_jwt_identity()
    image = Image.filter_by(user_id=user_id, id=id).first()

    if not image:
        return jsonify({'message': 'Image not found'}), 404

    if 'image_file' in request.files:
        image_file = request.files['image_file']
        image.image_data = image_file.read()

    if 'image_name' in request.form:
        image.image_name = request.form['image_name']

    db.session.commit()
    return jsonify(image.to_dict()), 200
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
    image_data = Image.query.filter_by(user_id=user_id).all()
    data_list = []
    if image_data:
        for data in image_data:
            binary_data = data.image_data

            # Decode the binary data into an image
            image = Image.open(io.BytesIO(binary_data))
            data_dict = {
                'id': data.id,
                'image_name':data.image_name,
                'image_data': image
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
                        'items': {
                            'type': 'integer',
                            'description': 'Histogram values'
                        },
                        'description': 'Flattened color histogram of the image'
                    },
                    'segmentation_mask': {
                        'type': 'array',
                        'items': {
                            'type': 'integer',
                            'description': 'Pixel values'
                        },
                        'description': 'Segmentation mask (example: binary threshold)'
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
    user_id = get_jwt_identity()
    image_data = Image.filter_by(user_id=user_id,id=id).first()
    if not image_data:
        return jsonify({'error': 'Data not found'}), 404

    # Convert binary data back to PIL Image
    image = Image.open(io.BytesIO(image_data.data))

    # Convert PIL Image to OpenCV format
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Generate color histogram
    hist, bins = cv2.calcHist([image_cv], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist_flattened = hist.flatten()

    # Generate segmentation mask (example: simple thresholding)
    ret, thresh = cv2.threshold(image_cv, 127, 255, cv2.THRESH_BINARY)

    # Return results
    return jsonify({
        'histogram': hist_flattened.tolist(),
        'segmentation_mask': thresh.tolist()
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
    image = Image.filter_by(user_id=user_id,id=id)
    if image:
        db.session.delete(image)
        db.session.commit()
        return jsonify({'message': 'Image deleted successfully'}), 200
    else:
        return jsonify({'message': 'the image not found'})







