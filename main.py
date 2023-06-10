import json
import boto3
import base64
from PIL import Image
from io import BytesIO

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Parse the body content
    body = json.loads(event["body"])
    flag = body.get("flag")
    image_content = body.get("image")

    # Decode and open the uploaded image
    user_image = Image.open(BytesIO(base64.b64decode(image_content)))

    # Download the flag image
    flag_key = f'flags/{flag}.png'
    flag_image = download_from_s3('country-background-flag-origin', flag_key)
    
    # Process the images
    combined_image = combine_images(user_image, flag_image)
    
    # Save the new image to a different S3 bucket
    output_key = f'output_{flag}.png'
    presigned_url = upload_to_s3('country-background-flag-destination', output_key, combined_image)
    
    # Return the presigned URL for the user to download
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'image_url': presigned_url})
    }

def download_from_s3(bucket, key):
    file_byte_string = s3_client.get_object(Bucket=bucket, Key=key)['Body'].read()
    return Image.open(BytesIO(file_byte_string))

def combine_images(user_image, flag_image):
    # Ensure both images are in RGBA mode to handle transparency correctly
    user_image = user_image.convert('RGBA')
    flag_image = flag_image.convert('RGBA')

    # Create a blank RGBA image with the size of the flag
    result_image = Image.new('RGBA', flag_image.size)

    # Paste the flag image onto the blank image
    result_image.paste(flag_image, (0, 0))

    # Calculate the position to center the user image
    width, height = flag_image.size
    user_width, user_height = user_image.size
    position = ((width - user_width) // 2, (height - user_height) // 2)

    # Paste the user image onto the flag background
    result_image.paste(user_image, position, user_image)

    # Return the combined image
    return result_image

def upload_to_s3(bucket, key, image):
    buffer = BytesIO()
    image.save(buffer, 'PNG')
    buffer.seek(0)
    
    # Upload to S3
    s3_client.upload_fileobj(buffer, bucket, key)

    # Generate a presigned URL
    url = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=300)
    
    return url
