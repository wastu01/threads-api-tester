from asyncio import threads
from math import e
from re import S
from flask import make_response, request, render_template, redirect, url_for # type: ignore

from src.threads_api import ThreadAPI
import json

def setup_routes(app, config, threadsAPI: ThreadAPI):
    @app.route('/callback')
    def auth():
        config.received_code = request.args.get('code')
        threadsAPI.set_auth_code(str(config.received_code))

        return render_template('auth.html')

    @app.route('/tokens', methods=['GET', 'POST'])
    def tokens():          

        # 檢查是否為 POST 請求
        if request.method == 'POST':
            # 確認表單中包含 image_url 和 account_id 兩個字段
            if 'image_url' in request.form and 'account_id' in request.form:
                image_url = request.form['image_url']  # 從表單中獲取圖片URL
                caption = request.form.get('caption', '')  # 獲取圖片描述，若無則為空字符串

                # 調用 upload_image 函數上傳圖片
                response = threadsAPI.upload_image(image_url, caption)
                # 檢查響應中是否包含錯誤訊息
                if response.get('error'):
                    print(f"Error uploading image: {response['error']}")  # 輸出錯誤訊息
        
        short_lived_access_token = threadsAPI.get_short_lived_access_token()
        if type(short_lived_access_token) is not str:
            response = make_response(short_lived_access_token['error'], 200) # type: ignore
            response.mimetype = "text/plain"
            return response
    
        long_lived_access_token = threadsAPI.get_long_lived_access_token()
        if type(long_lived_access_token) is not str:
            response = make_response(long_lived_access_token['error'], 200) # type: ignore
            response.mimetype = "text/plain"
            return response

        accounts = {}
        media_data = threadsAPI.get_recent_posts()
        # print("Type of media_data:", type(media_data))
        # print("Content of media_data:", media_data)
        accounts[threadsAPI.USER_ID] = {
            'media':  media_data.get('data', []),
            'info': threadsAPI.USER_ID
        }
        # print(type(accounts))
        # 寫入文件
        with open("accounts_data.txt", "w") as file:
            file.write(json.dumps(accounts, indent=4))  # 添加縮進，美化輸出

        
        user = threadsAPI.get_user_info()

        return render_template('tokens.html', 
            accounts=accounts, 
            short_lived_token_response=short_lived_access_token,
            long_lived_token_response=long_lived_access_token,
            code=threadsAPI.AUTH_CODE,
            user=user
        )

    # @app.route('/renew_tokens', methods=['POST'])
    # def renew_tokens():
    #     config.long_lived_token_response = get_long_lived_access_token(config.long_lived_token_response['access_token'], config.client_secret)
    #     return redirect(url_for('tokens'))
