#!/usr/bin/env python
from datetime import datetime, timedelta
from lead_gen.crew import  SalesTeamSupportCrew
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from base64 import b64encode
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

def run():
   
    inputs = {
         'instagram_url': 'https://www.instagram.com/dualbootpartners/',
         'linkedin_url': 'https://www.linkedin.com/company/dualbootpartners/',
         'website_url': 'https://dualbootpartners.com/',
            'city': 'United States',
    }
    
    leds_crew = SalesTeamSupportCrew()
    leds_crew.crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()
