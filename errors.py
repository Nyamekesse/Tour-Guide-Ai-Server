from flask import jsonify, make_response


def handle_no_content(msg):
    message = msg if msg else "No Content"
    return make_response(jsonify({"success": True, "message": message}), 204)


def handle_bad_request(msg):
    message = msg if msg else "Bad request"
    return make_response(jsonify({"success": False, "message": message}), 400)


def handle_unauthorized(msg):
    message = msg if msg else "Unauthorized"
    return make_response(jsonify({"success": False, "message": message}), 401)


def handle_forbidden(msg):
    message = msg if msg else "Forbidden"
    return make_response(jsonify({"success": False, "message": message}), 403)


def handle_not_found(msg):
    message = msg if msg else "Not found"
    return make_response(jsonify({"success": False, "message": message}), 404)


def handle_method_not_allowed(msg):
    message = msg if msg else "Method not allowed"
    return make_response(jsonify({"success": False, "message": message}), 405)


def handle_not_processable_error(msg):
    message = msg if msg else "Not Processable"
    return make_response(jsonify({"success": False, "message": message}), 422)


def handle_internal_server_error(msg):
    message = msg if msg else "Internal server error"
    return make_response(jsonify({"success": False, "message": message}), 500)
