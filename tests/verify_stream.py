import json
import urllib.request
import sys

URL = "http://localhost:8000/api/process_stream"
PAYLOAD = {
    "url": "https://www.youtube.com/watch?v=gP4tSArYSKY",
    "mode": "local",
    "task_type": "transcribe"
}

def verify_stream():
    print(f"Testing SSE Stream from {URL}...")
    print(f"Target Video: {PAYLOAD['url']}")
    print("-" * 50)

    req = urllib.request.Request(
        URL, 
        data=json.dumps(PAYLOAD).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            for line in response:
                line = line.decode('utf-8').strip()
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    try:
                        data = json.loads(data_str)
                        if "stage" in data:
                            # Print Progress Bar visualization
                            stage = data['stage']
                            percent = data.get('progress', 0)
                            bar_length = 20
                            filled_length = int(bar_length * percent // 100)
                            bar = '█' * filled_length + '-' * (bar_length - filled_length)
                            print(f"\r[{bar}] {percent}% | Stage: {stage}", end="", flush=True)
                            
                            if stage == "complete":
                                print("\n\nVerification Successful! ✅")
                                print("Transcript Preview:", data.get('transcript', '')[:50] + "...")
                        elif "transcript" in data: # Final result payload logic might differ
                             print("\n\nVerification Successful! ✅")
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        print(f"\nFailed: {e}")

if __name__ == "__main__":
    verify_stream()
