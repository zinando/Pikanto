"""This is the messenger class module"""
import requests
import os


class Messenger:
    """prepares messages to be sent via email or saved to database"""

    def __init__(self, base_url=None, url=None, recipient_email=None):
        """initialize the class with api endpoint or the recipient email"""
        self.base_url = base_url
        self.sender_email = recipient_email
        self.url = url

    def query_server(self, data=None, files=None) -> dict:
        """sends the data to api"""
        url = self.base_url + self.url
        request_headers = {'Content-Type': 'application/json'}
        try:
            if files is not None:
                files_dict = {field_name: (file_obj, base_name) for field_name, (file_obj, base_name) in files.items()}
                files_for_request = {field_name: (base_name, file_obj, 'application/octet-stream') for
                                     field_name, (file_obj, base_name) in files_dict.items()}
                response = requests.post(url, files=files_for_request)
            else:
                response = requests.post(url, headers=request_headers, json=data)

            if response.status_code == 400:
                # Log or display detailed information about the error response
                print(f"400 Error Response: {response.text}")

            response.raise_for_status()  # Raise exception for non-200 status codes

        except requests.HTTPError as http_err:
            # Handle HTTP errors (other than 400)
            return {'status': 2, 'message': str(http_err), 'data': None, 'error': [str(http_err)]}
        except Exception as e:
            # Handle other exceptions
            return {'status': 2, 'message': str(e), 'data': None, 'error': [str(e)]}

        return response.json()

    def check_for_existing_record(self, vehicle_id: str) -> dict:
        """prepares data and saves to data base"""
        response = self.query_server({'vehicle_id': vehicle_id})
        print(response)
        return response

