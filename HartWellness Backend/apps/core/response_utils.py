"""
Standardized API Response utilities.
All responses follow the format: {"success": true/false, "message": "...", "data": {...}, "metadata": {...}}
"""
import math
from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message=None, status_code=status.HTTP_200_OK, metadata=None):
    """
    Create a standardized success response.
    
    Args:
        data: The response data to be nested under 'data' field
        message: Optional message
        status_code: HTTP status code (default 200)
        metadata: Optional metadata to be included alongside data
    """
    response_data = {
        'success': True,
        'data': data if data is not None else {}
    }
    if message:
        response_data['message'] = message
    if metadata is not None:
        response_data['metadata'] = metadata
    return Response(response_data, status=status_code)


def error_response(message, data=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        data: Optional additional error data
        status_code: HTTP status code (default 400)
    """
    response_data = {
        'success': False,
        'message': message,
    }
    if data:
        response_data['data'] = data
    return Response(response_data, status=status_code)


class StandardizedResponseMixin:
    """
    Mixin for DRF views to standardize all responses.
    Wraps serializer data in {"success": true, "message": "...", "data": {...}}
    """
    
    def finalize_response(self, request, response, *args, **kwargs):
        """Override finalize_response to wrap successful responses."""
        response = super().finalize_response(request, response, *args, **kwargs)

        def _is_paginated_payload(payload):
            return (
                isinstance(payload, dict)
                and 'results' in payload
                and any(key in payload for key in ('count', 'next', 'previous'))
            )

        def _build_pagination_metadata(payload, request=None):
            count = payload.get('count', 0)
            page_size = 20
            current_page = 1
            if request and hasattr(request, 'query_params'):
                try:
                    page_size = int(request.query_params.get('page_size', 20))
                except (ValueError, TypeError):
                    page_size = 20
                try:
                    current_page = int(request.query_params.get('page', 1))
                except (ValueError, TypeError):
                    current_page = 1
            total_pages = math.ceil(count / page_size) if page_size and count > 0 else 1
            return {
                'total_count': count,
                'total_pages': total_pages,
                'current_page': current_page,
                'per_page': page_size,
            }
        
        # Only wrap successful responses (2xx)
        if response.status_code >= 200 and response.status_code < 300:
            # Don't wrap if already in standard format.
            if isinstance(response.data, dict):
                if 'success' not in response.data:  # Not already wrapped
                    if _is_paginated_payload(response.data):
                        response.data = {
                            'data': response.data.get('results', []),
                            'metadata': _build_pagination_metadata(response.data, request),
                        }
                        return response

                    response.data = {
                        'success': True,
                        'data': response.data
                    }
            elif isinstance(response.data, list):
                arr = response.data
                response.data = {
                    'data': arr,
                    'metadata': {
                        'total_count': len(arr),
                        'total_pages': 1,
                        'current_page': 1,
                        'per_page': len(arr) or 20,
                    }
                }
        else:
            # For error responses, standardize if not already done
            if isinstance(response.data, dict):
                if 'success' not in response.data:
                    # Determine if it's an error message or validation errors
                    if 'detail' in response.data:
                        error_msg = response.data.pop('detail')
                        response.data = {
                            'success': False,
                            'message': str(error_msg),
                            'data': response.data if response.data else {}
                        }
                    else:
                                # If the response contains field-level validation errors (dict of lists),
                                # aggregate them into a human-readable message while keeping the
                                # original structure in `data` for clients that need field details.
                                data_copy = response.data
                                aggregated_message = 'An error occurred'

                                try:
                                    if isinstance(data_copy, dict) and data_copy:
                                        parts = []
                                        for key, val in data_copy.items():
                                            # val can be list, dict, or string
                                            if isinstance(val, (list, tuple)):
                                                msgs = [str(x) for x in val]
                                                parts.append(f"{key}: {'; '.join(msgs)}")
                                            elif isinstance(val, dict):
                                                # nested errors, flatten one level
                                                nested_parts = []
                                                for nk, nv in val.items():
                                                    if isinstance(nv, (list, tuple)):
                                                        nested_parts.append(f"{nk}: {'; '.join([str(x) for x in nv])}")
                                                    else:
                                                        nested_parts.append(f"{nk}: {nv}")
                                                parts.append(f"{key}: {{ {'; '.join(nested_parts)} }}")
                                            else:
                                                parts.append(f"{key}: {val}")

                                        if parts:
                                            aggregated_message = ' | '.join(parts)
                                except Exception:
                                    # Fallback to a generic message if aggregation fails
                                    aggregated_message = 'An error occurred'

                                response.data = {
                                    'success': False,
                                    'message': aggregated_message,
                                    'data': data_copy
                                }
        
        return response

