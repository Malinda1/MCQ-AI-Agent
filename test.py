import os
import tempfile
from core.google_drive import GoogleDriveUploader  # Adjust import path as needed
from config.settings import settings

def create_test_file():
    """Create a simple test file"""
    temp_dir = tempfile.gettempdir()
    test_file_path = os.path.join(temp_dir, "test_upload.txt")
    
    with open(test_file_path, 'w') as f:
        f.write("This is a test file for Google Drive upload.\n")
        f.write("Created for testing purposes.\n")
        f.write("If you see this file in Google Drive, the upload worked!")
    
    print(f"✅ Test file created: {test_file_path}")
    return test_file_path

def test_settings():
    """Check if required settings are configured"""
    print("=== Checking Settings ===")
    
    required_settings = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET', 
        'GOOGLE_REFRESH_TOKEN',
        'GOOGLE_DRIVE_FOLDER_ID'
    ]
    
    for setting in required_settings:
        if hasattr(settings, setting) and getattr(settings, setting):
            print(f"✅ {setting}: Configured")
        else:
            print(f"❌ {setting}: Missing or empty")
            return False
    
    return True

def test_upload():
    """Test Google Drive upload functionality"""
    print("\n=== Testing Google Drive Upload ===")
    
    # Check settings first
    if not test_settings():
        print("❌ Settings configuration failed")
        return False
    
    # Create test file
    test_file_path = create_test_file()
    
    try:
        # Initialize uploader
        uploader = GoogleDriveUploader()
        print("✅ GoogleDriveUploader initialized")
        
        # Upload file
        file_id = uploader.upload_file(
            file_path=test_file_path,
            file_name="test_upload_file.txt"
        )
        
        if file_id:
            print(f"✅ File uploaded successfully!")
            print(f"📁 Google Drive File ID: {file_id}")
            print(f"🔗 View file at: https://drive.google.com/file/d/{file_id}/view")
            return True
        else:
            print("❌ Upload failed - no file ID returned")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    
    finally:
        # Cleanup test file
        try:
            os.remove(test_file_path)
            print(f"🗑️  Cleaned up test file: {test_file_path}")
        except:
            pass

def main():
    """Main test function"""
    print("🚀 Starting Google Drive Upload Test\n")
    
    success = test_upload()
    
    print("\n" + "="*40)
    if success:
        print("🎉 Google Drive upload test PASSED!")
        print("Check your Google Drive folder to confirm the file is there.")
    else:
        print("❌ Google Drive upload test FAILED!")
        print("Check your credentials and settings.")
    print("="*40)

if __name__ == "__main__":
    main()