import client as api

# Generate access token
acc_sid = '8f452a95-abb0-4b6b-8ea9-1dfc0fe27492'
username = 'waynealex'

response = api.generate_token(username, acc_sid)

if response["success"]:
    token = response["data"]["token"]
    balance = response["data"]["balance"]

    # Send chatgpt request to the server using Token
    prompt = 'who is usain bolt?'
    chatgpt_response = api.chatgpt(token, prompt)

    if chatgpt_response["success"]:
        chatgpt_resp = chatgpt_response["data"]["response"]
        print('Chatgpt Response >> ' ,chatgpt_resp)
    else:
        error_message = chatgpt_response["error"]["message"]
        print(f'Chatgpt Error: {error_message}')
else:
    error_message = response
    print(f'Error: {error_message}')
