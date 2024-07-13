import json
import uuid

import requests
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import SignUpForm
from .models import Mobile, Token

server_url = 'http://127.0.0.1:8001/sendMessage'


def send_message_to_server(message):
    try:
        # Create a JSON payload with the message
        payload = {'message': message}

        # Send a POST request to the server
        response = requests.post(server_url, json=payload)

        # Check the response status code
        if response.status_code == 200:
            return response  # Return the response object
        else:
            print('Server returned an unexpected status code:', response.status_code)
            return None  # Return None in case of an error

    except requests.exceptions.RequestException as e:
        print('An error occurred while sending the request:', str(e))
        return None


def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully signed in")
            return redirect('dashboard')
        else:
            messages.error(request, "There was an error while signing in")
            return redirect('home')
    else:
        return render(request, 'home.html')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            acc_ = Mobile(user_name=username)
            acc_.save()
            return redirect('verification')

    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form': form})


def dashboard(request):
    mobile = Mobile.objects.get(user_name=request.user.username)

    return render(request, 'dashboard.html', {'account': mobile})


def whatsapp(request):
    mobile = Mobile.objects.get(user_name=request.user.username)
    return render(request, 'whatsappApi.html', {'account': mobile, 'user': False})


def whatsappUser(request):
    mobile = Mobile.objects.get(user_name=request.user.username)
    callback_url = "http://127.0.0.1:8000/callback_url"
    if request.method == 'POST':
        sni = request.POST['SNI']
        callback_url = request.POST.get('callback_url', None)
        if not callback_url:
            # Use the default value when callback_url is empty or not provided
            callback_url = "http://127.0.0.1:8000/callback_url"
        config = {"serverUrl": "http://localhost:3001"}
        response = requests.get(f"{config['serverUrl']}/api/check-sni?sni={sni}")
        if response.status_code == 200:
            data = response.json()
            if data.get("exists"):
                messages.success(request, "The SNI symbol is already in use,choose another one.")
                return render(request, 'whatsappApi.html', {'account': mobile, 'user': True})
            else:
                config = {"serverUrl": "http://localhost:3001"}
                sni = sni
                sandbox_id = str(uuid.uuid4())
                user = request.user.username
                data = {"user": user, "sni": sni, "sandboxId": sandbox_id, "callback_url": callback_url}
                response = requests.post(f"{config['serverUrl']}/api/add-sni", json=data)
                if response.status_code == 201:
                    mobile.sni = sni
                    mobile.save()
                    messages.success(request, "You have successfully registered you SNI")
                    return render(request, 'whatsappApi.html', {'account': mobile, 'user': True})

                else:
                    messages.success(request, "Failed to registered you SNI,Try again if this persists contact owner")
                    return render(request, 'whatsappApi.html', {'account': mobile, 'user': True})
        else:
            messages.success(request,
                             "Failed to check availability of you SNI,Try again if this persists contact owner")
            return render(request, 'whatsappApi.html', {'account': mobile, 'user': True})

    # else:
    #     config = {"serverUrl": "http://localhost:3001"}
    #     user = request.user.username
    #     latest_message_response = requests.get(f"{config['serverUrl']}/api/get-last-unread?user={user}")
    #     if latest_message_response.status_code == 200:
    #         latest_message = latest_message_response.json()
    #         print("Latest Message:", latest_message["message"])
    #         print("Latest Message ID:", latest_message["id"])
    #     else:
    #         error_data = latest_message_response.json()  # Parse error response
    #         print(f"Error Code: {latest_message_response.status_code}")
    #         print("Error:", error_data["error"])

    return render(request, 'whatsappApi.html', {'account': mobile, 'user': True, 'callback_url': callback_url})


def chatgpt(request):
    mobile = Mobile.objects.get(user_name=request.user.username)
    return render(request, 'chatgpt.html', {'account': mobile})


def docs(request):
    return render(request, 'docs.html')


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('home')


def verify_phone(request):
    if request.method == 'POST':
        phone = request.POST.get('tel')
        print(phone)
        url = 'http://13.51.196.90:3000/trigger-function'
        payload = {'phone_number': phone}
        user_id = request.user.username

        try:
            acc_exists = Mobile.objects.filter(phone_number=phone).exists()

            if acc_exists:
                messages.error(request,
                               'The phone number is already in use by another user. Please try another number.')
                return render(request, 'verification.html', {'verification_code_sent': False})
            else:
                mobile, created = Mobile.objects.get_or_create(user_name=request.user.username)
                mobile.phone_number = phone
                mobile.save()

            response = requests.get(url, params=payload)
            response.raise_for_status()
            print(response.text)
            code = response.text.replace('Message successfully sent. Verification code is: ', '')
            print(code)

            # Store the code in the session
            request.session['verification_code'] = code

            return render(request, 'verification.html', {'verification_code_sent': True})

        except requests.exceptions.RequestException as e:
            messages.error(request, 'Error while sending the verification code.')
            print(f"Error: {e}")
            return render(request, 'verification.html', {'verification_code_sent': False})

    else:
        return render(request, 'verification.html', {'verification_code_sent': False})


def verify_code(request):
    if request.method == 'POST':
        # Retrieve the code from the session
        code = request.session.get('verification_code', None)
        print('verification code: ' + code)
        if not code:
            messages.success('Code not found,restart registration if problem persist inform admin')
            return redirect('verify_phone')

        # Process the code and check if it matches the user input.
        user_input_code = request.POST.get('verification_code')
        if code == user_input_code:
            messages.success(request, "Phone number successfully Verified")
            account = Mobile.objects.get(user_name=request.user.username)
            account.verified = True
            account.save()
            username = request.user.username
            return redirect('dashboard')  # Redirect to the appropriate URL for package selection
        else:
            # Code is incorrect, display an error message, or redirect back to the verification page.
            messages.success(request, "Verification code entered is incorrect.")
            logout(request)
            return redirect('verification')

    else:
        return redirect('verification')


def resend_code(request):
    # Code to resend the verification code goes here.
    return redirect('verify_phone_number')


def change_number(request):
    # Code to allow the user to change their phone number goes here.
    return redirect('verify_phone_number')


def generate_token(request):
    try:
        if request.method == 'GET':
            # Assuming the data is sent as JSON
            data = json.loads(request.body.decode('utf-8'))

            # Accessing the values from the JSON data
            username = data.get('username')
            acc_sid = data.get('acc_sid')

            print("Received JSON data:", data)
            print("Username:", username)
            print("Acc SID:", acc_sid)

        # Case-insensitive filtering for username and account SID
        acc_queryset = Mobile.objects.filter(user_name=username, account_sid=acc_sid)

        if not acc_queryset.exists():
            response_data = {"error": "Invalid credentials"}
            return JsonResponse(response_data, status=401)
        else:
            account = acc_queryset.first()  # Retrieve the first object from the queryset
            if account.account_balance < 0.5:
                response_data = {"error": "Insufficient Balance in your account"}
                return JsonResponse(response_data, status=401)
            else:
                account.account_balance = account.account_balance - 0.5
                account.save()
                token_value = str(uuid.uuid4())
                _token = Token(user_name=username, Token=token_value)
                _token.save()
                response_data = {"token": token_value, "balance": account.account_balance}
                return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def chatgpt_api(request):
    if request.method == 'POST':
        mobile = Mobile.objects.get(user_name=request.user.username)
        prompt = request.POST.get('messageBody')

        # Send the message to the server and get the response
        response = send_message_to_server(prompt)

        if response is not None:
            response_data = response.json()
            return render(request, 'chatgpt.html', {'response': response_data, 'account': mobile})
        else:
            # Handle the case when there's an issue with the server request
            return render(request, 'error.html')
    else:
        token = request.GET.get('token')
        prompt = request.GET.get('prompt')

        check = Token.objects.filter(Token=token)
        if not check:
            response_data = {"error": "Token verification failed"}
            return JsonResponse(response_data, status=401)  # Unauthorized
        else:
            check.delete()

            response = requests.post(server_url, json={'message': prompt})
            response_data = response.json()

            if 'response' in response_data:
                return JsonResponse({'response': response_data['response']}, status=200)
            elif 'error' in response_data:
                return JsonResponse({'error': response_data['error']}, status=500)  # Internal Server Error
            else:
                return JsonResponse({'error': 'An unknown error occurred.'}, status=500)  # Internal Server Error


@csrf_exempt
def callback_view(request):
    if request.method == 'POST':
        # Assuming the data is sent as JSON
        data = json.loads(request.body)

        # Accessing the values from the JSON data
        sandboxId = data.get('sandboxId')
        fromId = data.get('fromId')
        toId = data.get('toId')
        message = data.get('message')
        date = data.get('date')
        messageType = data.get('messageType')
        hasMedia = data.get('hasMedia')
        isForwarded = data.get('isForwarded')
        isStatus = data.get('isStatus')
        isGroup = data.get('isGroup')
        isReply = data.get('isReply')
        # print(data)

        # Now you can process the data as needed
        import requests

        api_url = "http://127.0.0.1:8001/sendMessage"
        message = message
        payload = {"message": message}

        try:
            response = requests.post(api_url, json=payload)

            if response.status_code == 200:
                response_data = response.json()
                response_message = response_data.get("response")
                # print("Server Response:", response_message)
                send_url = "http://127.0.0.1:3001/send-whatsapp-message"
                chatId = fromId
                messageContent = response_message
                payload = {
                    "chatId": chatId,
                    "messageContent": messageContent
                }
                try:
                    response = requests.post(send_url, json=payload)

                    if response.status_code == 200:
                        print("Message sent successfully:")
                    else:
                        print("Failed to send message. Server response:", response.status_code, response.text)

                except requests.RequestException as e:
                    print("Error sending request:", e)
            else:
                print("Error: Server returned status code", response.status_code)

        except requests.exceptions.RequestException as e:
            print("Error:", e)

        # Return a JSON response to acknowledge receipt of the data
        return JsonResponse({'status': 'success'})
    else:
        # Handle other HTTP methods if necessary
        return JsonResponse({'status': 'error', 'message': 'Unsupported method'}, status=405)


def email(request):
    mobile = Mobile.objects.get(user_name=request.user.username)

    return render(request, 'email.html', {'account': mobile})
