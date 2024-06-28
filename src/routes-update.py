from flask import Flask, make_response, request, render_template, redirect, url_for  # type: ignore
import threading
import time
import os


from src.threads_api import ThreadAPI

app = Flask(__name__)

class Config:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID", "your_default_client_id")  # 提供預設值或
        self.client_secret = os.getenv("CLIENT_SECRET", "your_default_client_secret")  # 提供預設值
        if not self.client_id or not self.client_secret:
            raise ValueError("CLIENT_ID and CLIENT_SECRET must be set")

        self.received_code = None

def setup_routes(app, config, threadsAPI):
    global posts  # 定義一個全局變量來存儲帖子數據
    posts = []

    def fetch_posts():
        global posts
        while True:
            try:
                new_posts = threadsAPI.get_recent_posts()
                posts = new_posts.get('data', [])
                print("Posts updated.")
            except Exception as e:
                print(f"Failed to fetch posts: {e}")
            time.sleep(60)  # 每60秒更新一次帖子

    # 在後台執行緒中運行 fetch_posts 函數
    thread = threading.Thread(target=fetch_posts)
    thread.daemon = True  # 將執行緒設置為守護執行緒，以便主程式結束時可以自動結束
    thread.start()

    @app.route('/callback')
    def auth():
        config.received_code = request.args.get('code')
        threadsAPI.set_auth_code(str(config.received_code))
        return render_template('auth.html')

    @app.route('/tokens', methods=['GET', 'POST'])
    def tokens():
        if request.method == 'POST':
            if 'image_url' in request.form and 'account_id' in request.form:
                image_url = request.form['image_url']
                caption = request.form.get('caption', '')
                response = threadsAPI.upload_image(image_url, caption)
                if response.get('error'):
                    print(f"Error uploading image: {response['error']}")

        short_lived_access_token = threadsAPI.get_short_lived_access_token()
        if type(short_lived_access_token) is not str:
            response = make_response(short_lived_access_token['error'], 200)
            response.mimetype = "text/plain"
            return response

        long_lived_access_token = threadsAPI.get_long_lived_access_token()
        if type(long_lived_access_token) is not str:
            response = make_response(long_lived_access_token['error'], 200)
            response.mimetype = "text/plain"
            return response

        accounts = {}
        media_data = threadsAPI.get_recent_posts()
        accounts[threadsAPI.USER_ID] = {
            'media': media_data.get('data', []),
            'info': threadsAPI.USER_ID
        }

        user = threadsAPI.get_user_info()

        return render_template('tokens.html',
                               accounts=accounts,
                               short_lived_token_response=short_lived_access_token,
                               long_lived_token_response=long_lived_access_token,
                               code=threadsAPI.AUTH_CODE,
                               user=user,
                               posts=posts)  # 傳遞更新後的帖子資料至前端

if __name__ == "__main__":
    config = Config()
    threadsAPI = ThreadAPI(config.client_id, config.client_secret)
    setup_routes(app, config, threadsAPI)
    app.run(debug=True)
