from flask import Flask, request

app = Flask(__name__)

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()
    to_address = data['to_address']
    subject = data['subject']
    body = data['body']
    # Call application logic to send email
    return "Email sent", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
