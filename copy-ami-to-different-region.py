import boto3
import time

SOURCE_REGION = 'ap-south-1'
DESTINATION_REGION = 'us-east-1'
INSTANCE_ID = 'i-0ba9f152beb641230'
AMI_NAME = 'custom-ami-name'

#Creating AMI from instance id in source region
def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    ami_name = f"{AMI_NAME}-{int(time.time())}"
    ec2_image = ec2.create_image(InstanceId=INSTANCE_ID, Name=ami_name, NoReboot=True)
    # return ec2_image
    image_id = ec2_image['ImageId']

    #Waiter to wait for image to become available
    waiter = ec2.get_waiter('image_available')
    waiter.wait(ImageIds=[image_id]) 
    print("Image Available")

#Copying AMI to other region
    ec2_target = boto3.client('ec2', DESTINATION_REGION)   
    copy_ami = ec2_target.copy_image(
        Name=ami_name,
        SourceImageId=image_id,
        SourceRegion= SOURCE_REGION
    )
    copy_id = copy_ami['ImageId']
    
    #Waiter to wait for image to become available
    waiter = ec2_target.get_waiter('image_available')
    waiter.wait(ImageIds=[copy_id]) 
    print(f"Image Available in {DESTINATION_REGION} region.")

    ec2.deregister_image(ImageId=image_id)
    print(f"Image id {image_id} deregistered successfully")