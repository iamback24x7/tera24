@app.route(rule='/api', methods=['GET'])
async def Api():
  try:
      url = request.args.get('url', 'No URL Provided')
      logging.info(f"Received request for URL: {url}")
      link_data = await fetch_download_link_async(url)
      if link_data:
          # Redirect to the direct download link of the first item
          download_link = link_data[0]["dlink"]
          logging.info(f"Redirecting to: {download_link}")
          return redirect(download_link)
      else:
          return jsonify({'status': 'error', 'message': 'No download link found', 'ShortLink': url})
  except Exception as e:
      logging.error(f"An error occurred: {e}")
      return jsonify({'status': 'error', 'message': str(e), 'Link': url})
