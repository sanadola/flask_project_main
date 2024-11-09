import io
import pandas as pd
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required, get_jwt_identity
)
from flasgger import swag_from
from flask_jwt_extended import get_jwt
from app import db
from app.models.tabular import TabularData
from app.models.user import User
from app.utils.auth_helpers import check_token_revoked

tabular_api = Blueprint('tabular_api', __name__)


# =====================================================================================================
#                                  Creating a Tabular For A User
# ======================================================================================================

@tabular_api.route('/create_tabular', methods=['POST'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Tabular'],
    'summary': 'Create a New Tabular Data',
    'description': 'Creates a new tabular data entry for the authenticated user',
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'CSV file to upload'
        },
        {
            'name': 'tabular_name',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Name of the tabular data'
        }
    ],
    'responses': {
        201: {
            'description': 'Tabular data created successfully'
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
def create_tabular():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        user = None
    if 'tabular_file' not in request.files:
        return jsonify({'message': 'No tabular file part'}), 400

    tabular_file = request.files['tabular_file']
    tabular_name = request.form.get('tabular_name')

    if not tabular_name:
        return jsonify({'message': 'Missing tabular name'}), 400

    # Read the CSV data into a Pandas DataFrame
    df = pd.read_csv(tabular_file)

    # Convert DataFrame to binary data
    data = df.to_csv(index=False).encode('utf-8')

    # Create a new TabularData instance
    new_data = TabularData(tabular_data=data, tabular_name=tabular_name,user=user)
    db.session.add(new_data)
    db.session.commit()

    return jsonify({'message': 'File uploaded successfully'}), 201
# ======================================================================================================================
#                      Update in Tabular Files
# ======================================================================================================================
@tabular_api.route('/update_tabular/<int:id>', methods=['PUT'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Tabular'],
    'summary': 'Update a Tabular Data Entry',
    'description': 'Updates details of a specific tabular data entry for the authenticated user',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the tabular data entry to update'
        },
        {
            'name': 'body',
            'in': 'formData',
            'required': False,
            'schema': {
                'type': 'object',
                'properties': {
                    'tabular_name': {
                        'type': 'string',
                        'description': 'New name for the tabular data'
                    },
                    'tabular_file': {
                        'type': 'file',
                        'description': 'New CSV file'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Tabular data updated successfully'
        },
        400: {
            'description': 'Invalid request data'
        },
        401: {
            'description': 'Unauthorized access'
        },
        404: {
            'description': 'Tabular data not found'
        }
    },
    'security': [{'Bearer': []}]
})
def update_tabular(id):
    user_id = get_jwt_identity()
    tabular_data = TabularData.query.filter_by(user_id=user_id, id=id).first()

    if not tabular_data:
        return jsonify({'message': 'Tabular data not found'}), 404

    if 'tabular_file' in request.files:
        tabular_file = request.files['tabular_file']
        df = pd.read_csv(tabular_file)
        new_data = df.to_csv(index=False).encode('utf-8')
        tabular_data.tabular_data = new_data

    if 'tabular_name' in request.form:
        tabular_data.tabular_name = request.form['tabular_name']

    db.session.commit()
    return jsonify(tabular_data.to_dict()), 200

# ====================================================================================================================
#                            List All Tabular Files
# ====================================================================================================================


@tabular_api.route('/list_all_tabular', methods=['GET'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Tabular'],
    'summary': 'List all Tabular data for a User',
    'description': 'Retrieve a list of all tabular data entries for the authenticated user',
    'responses': {
        200: {
            'description': 'List of tabular data',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': 'ID of the tabular data entry'},
                        'tabular_name': {'type': 'string', 'description': 'Name of the tabular data'},
                        'tabular_data': {'type': 'string', 'description': 'CSV data (decoded from binary)'}
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

def list_tabular():
    user_id = get_jwt_identity()
    tabular_data = TabularData.filter_by(user_id=user_id, id=id).all()
    data_list = []
    if tabular_data:
        for data in tabular_data:
            csv_data = data.tabular_data.decode('utf-8')

            # Create temporary in-memory file-like object
            csv_file = io.StringIO(csv_data)
            data_dict = {
                'id':data.id,
                'tabular_name': data.tabular_name,
                'tabular_data': csv_data  # Decode binary data to string
            }
            data_list.append(data_dict)


    return jsonify(data_list)


# =====================================================================================================================
#                             Get a Statistics From Specific Tabular File
# =====================================================================================================================


@tabular_api.route('/get_tabular/<int:id>', methods=['GET'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Tabular'],
    'summary': 'Get and Analyze Tabular Data',
    'description': 'Retrieve and analyze a specific tabular data entry for the authenticated user',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the tabular data entry'
        }
    ],
    'responses': {
        200: {
            'description': 'Tabular data analysis results',
            'schema': {
                'type': 'object',
                'properties': {
                    'statistics': {
                        'type': 'object',
                        'description': 'Statistical summary of the data'
                    },
                    'outliers': {
                        'type': 'array',
                        'items': {
                            'type': 'integer',
                            'description': 'Indexes of outlier data points'
                        },
                        'description': 'List of outlier data point indexes'
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized access'
        },
        404: {
            'description': 'Tabular data not found'
        }
    },
    'security': [{'Bearer': []}]
})

def get_tabular(id):
    user_id = get_jwt_identity()
    tabular_data = TabularData.filter_by(user_id=user_id,id=id)
    if not tabular_data:
        return jsonify({'error': 'Data not found'}), 404

    # Convert binary data back to Pandas DataFrame
    df = pd.read_csv(io.BytesIO(tabular_data.data))

    # Perform data analysis
    statistics = {
        'mean': df.mean().to_dict(),
        'median': df.median().to_dict(),
        'mode': df.mode().iloc[0].to_dict() if len(df) > 0 else None,  # Handle empty DataFrame
        'quartiles': df.quantile([0.25, 0.5, 0.75]).to_dict(),
    }
    q1 = df.quantile(0.25)
    q3 = df.quantile(0.75)
    iqr = q3 - q1
    outliers = df[(df < (q1 - 1.5 * iqr)) | (df > (q3 + 1.5 * iqr))].index.tolist()

    return jsonify({
        'statistics': statistics,
        'outliers': outliers,
    }),200


# ==================================================================================================================
#                                Delete Tabular Specific Files
# ==================================================================================================================

@tabular_api.route('/delete_tabular/<int:id>', methods=['DELETE'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Tabular'],
    'summary': 'Delete a Tabular Data Entry',
    'description': 'Deletes a specific tabular data entry for the authenticated user',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the tabular data entry to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Tabular data deleted successfully'
        },
        401: {
            'description': 'Unauthorized access'
        },
        404: {
            'description': 'Tabular data not found'
        }
    },
    'security': [{'Bearer': []}]
})
def delete_tabular(id):
    user_id = get_jwt_identity()  # Get user ID from JWT
    data = TabularData.filter_by(user_id=user_id,id=id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return jsonify({'message': 'the file deleted successfully'}), 200

    else:
        return jsonify({'message': 'the file not found'}), 404









