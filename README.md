# SMS Bot for Spectrum

This repo is a for an SMS bot that was meant to help students checkin, RSVP, and otherwise get information about a student organization on the UTSA campus.  

## Brief Description
It uses Django and Celery connected through RabbitMQ. All services are setup to work in Docker. Originally it used the wit.ai API and was meant to be a bit more intelligent, but that service proved very buggy and unreliable so instead it just uses simple keyword matching. Most of the features work through the text interface or command line, no GUI was developed other than the Django admin console.

## Features
- Checkin at meetings with a short code
- Send out mass text messages to everyone in database
- RSVP for meetings or events
- Check how many people have RSVPd
- View attendance history
