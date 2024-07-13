from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/generate_token', methods=['GET'])
def generate_token():
    try:
        username = request.args.get('username')
        Acc_SID = request.args.get('acc_sid')

        response_data = {"token": "your_generated_token"}
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/whatsapp_api', methods=['GET'])
def whatsapp_api():
    try:
        Token = request.args.get('token')
        To = request.args.get('to')
        message = request.args.get('message_body')

        # Your WhatsApp API logic here

        response_data = {"message": "sent_successfully"}
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/chatgpt_api', methods=['GET'])
def chatgpt_api():
    try:
        Token = request.args.get('token')
        prompt = request.args.get('prompt')



        response_data = {"response": "generated_response"}
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
