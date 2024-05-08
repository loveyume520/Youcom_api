from flask import Flask, Response, request, jsonify
import requests
import uuid
from datetime import datetime
import json
from flask_cors import CORS
import re
import random
import string

proxy = None
ua = 'Mozilla/5.0 (Windows NT 5.0) AppleWebKit/534.2 (KHTML, like Gecko) Chrome/59.0.865.0 Safari/534.2'
# 例: proxy = a:a@proxy.socks5.io:3005

if proxy:
    proxies = {'http':proxy,'https':proxy}
else:
    proxies = None

models = ['gpt_4', 'gpt_4_turbo', 'claude_2', 'claude_3_opus', 'claude_3_sonnet', 'claude_3_haiku', 'gemini_pro', 'gemini_1_5_pro', 'databricks_dbrx_instruct', 'command_r', 'command_r_plus', 'zephyr', 'claude_3_opus_2k']

headers = {
    'User-Agent': ua,
    'Accept': 'text/event-stream',
    'Referer': 'https://you.com/',
}



app = Flask(__name__)
CORS(app)

def update_files(content, cookies):
    response = requests.get('https://you.com/api/get_nonce', cookies=cookies, headers=headers, proxies=proxies)
    boundary = '----MyCustomBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    user_filename = f'{"".join(random.choices(string.ascii_letters + string.digits, k=5))}.txt'
    multipart_data = (
        '--' + boundary + '\r\n' +
        f'Content-Disposition: form-data; name="file"; filename={user_filename}\r\n' +
        'Content-Type: text/plain\r\n\r\n' +
        content
        +'\r\n'
        '--' + boundary + '--'
    )
    headers123 = {
        'User-Agent': ua,
        'Accept': 'text/event-stream',
        'Referer': 'https://you.com/',
        'accept': 'multipart/form-data',
        'accept-language': 'cmn',
        'content-type': 'multipart/form-data; boundary=' + boundary,
        'x-upload-nonce': response.text,
        'Content-Length': str(len(content.encode('utf-8'))),
    }
    response = requests.post('https://you.com/api/upload', headers=headers123, data=multipart_data.encode('utf-8'), cookies=cookies, proxies=proxies)
    filename = response.json()['filename']
    return filename, user_filename, str(len(content.encode('utf-8')))

def get_ck_parms(session, session_jwt, chat, chatid, model):
    cookies = {
        'youpro_subscription': 'true',
        'stytch_session': session,
        'stytch_session_jwt': session_jwt,
        'ydc_stytch_session': session,
        'ydc_stytch_session_jwt': session_jwt,
    }
    params = {
        'q':chat,
        'page':1,
        'count':10,
        'safeSearch':'Off',
        'responseFilter':'WebPages,TimeZone,Computation,RelatedSearches',
        'domain':'youchat',
        'use_personalization_extraction':'true',
        'queryTraceId':chatid,
        'chatId':chatid,
        'conversationTurnId':uuid.uuid4(),
        'pastChatLength':0,
        'isSmallMediumDevice':'true',
        'selectedChatMode':'custom',
        'selectedAIModel':model,
        'traceId':f'{chatid}|{uuid.uuid4()}|{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}'
    }
    return cookies,params

def parse_1(data):
    messages = data['messages']
    model = data['model']
    try:
        _stream = data['stream']
    except:
        _stream = False

    if '使用四到五个字直接返回这句话的简要主题，不要解释、不要标点、不要语气词、不要多余文本，不要加粗，如果没有主题，请直接返回“闲聊”' in str(messages):
        model = 'gpt_4_turbo'
    if model == 'gem_pro':
        model = 'gemini_pro'
    elif model == 'gem_1_5_pro':
        model = 'gemini_1_5_pro'
    elif model not in models:
        model = 'gpt_4_turbo'
    if model == 'command_r' or model == 'zephyr' or model == 'claude_2':
        add_t = "This is the api format of our previous conversation, please understand and reply to the user's last question"
        messages = add_t + str(messages)
    elif model == 'databricks_dbrx_instruct' or model == 'gemini_pro'or model == 'gemini_1_5_pro' or model == 'claude_3_opus_2k':
        for item in reversed(messages):
            if item['role'] == 'user':
                messages = item['content']
                break
    return str(messages),model,_stream

def chat_liu(chat, model, session, session_jwt):
    chatid = uuid.uuid4()
    cookies,params = get_ck_parms(session, session_jwt, chat, chatid, model)
    response = requests.get(
        'https://you.com/api/streamingSearch',
        cookies=cookies,
        headers=headers,
        params=params,
        stream=True,
        proxies=proxies
    )
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
                if 'event' in data:
                    continue
                else:
                    data = data[6:]
                if 'youChatToken' in data:
                    id = str(uuid.uuid4())
                    content = json.loads(data)['youChatToken']
                    if 'Please log in to access GPT-4 mode.' in content and 'Answering your question without GPT-4 mode:' in content:
                        content = 'cookie失效或会员到期，将默认使用智障模型!\n\n'
                    yield "data: {}\n\n".format(json.dumps({
                        "id": "chatcmpl-"+id,
                        "created": 0,
                        "model": model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": content,
                            }
                        }]
                    }))
        yield bytes(f"data: {['DONE']}", 'utf-8')
        yield bytes()
    else:
        if response.status_code == 403 and 'Just a moment...' in response.text:
            print('盾')
        return response.status_code
    
def claude_3_opus_2k(chat, model, session, session_jwt):
    model = 'claude_3_opus'
    cookies = {
        'youpro_subscription': 'true',
        'stytch_session': session,
        'stytch_session_jwt': session_jwt,
        'ydc_stytch_session': session,
        'ydc_stytch_session_jwt': session_jwt,
    }

    with open('wb.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    filename, user_filename, size = update_files(content.replace('{tihuan1145141919810}', chat), cookies)
    chatid = str(uuid.uuid4())
    params = {'q': 'Please review the attached prompt', 'page': '1', 'count': '10', 'safeSearch': 'Moderate', 'mkt': 'zh-HK', 'responseFilter': 'WebPages,TimeZone,Computation,RelatedSearches', 'domain': 'youchat', 'use_personalization_extraction': 'true', 
         'queryTraceId': chatid, 
         'chatId': chatid, 
         'conversationTurnId': str(uuid.uuid4()), 
         'pastChatLength': '0', 'isSmallMediumDevice': 'true', 'selectedChatMode': 'custom', 
         'userFiles': '[{"user_filename":"' + user_filename + '","filename":"' + filename + '","size":"' + size + '"}]', 
         'selectedAIModel': 'claude_3_opus', 
         'traceId': f'{chatid}|{uuid.uuid4()}|{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}',
         'chat': '[]'}
    response = requests.get(
        'https://you.com/api/streamingSearch',
        cookies=cookies,
        headers=headers,
        params=params,
        stream=True,
        proxies=proxies,
        timeout=500
    )
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
                if 'event' in data:
                    continue
                else:
                    data = data[6:]
                if 'youChatToken' in data:
                    id = str(uuid.uuid4())
                    content = json.loads(data)['youChatToken']
                    if 'Please log in to access GPT-4 mode.' in content and 'Answering your question without GPT-4 mode:' in content:
                        content = 'cookie失效或会员到期，将默认使用智障模型!\n\n'
                    yield "data: {}\n\n".format(json.dumps({
                        "id": "chatcmpl-"+id,
                        "created": 0,
                        "model": model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": content,
                            }
                        }]
                    }))
        yield bytes(f"data: {['DONE']}", 'utf-8')
        yield bytes()
    else:
        if response.status_code == 403 and 'Just a moment...' in response.text:
            print('盾')
        return response.status_code

def chat_feiliu(chat, model, session, session_jwt):
    chatid = uuid.uuid4()
    cookies,params = get_ck_parms(session, session_jwt, chat, chatid, model)
    response = requests.get(
        'https://you.com/api/streamingSearch',
        cookies=cookies,
        headers=headers,
        params=params,
        stream=True,
        proxies=proxies
    )
    chat_text = ''
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
                if 'event' in data:
                    continue
                else:
                    data = data[6:]
                if 'youChatToken' in data:
                    id = str(uuid.uuid4())
                    content = json.loads(data)['youChatToken']
                    if 'Please log in to access GPT-4 mode.' in content and 'Answering your question without GPT-4 mode:' in content:
                        content = 'cookie失效或会员到期，将默认使用智障模型!\n\n'
                    chat_text = chat_text + content
    else:
        return {"error": f'返回错误|{str(response.status_code)}'}, response.status_code
    return {"id":f"chatcmpl-{str(uuid.uuid4())}",
     "OAI-Device-Id":str(uuid.uuid4()),
     "conversation_id":str(uuid.uuid4()),
     "created":123,
     "model":"gpt-3.5-turbo",
     "choices":[{"index":0,"message":{"role":"assistant","content":chat_text},"finish_reason":"stop"}],
     "usage":{"prompt_tokens":0,"completion_tokens":0,"total_tokens":0}}


@app.route('/')
def stream():
    return 'ok'
    
@app.route('/v1/chat/completions', methods=['POST', 'OPTIONS'])
def chatv1_1():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        try:
            session_jwt = re.search(r'stytch_session_jwt=([^;]+)', request.headers.get('Authorization')).group(1)
            session = re.search(r'ydc_stytch_session=([^;]+)', request.headers.get('Authorization')).group(1)
        except:
            return {"error": "请确保传入的Authorization正确"}, 401
        try:
            messages,model,_stream = parse_1(request.get_json())
        except Exception as e:
            print(e)
            return {"error": "Invalid JSON body1"}, 404
        try:
            if model == 'claude_3_opus_2k':
                if _stream == False:
                    return {"error": "Only supports stream mode"}, 404
                return Response(claude_3_opus_2k(str(messages), model, session, session_jwt), mimetype='text/event-stream')
        except:
            return {"error": "Upload error or membership expiration"}, 404

        if _stream == True:
            return Response(chat_liu(str(messages), model, session, session_jwt), mimetype='text/event-stream')
        else:
            return chat_feiliu(messages, model, session, session_jwt)
    except Exception as e:
        print('error')
        print(e)
        return {"error": "Invalid JSON body"}, 404

@app.route('/v1/models', methods=['GET']) 
def models_v1():    
    try:
        models = ['gpt_4', 'gpt_4_turbo', 'claude_2', 'claude_3_opus', 'claude_3_sonnet', 'claude_3_haiku', 'gemini_pro', 'gemini_1_5_pro', 'databricks_dbrx_instruct', 'command_r', 'command_r_plus', 'zephyr', 'claude_3_opus_2k']
        return {
        "object": "list",
        "data": [{
            "id": m,
            "object": "model",
            "created": datetime.now().isoformat(),
            "owned_by": "popai"
        } for m in models]
    }
        # return jsonify(models)  
    except Exception as e:
        print('error')
        print(e) 
        return {"error": "Error retrieving models"}, 500

@app.route('/v1/messages', methods=['POST'])
def messages():
    raw_body = request.get_data(as_text=True)
    try:
        json_body = json.loads(raw_body)
        if json_body.get('stream') == False:
            return jsonify({
                'id': str(uuid.uuid4()),
                'content': [
                    {
                        'text': 'Please turn on streaming.',
                    },
                    {
                        'id': 'string',
                        'name': 'string',
                        'input': {},
                    },
                ],
                'model': 'string',
                'stop_reason': 'end_turn',
                'stop_sequence': 'string',
                'usage': {
                    'input_tokens': 0,
                    'output_tokens': 0,
                },
            })
        elif json_body.get('stream') == True:
            # 计算用户消息长度
            user_message = [{'question': '', 'answer': ''}]
            user_query = ''
            last_update = True
            if json_body.get('system'):
                # 把系统消息加入messages的首条
                json_body['messages'].insert(0, {'role': 'system', 'content': json_body['system']})
            print(json_body['messages'])
            for msg in json_body['messages']:
                if msg['role'] == 'system' or msg['role'] == 'user':
                    if last_update:
                        user_message[-1]['question'] += msg['content'] + '\n'
                    elif user_message[-1]['question'] == '':
                        user_message[-1]['question'] += msg['content'] + '\n'
                    else:
                        user_message.append({'question': msg['content'] + '\n', 'answer': ''})
                    last_update = True
                elif msg['role'] == 'assistant':
                    if not last_update:
                        user_message[-1]['answer'] += msg['content'] + '\n'
                    elif user_message[-1]['answer'] == '':
                        user_message[-1]['answer'] += msg['content'] + '\n'
                    else:
                        user_message.append({'question': '', 'answer': msg['content'] + '\n'})
                    last_update = False
            user_query = user_message[-1]['question']

            # 获取traceId
            trace_id = str(uuid.uuid4())

            # 试算用户消息长度
            if len(json.dumps(user_message)) + len(user_query) > 32000:
                # 太长了，需要上传
                # user message to plaintext
                previous_messages = '\n\n'.join([msg['content'] for msg in json_body['messages']])
                user_query = 'Please view the document and reply.'
                user_message = []

                # GET https://you.com/api/get_nonce to get nonce
                nonce_response = requests.get('https://you.com/api/get_nonce')
                nonce = nonce_response.json()
                if not nonce:
                    raise Exception('Failed to get nonce')

                # POST https://you.com/api/upload to upload user message
                message_buffer = create_docx(previous_messages)
                files = {'file': ('messages.docx', message_buffer, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                headers = {'X-Upload-Nonce': nonce}
                upload_response = requests.post('https://you.com/api/upload', files=files, headers=headers)
                uploaded_file = upload_response.json().get('filename')
                if not uploaded_file:
                    raise Exception('Failed to upload messages')

            msg_id = str(uuid.uuid4())

            # send message start
            yield create_event('message_start', {
                'type': 'message_start',
                'message': {
                    'id': trace_id,
                    'type': 'message',
                    'role': 'assistant',
                    'content': [],
                    'model': 'claude_3_haiku',
                    'stop_reason': None,
                    'stop_sequence': None,
                    'usage': {'input_tokens': 8, 'output_tokens': 1},
                },
            })
            yield create_event('content_block_start', {'type': 'content_block_start', 'index': 0, 'content_block': {'type': 'text', 'text': ''}})
            yield create_event('ping', {'type': 'ping'})

            # proxy response
            params = {
                'page': '1',
                'count': '10',
                'safeSearch': 'Off',
                'q': user_query.strip(),
                'incognito': 'true',
                'chatId': trace_id,
                'traceId': f'{trace_id}|{msg_id}|{datetime.utcnow().isoformat()}',
                'conversationTurnId': msg_id,
                'selectedAIModel': 'claude_3_opus',
                'selectedChatMode': 'custom',
                'pastChatLength': len(user_message),
                'queryTraceId': trace_id,
                'use_personalization_extraction': 'false',
                'domain': 'youchat',
                'responseFilter': 'WebPages,TimeZone,Computation,RelatedSearches',
                'mkt': 'zh-CN',
                'userFiles': json.dumps([{'user_filename': 'messages.docx', 'filename': uploaded_file, 'size': len(message_buffer)}]) if uploaded_file else '',
                'chat': json.dumps(user_message),
            }
            headers = {
                'accept': 'text/event-stream',
                'referer': 'https://you.com/search?q=&fromSearchBar=true&tbm=youchat&chatMode=custom'
            }
            proxy_req = requests.get('https://you.com/api/streamingSearch', params=params, headers=headers, stream=True)

            cached_line = ''
            for chunk in proxy_req.iter_content(chunk_size=1, decode_unicode=True):
                if cached_line:
                    chunk = cached_line + chunk
                    cached_line = ''

                if not chunk.endswith('\n'):
                    lines = chunk.split('\n')
                    cached_line = lines.pop()
                    chunk = '\n'.join(lines)

                if 'event: youChatToken' in chunk:
                    for line in chunk.split('\n'):
                        if line.startswith('data: {"youChatToken"'):
                            data = line[6:]
                            json_data = json.loads(data)
                            chunk_json = json.dumps({
                                'type': 'content_block_delta',
                                'index': 0,
                                'delta': {'type': 'text_delta', 'text': json_data['youChatToken']},
                            })
                            yield create_event('content_block_delta', chunk_json)

            # send ending
            yield create_event('content_block_stop', {'type': 'content_block_stop', 'index': 0})
            yield create_event('message_delta', {
                'type': 'message_delta',
                'delta': {'stop_reason': 'end_turn', 'stop_sequence': None},
                'usage': {'output_tokens': 12},
            })
            yield create_event('message_stop', {'type': 'message_stop'})

        else:
            raise Exception('Invalid request')
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=50600,host='0.0.0.0')