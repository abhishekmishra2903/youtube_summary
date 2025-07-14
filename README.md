# youtube_summary
A multi-agent workflow classifies a YouTube video into 'entertainment' or 'educational'. For 'entertainment', it gives the summary, genre, and age-group, while for 'education', it gives 'title', 'summary', and 'prerequisites'

Steps to be followed to deploy it on AWS (EC2):

Step 1: Create an EC2 instance on aws, keep the OS as Amazon-linux, generate a key-value pair and download the pem file. Also make sure to tick HTTP in network settings. Create a custom TCP with port 8501 because this is the port which is used by default by streamlit applications.

Step 2: Install docker on local machine and create a docker-image with the following command. Note that if using mac, the default architecture of the image is arm64 which can have confilict with Amazon-linux OS at virtual machine, so we are using buildx method.

docker buildx build --platform linux/amd64 -t ad-generator:latest --load .

Step 3: Save the docker image as marketing.tar file in the working directory and provide a tag(latest) to the image.

docker save -o marketing.tar ad-generator:latest

Step 4: By default the pem file has too much access, so restrict the access with chmod method

chmod 400 marketing.pem

Step 5: With SCP( Secured Copy Protocol) copy the .tar file on virtual machine. Note that you need to provide public IPv4 address of your own instance in place of 13.233.79.194
scp -i marketing.pem marketing.tar ec2-user@13.233.79.194:~/

Step 6: Establish a Secure Shell connection with the virtual machine

ssh -i marketing.pem ec2-user@13.233.79.194

Step 6: Load the docker image file on the virtual machine

docker load -i marketing.tar

Step 7: Since .env file is not a part of the docker image. create the .env file with Gemini_api_key

nano .env 

Step 8: Run the instance

docker run -d --name marketing-app -p 8501:8501\
 --env-file .env ad-generator:latest

Step 9: Instead of Step 7 and 8, the API key can be directly passed while initiating. Replace 'you_actual_api_key_here' with Gemini API key before launcing the application.

docker run -d --name marketing-app -p 8501:8501 \
-e GEMINI_API_KEY="your_actual_api_key_here" \
ad-generator:latest


