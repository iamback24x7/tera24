from flask import Flask, request, redirect, jsonify
import os
import aiohttp
import asyncio
import logging
from urllib.parse import parse_qs, urlparse

app = Flask(__name__)

# (Cookies and headers definitions remain the same)

def find_between(string, start, end):
    start_index = string.find(start) + len(start)
    end_index = string.find(end, start_index)
    return string[start_index:end_index]

async def fetch_download_link_async(url):
    try:
        async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
            async with session.get(url) as response1:
                response1.raise_for_status()
                response_data = await response1.text()
                js_token = find_between(response_data, 'fn%28%22', '%22%29')
                log_id = find_between(response_data, 'dp-logid=', '&')

                if not js_token or not log_id:
                    return None

                request_url = str(response1.url)
                surl = request_url.split('surl=')[1]
                params = {
                    'app_id': '250528',
                    'web': '1',
                    'channel': 'dubox',
                    'clienttype': '0',
                    'jsToken': js_token,
                    'dplogid': log_id,
                    'page': '1',
                    'num': '20',
                    'order': 'time',
                    'desc': '1',
                    'site_referer': request_url,
                    'shorturl': surl,
                    'root': '1'
                }

                async with session.get('https://www.1024tera.com/share/list', params=params) as response2:
                    response_data2 = await response2.json()
                    if 'list' not in response_data2:
                        return None

                    # If the first item is a directory, perform another request to list its content
                    if response_data2['list'][0]['isdir'] == "1":
                        params.update({
                            'dir': response_data2['list'][0]['path'],
                            'order': 'asc',
                            'by': 'name',
                            'dplogid': log_id
                        })
                        params.pop('desc')
                        params.pop('root')

                        async with session.get('https://www.1024tera.com/share/list', params=params) as response3:
                            response_data3 = await response3.json()
                            if 'list' not in response_data3:
                                return None
                            return response_data3['list']
                    return response_data2['list']
    except aiohttp.ClientResponseError as e:
        logging.error(f"Error fetching download link: {e}")
        return None

@app.route('/')
def hello_world():
    response = {'status': 'success', 'message': 'Working Fully', 'Contact': '@Devil_0p || @GuyXD'}
    return response

@app.route('/api', methods=['GET'])
async def api():
    try:
        url = request.args.get('url', None)
        if not url:
            return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

        logging.info(f"Received request for URL: {url}")
        link_data = await fetch_download_link_async(url)
        if link_data and len(link_data) > 0:
            # Redirect to the direct download link from the first item
            download_link = link_data[0]["dlink"]
            logging.info(f"Redirecting to download link: {download_link}")
            return redirect(download_link)
        else:
            return jsonify({'status': 'error', 'message': 'No download link found'}), 404
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/help', methods=['GET'])
async def help():
    try:
        response = {
            'Info': "Use the API by accessing the following URL format:",
            'Example': 'https://server_url/api?url=https://terafileshare.com/s/1_1SzMvaPkqZ-yWokFCrKyA'
        }
        return jsonify(response)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        response = {
            'Info': "Use the API by accessing the following URL format:",
            'Example': 'https://server_url/api?url=https://terafileshare.com/s/1_1SzMvaPkqZ-yWokFCrKyA'
        }
        return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
