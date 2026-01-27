from PIL import Image
import os

def process_icon(input_path, output_path=None):
    if output_path is None:
        output_path = input_path
        
    print(f"Processing: {input_path}")
    
    try:
        img = Image.open(input_path)
        img = img.convert("RGBA")
        
        datas = img.getdata()
        
        newData = []
        # Tolerance for "white". Background is likely pure white or near pure white.
        # Let's make it aggressive: any pixel "close to white" becomes transparent.
        threshold = 200 # More aggressive (was 240)
        
        for item in datas:
            # item is (R, G, B, A)
            # Check if pixel is "light" enough to be background
            if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                newData.append((255, 255, 255, 0)) # Transparent
            else:
                newData.append(item)
        
        img.putdata(newData)
        
        # Save intermediate state to check
        # img.save(output_path.replace(".png", "_debug.png"))

        # Crop to bounding box (remove empty transparent space)
        bbox = img.getbbox()
        if bbox:
            print(f"Original BBox: {bbox}")
            # Add a small padding if we crop closely
            img = img.crop(bbox)
            print(f"Cropped to: {bbox}")
        
        img.save(output_path, "PNG")
        print(f"Saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Path is relative to where script is run, assuming run from project root or backend
    icon_path = "../frontend/public/icon.png"
    # Adjust path if running from backend dir directly
    if not os.path.exists(icon_path):
         # Try absolute path based on user context if relative fails, or just simple check
         # Let's try to find it relative to this script
         script_dir = os.path.dirname(os.path.abspath(__file__))
         icon_path = os.path.join(script_dir, "../../frontend/public/icon.png")

    icon_path = os.path.abspath(icon_path)
    
    if os.path.exists(icon_path):
        process_icon(icon_path)
    else:
        print(f"File not found: {icon_path}")
