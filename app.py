import http.server
import socketserver
import urllib.parse
import re
import base64
import os
from collections import Counter

# 1. Path to your local logo image
IMAGE_PATH = r"C:\Users\hp\Pictures\Saved Pictures\napdragon-logo-vector-png_1020x.jpg"

# Convert local image to base64 for browser compatibility
logo_src = ""
if os.path.exists(IMAGE_PATH):
    with open(IMAGE_PATH, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        logo_src = f"data:image/jpeg;base64,{encoded_string}"

logo_html = f'<img src="{logo_src}" style="height: 32px; width: auto; object-fit: contain;">' if logo_src else '<div class="logo-icon">⚡</div>'

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snapdragon Local Text Summarizer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #08080a; color: #ffffff; min-height: 100vh; display: flex; flex-direction: column; justify-content: space-between; padding: 20px 40px; background-image: radial-gradient(circle at 10% 20%, rgba(225, 0, 0, 0.15) 0%, transparent 40%), radial-gradient(circle at 90% 50%, rgba(225, 0, 0, 0.1) 0%, transparent 40%); }
        .top-nav { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); }
        .logo-group { display: flex; align-items: center; gap: 12px; }
        .logo-icon { width: 32px; height: 32px; background: #e10000; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(225, 0, 0, 0.6); }
        .logo-text { font-size: 22px; font-weight: 700; letter-spacing: -0.5px; }
        .brand-divider { width: 1px; height: 24px; background: rgba(255, 255, 255, 0.2); margin: 0 10px; }
        .tagline { font-size: 12px; color: #888; line-height: 1.2; }
        .badges { display: flex; gap: 20px; align-items: center; font-size: 13px; color: #ccc; }
        .badge { display: flex; align-items: center; gap: 6px; }
        .badge-red { color: #ff3333; }
        
        .hero-section { max-width: 900px; margin: 30px auto 0; text-align: center; width: 100%; }
        .title-container { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 8px; }
        .main-title { font-size: 36px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
        .highlight { color: #e10000; }
        .sub-title { font-size: 14px; color: #aaa; margin-bottom: 30px; font-style: italic; }

        .card-box { background: rgba(15, 15, 20, 0.7); border: 1px solid #ff1a1a; border-radius: 16px; padding: 24px; box-shadow: 0 0 25px rgba(225, 0, 0, 0.25), inset 0 0 15px rgba(225, 0, 0, 0.1); backdrop-filter: blur(10px); position: relative; margin-bottom: 25px; text-align: left; }
        .card-header-pill { position: absolute; top: 16px; right: 20px; background: rgba(255, 0, 0, 0.15); border: 1px solid rgba(255, 0, 0, 0.4); padding: 4px 12px; border-radius: 20px; font-size: 11px; color: #ff8888; font-weight: 600; display: flex; align-items: center; gap: 6px; }
        .card-header-pill::before { content: "✦"; color: #e10000; }
        
        textarea { width: 100%; height: 140px; background: transparent; border: none; outline: none; color: #fff; font-size: 15px; resize: vertical; margin-top: 10px; margin-bottom: 15px; }
        textarea::placeholder { color: #555; }

        .btn-submit { background: linear-gradient(135deg, #e10000 0%, #990000 100%); color: white; border: none; padding: 12px 28px; font-size: 15px; font-weight: 700; border-radius: 10px; cursor: pointer; display: flex; align-items: center; gap: 10px; box-shadow: 0 0 15px rgba(225, 0, 0, 0.5); transition: all 0.2s ease; }
        .btn-submit:hover { transform: translateY(-1px); box-shadow: 0 0 25px rgba(225, 0, 0, 0.8); }

        .results-box { background: rgba(20, 20, 25, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #e10000; border-radius: 12px; padding: 20px; margin-top: 20px; text-align: left; }
        .results-box h3 { color: #ff4d4d; font-size: 16px; margin-bottom: 8px; font-weight: 700; text-transform: uppercase; }
        .results-box p, .results-box ul { font-size: 14px; color: #ddd; margin-bottom: 12px; line-height: 1.5; }
        .results-box ul { list-style-position: inside; padding-left: 5px; }

        .bottom-features { display: flex; justify-content: space-around; align-items: center; padding-top: 30px; border-top: 1px solid rgba(255, 255, 255, 0.08); width: 100%; max-width: 1000px; margin: 0 auto; }
        .feature-item { display: flex; align-items: center; gap: 12px; }
        .feature-icon { width: 36px; height: 36px; border-radius: 50%; background: rgba(225, 0, 0, 0.15); border: 1px solid rgba(225, 0, 0, 0.3); display: flex; align-items: center; justify-content: center; color: #ff3333; font-weight: bold; }
        .feature-title { font-size: 13px; font-weight: 700; color: #fff; }
        .feature-desc { font-size: 11px; color: #777; }
    </style>
</head>
<body>
    <div>
        <div class="top-nav">
            <div class="logo-group">
                <!--LOGO_SECTION-->
                <div class="logo-text">Snapdragon</div>
                <div class="brand-divider"></div>
                <div class="tagline">Smarter AI. Local.<br><strong>Your Device. Your Data.</strong></div>
            </div>
            <div class="badges">
                <div class="badge"><span class="badge-red">🔲</span> On-Device AI</div>
                <div class="badge"><span class="badge-red">🔒</span> Privacy First</div>
                <div class="badge badge-red">⚡ Powered by Snapdragon</div>
            </div>
        </div>

        <div class="hero-section">
            <div class="title-container">
                <h1 class="main-title">Snapdragon Local <br><span class="highlight">Text Processing Assistant</span></h1>
            </div>
            <p class="sub-title">On-Device, Privacy-First Local NLP Utility for Snapdragon PCs</p>

            <form method="POST">
                <div class="card-box">
                    <div class="card-header-pill">Local • Private • Fast</div>
                    <textarea name="text" placeholder="Paste your document or notes here..."><!--TEXT_VALUE--></textarea>
                    <button type="submit" class="btn-submit">
                        🔲 Analyze Document &rarr;
                    </button>
                </div>
            </form>

            <!--RESULTS_SECTION-->
        </div>
    </div>

    <div class="bottom-features">
        <div class="feature-item">
            <div class="feature-icon">🛡️</div>
            <div>
                <div class="feature-title">Your Data Stays</div>
                <div class="feature-desc">On Your Device</div>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">⚡</div>
            <div>
                <div class="feature-title">Fast & Efficient</div>
                <div class="feature-desc">Snapdragon NPU</div>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🔒</div>
            <div>
                <div class="feature-title">Privacy First</div>
                <div class="feature-desc">No Cloud Required</div>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🧠</div>
            <div>
                <div class="feature-title">Powerful NLP</div>
                <div class="feature-desc">Summarize • Extract • Analyze</div>
            </div>
        </div>
    </div>
</body>
</html>"""

def render_page(text_val="", results_val=""):
    page = HTML.replace("<!--LOGO_SECTION-->", logo_html)
    page = page.replace("<!--TEXT_VALUE-->", text_val)
    page = page.replace("<!--RESULTS_SECTION-->", results_val)
    return page

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(render_page().encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed = urllib.parse.parse_qs(post_data)
        text = parsed.get('text', [''])[0]

        results = ""
        if text.strip():
            sentences = re.split(r'(?<=[.!?]) +', text.strip())
            summary = " ".join(sentences[:min(3, len(sentences))])
            
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
            keywords = Counter(words).most_common(5)
            kw_list = "".join([f"<li><b>{w.capitalize()}</b> ({c} occurrences)</li>" for w, c in keywords])

            results = f"""
            <div class="results-box">
                <h3>📝 Key Summary</h3>
                <p>{summary}</p>
                <h3>📌 Key Keywords Extracted</h3>
                <ul>{kw_list or 'None'}</ul>
                <h3>📊 Metrics</h3>
                <p>Total Words: {len(text.split())} | Total Sentences: {len(sentences)}</p>
            </div>
            """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(render_page(text, results).encode("utf-8"))

if __name__ == "__main__":
    PORT = 8001
    print(f"Running locally at http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()