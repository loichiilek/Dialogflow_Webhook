#!/usr/bin/env python
import base64
import hashlib
import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = make_webhook_result(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def send_email(body, to_email_address):
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    bcc_email = "cloi002@e.ntu.edu.sg"

    from_email_address = "enetschatbot@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = from_email_address
    msg['To'] = to_email_address
    msg['Subject'] = "NETS Customer Bot"
    # msg['BCC'] = bcc_email

    to_email_addresses = [to_email_address] + [bcc_email]

    body = "User's query: " + body

    msg.attach(MIMEText(body, 'plain'))

    import smtplib
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("enetschatbot@gmail.com", "kanxhwcotycpwill")
    text = msg.as_string()
    server.sendmail(from_email_address, to_email_addresses, text)


def contact_staff(req):
    query_result = req.get("queryResult")
    parameters = query_result.get("parameters")
    email = parameters.get("email")
    body = parameters.get("query")

    print(email)
    print(body)
    send_email(body, email)

    response = "Your query has been sent to our support staffs. We will contact you soon through {}"\
        .format(email)

    return {
        "fulfillmentText": response,
        "source": "NETSBot"
    }


def definition(req):
    query_result = req.get("queryResult")
    parameters = query_result.get("parameters")
    keyword = parameters.get("term")

    s = open('keyword.txt', 'r').read()
    keyword_dict = eval(s)
    print(keyword)

    if keyword in keyword_dict:
        response = "{}".format(keyword_dict[keyword])
    else:
        response = "Please enter a valid key word."

    definition_text = "definition: " + str(keyword)
    definition_text = definition_text.upper()

    return {
        "fulfillmentMessages": [
          {
            "platform": "ACTIONS_ON_GOOGLE",
            "basicCard": {
              "title": definition_text,
              "formattedText": response,
              "image": {
                "imageUri": "https://www.svgrepo.com/show/7249/dictionary-book-with-letters-a-to-z.svg",
                "accessibilityText": "dictionary"
              }
            }
          }],
        "source": "NETSBot"
    }


def find_error(req):
    query_result = req.get("queryResult")
    parameters = query_result.get("parameters")
    error_code = parameters.get("error-code")

    response_code = error_code[-5:]
    response_code_int = int(response_code)

    s = open('error_code.txt', 'r').read()
    error_code_dict = eval(s)

    if response_code in error_code_dict:
        response = "{}".format(error_code_dict[response_code])
    elif 8999 < response_code_int < 10000:
        response = "System error. NETS internal error has occurred."
    elif 50000 < response_code_int < 50500:
        response = "System error. Gateway internal error has occurred"
    else:
        response = "Sorry, I could not find the error code. " \
                   "Please ensure you have keyed in the correct error code in the format of XXXX-XXXXX."

    print("Response:")
    print(response)

    error_text = "ERROR-CODE: " + error_code

    return {
        "fulfillmentMessages": [
          {
            "platform": "ACTIONS_ON_GOOGLE",
            "basicCard": {
              "title": error_text,
              "formattedText": response,
              "image": {
                "imageUri": "https://www.svgrepo.com/show/10306/warning-exclamation-sign-in-filled-triangle.svg",
                "accessibilityText": "dictionary"
              }
            }
          }],
        "source": "NETSBot"
    }


# def generate_signature(txn_req, secret_key):
#     # print(secret_key)
#     # print(txn_req)
#     #
#     # print(type(secret_key))
#     # print(type(txn_req))
#     concat_payload_and_secret_key = bytes(txn_req + secret_key, 'utf-8')
#     h = hashlib.sha256()
#     h.update(concat_payload_and_secret_key)
#     convert_to_byte_array = bytearray(h.digest())
#     encode_base64 = base64.b64encode(convert_to_byte_array)
#     return encode_base64.decode('utf-8')
#
#
# def calculate_hmac(req):
#     query_result = req.get("queryResult")
#     parameters = query_result.get("parameters")
#     secret_key = parameters.get("secret_key")
#     payload = parameters.get("payload")
#
#     signature = generate_signature(payload, secret_key)
#     print(signature)
#
#     return {
#         "fulfillmentText": signature,
#         "source": "NETSBot"
#     }


def compare_keywords(req):
    query_result = req.get("queryResult")
    parameters = query_result.get("parameters")
    keywords = parameters.get("term")

    response = "Unable to make comparison between {} and {}".format(keywords[0], keywords[1])
    compare_text = keywords[0] + " VS " + keywords[1]
    compare_text = compare_text.upper()

    if "nps" in keywords and "soapi" in keywords:
        response = "The difference between SOAPI and NPS lies in their support for different payment methods. " \
                   "SOAPI supports Credit, Debit and QR payment while NPS supports only QR payment."

    if "umapi" in keywords and "soapi" in keywords:
        response = "Both SOAPI (stable) and UMAPI (legacy) fall under the category of eNETS Credit API" \
                   "They differ entirely in their method of integration."

    return {
        "fulfillmentMessages": [
            {
                "platform": "ACTIONS_ON_GOOGLE",
                "basicCard": {
                    "title": compare_text,
                    "formattedText": response,
                    "image": {
                        "imageUri": "https://www.svgrepo.com/show/7249/dictionary-book-with-letters-a-to-z.svg",
                        "accessibilityText": "dictionary"
                    }
                }
            }],
        "source": "NETSBot"
    }


def make_webhook_result(req):
    print(req["queryResult"]["action"])
    if req["queryResult"]["action"] == "find_error":
        return find_error(req)

    if req["queryResult"]["action"] == "definition":
        return definition(req)

    if req["queryResult"]["action"] == "email":
        return contact_staff(req)

    if req["queryResult"]["action"] == "compare_keywords":
        return compare_keywords(req)
    #
    # if req["queryResult"]["action"] == "calculate_hmac":
    #     return calculate_hmac(req)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 6000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')