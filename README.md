# Image Upload Service

This repository contains a Serverless-based application that allows users to upload images, list images, view/download images, and delete images. The service uses **AWS S3** for image storage, **AWS DynamoDB** for metadata storage, and **AWS Lambda** for function execution. It also uses **LocalStack** for local emulation of AWS services.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [Service Overview](#service-overview)
4. [API Endpoints](#api-endpoints)
5. [Testing Locally](#testing-locally)
6. [Deployment](#deployment)
7. [Clean Up](#clean-up)
8. [License](#license)

---

## Prerequisites

Before you can run this service, ensure that you have the following installed:

- **Node.js** (v10+)
- **npm** (Node package manager)
- **Docker** (for running LocalStack locally)
- **Python 3.7+** (for Lambda functions)
- **Serverless Framework** (for deployment)
- **AWS CLI** (for interacting with AWS services)

If you don’t have them installed, you can install them as follows:

1. Install [Node.js](https://nodejs.org/).
2. Install [AWS CLI](https://aws.amazon.com/cli/).
3. Install the [Serverless Framework](https://www.serverless.com/):

   ```bash
   npm install -g serverless

 ## Setup Instructions

 Follow these steps to set up the project on your local machine:

 git clone https://github.com/yourusername/image-upload-service.git
 cd image-upload-service

 ## Install Dependencies:

 Install all the required dependencies for both the Lambda functions and the local testing environment.

 pip install -r requirements.txt
 npm install

 ## Start LocalStack:

 docker-compose -f localstack-docker-compose.yml up

 ## Deployment
  ```serverless deploy --stage dev --region us-east-1```

 ## Service Overview

 This service provides the following functionality:

 Upload Image: Upload an image to S3 with metadata.

 List Images: Retrieve a list of all uploaded images (with filter support).

 View Image: Retrieve or download an image from S3 by its image_id.

 Delete Image: Remove an image from S3 and its metadata from DynamoDB.

 ## API Endpoints
    Below are the available API endpoints:

    Upload Image
        URL: /upload

        Method: POST

        Request Body: multipart/form-data (image file)

        Description: Upload an image and its metadata to S3 and DynamoDB.

    Example Request:
        POST: http://localhost:3000/upload

        Body: Choose form-data and select an image file to upload.


