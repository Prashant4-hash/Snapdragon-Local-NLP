import http.server
import socketserver
import json
import re
from collections import Counter
import pypdf
import docx

PORT = 8001

def parse_pdf(file_bytes):
    import io
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def parse_docx(file_bytes):
    import io
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])

def analyze_text(text):
    words = re.findall(r'\b\w+\b', text.lower())
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    word_count = len(words)
    sentence_count = len(sentences)
    
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that', 'these', 'those', 'as', 'from', 'be', 'has', 'have', 'had'}
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
    keywords = Counter(filtered_words).most_common(5)
    
    # Advanced Local Extractive Summary
    if sentence_count <= 2:
        summary = ". ".join(sentences) + "." if sentences else "No summary available."
    else:
        # Score sentences by frequency of key non-stop words
        word_freq = Counter(filtered_words)
        sentence_scores = {}
        for idx, sentence in enumerate(sentences):
            score = 0
            s_words = re.findall(r'\b\w+\b', sentence.lower())
            for w in s_words:
                if w in word_freq:
                    score += word_freq[w]
            sentence_scores[idx] = score / (len(s_words) + 1)  # Normalize by sentence length
        
        # Select top scored sentences across different paragraphs
        top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:3]
        top_indices.sort()  # Keep natural document flow
        
        summary = ". ".join([sentences[i] for i in top_indices]) + "."
    
    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "summary": summary,
        "keywords": keywords
    }

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Snapdragon Local NLP</title>
                <style>
                    body { font-family: Arial, sans-serif; background: #121212; color: #fff; padding: 20px; }
                    h1 { color: #E10000; display: flex; align-items: center; gap: 8px; }
                    .card { background: #1e1e1e; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #333; }
                    textarea { width: 100%; height: 120px; background: #2a2a2a; color: #fff; border: 1px solid #444; border-radius: 4px; padding: 10px; box-sizing: border-box; }
                    input[type="file"] { margin-bottom: 10px; color: #ccc; }
                    button { background: #E10000; color: #fff; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold; }
                    button:hover { background: #ff1a1a; }
                    #output p { margin: 8px 0; line-height: 1.5; }
                </style>
            </head>
            <body>
                <h1>⚡ Snapdragon Local Text Processing Assistant</h1>
                <div class="card">
                    <h3>Upload Document (.pdf, .docx, .txt)</h3>
                    <input type="file" id="fileInput" accept=".pdf,.docx,.txt"><br><br>
                    <h3>Or Paste Text Below</h3>
                    <textarea id="textInput" placeholder="Paste your text here..."></textarea><br><br>
                    <button onclick="processData()">Analyze Text</button>
                </div>
                
                <div class="card">
                    <h3>Analysis Results</h3>
                    <div id="output"><p>Results will appear here...</p></div>
                </div>

                <script>
                    async function processData() {
                        const fileInput = document.getElementById('fileInput');
                        const textInput = document.getElementById('textInput').value;

                        let bodyData;
                        let headers = {};

                        if (fileInput.files.length > 0) {
                            const formData = new FormData();
                            formData.append('file', fileInput.files[0]);
                            bodyData = formData;
                        } else if (textInput.trim() !== '') {
                            bodyData = textInput;
                            headers['Content-Type'] = 'text/plain; charset=utf-8';
                        } else {
                            alert('Please select a file or paste text first!');
                            return;
                        }

                        const response = await fetch('/analyze', {
                            method: 'POST',
                            headers: headers,
                            body: bodyData
                        });

                        const result = await response.json();
                        document.getElementById('output').innerHTML = `
                            <p><strong>Words:</strong> ${result.word_count} | <strong>Sentences:</strong> ${result.sentence_count}</p>
                            <p><strong>Summary:</strong> ${result.summary}</p>
                            <p><strong>Top Keywords:</strong> ${result.keywords.map(k => k[0] + ' (' + k[1] + ')').join(', ')}</p>
                        `;
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        if self.path == '/analyze':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            text_content = ""
            
            if b'filename="' in body:
                filename = body.split(b'filename="')[1].split(b'"')[0].lower()
                file_data = body.split(b'\r\n\r\n', 1)[1].rsplit(b'\r\n--', 1)[0]
                
                if filename.endswith(b'.pdf'):
                    text_content = parse_pdf(file_data)
                elif filename.endswith(b'.docx'):
                    text_content = parse_docx(file_data)
                elif filename.endswith(b'.txt'):
                    text_content = file_data.decode('utf-8', errors='ignore')
            else:
                text_content = body.decode('utf-8', errors='ignore')

            results = analyze_text(text_content)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode('utf-8'))

with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()